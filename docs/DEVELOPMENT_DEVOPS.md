# DevOps & Infrastructure Development Guide

This guide is for testing the full infrastructure stack, including Nginx reverse proxies, monitoring (Prometheus/Grafana), and Ansible deployment roles. It uses Vagrant to simulate a production-like target environment.

## Prerequisites

- **Vagrant**
- **VirtualBox** (or Libvirt/Docker provider for Vagrant)
- **Ansible**
- **sshpass** (optional, for password auth)

## Infrastructure Testing Workflow

### 1. Provision the Target VM

Start the backend VM defined in the project root:

```bash
vagrant up
```

### 2. Run Deployment Roles

Use the test deploy script to run the Ansible playbook against the Vagrant VM:

```bash
./deployments/test_deploy.sh
```

This script:

1. Syncs project files to `/opt/places_backend` on the VM.
2. Generates self-signed SSL certificates.
3. Sets up Nginx and Internal Proxy configurations.
4. Starts the full Docker stack (App + Monitoring).

### 3. Access Internal Tools

Administrative tools are bound to `localhost` within the VM. Use the tunnel script to access them from your host:

```bash
./deployments/connect_internal.sh
```

Access via:

- **Prometheus**: `http://prometheus.internal:8080`
- **Grafana**: `http://grafana.internal:8080`
- **Portainer**: `http://portainer.internal:8080`

## Common DevOps Tasks

### Debugging Ansible

Run roles with higher verbosity:

```bash
ansible-playbook -i deployments/ansible/test_inventory.ini \
    deployments/ansible/playbook.yml -vvv
```

### Verifying Nginx Config

SSH into the shell and test Nginx configurations:

```bash
vagrant ssh backend
sudo docker exec places_backend-nginx-1 nginx -t
```

### Monitoring Health

Check if metrics are being scraped correctly via the Prometheus UI after establishing the SSH tunnel.
