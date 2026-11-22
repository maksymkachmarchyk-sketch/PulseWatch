#!/bin/sh
set -e
python manage.py migrate --noinput

# checks scheduler in the same container (restarts itself if it ever exits)
( while true; do python manage.py runchecks --every 10 || sleep 5; done ) &

exec gunicorn PulseWatch.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 60
