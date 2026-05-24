#!/usr/bin/env bash
# Start script for Render deployment
# Using python -m gunicorn avoids PATH issues on Render
# This script runs migrations and starts the application

set -o errexit
set -o pipefail

echo "[start.sh] Starting application startup script"

echo "[start.sh] Running migrations"
python manage.py migrate --noinput

echo "[start.sh] Migrations complete"

echo "[start.sh] Launching Gunicorn with python -m"
exec python -m gunicorn \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 3 \
  --worker-class sync \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  nwo_portal.wsgi:application
