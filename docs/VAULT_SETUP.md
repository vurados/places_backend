# Vault Initialization & Setup Guide

This guide provides step-by-step instructions for initializing HashiCorp Vault, setting up policies, and managing secrets for the Urban Places application.

## 1. Initialization (First Time Setup)

Vault starts in a "sealed" state. You must initialize it to generate the **Root Token** and **Unseal Keys**.

### Option A: Web GUI (Recommended for simplicity)

1. **Access Vault**: Open `http://<YOUR_SERVER_IP>:8200` in your browser.
2. **Initialize**:
    * Set **Key Shares** (e.g., 5) and **Key Threshold** (e.g., 3).
    * Click **Initialize**.
3. **Save Credentials**:
    * **IMPORTANT**: Copy the **Initial Root Token** and **Unseal Keys** immediately.
    * Store them securely (e.g., password manager, physically). You will *not* see them again.
4. **Continue**: Click to proceed to unseal.

### Option B: CLI

ssh into your server and run:

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
vault operator init
```

Save the output!

## 2. Unseal Vault

After initialization (and every restart), Vault is sealed.

### Web GUI

1. Enter one of your **Unseal Keys** and click **Unseal**.
2. Repeat until the threshold (e.g., 3/5) is met.

### CLI

```bash
vault operator unseal <Unseal_Key_1>
vault operator unseal <Unseal_Key_2>
vault operator unseal <Unseal_Key_3>
```

## 3. Enable Secret Engine

The application expects secrets at `secret/data/places-backend`. First, ensure the KV v2 engine is enabled.

### Web GUI

1. **Login** using your **Root Token**.
2. Click **Enable new engine** -> **KV**.
3. Path: `secret`.
4. Version: **2** (Important!).
5. Click **Enable Engine**.

### CLI

```bash
vault login <ROOT_TOKEN>
vault secrets enable -path=secret kv-v2
```

## 4. Create Secrets

Populate the secrets required by the application (see `README.md` for the list).

### Web GUI

1. Navigate to **secret** -> **Create secret**.
2. Path: `places-backend`.
3. Add Key-Value pairs:
    * `DB_PASSWORD` = `...`
    * `SECRET_KEY` = `...`
    * (Add all other required fields)
4. Click **Save**.

### CLI

```bash
vault kv put secret/places-backend \
    DB_PASSWORD="your_secure_password" \
    SECRET_KEY="your_secret_key" \
    ...
```

## 5. AppRole Setup (Authentication)

The application (Vault Agent) uses AppRole to authenticate.

### Manual Setup Steps

If you need to do this manually:

1. **Enable AppRole**: `vault auth enable approle`
2. **Create Policy**: Define what the app can read.

    ```hcl
    path "secret/data/places-backend" {
      capabilities = ["read"]
    }
    ```

3. **Create Role**: Bind the policy to a role named `places-backend-role`.
4. **Get Credentials**:
    * **Role ID**: `vault read auth/approle/role/places-backend-role/role-id`
    * **Secret ID**: `vault write -f auth/approle/role/places-backend-role/secret-id`

These credentials (`role_id` and `secret_id`) must be placed in `/opt/places_backend/deployments/configs/vault-agent/` on the server.
