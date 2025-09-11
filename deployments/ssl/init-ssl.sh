#!/bin/bash

docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d your-domain.com \
  -d www.your-domain.com