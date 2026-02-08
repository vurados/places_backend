# Production Deployment Guide

This guide covers the step-by-step process for deploying the Urban Places Backend to a production server (VPS).

## Prerequisites

1. **Server**: A clean Ubuntu 22.04+ VPS with root/sudo access.
2. **Controller Machine**: Your local machine with:
    * **Ansible** 2.9+ installed.
    * **Git** installed.
    * **SSH Key**: Your public SSH key must be added to the server's `~/.ssh/authorized_keys`.

## Deployment Workflow

### 1. Clone the Project

Verify you have the latest version of the code:

```bash
git clone https://github.com/vurados/places_backend.git
cd places_backend
```

### 2. Configure Inventory

Define your target server IP address.

Edit `ansible/inventories/production/hosts.ini`:

```ini
[vps]
<YOUR_SERVER_IP> ansible_user=root ansible_ssh_private_key_file=~/.ssh/id_rsa
```

*Replace `<YOUR_SERVER_IP>` with your actual server IP.*

> [!CAUTION]
> **Use a Sudo User**: For security, avoid using `root` directly. Create a dedicated user with `sudo` privileges (e.g., `deploy`) and use that in your inventory:
> `ansible_user=deploy`

### 3. Bootstrap Server

Run the `bootstrap.yml` playbook. This installs Docker, Nginx, Python dependencies, and **HashiCorp Vault**.

```bash
cd ansible
ansible-playbook -i inventories/production/hosts.ini playbooks/bootstrap.yml
```

### 4. Initialize & Configure Vault

**STOP!** Before deploying the application, you must initialize Vault and set up the secrets.

> [!IMPORTANT]
> Follow the **[Vault Initialization & Setup Guide](VAULT_SETUP.md)** to:
>
> 1. Initialize Vault & get Root Token.
> 2. Create the `secret/places-backend` KV secrets.
> 3. Generate **Role ID** and **Secret ID** for the AppRole.

### 5. Deploy Application

Once Vault is ready and you have your `Role ID` and `Secret ID`, run the deployment.

Pass the Vault credentials as extra variables (`-e`).

```bash
ansible-playbook -i inventories/production/hosts.ini playbooks/deploy.yml \
  -e "vault_role_id=<YOUR_ROLE_ID>" \
  -e "vault_secret_id=<YOUR_SECRET_ID>" \
  -e "env_name=prod"
```

**What this does:**

1. Syncs project files to `/opt/places_backend`.
2. Provisions Vault Agent with the provided Role/Secret IDs.
3. Starts Vault Agent to generate `secrets.env`.
4. Starts the application stack via Docker Compose.
5. Sets up Let's Encrypt SSL (if `env_name=prod`).

### 6. Verify Deployment

SSH into your server and check the status:

```bash
ssh root@<YOUR_SERVER_IP>

# Check containers
docker ps

# Check Vault Agent logs (to verify secret generation)
docker logs vault-agent

# Check App logs
docker logs places_backend-app-1
```

## Troubleshooting

### "secrets.env not generated"

Check `docker logs vault-agent`. Common errors:

* Invalid `role_id` or `secret_id`.
* Vault is sealed (Check `VAULT_SETUP.md` for unsealing).
* Policy does not allow reading `secret/data/places-backend`.
