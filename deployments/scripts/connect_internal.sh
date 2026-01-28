#!/usr/bin/env bash

# Default values
DEFAULT_USER="vagrant"
DEFAULT_HOST="192.168.56.2"
LOCAL_PORT=8080
REMOTE_PORT=8080

# Prompt function
prompt_value() {
    read -p "$1 [$2]: " val
    echo "${val:-$2}"
}

# Ensure script is run from project root or checks paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Get connection details
echo "Configure SSH Tunnel Connection:"
SERVER_USER=$(prompt_value "Enter SSH User" "$DEFAULT_USER")
SERVER_HOST=$(prompt_value "Enter Server IP/Host" "$DEFAULT_HOST")
IDENTITY_FILE="$PROJECT_ROOT/.vagrant/machines/backend/libvirt/private_key"

# Check if we need to ask for identity file (e.g., for AWS/VPS)
read -p "Use specific SSH key? (y/N): " use_key
if [[ $use_key =~ ^[Yy]$ ]]; then
    read -e -p "Enter path to SSH private key: " IDENTITY_FILE
fi

SSH_CMD="ssh -N -L $LOCAL_PORT:localhost:$REMOTE_PORT $SERVER_USER@$SERVER_HOST"
if [ ! -z "$IDENTITY_FILE" ]; then
    SSH_CMD="$SSH_CMD -i $IDENTITY_FILE"
fi

echo ""
echo "Opening secure tunnel to internal tools..."
echo "Running: $SSH_CMD"
echo ""
echo "You can now access your tools at:"
echo "------------------------------------------------"
echo "- Grafana:      http://grafana.internal:$LOCAL_PORT"
echo "- Portainer:    http://portainer.internal:$LOCAL_PORT"
echo "- Prometheus:   http://prometheus.internal:$LOCAL_PORT"
echo "- Alertmanager: http://alertmanager.internal:$LOCAL_PORT"
echo "------------------------------------------------"
echo "NOTE: Add these lines to your local /etc/hosts file:"
echo "127.0.0.1 grafana.internal portainer.internal prometheus.internal alertmanager.internal"
echo "------------------------------------------------"
echo "Press Ctrl+C to close the tunnel."

$SSH_CMD
