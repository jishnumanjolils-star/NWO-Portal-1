#!/usr/bin/env bash
# NWO Portal - Render Deployment Start Script
# This script safely manages migrations and starts the application

set -o errexit
set -o pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging helper
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log "Starting NWO Portal application"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    error "DATABASE_URL environment variable is not set!"
    exit 1
fi

log "Database URL: ${DATABASE_URL%%@*}@***"

# Attempt to run migrations
log "Running Django migrations..."
if python manage.py migrate --noinput 2>&1; then
    log "Migrations completed successfully"
else
    error "Migrations failed"
    exit 1
fi

log "Creating default division users..."
if python manage.py create_division_users 2>&1; then
    log "Default division users created successfully"
else
    error "Creating default division users failed"
    exit 1
fi

log "Populating Telephone Exchanges (TE Master List)..."
if python populate_exchanges.py 2>&1; then
    log "TE population completed (idempotent)."
else
    warn "TE population encountered an issue (non-critical), continuing..."
fi

log "Fixing user passwords to match deployment defaults..."
if python manage.py fix_user_passwords 2>&1; then
    log "User passwords fixed successfully"
else
    warn "Password fix encountered an issue (non-critical), continuing..."
fi

# Verify gunicorn is available
log "Checking Gunicorn installation..."
if ! python -m gunicorn --version &>/dev/null; then
    error "Gunicorn not found. Please check requirements.txt"
    exit 1
fi

log "Starting Gunicorn application server"
log "Binding to 0.0.0.0:${PORT:-8000}"

# Start Gunicorn with python -m for better module resolution
exec python -m gunicorn \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 3 \
  --worker-class sync \
  --timeout 60 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  nwo_portal.wsgi:application
