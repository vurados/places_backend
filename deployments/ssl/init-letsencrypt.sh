#!/bin/bash

set -e

DOMAIN=vurados.ru
EMAIL=kryuchkov2020@gmail.com # почта для Let's Encrypt
DATA_PATH="./deploy/certs"
WEBROOT_PATH="./deploy/certs-data"

if [ -d "$DATA_PATH" ]; then
  echo ">>> Сертификаты уже существуют: $DATA_PATH"
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
