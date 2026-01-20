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
# Ensure group_vars directory exists
mkdir -p deployments/ansible/group_vars/all

# Copy vagrant vars to the expected env file location
cp deployments/ansible/test_vars.yml deployments/ansible/group_vars/all/env.yml

# Check if file exists before encrypting
if [ ! -f "deployments/ansible/group_vars/all/env.yml" ]; then
    echo "Error: env.yml not found!"
    exit 1
fi

echo "Encrypting vars..."
ansible-vault encrypt deployments/ansible/group_vars/all/env.yml --vault-password-file vault_pass.txt

echo "Running fast API update..."
ansible-playbook -i deployments/ansible/test_inventory.ini \
    deployments/ansible/update_api.yml \
    --vault-password-file vault_pass.txt

# Cleanup
rm vault_pass.txt
rm -rf deployments/ansible/group_vars
