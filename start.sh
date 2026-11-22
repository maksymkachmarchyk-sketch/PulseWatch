#!/bin/sh
set -e
python manage.py migrate --noinput

# optional: create an admin on first start (set DJANGO_SUPERUSER_* env vars; ignored if the user already exists)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --noinput || true
fi

# checks scheduler in the same container (restarts itself if it ever exits)
( while true; do python manage.py runchecks --every 10 || sleep 5; done ) &

exec gunicorn PulseWatch.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 60
