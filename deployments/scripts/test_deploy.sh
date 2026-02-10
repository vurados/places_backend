#!/usr/bin/env bash

# Exit on error
set -e

# Configuration
VAULT_ADDR="http://192.168.56.2:8200"
VAULT_KEYS_FILE="vault_keys.json"
ENV_FILE=".env"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    if ! command -v jq &> /dev/null; then
        error "jq is required but not installed. Please install it (e.g., sudo apt install jq)."
        exit 1
    fi
    if ! command -v curl &> /dev/null; then
        error "curl is required but not installed."
        exit 1
    fi
    if ! command -v vagrant &> /dev/null; then
        error "vagrant is required but not installed."
        exit 1
    fi
    if ! command -v ansible-playbook &> /dev/null; then
        error "ansible-playbook is required but not installed."
        exit 1
    fi
}

check_vagrant() {
    log "Checking Vagrant status..."
    cd "$PROJECT_ROOT"
    
    if [ ! -f "Vagrantfile" ]; then
        error "Vagrantfile not found in $PROJECT_ROOT"
        exit 1
    fi
    
    # Check if backend VM is running
    STATUS=$(vagrant status --machine-readable | grep "backend,state," | cut -d, -f4)
    
    if [[ "$STATUS" != *"running"* ]]; then
        warn "Vagrant VM is not running (Status: $STATUS)."
        read -p "Do you want to start the Vagrant environment? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Starting Vagrant..."
            vagrant up
        else
            error "Aborted. VM must be running."
            exit 1
        fi
    else
        log "Vagrant VM is running."
    fi
}

run_bootstrap() {
    log "Running Bootstrap Playbook..."
    cd "$PROJECT_ROOT/ansible"
    ansible-playbook -i inventories/test/hosts.ini playbooks/bootstrap.yml
}

configure_vault() {
    log "Configuring Vault..."
    
    # 1. Check Initialization
    INIT_STATUS=$(curl -s "$VAULT_ADDR/v1/sys/init" | jq -r .initialized)
    
    if [ "$INIT_STATUS" == "false" ]; then
        log "Initializing Vault..."
        # Initialize and save keys
        curl -s --request POST --data '{"secret_shares": 1, "secret_threshold": 1}' "$VAULT_ADDR/v1/sys/init" > "$PROJECT_ROOT/$VAULT_KEYS_FILE"
        chmod 600 "$PROJECT_ROOT/$VAULT_KEYS_FILE"
        log "Vault initialized. Keys saved to $PROJECT_ROOT/$VAULT_KEYS_FILE"
    else
        log "Vault is already initialized."
        if [ ! -f "$PROJECT_ROOT/$VAULT_KEYS_FILE" ]; then
             warn "Vault is initialized but $VAULT_KEYS_FILE is missing. Make sure you have the keys to unseal!"
             # In a real script we might prompt for the key, but for now we assume it might be unsealed or user has to handle it.
        fi
    fi
    
    # Load Keys
    if [ -f "$PROJECT_ROOT/$VAULT_KEYS_FILE" ]; then
        UNSEAL_KEY=$(jq -r .keys_base64[0] "$PROJECT_ROOT/$VAULT_KEYS_FILE")
        ROOT_TOKEN=$(jq -r .root_token "$PROJECT_ROOT/$VAULT_KEYS_FILE")
    else
        # If we don't have the file, we can't automate unsealing if it's sealed.
        warn "No keys file found. Skipping automated unseal."
    fi

    # 2. Unseal
    SEAL_STATUS=$(curl -s "$VAULT_ADDR/v1/sys/seal-status" | jq -r .sealed)
    if [ "$SEAL_STATUS" == "true" ]; then
        if [ -z "$UNSEAL_KEY" ]; then
            error "Vault is sealed and no unseal key found in $VAULT_KEYS_FILE."
            exit 1
        fi
        log "Unsealing Vault..."
        curl -s --request POST --data "{\"key\": \"$UNSEAL_KEY\"}" "$VAULT_ADDR/v1/sys/unseal" > /dev/null
    else
        log "Vault is already unsealed."
    fi

    # Check unseal again
    SEAL_STATUS=$(curl -s "$VAULT_ADDR/v1/sys/seal-status" | jq -r .sealed)
    if [ "$SEAL_STATUS" == "true" ]; then
        error "Failed to unseal Vault."
        exit 1
    fi

    if [ -z "$ROOT_TOKEN" ]; then
        warn "No root token found. Skipping configuration steps (Auth/Secrets/Policies)."
        return
    fi

    # Helper for authenticated curl
    vault_curl() {
        curl -s -H "X-Vault-Token: $ROOT_TOKEN" "$@"
    }
    
    # 3. Enable KV Secrets Engine
    log "Enabling KV secrets engine at 'secret/'..."
    # Check if mounted
    MOUNTS=$(vault_curl "$VAULT_ADDR/v1/sys/mounts")
    if echo "$MOUNTS" | jq -e '."secret/"' > /dev/null; then
        log "KV engine already enabled."
    else
        vault_curl --request POST --data '{"type": "kv", "options": {"version": "2"}}' "$VAULT_ADDR/v1/sys/mounts/secret"
    fi

    # 4. Enable AppRole Auth
    log "Enabling AppRole auth..."
    AUTH_METHODS=$(vault_curl "$VAULT_ADDR/v1/sys/auth")
    if echo "$AUTH_METHODS" | jq -e '."approle/"' > /dev/null; then
        log "AppRole already enabled."
    else
        vault_curl --request POST --data '{"type": "approle"}' "$VAULT_ADDR/v1/sys/auth/approle"
    fi

    # 5. Create Policy
    log "Creating/Updating policy 'places-backend'..."
    POLICY='path "secret/data/places-backend" { capabilities = ["read"] } path "secret/data/monitoring" { capabilities = ["read"] }'
    # Escape quotes for JSON
    POLICY_JSON=$(jq -n --arg pol "$POLICY" '{"policy": $pol}')
    vault_curl --request PUT --data "$POLICY_JSON" "$VAULT_ADDR/v1/sys/policies/acl/places-backend" > /dev/null

    # 6. Create AppRole
    log "Creating/Updating AppRole 'places-backend'..."
    vault_curl --request POST --data '{"token_policies": "places-backend", "token_ttl": "1h", "token_max_ttl": "4h"}' "$VAULT_ADDR/v1/auth/approle/role/places-backend" > /dev/null

    # 7. Inject Secrets from .env
    if [ -f "$PROJECT_ROOT/$ENV_FILE" ]; then
        log "Injecting secrets from $ENV_FILE..."
        # Convert .env to JSON, excluding comments and empty lines
        # Using python to safeguard special chars in robust way or jq
        # Simple jq approach: read raw input, split by newline, filter empty/comments, parse K=V
        
        # We'll use a python one-liner for robustness with .env parsing
        JSON_PAYLOAD=$(python3 -c "
import json
import os

env_vars = {}
with open('$PROJECT_ROOT/$ENV_FILE', 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        try:
            key, value = line.split('=', 1)
            # Remove quotes if present
            if (value.startswith('\"') and value.endswith('\"')) or (value.startswith('\'') and value.endswith('\n')):
                 value = value[1:-1]
            env_vars[key] = value
        except ValueError:
            continue

print(json.dumps({'data': env_vars}))
")
        vault_curl --request POST --data "$JSON_PAYLOAD" "$VAULT_ADDR/v1/secret/data/places-backend" > /dev/null
        
        # Also inject dummy monitoring secrets if needed, or just rely on backend secrets
        log "Secrets injected."
    else
        warn "$ENV_FILE not found. Skipping secret injection."
    fi

    # 8. Get RoleID and SecretID
    log "Generating Credentials..."
    ROLE_ID=$(vault_curl "$VAULT_ADDR/v1/auth/approle/role/places-backend/role-id" | jq -r .data.role_id)
    SECRET_ID=$(vault_curl --request POST "$VAULT_ADDR/v1/auth/approle/role/places-backend/secret-id" | jq -r .data.secret_id)

    if [ "$ROLE_ID" == "null" ] || [ "$SECRET_ID" == "null" ]; then
        error "Failed to retrieve AppRole credentials."
        exit 1
    fi
    
    log "Credentials generated."
    
    # Export for next step
    export VAULT_ROLE_ID="$ROLE_ID"
    export VAULT_SECRET_ID="$SECRET_ID"
}

run_deploy() {
    log "Running Deploy Playbook..."
    cd "$PROJECT_ROOT/ansible"
    
    # Check if we have credentials
    if [ -z "$VAULT_ROLE_ID" ] || [ -z "$VAULT_SECRET_ID" ]; then
        error "Vault credentials missing. Cannot deploy."
        exit 1
    fi
    
    ansible-playbook -i inventories/test/hosts.ini playbooks/deploy.yml \
        -e "vault_role_id=$VAULT_ROLE_ID" \
        -e "vault_secret_id=$VAULT_SECRET_ID" \
        -e "vault_addr=$VAULT_ADDR"
}

# Main Execution Flow
check_dependencies
check_vagrant
run_bootstrap
configure_vault
run_deploy

log "Deployment Complete!"
log "Vault UI: $VAULT_ADDR/ui"
if [ -f "$PROJECT_ROOT/$VAULT_KEYS_FILE" ]; then
    log "Root Token is in $PROJECT_ROOT/$VAULT_KEYS_FILE"
else 
    warn "Root Token unknown (keys file missing)"
fi