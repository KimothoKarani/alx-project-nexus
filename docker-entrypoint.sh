#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Wait for PostgreSQL to be ready (only if using local database)
if [ "$POSTGRES_HOST" = "db" ]; then
    echo "Waiting for postgres..."
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files (important for production)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if environment variable is set (optional)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput --email admin@example.com || true
fi

# Start Gunicorn server with dynamic port
echo "Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn nexus_commerce.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --access-logfile -