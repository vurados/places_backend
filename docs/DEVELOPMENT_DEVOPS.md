# Development DevOps Guide

This guide focuses on local infrastructure testing and DevOps workflows using Vagrant. Use this environment to test Ansible playbooks and full stack deployment locally before pushing to production.

## Prerequisites

### Required Software

- **Ansible** 2.9+
- **Vagrant** 2.2+
- **VirtualBox or libvirt** (Vagrant provider)

### Install Ansible

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ansible

# macOS
brew install ansible
```

### Install Vagrant

```bash
# Ubuntu/Debian
sudo apt install vagrant

# macOS
brew install vagrant
```

---

## Local Testing with Vagrant

Test the full deployment locally before deploying to production.

### 1. Start Vagrant VM

```bash
vagrant up
```

This creates an Ubuntu 22.04 VM at `192.168.56.2`.

### 2. Run Test Deployment

```bash
./deployments/scripts/test_deploy.sh
```

**What this script does:**

- Checks Vagrant is installed and VM is running
- Encrypts `ansible/inventories/test/group_vars/all.yml` with Ansible Vault
- Runs Ansible playbook against the Vagrant VM
- Deploys all services (Nginx, App, PostgreSQL, Redis, MinIO)
- Generates self-signed SSL certificates
- Cleans up temporary files

### 3. Verify Deployment

```bash
# From host machine
curl -k https://192.168.56.2/health

# Expected response
{"status":"healthy"}
```

### 4. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| API | <https://192.168.56.2> | - |
| API Docs | <https://192.168.56.2/docs> | - |
| MinIO Console | <http://192.168.56.2:9001> | See `ansible/inventories/test/group_vars/all.yml` |

### 5. SSH into VM

```bash
vagrant ssh backend
```

### 6. View Logs

```bash
vagrant ssh backend -c "sudo docker logs places_backend-app-1 --tail 50"
```

### 7. Destroy VM

When finished testing:

```bash
vagrant destroy -f
```
