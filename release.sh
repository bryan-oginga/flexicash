#!/bin/bash
set -e  # Exit immediately if any command fails

# Step 1: Check if migrations are needed
echo "Checking for pending migrations..."
python manage.py check_migrations

# Step 2: Apply migrations if needed
echo "Running migrations..."
python manage.py migrate

# Step 3: Collect static files (if necessary)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# You can add other release-related tasks below as needed
echo "Release process completed."
