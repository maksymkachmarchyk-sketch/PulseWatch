# PulseWatch

## Run locally
    python -m venv .venv
    .venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
    pip install -r requirements.txt
    cd backend
    python manage.py migrate
    python manage.py runserver      # terminal 1  -> http://localhost:8000
    python manage.py runchecks      # terminal 2  -> performs the checks (no Redis needed)

Open http://localhost:8000 — Django serves the `frontend/` folder itself, so the site and the API share one origin.
Register, sign in, add a monitor (e.g. https://example.com) and wait for the first check.

`.env` (project root) needs `AUTO_VERIFY_USERS=True` for local use; see `.env.example`.

## With Redis + Celery (production-like)
    celery -A PulseWatch worker -l info      # add  -P solo  on Windows
    celery -A PulseWatch beat -l info
