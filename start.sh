#!/usr/bin/env bash
set -o errexit
set -o pipefail

 echo "[start.sh] starting application startup script"

echo "[start.sh] running migrations"
python manage.py migrate --noinput

echo "[start.sh] migrations complete"

echo "[start.sh] launching gunicorn"
exec python -m gunicorn --bind 0.0.0.0:$PORT nwo_portal.wsgi:application
