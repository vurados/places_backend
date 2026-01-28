#!/bin/bash

# Ensure script is run from project root or checks paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$PROJECT_ROOT"

DOMAIN=vurados.ru
EMAIL=kryuchkov2020@gmail.com # почта для Let's Encrypt
DATA_PATH="./data/certbot/conf"
WEBROOT_PATH="./data/certbot/www"

if [ -d "$DATA_PATH/live/$DOMAIN" ]; then
  echo ">>> Сертификаты уже существуют: $DATA_PATH/live/$DOMAIN"
  exit 0
fi

echo ">>> Получение нового сертификата для $DOMAIN ..."

mkdir -p "$DATA_PATH" "$WEBROOT_PATH"

docker run --rm \
  -v "$DATA_PATH:/etc/letsencrypt" \
  -v "$WEBROOT_PATH:/data/letsencrypt" \
  certbot/certbot certonly \
    --webroot -w /data/letsencrypt \
    --email $EMAIL \
    -d $DOMAIN \
    --agree-tos \
    --no-eff-email

echo ">>> Сертификат получен!"
