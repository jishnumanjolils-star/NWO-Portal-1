#!/usr/bin/env bash
set -o errexit

# Run database migrations at service startup since Render free tier does not support pre-deploy commands.
python manage.py migrate --noinput

# Launch the production WSGI server.
exec gunicorn --bind 0.0.0.0:$PORT nwo_portal.wsgi:application
