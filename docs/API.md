# API Reference

Base URL: `http://localhost:8000` · Versioned API under `/api/v1`.
Interactive docs (when `DOCS_ENABLED=true`): **`/docs`** (Swagger) · **`/redoc`**.

All responses are JSON. Errors use a uniform envelope:
```json
{ "error": "not_found", "message": "…", "details": null, "request_id": "…" }
```
Every response carries `X-Request-ID`; rate-limited routes also return
`X-RateLimit-Limit` / `X-RateLimit-Remaining`.

## System
| Method | Path | Description |
|---|---|---|
| GET | `/` | Service metadata |
| GET | `/health` | Liveness probe |
| GET | `/health/ready` | Readiness (checks Postgres + Redis); 503 if degraded |

## Orchestrated planning
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/plan` | **Run the full workflow.** Body: `{ "request", "include_weather", "provided_flight?", "provided_hotel?" }`. Returns the structured summary + Markdown. |

## Individual agents
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/planner/extract` | Extract `TripParameters` from free text |
| POST | `/api/v1/flights/search` | Flight offers for a trip |
| POST | `/api/v1/hotels/search` | Hotel offers + recommendation |
| POST | `/api/v1/weather/forecast` | Forecast + clothing + best time |
| POST | `/api/v1/budget/estimate` | Cost breakdown vs. budget |
| POST | `/api/v1/summary/compose` | Synthesize final summary from agent outputs |

## LLM utilities
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/chat` | Chat with the configured LLM |
| POST | `/api/v1/travel/assistant` | Structured destination recommendation |

## Persistence (CRUD)
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/users` | Create user |
| GET | `/api/v1/users` | List users |
| GET | `/api/v1/users/{id}` | Get user |
| PATCH | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user |

## Example — end-to-end plan
```bash
curl -X POST http://localhost:8000/api/v1/plan \
  -H 'content-type: application/json' \
  -d '{"request":"5 day trip from Mumbai to Tokyo for 2, budget $4000","include_weather":true}'
```

> The full request/response schemas are auto-generated and always current at
> `/openapi.json` — treat that as the source of truth.
