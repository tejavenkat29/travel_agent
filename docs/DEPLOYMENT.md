# Deployment Guide

## 1. Prerequisites
- Docker + Docker Compose (or a container runtime + managed Postgres/Redis)
- A reachable PostgreSQL 16 and Redis 7 (compose provides both)
- LLM provider credentials (OpenAI / Gemini, or a self-hosted Ollama)

## 2. Configuration
All configuration is environment-driven and validated at startup
([app/core/config.py](../app/core/config.py)). Copy and edit the template:

```bash
cp .env.example .env
```

**Required for production** (the app refuses to start otherwise):
- `APP_ENV=production`
- `DEBUG=false`
- `SECRET_KEY=<long random string>`  (e.g. `openssl rand -hex 32`)

**Strongly recommended:**
- `BACKEND_CORS_ORIGINS=https://your-frontend.example`  (never `*`)
- `DATABASE_URL`, `REDIS_URL` pointing at managed instances
- `LLM_PROVIDER` + the matching API key
- `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY` for observability

## 3. Run with Docker Compose
```bash
docker compose up -d --build
```
On startup the API container automatically:
1. waits for Postgres + Redis to be **healthy** (`depends_on`),
2. applies DB migrations (`alembic upgrade head`),
3. starts Uvicorn (`WEB_CONCURRENCY` workers).

Verify:
```bash
curl http://localhost:8000/health          # liveness
curl http://localhost:8000/health/ready     # readiness (DB + Redis)
```

## 4. Scaling
- **Vertical:** raise `WEB_CONCURRENCY` (Uvicorn workers per container).
- **Horizontal:** run multiple API replicas behind a load balancer. Redis-backed
  rate limiting and caching are shared across replicas, so limits hold globally.
- Run migrations as a **one-off job** (`RUN_MIGRATIONS=0` on web replicas, a
  separate `alembic upgrade head` task) to avoid concurrent migration races.

## 5. Migrations
```bash
docker compose exec api alembic upgrade head     # apply
docker compose exec api alembic downgrade -1     # roll back one
docker compose exec api alembic revision --autogenerate -m "msg"  # new
```

## 6. CI/CD
- **CI** ([.github/workflows/ci.yml](../.github/workflows/ci.yml)): lint (ruff) →
  test (pytest) → docker build on every push/PR.
- **Deploy** ([.github/workflows/deploy.yml](../.github/workflows/deploy.yml)):
  on a `vX.Y.Z` tag, builds and pushes the image to GHCR. Wire the final step to
  your target (k8s, Fly.io, Render, SSH, …).

## 7. Operations
- **Logs:** structured JSON in production (`docker compose logs -f api`), each
  line carries a `request_id`.
- **Tracing:** LangSmith dashboard (per-request agent timeline, tokens, latency).
- **Health:** point your orchestrator's liveness at `/health` and readiness at
  `/health/ready`.
- **Rollback:** redeploy the previous image tag; `alembic downgrade` if schema
  changed.
