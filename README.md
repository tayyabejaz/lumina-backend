# Backend — Adaptive Exam-Prep Platform

**Python · FastAPI · async · Supabase (PostgreSQL).** Designed with **SOLID** layering and
**ACID** transactions, and architected to scale toward very high throughput (target: 100K
requests/second) by staying fully asynchronous and horizontally stateless.

## Stack

- **FastAPI** (async) + Pydantic v2 · served by Gunicorn + Uvicorn workers
- **Supabase** — managed PostgreSQL (+ Auth, Storage). Connect via the **Supavisor pooler**
  (transaction mode) so huge client concurrency multiplexes onto a small DB pool
- **SQLAlchemy 2.0 async** + **asyncpg** driver
- **Redis** (cache, sessions, rate limits) · **arq** async workers on Redis
- Supabase Auth (JWT) · RBAC + ReBAC authorization · Stripe entitlements
- OpenTelemetry + Sentry

## SOLID layering (every module)

The HTTP edge is thin and business logic depends on **abstractions**, not on the database:

```
app/modules/<name>/
  router.py        Presentation/HTTP edge — wires deps + Unit of Work, no logic   (SRP)
  service.py       Application use-cases — orchestration; depends on interfaces    (SRP, DIP)
  interfaces.py    Protocols (repository, marker, …) the service depends on        (DIP, ISP)
  repository.py    Async Supabase/Postgres implementation of those Protocols       (OCP, LSP)
  domain.py        Pure entities — no framework/DB imports                         (SRP)
  schemas.py       Pydantic DTOs — request/response contract (OpenAPI)
```

- **S**ingle responsibility — router ≠ service ≠ repository ≠ domain.
- **O**pen/closed — add a new marker/repository by implementing a Protocol, no edits to services.
- **L**iskov — any implementation of a Protocol is substitutable (real vs. in-memory test double).
- **I**nterface segregation — small Protocols (`AttemptRepository`, `Marker`) not god-interfaces.
- **D**ependency inversion — services receive abstractions via constructor injection; FastAPI
  `Depends` wires concretes at the edge.

> See `app/modules/practice/` for a fully worked example of all six files.

## ACID

Each write use-case runs inside a **Unit of Work** (`app/core/uow.py`) that opens one
transaction and commits on success / rolls back on error — so, e.g., an attempt and its marks
persist **atomically**. PostgreSQL (via Supabase) provides the consistency, isolation and
durability guarantees; attempts/answer_marks remain append-only.

## Async & high-scale design (→ 100K req/s)

Everything on the hot path is `async def` — no blocking calls in request handlers.

- **Connection multiplexing:** clients connect through Supabase **Supavisor** (transaction
  pooling) so 10Ks of connections share a small Postgres backend pool (`app/core/db.py`).
- **Read/write split:** writes → primary engine; heavy reads → **read-replica** engine.
- **Stateless app tier:** scale out Uvicorn workers horizontally behind a load balancer; all
  state lives in Supabase / Redis / object storage.
- **Cache aggressively:** Redis for sessions, hot content, seen-sets, and rate limiting to keep
  reads off the DB.
- **Offload slow work:** free-text marking, plan generation and analytics run on the **arq**
  worker pool (idempotent, retries, DLQ) — never inline.
- **Partition the firehose:** time-partition `attempts`; move analytical scans to a warehouse.
- **Backpressure:** per-user/per-IP rate limits at the edge; graceful degradation
  ("marking pending") so the practice loop never blocks.

> Note: 100K req/s is a large target. This design removes the architectural blockers to reach it
> (async, pooling, replicas, cache, queues, partitioning); the actual ceiling is then a matter of
> instance count and DB tier, proven via load testing (backlog REL-5).

## Layout

```
app/
  main.py            FastAPI app (async), health, router wiring
  core/              config, db (async engines + sessions), uow (ACID), security
  modules/           11 domain modules in the SOLID shape above
  shared/            authz (RBAC+ReBAC), scaling helpers
  workers/           arq async workers (marking, planning, analytics, email)
db/
  schema.sql         Canonical PostgreSQL schema (Supabase-compatible)
  migrations/        Alembic migrations
tests/
```

## Getting started (later)

Dependencies are managed with **[uv](https://docs.astral.sh/uv/)** (config in `pyproject.toml`,
pinned in `uv.lock`, Python pinned in `.python-version`).

```bash
# install uv once: https://docs.astral.sh/uv/getting-started/installation/
uv sync                        # create .venv + install deps (incl. dev group) from uv.lock
cp .env.example .env           # set Supabase pooler URL + keys
uv run alembic upgrade head
uv run uvicorn app.main:app --reload              # API (dev)
uv run arq app.workers.worker.WorkerSettings      # worker pool
# prod: uv sync --no-dev  then  gunicorn -k uvicorn.workers.UvicornWorker -w <N> app.main:app
```

Common uv commands: `uv add <pkg>` (add a dep), `uv add --dev <pkg>` (dev dep),
`uv lock` (refresh the lockfile), `uv run <cmd>` (run inside the env). Commit `uv.lock`.

> Scaffold only — no dependencies installed yet. Maps to backlog Epic E1 + the practice/marking
> stories (FND-*, PRC-1/2, MRK-1).
