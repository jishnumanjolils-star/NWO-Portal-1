#!/usr/bin/env bash
# exit on error
set -o errexit

echo "====== STARTING RENDER BUILD SYSTEM ======"

# 1. Upgrade pip and install all Python requirements
echo "Installing requirements from requirements.txt..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 2. Collect static files for production delivery via Whitenoise
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "====== RENDER BUILD COMPLETE ======"
