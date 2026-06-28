# 🧭 AI Multi-Agent Travel Planner

A production-ready, multi-agent travel planning platform built on **FastAPI**,
**LangChain**, **LangGraph**, **LangSmith** and **LangFlow**, backed by
**PostgreSQL** and **Redis**, containerised with **Docker**, and pluggable
across **OpenAI / Gemini / Ollama** LLM providers.

> **Status:** project scaffold only. Business logic (agents, graphs, tools,
> persistence, endpoints) is **not** implemented yet — this commit establishes
> the structure, configuration, and developer setup following **clean
> architecture** principles.

---

## ✨ Tech stack

| Concern              | Technology                                   |
| -------------------- | -------------------------------------------- |
| API / web framework  | FastAPI + Uvicorn                            |
| Agent orchestration  | LangChain · LangGraph                        |
| Observability        | LangSmith (tracing)                          |
| Visual flow design   | LangFlow                                     |
| LLM providers        | OpenAI · Google Gemini · Ollama (local)      |
| Relational store     | PostgreSQL (async via SQLAlchemy + asyncpg)  |
| Cache / state        | Redis                                        |
| Migrations           | Alembic                                      |
| Packaging / runtime  | Docker · docker-compose                      |

---

## 🏛️ Architecture

The codebase follows **clean architecture**: dependencies point *inward*.
Inner layers (domain) know nothing about outer layers (frameworks, DB, web).

```
            ┌─────────────────────────────────────────────┐
            │                  api  (web)                  │  ← FastAPI routes
            ├─────────────────────────────────────────────┤
            │              use_cases (application)         │  ← orchestration
            ├─────────────────────────────────────────────┤
            │                 domain (core)                │  ← entities + ports
            ├─────────────────────────────────────────────┤
            │   infrastructure  (db · cache · llm · ext)   │  ← adapters
            └─────────────────────────────────────────────┘
                 agents (LangGraph) sit beside use_cases
```

Outer layers depend on inner ones through **interfaces** defined in
`app/domain/interfaces`, so implementations (Postgres, Redis, a specific LLM)
can be swapped without touching business rules.

---

## 📁 Folder structure

```text
travel_agent/
├── app/                          # Application source (the importable package)
│   ├── main.py                   # FastAPI entrypoint & app factory
│   │
│   ├── api/                      # PRESENTATION layer — HTTP transport only
│   │   └── v1/                   # Versioned API surface
│   │       ├── routes/           # Route handlers (thin; delegate to use_cases)
│   │       └── dependencies.py   # FastAPI dependency-injection wiring
│   │
│   ├── core/                     # Cross-cutting framework concerns
│   │   ├── config.py             # Typed settings loaded from env/.env
│   │   └── logging.py            # Structured logging setup
│   │
│   ├── domain/                   # ENTERPRISE business rules (framework-free)
│   │   ├── entities/             # Core domain models (Trip, Itinerary, ...)
│   │   └── interfaces/           # Ports: abstract repos & service contracts
│   │
│   ├── use_cases/                # APPLICATION business rules / orchestrators
│   │
│   ├── agents/                   # LLM multi-agent system
│   │   ├── graph/                # LangGraph state graphs & workflow wiring
│   │   ├── nodes/                # Individual agent nodes (planner, flights...)
│   │   ├── tools/                # Tools agents can call (search, weather...)
│   │   └── prompts/              # Prompt templates
│   │
│   ├── infrastructure/           # ADAPTERS — concrete external implementations
│   │   ├── db/
│   │   │   ├── models/           # SQLAlchemy ORM models
│   │   │   └── repositories/     # Repository implementations (impl. of ports)
│   │   ├── cache/                # Redis client & cache adapters
│   │   ├── llm/                  # Provider factory (OpenAI/Gemini/Ollama)
│   │   └── external/             # 3rd-party travel API clients
│   │
│   ├── schemas/                  # Pydantic request/response DTOs (API contracts)
│   └── utils/                    # Pure, reusable helpers
│
├── tests/                        # Test suite
│   ├── unit/                     # Fast, isolated tests
│   └── integration/              # Tests touching DB/Redis/LLM
│
├── migrations/                   # Alembic migration scripts
├── scripts/                      # Operational/dev scripts (seed, lint, ...)
├── docker/                       # Dockerfiles & container assets
├── flows/                        # Exported LangFlow flows (.json)
├── docs/                         # Project documentation
│
├── .env.example                  # Template for environment variables
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Why each folder exists

- **`app/api`** — The *presentation* layer. HTTP-specific code only: routing,
  request validation, status codes. Handlers stay thin and call use cases.
  Versioned (`v1/`) so the public contract can evolve without breaking clients.
- **`app/core`** — Framework-level cross-cutting concerns shared everywhere:
  configuration (`config.py`) and logging. No business rules live here.
- **`app/domain`** — The heart of clean architecture. `entities/` holds
  framework-agnostic business objects; `interfaces/` holds the **ports**
  (abstract base classes) that outer layers must implement. Depends on nothing.
- **`app/use_cases`** — *Application* business rules. Each use case orchestrates
  entities, repositories (via interfaces) and agents to fulfil one user goal
  (e.g. "plan a trip"). It is where workflows are coordinated.
- **`app/agents`** — The multi-agent system. `graph/` defines LangGraph state
  machines; `nodes/` are the individual specialised agents; `tools/` are the
  callable capabilities; `prompts/` keeps prompt templates out of code.
- **`app/infrastructure`** — *Adapters* implementing the domain interfaces with
  real technology: PostgreSQL (`db/`), Redis (`cache/`), the LLM provider
  factory (`llm/`), and external travel APIs (`external/`). Swappable.
- **`app/schemas`** — Pydantic DTOs that define the API's input/output shapes,
  kept separate from domain entities so transport concerns never leak inward.
- **`app/utils`** — Small, pure, dependency-free helpers reused across layers.
- **`tests`** — `unit/` for fast isolated tests, `integration/` for tests that
  exercise real infrastructure.
- **`migrations`** — Alembic schema migrations, versioned with the code.
- **`scripts`** — One-off and operational scripts (DB seeding, maintenance).
- **`docker`** — Container build assets kept out of the project root.
- **`flows`** — Exported LangFlow visual flows for design/prototyping.
- **`docs`** — Architecture decisions and developer documentation.

---

## 🚀 Getting started

### 1. Prerequisites
- Python 3.10+
- Docker & docker-compose (for PostgreSQL + Redis)

### 2. Set up the environment

```bash
# Create & activate the virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env            # then edit .env with your keys
```

### 3. Run backing services

```bash
docker compose up -d postgres redis
```

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

Then open:
- API docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

---

## 🔧 Configuration

All configuration is environment-driven and validated at startup by
`app/core/config.py`. See **`.env.example`** for the full list of variables
(application, security, LLM providers, LangSmith, PostgreSQL, Redis, external
APIs). Never commit your real `.env`.

---

## 🧪 Testing

```bash
pytest                 # run the suite
pytest --cov=app       # with coverage
```

## 🧹 Code quality

```bash
ruff check .           # lint
black .                # format
mypy app               # type-check
```

---

## 🗺️ Roadmap (next milestones)

1. Domain entities & repository interfaces.
2. LLM provider factory (OpenAI / Gemini / Ollama).
3. PostgreSQL & Redis adapters + Alembic migrations.
4. LangGraph multi-agent workflow (planner, flights, hotels, budget, weather).
5. Trip-planning use cases & API endpoints.
6. LangSmith tracing & evaluation harness.

---

## 📄 License

TBD.
