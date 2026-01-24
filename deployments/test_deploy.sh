#!/usr/bin/env bash

# Run ansible playbook against Vagrant VM
# Requires sshpass if using password auth
# Usage: ./deploy_vagrant.sh

# Ensure script is run from project root or checks paths
# If run from root, SCRIPT_DIR is deployments
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Function to check Vagrant status
check_vagrant() {
    if ! command -v vagrant &> /dev/null; then
        echo "Error: Vagrant is not installed or not in PATH."
        exit 1
    fi

    if [ ! -f "Vagrantfile" ]; then
        echo "Error: Vagrantfile not found in $(pwd)."
        exit 1
    fi
    
    # Check if any VM is running
    STATUS=$(vagrant status --machine-readable | grep "backend,state," | cut -d, -f4)
    
    if [[ "$STATUS" != *"running"* ]]; then
        echo "Vagrant VM is not running. Current status: $STATUS"
        read -p "Do you want to start the Vagrant VM now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Starting Vagrant VM..."
            vagrant up
            if [ $? -ne 0 ]; then
                echo "Error: Failed to start Vagrant VM."
                exit 1
            fi
        else
            echo "Aborting deployment. VM must be running."
            exit 1
        fi
    else
        echo "Vagrant VM is running."
    fi
}

check_vagrant

echo "Running playbook..."
cd ansible/
# Use vault password file from root if it exists
VAULT_OPT=""
if [ -f "../vault_pass.txt" ]; then
    VAULT_OPT="--vault-password-file ../vault_pass.txt"
fi

ansible-playbook -i inventories/test/hosts.ini \
    playbooks/site.yml \
    $VAULT_OPT
cd ../

echo "Deployment finished."