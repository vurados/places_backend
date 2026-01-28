# Deployment Guide

This guide covers deploying the Urban Places Backend using Ansible, both for local testing with Vagrant and production deployment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Testing with Vagrant](#local-testing-with-vagrant)
- [Production Deployment](#production-deployment)
- [Ansible Vault Setup](#ansible-vault-setup)
- [SSL Certificates](#ssl-certificates)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Ansible** 2.9+
- **Vagrant** 2.2+ (for local testing)
- **VirtualBox or libvirt** (Vagrant provider)
- **Git**

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

---

## Production Deployment

### 1. Set Up Inventory

Edit `ansible/inventories/production/hosts.ini`:

```ini
[vps]
your-server-ip ansible_user=your_user ansible_ssh_private_key_file=~/.ssh/your_key
```

### 2. Create Production Variables

Edit `ansible/inventories/production/group_vars/all.yml`:

```yaml
db_user: "prod_user"
db_password: "strong_random_password"
# ... other variables
```

### 3. Encrypt with Ansible Vault

```bash
cd ansible
ansible-vault encrypt inventories/production/group_vars/all.yml
# Enter vault password when prompted
```

### 4. Run Deployment

The project provides three main playbooks for different scenarios:

| Playbook | Description | Usage |
|----------|-------------|-------|
| `bootstrap.yml` | Initial server setup (Docker, dependencies) | New server setup |
| `deploy.yml` | Application updates (Sync code, restart containers) | Regular updates |
| `site.yml` | Full flow (Bootstrap + Deploy) | Full site deployment |

**Example (Production Deployment):**

```bash
cd ansible

# First time setup
ansible-playbook -i inventories/production/hosts.ini playbooks/bootstrap.yml --ask-vault-pass

# Regular updates
ansible-playbook -i inventories/production/hosts.ini playbooks/deploy.yml --ask-vault-pass
```

### 5. Set Up Let's Encrypt

SSH into your server and run:

```bash
sudo docker compose --profile prod up -d
```

This starts Certbot which will:

- Obtain SSL certificates from Let's Encrypt
- Automatically renew certificates every 12 hours

---

## Ansible Vault Setup

### Creating the Vault Password File (Optional)

For CI/CD, store vault password in a file:

```bash
echo "your-vault-password" > ~/.vault_pass
chmod 600 ~/.vault_pass
```

Then use in GitLab CI:

```yaml
vault_password_variable: $ANSIBLE_VAULT_PASSWORD
```

### Encrypting Secrets

```bash
# Encrypt existing file
ansible-vault encrypt ansible/inventories/production/group_vars/all.yml

# Edit encrypted file
ansible-vault edit ansible/inventories/production/group_vars/all.yml

# Decrypt file (for debugging only!)
ansible-vault decrypt ansible/inventories/production/group_vars/all.yml
```

### Viewing Encrypted Content

```bash
ansible-vault view ansible/inventories/production/group_vars/all.yml
```

---

## SSL Certificates

### Development/Testing (Self-Signed)

For local Vagrant deployment, Ansible automatically generates self-signed certificates.

**Certificates location:** `/opt/places_backend/data/certbot/conf/live/{domain}/`

### Production (Let's Encrypt)

When `env_name: "prod"`, Certbot handles certificate generation:

1. **Initial Setup**: Ensure port 80 is accessible (for ACME challenge)
2. **Start with profile**: `docker compose --profile prod up -d`
3. **Verify certificates**: Check `/opt/places_backend/data/certbot/conf/live/{domain}/`

**Renewal**: Certbot automatically renews certificates every 12 hours.

### Force Certificate Renewal

```bash
sudo docker exec places_backend-certbot-1 certbot renew --force-renewal
sudo docker restart places_backend-nginx-1
```

---

## Environment Configuration

### Environment Modes

| Mode | Profile | Certbot | Certificates |
|------|---------|---------|--------------|
| `test` | None | Disabled | Self-signed |
| `prod` | `--profile prod` | Enabled | Let's Encrypt |

### Docker Compose Profiles

- **Default** (no profile): App, Nginx, DB, Redis, MinIO
- **prod**: Adds Certbot for Let's Encrypt
- **monitoring**: Adds Prometheus, Grafana (see [MONITORING.md](MONITORING.md))
- **portainer**: Adds Portainer for container management

### Environment Variables Flow

```
ansible/inventories/test/group_vars/all.yml (test) / ansible/inventories/production/group_vars/all.yml (prod)
           ↓
    Ansible Vault (encrypted)
           ↓
   Ansible Environment Variables
           ↓
   docker-compose.yml (${VAR})
           ↓
      Docker Containers
```

**Key Point**: Secrets are **never** stored in plain text on disk. They exist only:

1. Encrypted in Ansible Vault
2. In memory during Ansible execution
3. As environment variables in running containers

---

## Troubleshooting

### Vagrant VM Network Issues

**Problem**: DNS resolution failures inside containers

**Solution**: VM uses systemd-resolved which conflicts with Docker DNS

- Fix applied: Explicit DNS servers (`8.8.8.8`, `1.1.1.1`) in `docker-compose.yml`

```bash
# Test DNS from VM
vagrant ssh backend -c "ping -c 3 google.com"
```

### Nginx Not Starting

**Problem**: SSL certificate errors

**Solution**: Check certificate paths and permissions

```bash
vagrant ssh backend
sudo docker logs places_backend-nginx-1
ls -la /opt/places_backend/data/certbot/conf/live/192.168.56.2/
```

### Database Connection Failures

**Problem**: Wrong credentials or service names

**Solution**: Verify environment variables

```bash
# Check what the app sees
vagrant ssh backend -c "sudo docker logs places_backend-app-1 | grep 'Using database URI'"

# Should show: postgresql+asyncpg://test_user:test_password@db:5432/places_db
```

### Permission Denied on Logs

**Problem**: App can't write to `/var/log/`

**Solution**: Already fixed - logs write to `/app/logs/` (writable by `appuser`)

### Ansible Vault Password Issues

**Problem**: "ERROR! Vault password file not found"

**Solution**: Use `--ask-vault-pass` flag or set up vault password file

```bash
ansible-playbook -i inventory.ini deploy.yml --ask-vault-pass
```

### Port Already in Use

**Problem**: Port 80/443 already bound

**Solution**: Check for existing services

```bash
sudo netstat -tlnp | grep :80
sudo systemctl stop apache2  # or nginx, if running
```

---

## Next Steps

After successful deployment:

1. **Configure DNS**: Point your domain to the server IP
2. **Set up monitoring**: See [MONITORING.md](MONITORING.md)
3. **Configure backups**: Set up database and MinIO backups
4. **Review security**: Check [Security Checklist](#security-checklist)

### Security Checklist

- [ ] Firewall configured (allow only 80, 443, SSH)
- [ ] SSH key-based authentication enabled
- [ ] Ansible Vault passwords are strong and secure
- [ ] Database passwords rotated from defaults
- [ ] Let's Encrypt certificates installed (production)
- [ ] HTTPS redirect enabled
- [ ] Rate limiting configured in Nginx
- [ ] Regular security updates scheduled

---

## Additional Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [Vagrant Documentation](https://www.vagrantup.com/docs)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
