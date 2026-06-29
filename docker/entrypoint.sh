#!/usr/bin/env bash
# Container entrypoint: apply DB migrations, then launch the API server.
# Postgres readiness is guaranteed by compose `depends_on: service_healthy`,
# so migrations can run immediately.
set -euo pipefail

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  echo "[entrypoint] Applying database migrations (alembic upgrade head)..."
  alembic upgrade head
fi

echo "[entrypoint] Starting API on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
