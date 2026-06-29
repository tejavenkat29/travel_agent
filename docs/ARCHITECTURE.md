# Architecture

## Overview
A multi-agent travel planner built on FastAPI + LangGraph, following **clean
architecture**: dependencies point inward, and outer layers (web, DB, cache,
LLM providers) depend on abstractions (ports) defined in the domain.

```
            HTTP
             │
      ┌──────▼───────────────────────────────────────────┐
      │ Presentation  app/api  (routes, middleware)       │
      ├───────────────────────────────────────────────────┤
      │ Application   app/agents, app/use_cases           │
      │   - LangGraph workflow orchestrates the agents    │
      ├───────────────────────────────────────────────────┤
      │ Domain        app/domain (entities + interfaces)  │  ← ports, no deps
      ├───────────────────────────────────────────────────┤
      │ Infrastructure app/infrastructure                 │
      │   db (Postgres) · cache (Redis) · llm · external  │  ← adapters
      └───────────────────────────────────────────────────┘
```

## The agent workflow (LangGraph)
```
START → planner → ┌─ flights ─┐
                  ├─ hotel   ─┤→ budget → final_response → END
                  └─ weather ─┘
```
- **Shared state** (`TravelState`) flows through every node; each node reads
  what it needs and writes its result.
- **Parallel** fan-out (flights/hotel/weather) → **join** at budget.
- **Conditional routing** skips flight/hotel/weather when the user already has
  that info (`route_after_planner`).
- Agents are framework-agnostic, so the *same* agents power both the LangGraph
  workflow and the LangFlow visual flow.

## Key design patterns
| Pattern | Where | Why |
|---|---|---|
| Ports & adapters | `domain/interfaces` ↔ `infrastructure` | Swap Postgres/Redis/LLM/providers without touching logic |
| Repository | `db/repositories` | CRUD behind an interface; one transaction per request |
| Provider factory + decorator | `infrastructure/external/*` | Mock↔real selection; caching wrappers (cache-aside) |
| Dependency injection | `api/v1/dependencies.py` | Cached singletons (agents, workflow, cache) |
| Unit of work | `db/session.get_db` | Commit on success, rollback on error |

## Cross-cutting concerns
- **Config:** `pydantic-settings`, validated at startup (fails fast in prod).
- **Logging:** `structlog`; JSON in production, request-id correlation.
- **Observability:** LangSmith tracing across all agents (prompts, tokens, latency).
- **Caching:** Redis cache-aside on flight/hotel/weather, per-category TTLs.
- **Resilience:** healthcheck + readiness probe, graceful error envelope.
- **Security:** security headers, per-IP rate limiting, locked-down CORS,
  non-root container, secret/DEBUG validation.

## Data model
`users 1─* trips`, `users 1─* chat_history`, `trips 1─* chat_history`
(see [migrations/versions/0001_initial.py](../migrations/versions/0001_initial.py)).

## Runtime topology
```
client → [load balancer] → API replicas (Uvicorn workers)
                              ├─ PostgreSQL (asyncpg)
                              ├─ Redis (cache + rate limit)
                              └─ LLM provider (OpenAI/Gemini/Ollama)
                                   └─ LangSmith (traces)
```
