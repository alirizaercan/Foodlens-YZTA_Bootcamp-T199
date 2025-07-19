#!/bin/bash

# FoodLens PostgreSQL Database Backup Script
# This script creates automated backups of the FoodLens database
# Usage: ./backup_database.sh [environment]

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR/backups"
LOG_FILE="$SCRIPT_DIR/backup.log"
MAX_BACKUPS=30  # Keep last 30 backups

# Environment (default: development)
ENVIRONMENT=${1:-development}

# Load environment variables
if [ -f "$SCRIPT_DIR/../../.env" ]; then
    source "$SCRIPT_DIR/../../.env"
fi

# Database configuration based on environment
case $ENVIRONMENT in
    "production")
        DB_HOST=${PROD_DB_HOST:-localhost}
        DB_PORT=${PROD_DB_PORT:-5432}
        DB_NAME=${PROD_DB_NAME:-foodlens_prod}
        DB_USER=${PROD_DB_USER:-postgres}
        DB_PASSWORD=${PROD_DB_PASSWORD}
        ;;
    "staging")
        DB_HOST=${STAGING_DB_HOST:-localhost}
        DB_PORT=${STAGING_DB_PORT:-5432}
        DB_NAME=${STAGING_DB_NAME:-foodlens_staging}
        DB_USER=${STAGING_DB_USER:-postgres}
        DB_PASSWORD=${STAGING_DB_PASSWORD}
        ;;
    *)
        DB_HOST=${DEV_DB_HOST:-localhost}
        DB_PORT=${DEV_DB_PORT:-5432}
        DB_NAME=${DEV_DB_NAME:-foodlens_dev}
        DB_USER=${DEV_DB_USER:-postgres}
        DB_PASSWORD=${DEV_DB_PASSWORD}
        ;;
esac

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${ENVIRONMENT}_${TIMESTAMP}.sql"
COMPRESSED_BACKUP="$BACKUP_FILE.gz"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling function
handle_error() {
    log "ERROR: Backup failed at line $1"
    # Send notification (implement based on your needs)
    # curl -X POST "https://hooks.slack.com/..." -d "{'text':'FoodLens DB Backup Failed'}"
    exit 1
}

trap 'handle_error $LINENO' ERR

log "Starting backup for $ENVIRONMENT environment"
log "Database: $DB_NAME on $DB_HOST:$DB_PORT"

# Set PostgreSQL password
export PGPASSWORD="$DB_PASSWORD"

# Create database backup
log "Creating backup: $BACKUP_FILE"
pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --no-password \
    --verbose \
    --clean \
    --if-exists \
    --create \
    --format=plain \
    --file="$BACKUP_FILE"

# Verify backup was created
if [ ! -f "$BACKUP_FILE" ]; then
    log "ERROR: Backup file was not created"
    exit 1
fi

# Get backup file size
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "Backup created successfully: $BACKUP_SIZE"

# Compress backup
log "Compressing backup..."
gzip "$BACKUP_FILE"

if [ -f "$COMPRESSED_BACKUP" ]; then
    COMPRESSED_SIZE=$(du -h "$COMPRESSED_BACKUP" | cut -f1)
    log "Backup compressed successfully: $COMPRESSED_SIZE"
else
    log "ERROR: Backup compression failed"
    exit 1
fi

# Create backup metadata
METADATA_FILE="$BACKUP_DIR/${DB_NAME}_${ENVIRONMENT}_${TIMESTAMP}.meta"
cat > "$METADATA_FILE" << EOF
{
    "environment": "$ENVIRONMENT",
    "database": "$DB_NAME",
    "host": "$DB_HOST",
    "port": "$DB_PORT",
    "backup_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "backup_file": "$(basename "$COMPRESSED_BACKUP")",
    "original_size": "$BACKUP_SIZE",
    "compressed_size": "$COMPRESSED_SIZE",
    "backup_type": "full",
    "created_by": "$(whoami)",
    "script_version": "1.0"
}
EOF

log "Metadata file created: $METADATA_FILE"

# Clean up old backups (keep only last MAX_BACKUPS)
log "Cleaning up old backups (keeping last $MAX_BACKUPS)..."
cd "$BACKUP_DIR"
ls -t ${DB_NAME}_${ENVIRONMENT}_*.sql.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f
ls -t ${DB_NAME}_${ENVIRONMENT}_*.meta 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f

# Count remaining backups
BACKUP_COUNT=$(ls -1 ${DB_NAME}_${ENVIRONMENT}_*.sql.gz 2>/dev/null | wc -l)
log "Cleanup completed. $BACKUP_COUNT backups remaining."

# Verify backup integrity (optional)
if command -v pg_restore &> /dev/null; then
    log "Verifying backup integrity..."
    if pg_restore --list "$COMPRESSED_BACKUP" > /dev/null 2>&1; then
        log "Backup integrity verified successfully"
    else
        log "WARNING: Backup integrity check failed"
    fi
fi

# Clear password from environment
unset PGPASSWORD

log "Backup process completed successfully"
log "Backup location: $COMPRESSED_BACKUP"

# Send success notification (implement based on your needs)
# curl -X POST "https://hooks.slack.com/..." -d "{'text':'FoodLens DB Backup Completed Successfully'}"

exit 0
