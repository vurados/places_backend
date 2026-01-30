vault {
  # Address is set via VAULT_ADDR environment variable
}

auto_auth {
  method "approle" {
    config = {
      role_id_file_path   = "/etc/vault-agent/role_id"
      secret_id_file_path = "/etc/vault-agent/secret_id"
      remove_secret_id_on_read = false
    }
  }

  sink "file" {
    config = {
      path = "/tmp/vault_token"
    }
  }
}

template {
  source      = "/etc/vault-agent/dotenv.ctmpl"
  destination = "/app/.env"
}
