#!/usr/bin/env bash

# Exit on error
set -e

echo "Starting deployment..."

# Ensure script is run from project root or checks paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$PROJECT_ROOT"

# Pull latest changes
git pull origin main

# Pull latest Docker images
docker compose -f compose/docker-compose.yml -f compose/docker-compose.monitoring.yml pull

# Recreate containers
docker compose -f compose/docker-compose.yml -f compose/docker-compose.monitoring.yml up -d --force-recreate

# Run migrations
docker compose -f compose/docker-compose.yml exec app alembic upgrade head

# Clean up old images
docker system prune -f

echo "Deployment completed successfully!"