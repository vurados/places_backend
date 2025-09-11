#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec db pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Backup Redis
docker-compose exec redis redis-cli --rdb - > $BACKUP_DIR/redis_backup_$DATE.rdb

# Backup MinIO data (if using local storage)
tar -czf $BACKUP_DIR/minio_backup_$DATE.tar.gz ./data/minio

# Encrypt backups (optional)
# gpg --encrypt --recipient your-email@example.com $BACKUP_DIR/db_backup_$DATE.sql

# Rotate backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql" -type f -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -type f -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -type f -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR"