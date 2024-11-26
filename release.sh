#!/bin/bash
set -e  # Exit immediately if any command fails

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Making migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate
