#!/bin/bash
set -e

echo "Running database migrations..."
python3 -m alembic upgrade head || echo "Migration skipped or database up to date"

echo "Starting FastAPI Application on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
