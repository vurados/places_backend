#!/usr/bin/env bash

# Function to check if Vagrant VM is running
check_vagrant() {
    if [ -f "Vagrantfile" ]; then
        STATUS=$(vagrant status --machine-readable | grep "backend,state," | cut -d, -f4)
        if [ "$STATUS" == "running" ]; then
            echo "Vagrant VM is running."
        else
            echo "Vagrant VM is NOT running. Starting it..."
            vagrant up
            if [ $? -eq 0 ]; then
                echo "Vagrant VM started successfully."
            else
                echo "Failed to start Vagrant VM."
                exit 1
            fi
        fi
    else
        echo "No Vagrantfile found. Skipping Vagrant check."
    fi
}

check_vagrant

# vault setup
echo "dummy_vault_password" > vault_pass.txt

echo "Running fast API update..."
cd ansible/
ansible-playbook -i inventories/test/hosts.ini \
    playbooks/update_api.yml \
    --vault-password-file ../vault_pass.txt
cd ../

# Cleanup
rm vault_pass.txt
