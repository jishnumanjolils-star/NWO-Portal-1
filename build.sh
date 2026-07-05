#!/usr/bin/env bash
# NWO Portal - Render Build Script
# Installs dependencies and prepares static files

set -o errexit
set -o pipefail

echo "====== NWO PORTAL BUILD STARTED ======"
echo "Build started at: $(date)"

# Step 1: Upgrade pip
echo ""
echo "Step 1/3: Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org

# Step 2: Install dependencies
echo ""
echo "Step 2/3: Installing Python dependencies from requirements.txt..."
if ! python -m pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi
echo "Dependencies installed successfully"

# Step 3: Collect static files
echo ""
echo "Step 3/3: Collecting static files..."
if ! python manage.py collectstatic --noinput --clear; then
    echo "WARNING: Static file collection encountered issues, but continuing..."
fi
echo "Static files collected"

echo ""
echo "====== NWO PORTAL BUILD COMPLETED ======"
echo "Build completed at: $(date)"

# Force manual redeployment to ensure all template and views changes are fully live
