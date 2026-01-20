#!/usr/bin/env bash

# Exit on error
set -e

echo "Starting deployment..."

# Pull latest changes
git pull origin main

# Pull latest Docker images
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml pull

# Recreate containers
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d --force-recreate

# Run migrations
docker-compose exec app alembic upgrade head

# Clean up old images
docker system prune -f

echo "Deployment completed successfully!"