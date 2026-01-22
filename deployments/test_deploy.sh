#!/usr/bin/env bash

# Run ansible playbook against Vagrant VM
# Requires sshpass if using password auth
# Usage: ./deploy_vagrant.sh

# Ensure script is run from project root or checks paths
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT="$SCRIPT_DIR/../.."

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
    
    # Check if any VM is running (naive check for 'running' string in status)
    # vagrant status --machine-readable returns state line like:
    # timestamps,target,state,running
    # We'll check for the backend machine specifically if possible, or any running machine
    
    # Using 'vagrant status' machine readable output
    STATUS=$(vagrant status --machine-readable | grep "backend,state," | cut -d, -f4)
    
    # Check if "running" is in the status output
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

# vault setup
echo "dummy_vault_password" > vault_pass.txt

# In the new structure, we don't need to copy/encrypt env.yml manually 
# because it's already in inventories/test/group_vars/all.yml
# We just need to make sure it's decrypted or use the vault pass if encrypted.
# Local test vars are currently plain text in inventories/test/group_vars/all.yml

echo "Running playbook..."
cd ansible/
ansible-playbook -i inventories/test/hosts.ini \
    playbooks/site.yml \
    --vault-password-file ../vault_pass.txt
cd ../

# Cleanup
rm vault_pass.txt