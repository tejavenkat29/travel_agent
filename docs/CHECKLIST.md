# Production Readiness Checklist

## Configuration & secrets
- [x] All config via env vars, validated at startup (`pydantic-settings`)
- [x] Startup fails on insecure prod config (default `SECRET_KEY`, `DEBUG=true`)
- [ ] `SECRET_KEY` provided from a secret manager (not committed)
- [ ] `BACKEND_CORS_ORIGINS` set to real origin(s), not `*`
- [ ] LLM provider key set; `LLM_PROVIDER` chosen

## Reliability
- [x] Liveness probe `/health`
- [x] Readiness probe `/health/ready` (Postgres + Redis), 503 when degraded
- [x] Healthchecks in Docker + compose `depends_on: service_healthy`
- [x] Graceful, uniform error responses; no internals leaked in prod
- [x] Per-request transaction (unit of work) with rollback

## Performance
- [x] Parallel agent execution (fan-out/fan-in) — verified by timing test
- [x] Redis caching (cache-aside) with per-category TTLs
- [x] Horizontal scaling supported (shared Redis for cache + limits)
- [x] Tunable `WEB_CONCURRENCY` workers

## Security
- [x] Non-root container user
- [x] Security headers (CSP, X-Frame-Options, nosniff, …)
- [x] Per-IP rate limiting (429 + headers), distributed via Redis
- [x] CORS restricted by config
- [x] Optional `DOCS_ENABLED=false` to hide docs publicly
- [ ] TLS terminated at the proxy/LB
- [ ] Authentication/authorization (next milestone)

## Observability
- [x] Structured JSON logging with request-id correlation
- [x] LangSmith tracing across all agents (prompts, responses, tokens, latency)
- [ ] Metrics/alerting wired to your monitoring stack

## Delivery
- [x] Dockerized (multi-stage, slim, non-root)
- [x] One-command stack: `docker compose up`
- [x] Auto-migrations on startup
- [x] CI: lint + test + image build
- [x] CD: image publish on version tags
- [ ] Deploy step wired to the real target

## Data
- [x] Alembic migrations (versioned, reversible)
- [x] Repository-pattern CRUD
- [x] Persistent volumes for Postgres/Redis
- [ ] Backup/restore policy for Postgres

## Documentation
- [x] Deployment guide, architecture, API reference, this checklist
- [x] Auto-generated OpenAPI at `/openapi.json`

Legend: `[x]` implemented in the codebase · `[ ]` deployment-time action you own.
