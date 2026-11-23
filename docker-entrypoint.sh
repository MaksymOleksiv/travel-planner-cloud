#!/bin/sh
set -e

# Apply database migrations, then start the API.
alembic upgrade head

# exec: uvicorn becomes PID 1 and receives SIGTERM directly (graceful shutdown)
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'
