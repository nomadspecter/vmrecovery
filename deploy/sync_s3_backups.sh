#!/bin/bash
# ==============================================================================
# AWS S3 Offsite Disaster Recovery Synchronization Script
# Automated Virtual Machine Recovery System (VMRecovery)
# ==============================================================================
# Synchronizes local standalone .ova appliance backups and SQLite database
# online backups to an Amazon S3 bucket, fulfilling the 3-2-1 backup strategy.
#
# Usage:
#   ./deploy/sync_s3_backups.sh [--dry-run] [--bucket BUCKET_NAME]
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source environment variables if present
if [ -f "$APP_DIR/.env" ]; then
    # shellcheck disable=SC1091
    source "$APP_DIR/.env" || true
fi
if [ -f "$APP_DIR/instance/vmrecovery.env" ]; then
    # shellcheck disable=SC1091
    source "$APP_DIR/instance/vmrecovery.env" || true
fi

S3_BUCKET="${VMR_S3_BUCKET:-vmrecovery-disaster-recovery-backups}"
BACKUP_DIR="${VMR_BACKUP_DIR:-$APP_DIR/backups}"
DB_BACKUP_DIR="${APP_DIR}/instance/backups"
STORAGE_CLASS="${VMR_S3_STORAGE_CLASS:-STANDARD_IA}"
DRY_RUN=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN="--dryrun"
            shift
            ;;
        --bucket)
            S3_BUCKET="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [--dry-run] [--bucket BUCKET_NAME]" >&2
            exit 1
            ;;
    esac
done

echo "========================================================================"
echo "VMRECOVERY: AWS S3 OFFSITE DISASTER RECOVERY SYNC"
echo "========================================================================"
echo "Timestamp:      $(date '+%Y-%m-%d %H:%M:%S')"
echo "Target S3 URI:  s3://${S3_BUCKET}/"
echo "Storage Class:  ${STORAGE_CLASS}"
if [ -n "$DRY_RUN" ]; then
    echo "Mode:           DRY RUN (Simulation - no data transferred)"
fi
echo "========================================================================"

# Check AWS CLI
if ! command -v aws >/dev/null 2>&1; then
    echo "Error: AWS CLI is not installed or not in PATH." >&2
    exit 1
fi

mkdir -p "$BACKUP_DIR" "$DB_BACKUP_DIR"

echo "1. Synchronizing VM Appliance Backups (.ova)..."
aws s3 sync "$BACKUP_DIR" "s3://${S3_BUCKET}/appliances/" \
    --storage-class "$STORAGE_CLASS" \
    --exclude "*" \
    --include "*.ova" \
    --include "*.json" \
    $DRY_RUN

echo "2. Synchronizing SQLite Online Database Hot Backups..."
aws s3 sync "$DB_BACKUP_DIR" "s3://${S3_BUCKET}/database/" \
    --storage-class "$STORAGE_CLASS" \
    --exclude "*" \
    --include "*.db" \
    --include "*.sqlite" \
    $DRY_RUN

echo "3. Offsite Backup Sync Status:"
if [ -z "$DRY_RUN" ]; then
    echo "   Listing remote disaster recovery repository:"
    aws s3 ls "s3://${S3_BUCKET}/" --recursive --human-readable || echo "   (Bucket query completed)"
fi

echo "========================================================================"
echo "AWS S3 Sync Completed Successfully at $(date '+%H:%M:%S')."
echo "========================================================================"
