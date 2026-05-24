#!/usr/bin/env bash
# Start script for Render deployment
# Using python -m gunicorn avoids PATH issues

set -o errexit

echo "====== STARTING GUNICORN SERVER ======"

# Use python -m gunicorn to avoid PATH issues on Render
python -m gunicorn \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 3 \
  --worker-class sync \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  nwo_portal.wsgi:application

echo "====== GUNICORN SERVER STOPPED ======"
