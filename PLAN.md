# Polymath — Build Plan

> A personal web platform: portfolio + blog on the outside, AI-powered tools, productivity, analytics, and games on the inside. One domain, multiple services, shared backbone.

**Codename:** `polymath`
**Why this name:** It captures the "many disciplines, one mind" feel of the project — AI tools, productivity, analytics, games, writing all under one roof. It's also short, ownable as a domain (`polymath.dev`, `polymath.app`, or `<yourhandle>.polymath.dev`), pronounceable, and reads well in code (`polymath-api`, `polymath.gateway`). Backup names if taken: **Atlas**, **Lighthouse**, **Workshop**, **Garden** (as in "digital garden"), **Forge**.

---

## 0. How to read this document (instructions for Claude Code)

This document is the source of truth for building Polymath. When implementing:

1. **Follow the build order in §11 strictly.** Each phase delivers a working slice. Do not skip ahead.
2. **Every service follows the template in §6.** Don't invent new patterns per service.
3. **All ADRs in §13 are binding decisions.** If something seems wrong, surface it before deviating.
4. **Test as you go.** Every PR must include tests. Coverage gate: 70% on services, 90% on shared libs.
5. **Observability is not optional.** Every service emits traces, structured logs, and metrics from day one.
6. **When in doubt, prefer boring tech.** This is a personal project — every dependency is debt the owner pays alone at 2am.

---

## 1. Vision & scope

### 1.1 What Polymath is
A single-domain personal platform that serves three audiences:
- **The owner** (authenticated): productivity tools, AI playground, personal data dashboards, agent-driven automations.
- **Visitors** (public): portfolio, blog, learning log, public games & demos, useful utilities (token calculator, JSON tools, etc.).
- **Future-me**: a substrate where adding a new feature is a weekend, not a project.

### 1.2 Non-goals
- Not a SaaS. No multi-tenancy, no billing, no marketing site.
- Not a startup. Optimize for owner's daily use and learning, not viral growth.
- Not Kubernetes. Single VPS until proven otherwise.
- Not a microservices showcase for its own sake. Services exist because they have different scaling/deployment/lifecycle needs, not because microservices are cool.

### 1.3 Success criteria
- Owner uses ≥3 internal tools weekly within 60 days of launch.
- New feature ("phase N+1") can ship end-to-end in <1 weekend after phase 6.
- Cold-start to local dev environment is <10 minutes via `make bootstrap`.
- Production deploys via single command, zero manual steps.
- p95 latency <300ms for read endpoints, <1s for LLM-backed endpoints (excluding model time).

---

## 2. High-level architecture

```
                              ┌──────────────────────┐
                              │   Cloudflare (edge)  │
                              │  DNS / CDN / WAF     │
                              └──────────┬───────────┘
                                         │
                              ┌──────────▼───────────┐
                              │   Next.js (web)      │  ← public site + authed app
                              │   App Router         │     (one frontend, one domain)
                              └──────────┬───────────┘
                                         │ HTTPS
                              ┌──────────▼───────────┐
                              │   API Gateway (BFF)  │  FastAPI
                              │   - auth check       │
                              │   - request shaping  │
                              │   - rate limit       │
                              │   - fan-out          │
                              └──────────┬───────────┘
                                         │ HTTP (internal network)
        ┌────────────────┬───────────────┼──────────────┬───────────────┬──────────────┐
        │                │               │              │               │              │
   ┌────▼─────┐   ┌──────▼─────┐   ┌─────▼────┐   ┌─────▼────┐   ┌──────▼─────┐  ┌─────▼─────┐
   │ llm-gw   │   │ notes-svc  │   │ habits   │   │ content  │   │ analytics  │  │ games-svc │
   │          │   │ + RAG      │   │ -svc     │   │ -svc     │   │ -svc       │  │           │
   └────┬─────┘   └──────┬─────┘   └─────┬────┘   └─────┬────┘   └──────┬─────┘  └─────┬─────┘
        │                │               │              │               │              │
        └────────────────┴───────────────┼──────────────┴───────────────┴──────────────┘
                                         │
                          ┌──────────────┼──────────────┐
                          │              │              │
                   ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
                   │  Postgres   │ │   Redis   │ │  R2/MinIO   │
                   │  + pgvector │ │ cache/bus │ │   objects   │
                   └─────────────┘ └───────────┘ └─────────────┘

                   ┌──────────────────────────────────────────┐
                   │  jobs-svc (Arq workers, scheduled tasks) │  ← reads same Postgres/Redis
                   └──────────────────────────────────────────┘

                   ┌──────────────────────────────────────────┐
                   │  OpenTelemetry collector → Grafana Cloud │
                   └──────────────────────────────────────────┘
```

### 2.1 Service boundaries — the rules
- **Frontend never talks to internal services directly.** Always through gateway. This is the seam that lets backends evolve.
- **Services don't call each other synchronously by default.** They emit events on Redis pub/sub or write to a shared outbox table. Synchronous internal calls are allowed only when latency demands it (e.g., gateway → llm-gateway). Each cross-service sync call is an ADR.
- **Each service owns its schema** (Postgres schema, not database). Other services read via API, not via SQL.
- **No shared ORM models across services.** Shared types live in a generated OpenAPI client (§7.4).

---

## 3. Tech stack — locked decisions

| Layer | Choice | Why |
|---|---|---|
| Language (backend) | Python 3.12 | Owner's primary language; ecosystem fits AI work |
| Web framework | FastAPI 0.115+ | Async, OpenAPI for free, Pydantic-native |
| ORM | SQLAlchemy 2.0 (async) | Mature, type-safe with new API |
| Migrations | Alembic | Standard with SQLAlchemy |
| Validation | Pydantic v2 | Required by FastAPI, also used standalone |
| Job queue | Arq | Redis-only, async-native, lighter than Celery |
| LLM SDK | `anthropic`, `openai`, `litellm` | LiteLLM as fallback router |
| Vector store | pgvector in Postgres | Avoid running a second DB |
| Embeddings | Voyage AI or OpenAI `text-embedding-3-small` | Cost-effective; pluggable via gateway |
| Frontend | Next.js 15 (App Router) | Standard, great DX, owner doesn't need to love it |
| UI | Tailwind 4 + shadcn/ui | Composable, no design system to build |
| Auth | Clerk (managed) for v1 | Owner is solo; do not build auth from scratch |
| DB | Postgres 16 | Boring, vector + JSONB + FTS in one |
| Cache / queue / pubsub | Redis 7 | Multi-purpose, single dependency |
| Object storage | Cloudflare R2 | S3 API, zero egress |
| Edge | Cloudflare | DNS, CDN, WAF, tunnels (free tier sufficient) |
| Container | Docker + Compose | Local + prod parity |
| Orchestration | Coolify on Hetzner CX22 | Self-hosted Heroku-equivalent |
| CI | GitHub Actions | Standard |
| Registry | GHCR | Free, integrated |
| Observability | OpenTelemetry → Grafana Cloud free tier | Traces, logs, metrics in one place |
| Error tracking | Sentry (free tier) | Best-in-class, complements OTel |
| Linter | Ruff | Replaces black + isort + flake8 |
| Type checker | mypy (strict on shared libs) | Catch dumb mistakes |
| Test | pytest, pytest-asyncio, httpx | Standard |
| Pre-commit | pre-commit framework | ruff, mypy, secrets scan |
| Dependency mgmt | uv | Fast, lockfile-based |
| Package mgmt (frontend) | pnpm | Fast, disk-efficient |

### 3.1 Things explicitly rejected
- **Kubernetes** — overkill for a personal project; revisit at 1k+ DAU.
- **MongoDB / DynamoDB** — Postgres handles all use cases here.
- **Pinecone / Weaviate** — pgvector is enough for <10M vectors.
- **GraphQL** — REST + OpenAPI is simpler and the frontend is single-consumer.
- **gRPC** — internal HTTP is fine at this scale; debugging beats a few ms saved.
- **Microfrontends** — no.
- **Custom auth** — Clerk for v1; revisit only if cost or feature needs justify.
- **Server-side rendering for the authed app** — client-side is fine for the dashboard pages; SSR for marketing/blog only.

---

## 4. Repository layout (monorepo)

Single Git repo. Reasoning: one owner, atomic cross-service changes are common, easy to share types and tooling.

```
polymath/
├── README.md
├── PLAN.md                      # this document
├── Makefile                     # bootstrap, dev, test, deploy
├── docker-compose.yml           # local dev (all services)
├── docker-compose.prod.yml      # prod overrides
├── .env.example
├── .github/
│   └── workflows/
│       ├── ci.yml               # lint, type, test, build images
│       ├── deploy.yml           # on tag → push to GHCR → notify Coolify
│       └── codeql.yml           # security scan
├── .pre-commit-config.yaml
├── pyproject.toml               # workspace root (uv workspaces)
├── uv.lock
│
├── apps/
│   ├── web/                     # Next.js 15 frontend
│   │   ├── app/
│   │   │   ├── (public)/        # marketing, blog, public games
│   │   │   ├── (app)/           # authed dashboard, tools
│   │   │   └── api/             # ONLY for Clerk webhooks; no business logic
│   │   ├── components/
│   │   ├── lib/
│   │   │   ├── api-client.ts    # generated from OpenAPI
│   │   │   └── auth.ts
│   │   ├── package.json
│   │   └── ...
│   │
│   ├── gateway/                 # FastAPI BFF
│   ├── llm-gateway/             # FastAPI service
│   ├── notes-svc/
│   ├── habits-svc/
│   ├── content-svc/
│   ├── analytics-svc/
│   ├── games-svc/
│   └── jobs-svc/                # Arq workers + scheduler
│
├── libs/
│   ├── polymath-core/           # shared utilities (logging, config, errors)
│   ├── polymath-db/             # SQLAlchemy base, session, migration helpers
│   ├── polymath-events/         # Redis pub/sub helpers, event schemas
│   ├── polymath-llm/            # LLM client wrapper (used by llm-gateway)
│   └── polymath-testing/        # test fixtures, factories
│
├── infra/
│   ├── coolify/                 # Coolify configs
│   ├── grafana/                 # dashboards as code
│   ├── postgres/
│   │   └── init/                # init SQL (extensions, schemas)
│   └── nginx/                   # if needed for local prod-like
│
├── scripts/
│   ├── bootstrap.sh             # one-command setup
│   ├── new-service.sh           # scaffold a new service from template
│   ├── gen-client.sh            # generate frontend API client from OpenAPI
│   └── seed.py                  # seed dev data
│
└── docs/
    ├── adr/                     # architecture decision records (numbered)
    │   ├── 0001-monorepo.md
    │   ├── 0002-postgres-only.md
    │   └── ...
    ├── runbooks/
    │   ├── deploy.md
    │   ├── incident.md
    │   └── rotate-secrets.md
    └── api/                     # generated OpenAPI snapshots
```

### 4.1 Workspace tooling
- `uv` workspaces: each `apps/*` and `libs/*` Python package is a member.
- `pnpm` workspaces: only `apps/web` for now (prepared for future Next.js apps).
- Single `Makefile` at root orchestrates both.

### 4.2 Branching & commits
- `main` is always deployable. No long-lived branches.
- Feature branches → squash-merge PRs.
- [Conventional Commits](https://www.conventionalcommits.org/): `feat(notes): add semantic search`, `fix(gateway): retry on 502`.
- `release-please` for changelog & semver tags on `main` (optional but recommended).

---

## 5. Data architecture

### 5.1 One Postgres, schema-per-service

```sql
CREATE SCHEMA auth;          -- Clerk webhook mirror (users table)
CREATE SCHEMA notes;
CREATE SCHEMA habits;
CREATE SCHEMA content;
CREATE SCHEMA analytics;
CREATE SCHEMA games;
CREATE SCHEMA llm;           -- prompt versions, runs, evals, cost ledger
CREATE SCHEMA jobs;          -- arq job state if needed
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

Each service has its own DB user with access only to its schema:
```sql
CREATE USER notes_svc WITH PASSWORD '...';
GRANT USAGE ON SCHEMA notes TO notes_svc;
GRANT ALL ON ALL TABLES IN SCHEMA notes TO notes_svc;
```

This enforces the "no cross-schema reads" rule at the DB level.

### 5.2 Common columns on every table

Every domain table has:
- `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- `user_id UUID` (where applicable, FK conceptually to `auth.users.id`, no actual FK across schemas)

`updated_at` maintained by a trigger (defined once in `polymath-db`).

### 5.3 Soft deletes — only where needed
Default to hard deletes. Add `deleted_at TIMESTAMPTZ` only for: notes, content posts, games saves. Not for ephemeral data (analytics events, llm runs, job records).

### 5.4 Outbox pattern for cross-service events
Each service that emits events has a `<schema>.outbox` table. A worker (in `jobs-svc`) polls and publishes to Redis. This guarantees at-least-once delivery without two-phase commit.

```sql
CREATE TABLE notes.outbox (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ
);
```

### 5.5 Event schema
Events are versioned, JSON, with a strict envelope:
```json
{
  "event_id": "uuid",
  "event_type": "notes.note.created",
  "version": 1,
  "occurred_at": "2026-05-03T10:00:00Z",
  "actor": {"type": "user", "id": "uuid"},
  "data": { /* event-specific */ }
}
```
Topic naming: `<service>.<entity>.<action>` (e.g., `notes.note.created`, `habits.streak.broken`).

Schemas live in `libs/polymath-events/schemas/`, validated on publish and consume.

### 5.6 Migrations
Each service has its own Alembic env, pointed at its own schema. CI runs `alembic upgrade head --sql` against a clean DB to verify migrations apply cleanly. Production migrations run as part of deploy, before service rollout.

---

## 6. Service template

Every backend service follows this layout. Use `scripts/new-service.sh <name>` to scaffold.

```
apps/<svc>/
├── pyproject.toml
├── Dockerfile
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── src/
│   └── <svc>/
│       ├── __init__.py
│       ├── main.py              # FastAPI app factory
│       ├── config.py            # Pydantic Settings, env-driven
│       ├── deps.py              # FastAPI dependencies (DB, auth, etc.)
│       ├── api/
│       │   ├── __init__.py      # router aggregation
│       │   ├── v1/
│       │   │   ├── routes_xxx.py
│       │   │   └── schemas.py   # Pydantic request/response models
│       │   └── health.py        # /healthz, /readyz
│       ├── domain/              # pure business logic, no I/O
│       │   ├── models.py        # domain entities (dataclasses or Pydantic)
│       │   └── services.py      # use cases
│       ├── infra/               # I/O adapters
│       │   ├── db/
│       │   │   ├── models.py    # SQLAlchemy ORM
│       │   │   └── repos.py     # repositories
│       │   ├── events.py        # outbox writer
│       │   └── clients/         # HTTP clients to other services
│       └── workers/             # if service has background work
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/             # uses testcontainers for Postgres/Redis
│   └── contract/                # OpenAPI conformance
└── README.md                    # runbook for THIS service
```

### 6.1 Layering rules
- `api` → `domain` → `infra`. `domain` never imports from `api` or `infra`.
- I/O is injected as protocols (Python `typing.Protocol`); domain depends on abstractions.
- This makes unit tests fast and forces clean boundaries.

### 6.2 Standard endpoints every service exposes
- `GET /healthz` — liveness, returns 200 if process is up.
- `GET /readyz` — readiness, returns 200 only if DB + Redis reachable.
- `GET /openapi.json` — auto-generated.
- `GET /metrics` — Prometheus exposition (via `prometheus-fastapi-instrumentator`).
- `GET /version` — git SHA + build time.

### 6.3 Standard middleware (in this order)
1. Request ID (generates or propagates `X-Request-ID`)
2. OpenTelemetry trace context
3. Structured logging (logs include `request_id`, `trace_id`, `user_id`)
4. Auth (validates JWT from gateway, sets `user_id` in request state)
5. Rate limiting (per-user, Redis-backed, via `slowapi` or custom)
6. Error handler (catches everything, returns RFC 7807 problem+json)

### 6.4 Error format (RFC 7807)
```json
{
  "type": "https://polymath.dev/errors/note-not-found",
  "title": "Note not found",
  "status": 404,
  "detail": "Note 'abc-123' does not exist or you don't have access",
  "instance": "/v1/notes/abc-123",
  "request_id": "..."
}
```

### 6.5 Versioning
URL versioning: `/v1/...`. Breaking changes ship as `/v2/...` with `/v1` deprecated for ≥30 days. Non-breaking additions go in `/v1`.

---

## 7. Gateway (BFF) details

The gateway is the only service the frontend talks to. It does:
- Auth verification (Clerk JWT → user context).
- Request fan-out and aggregation for screens that need multiple services.
- Rate limiting at the edge of the internal network.
- Response shaping (the frontend should never need to merge data itself).

### 7.1 What the gateway does NOT do
- No business logic. If logic creeps in, it belongs in a service.
- No database access. Talks only to other services.

### 7.2 Internal service auth
Gateway → service calls carry:
- `X-Polymath-User-Id` (the authenticated user)
- `X-Polymath-Service-Token` (HMAC of body+timestamp with shared secret)
- `X-Request-ID`, `traceparent` (for OTel)

Services trust the gateway and validate the service token. No mTLS for v1; revisit if running across networks.

### 7.3 Timeouts & retries
- Gateway → service: 5s default, 30s for LLM-backed routes.
- Retry on 502/503/504 with exponential backoff, max 3 attempts, only for idempotent requests (GET, PUT with idempotency key).
- Circuit breaker per downstream (using `purgatory` or hand-rolled): trip after 5 failures in 10s, half-open after 30s.

### 7.4 OpenAPI client generation
```bash
make gen-client
# 1. Hits each service's /openapi.json in dev
# 2. Merges into a single spec via `openapi-merge-cli`
# 3. Generates TS client into apps/web/lib/api-client/ via `openapi-typescript`
```
Run on every PR via CI to ensure frontend types match backend reality.

---

## 8. The LLM gateway (the most important service)

This is the one piece every AI feature depends on. Build it carefully.

### 8.1 Responsibilities
1. **Provider routing** — Anthropic, OpenAI, local (Ollama), via LiteLLM under the hood.
2. **Prompt management** — versioned prompts stored in DB, referenced by ID.
3. **Cost tracking** — every call logs tokens in/out, model, cost in micro-USD.
4. **Caching** — exact-match prompt+model cache (Redis), opt-in semantic cache (pgvector).
5. **Retries & fallbacks** — provider down → fall back to alternative.
6. **Streaming** — SSE passthrough.
7. **Eval harness** — run a prompt against a test set, score outputs, store results.
8. **Rate limiting & budget** — per-user daily/monthly $ cap; hard stop when exceeded.
9. **Tool use orchestration** — accept tool definitions, dispatch tool calls back to caller via callback URL or queue.

### 8.2 Schema (`llm.*`)
```sql
-- Prompt registry (think Git for prompts)
CREATE TABLE llm.prompts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE llm.prompt_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_id UUID NOT NULL REFERENCES llm.prompts(id) ON DELETE CASCADE,
  version INT NOT NULL,
  template TEXT NOT NULL,             -- Jinja2 with {{ vars }}
  variables JSONB NOT NULL,           -- schema for vars
  default_model TEXT NOT NULL,
  default_params JSONB NOT NULL,      -- temperature, max_tokens, etc.
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (prompt_id, version)
);

-- Every LLM call logged
CREATE TABLE llm.runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,                       -- nullable for system runs
  prompt_version_id UUID REFERENCES llm.prompt_versions(id),
  model TEXT NOT NULL,
  provider TEXT NOT NULL,
  input JSONB NOT NULL,               -- messages, vars
  output JSONB,                       -- response (if not streaming) or stream summary
  input_tokens INT,
  output_tokens INT,
  cost_micro_usd BIGINT,              -- store as integer micro-USD
  latency_ms INT,
  status TEXT NOT NULL,               -- 'ok'|'error'|'rate_limited'|'budget_exceeded'
  error JSONB,
  trace_id TEXT,
  cache_hit BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON llm.runs (user_id, created_at DESC);
CREATE INDEX ON llm.runs (prompt_version_id);

-- Eval test sets
CREATE TABLE llm.evals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE llm.eval_cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  eval_id UUID NOT NULL REFERENCES llm.evals(id) ON DELETE CASCADE,
  input JSONB NOT NULL,
  expected JSONB,                     -- nullable for open-ended evals
  scorer TEXT NOT NULL,               -- 'exact'|'contains'|'llm-judge'|'regex'|'json-schema'
  scorer_config JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE llm.eval_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  eval_id UUID NOT NULL REFERENCES llm.evals(id),
  prompt_version_id UUID NOT NULL REFERENCES llm.prompt_versions(id),
  model TEXT NOT NULL,
  pass_count INT NOT NULL,
  fail_count INT NOT NULL,
  avg_latency_ms INT,
  total_cost_micro_usd BIGINT,
  results JSONB NOT NULL,             -- [{case_id, passed, score, output, error}]
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Per-user budget
CREATE TABLE llm.budgets (
  user_id UUID PRIMARY KEY,
  daily_limit_micro_usd BIGINT NOT NULL DEFAULT 5000000,    -- $5/day
  monthly_limit_micro_usd BIGINT NOT NULL DEFAULT 100000000, -- $100/mo
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 8.3 Key endpoints
```
POST /v1/complete              # one-shot completion (streaming or not)
POST /v1/complete/by-prompt    # uses a registered prompt version
POST /v1/embed                 # batch embeddings
GET  /v1/prompts               # list
POST /v1/prompts               # create new prompt
POST /v1/prompts/{slug}/versions   # new version (immutable)
GET  /v1/prompts/{slug}/versions/{v}
POST /v1/evals/{id}/run        # kicks off eval (async via jobs-svc)
GET  /v1/evals/runs/{id}
GET  /v1/usage                 # cost for current user, day/month
POST /v1/cache/invalidate
```

### 8.4 Caching strategy
- **Exact cache key:** `sha256(model + json(messages) + json(params))`. TTL 24h. Stored in Redis.
- **Semantic cache (opt-in per request):** embed the user query, search recent cached responses with cosine similarity ≥ 0.97, return if hit. Stored in pgvector.
- Cache hits set `cache_hit=true` in the run record but still log (with zero cost).

### 8.5 Cost tracking
- On every completion, compute cost from provider pricing table (in code, updated quarterly).
- Aggregate views: `llm.runs_daily_by_user`, `llm.runs_monthly_by_user` materialized views, refreshed by a cron job.
- Budget check happens BEFORE the call: estimate cost = `input_tokens * input_price + max_tokens * output_price`. If projected daily spend > limit, return 429 with `Retry-After`.

---

## 9. Service-by-service spec

### 9.1 `notes-svc`
**Purpose:** Notes with bidirectional links, full-text search, semantic search, auto-tagging.

**Schema:**
```sql
CREATE TABLE notes.notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  title TEXT NOT NULL,
  body_md TEXT NOT NULL,
  body_html TEXT,                  -- rendered cache
  tags TEXT[] NOT NULL DEFAULT '{}',
  embedding vector(1536),
  fts tsvector GENERATED ALWAYS AS (to_tsvector('english', title || ' ' || body_md)) STORED,
  metadata JSONB NOT NULL DEFAULT '{}',
  deleted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON notes.notes USING gin(fts);
CREATE INDEX ON notes.notes USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON notes.notes (user_id, updated_at DESC);

CREATE TABLE notes.links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id UUID NOT NULL REFERENCES notes.notes(id) ON DELETE CASCADE,
  target_id UUID NOT NULL REFERENCES notes.notes(id) ON DELETE CASCADE,
  context TEXT,                    -- snippet around the link
  UNIQUE (source_id, target_id)
);

CREATE TABLE notes.attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  note_id UUID NOT NULL REFERENCES notes.notes(id) ON DELETE CASCADE,
  r2_key TEXT NOT NULL,
  filename TEXT NOT NULL,
  mime TEXT NOT NULL,
  size_bytes BIGINT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RAG corpus (separate from personal notes)
CREATE TABLE notes.documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  title TEXT NOT NULL,
  source_url TEXT,
  source_type TEXT NOT NULL,       -- 'pdf'|'web'|'arxiv'|'manual'
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE notes.document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES notes.documents(id) ON DELETE CASCADE,
  chunk_index INT NOT NULL,
  text TEXT NOT NULL,
  embedding vector(1536) NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}',
  UNIQUE (document_id, chunk_index)
);
CREATE INDEX ON notes.document_chunks USING ivfflat (embedding vector_cosine_ops);
```

**Endpoints:**
```
GET    /v1/notes                  # list, paginated, ?q=&tag=&since=
POST   /v1/notes
GET    /v1/notes/{id}
PUT    /v1/notes/{id}
DELETE /v1/notes/{id}
GET    /v1/notes/{id}/backlinks
POST   /v1/notes/search           # body: {query, mode: 'fts'|'semantic'|'hybrid'}
POST   /v1/notes/{id}/auto-tag    # async via jobs-svc

POST   /v1/documents              # ingest (multipart for files, json for URLs)
GET    /v1/documents
POST   /v1/rag/query              # RAG over user's documents
```

**Background jobs (in jobs-svc):**
- `notes.reindex` — re-embed notes whose body changed.
- `notes.parse_links` — re-extract `[[link]]` references.
- `notes.auto_tag` — LLM call to suggest tags.
- `documents.ingest` — chunk + embed uploaded docs.

**Events emitted:** `notes.note.{created,updated,deleted}`, `notes.document.ingested`.

---

### 9.2 `habits-svc`
**Purpose:** Habits, todos, streaks, daily check-ins.

**Schema:**
```sql
CREATE TABLE habits.habits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  cadence TEXT NOT NULL,           -- 'daily'|'weekly'|'custom'
  cadence_config JSONB NOT NULL DEFAULT '{}',
  target_per_period INT NOT NULL DEFAULT 1,
  archived_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE habits.checkins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  habit_id UUID NOT NULL REFERENCES habits.habits(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  occurred_on DATE NOT NULL,
  count INT NOT NULL DEFAULT 1,
  note TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (habit_id, occurred_on)
);
CREATE INDEX ON habits.checkins (user_id, occurred_on DESC);

CREATE TABLE habits.todos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  title TEXT NOT NULL,
  body_md TEXT,
  due_at TIMESTAMPTZ,
  priority INT NOT NULL DEFAULT 3,    -- 1 highest .. 5 lowest
  status TEXT NOT NULL DEFAULT 'open', -- 'open'|'done'|'cancelled'
  parsed_from TEXT,                    -- original NL input if any
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON habits.todos (user_id, status, due_at);
```

**Endpoints:** standard CRUD, plus:
```
POST /v1/todos/parse              # NL → structured todo via llm-gateway
GET  /v1/habits/heatmap           # year-by-day grid
GET  /v1/habits/{id}/streak       # current + longest
POST /v1/checkins/today           # convenience: check in habit for today
```

**Computed views:**
```sql
CREATE MATERIALIZED VIEW habits.streaks AS
  WITH ... -- gap-and-island over checkins
;
-- Refreshed by jobs-svc nightly + on-demand on checkin events.
```

**Events:** `habits.checkin.created`, `habits.streak.broken`, `habits.todo.completed`.

---

### 9.3 `content-svc`
**Purpose:** Blog, learning log, project log, "now" page. Public read, authed write.

**Schema:**
```sql
CREATE TABLE content.posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL,              -- 'post'|'note'|'log'|'page'
  title TEXT NOT NULL,
  summary TEXT,
  body_mdx TEXT NOT NULL,
  tags TEXT[] NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'draft', -- 'draft'|'published'|'archived'
  published_at TIMESTAMPTZ,
  cover_image_url TEXT,
  reading_minutes INT,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON content.posts (status, published_at DESC);

CREATE TABLE content.reading_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  title TEXT NOT NULL,
  url TEXT,
  source TEXT,
  finished_on DATE,
  rating INT,                      -- 1..5
  notes_md TEXT,
  tags TEXT[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Endpoints:**
```
GET  /v1/posts                    # public, ?kind=&tag=&limit=
GET  /v1/posts/{slug}             # public
POST /v1/posts                    # authed
PUT  /v1/posts/{id}
POST /v1/posts/{id}/publish
GET  /v1/feed.rss                 # public RSS
GET  /v1/feed.json                # public JSON Feed
GET  /v1/sitemap.xml              # public

GET  /v1/reading-log              # public (read-only) + authed (write)
POST /v1/reading-log
```

**MDX rendering:** content-svc returns raw MDX; the Next.js frontend compiles via `next-mdx-remote/rsc`. Custom components (callouts, code blocks with Pyodide, charts) registered in the frontend.

---

### 9.4 `analytics-svc`
**Purpose:** Self-hosted, privacy-respecting analytics for the public site + tools.

**Schema:**
```sql
CREATE TABLE analytics.events (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  visitor_hash TEXT NOT NULL,      -- hash(ip + ua + daily salt), no IP stored
  session_id TEXT NOT NULL,
  event_name TEXT NOT NULL,        -- 'pageview'|'tool_used'|...
  path TEXT,
  referrer TEXT,
  country TEXT,
  ua_browser TEXT,
  ua_os TEXT,
  ua_device TEXT,
  props JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX ON analytics.events (ts DESC);
CREATE INDEX ON analytics.events (event_name, ts DESC);

-- Hourly rollup table (refreshed by jobs-svc)
CREATE TABLE analytics.events_hourly (
  hour TIMESTAMPTZ NOT NULL,
  event_name TEXT NOT NULL,
  path TEXT,
  count BIGINT NOT NULL,
  unique_visitors BIGINT NOT NULL,
  PRIMARY KEY (hour, event_name, path)
);
```

**Daily salt rotation:** salt rotates at UTC midnight, making cross-day fingerprinting impossible. Implements GDPR-friendly anonymous tracking.

**Endpoints:**
```
POST /v1/collect                  # public, no auth, used by frontend beacon
GET  /v1/dashboard                # authed, owner only
GET  /v1/dashboard/realtime
```

**Frontend integration:** small TS beacon (`apps/web/lib/analytics.ts`) sends events with `navigator.sendBeacon` for reliability, no cookies.

---

### 9.5 `games-svc`
**Purpose:** Game state, daily puzzles, leaderboards, multiplayer rooms.

**Schema:**
```sql
CREATE TABLE games.daily_puzzles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_slug TEXT NOT NULL,         -- 'pyworld', 'ml-papers', etc.
  for_date DATE NOT NULL,
  payload JSONB NOT NULL,          -- the puzzle itself
  solution JSONB NOT NULL,
  generated_by TEXT NOT NULL,      -- 'manual'|'llm'|'curated'
  UNIQUE (game_slug, for_date)
);

CREATE TABLE games.attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,                    -- nullable for anon
  visitor_hash TEXT,               -- if anon
  game_slug TEXT NOT NULL,
  puzzle_id UUID REFERENCES games.daily_puzzles(id),
  guesses JSONB NOT NULL DEFAULT '[]',
  solved_at TIMESTAMPTZ,
  duration_ms INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE games.rooms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_slug TEXT NOT NULL,
  code TEXT NOT NULL UNIQUE,       -- short joinable code
  host_user_id UUID,
  state JSONB NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'lobby',  -- 'lobby'|'active'|'ended'
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ended_at TIMESTAMPTZ
);
```

**Endpoints:**
```
GET  /v1/games                          # list available games
GET  /v1/games/{slug}/today             # today's puzzle
POST /v1/games/{slug}/attempts          # submit guess
GET  /v1/games/{slug}/leaderboard       # ?period=today|week|all
POST /v1/games/{slug}/rooms             # create room
POST /v1/games/{slug}/rooms/{code}/join
WS   /v1/games/{slug}/rooms/{code}      # WebSocket for live game
```

---

### 9.6 `jobs-svc`
**Purpose:** All scheduled and async work. One service, many job types.

**Stack:** Arq (Redis queue) + APScheduler for cron-style schedules, both inside one process group.

**Job catalog (initial):**
- `notes.reindex_changed` — every 5 min
- `notes.auto_tag` — triggered by event
- `documents.ingest` — triggered by upload
- `arxiv.daily_digest` — cron: 06:00 UTC daily; reads owner's interests from a config table, queries arXiv API, summarizes via llm-gateway, sends email
- `analytics.rollup_hourly` — every hour
- `habits.refresh_streaks` — nightly + on event
- `outbox.publish` — every 1s, scans all `*.outbox` tables
- `llm.cost_rollup` — nightly
- `backups.dump_postgres` — nightly to R2
- `sitemap.regenerate` — on content events
- `health.synthetic_check` — every 5 min, hits each service's `/readyz`

**Schema:**
```sql
CREATE TABLE jobs.cron (
  name TEXT PRIMARY KEY,
  schedule TEXT NOT NULL,
  last_run_at TIMESTAMPTZ,
  last_status TEXT,
  enabled BOOLEAN NOT NULL DEFAULT true
);
```

---

## 10. Frontend (`apps/web`) details

### 10.1 Routing

```
app/
├── (public)/
│   ├── page.tsx                    # home / landing
│   ├── about/page.tsx
│   ├── blog/
│   │   ├── page.tsx                # post list
│   │   └── [slug]/page.tsx
│   ├── log/page.tsx                # learning log
│   ├── now/page.tsx
│   ├── reading/page.tsx
│   ├── games/
│   │   ├── page.tsx                # game directory
│   │   └── [slug]/page.tsx
│   ├── tools/
│   │   ├── token-calculator/page.tsx
│   │   ├── json/page.tsx
│   │   └── regex/page.tsx
│   ├── feed.rss/route.ts
│   └── sitemap.xml/route.ts
├── (app)/
│   ├── layout.tsx                  # auth-gated, sidebar nav
│   ├── dashboard/page.tsx
│   ├── notes/...
│   ├── habits/...
│   ├── todos/...
│   ├── chat/...                    # multi-model chat
│   ├── prompts/...                 # prompt lab
│   ├── rag/...
│   ├── evals/...
│   └── settings/...
└── api/                            # tiny — Clerk webhook only
    └── webhooks/clerk/route.ts
```

### 10.2 Data fetching
- Server components for public read pages → call gateway with service token (server-to-server).
- Client components in authed app → use generated TS client + TanStack Query.
- No `fetch` directly in components; always through `apps/web/lib/api/<resource>.ts` wrappers.

### 10.3 Public site design
- Typography-first, monospace accents, dark mode default.
- Avoid generic AI/SaaS landing aesthetic. Inspirations: maggieappleton.com, jvns.ca, simonwillison.net.
- Accessibility: must pass axe with zero violations, keyboard-navigable everywhere.
- Performance budget: LCP <1.5s, CLS <0.05, TBT <200ms on mid-tier mobile. Lighthouse CI in pipeline.

### 10.4 Authed app shell
- Left sidebar with collapsible groups: AI, Productivity, Content, Analytics, Games.
- Command palette (`⌘K`) — global search across notes, todos, posts; quick-run prompts; navigate.
- Right-side "context drawer" — opens for AI assistance on the current page.

### 10.5 State management
- TanStack Query for server state.
- Zustand for ephemeral UI state (open modals, draft buffers).
- No Redux. No Recoil. No Jotai unless TanStack + Zustand prove insufficient.

---

## 11. Build order — phased plan

Each phase ends with a deployable, useful slice. **Do not skip phases.**

### Phase 0 — Repo & local dev (Days 1–2) ✅ DONE
- [x] `git init`, monorepo skeleton, MIT or unlicense.
- [x] `pyproject.toml` workspace, `uv` install.
- [x] `pnpm` workspace for `apps/web`.
- [x] Pre-commit: ruff, mypy, gitleaks, prettier.
- [x] `Makefile`: `bootstrap`, `dev`, `test`, `lint`, `format`, `typecheck`, `clean`.
- [x] `docker-compose.yml`: postgres, redis, minio (R2-equivalent locally).
- [x] `scripts/bootstrap.sh`: pulls deps, starts compose, runs migrations, seeds data.
- [x] CI skeleton (`.github/workflows/ci.yml`): lint + type + test on PR.

**Definition of done:** `make bootstrap && make dev` brings up Postgres, Redis, MinIO. `make test` passes (no tests yet, just the framework).

### Phase 1 — Foundation services (Week 1) ✅ DONE (local)
- [x] `libs/polymath-core`: settings (Pydantic Settings), logging (structlog), problem+json errors, request ID.
- [x] `libs/polymath-db`: SQLAlchemy async session factory, base model, `updated_at` trigger, Alembic helpers.
- [x] `libs/polymath-events`: Redis pubsub wrapper, outbox writer, JSON Schema validators.
- [x] `apps/gateway`: FastAPI skeleton, Clerk JWT middleware, `/healthz`, `/readyz`, `/version`, `/metrics`.
- [x] `apps/web`: Next.js skeleton, Clerk integration, public home page, authed `/dashboard` placeholder.
- [ ] OpenTelemetry SDK wired in core lib; collector running locally.
- [ ] First ADR: `0001-monorepo.md`.
- [ ] First deploy: Coolify on Hetzner, `polymath.dev` resolves, Cloudflare in front, Clerk auth works end-to-end.

**Definition of done:** Owner can sign up via Clerk, see authed dashboard, public home page is live at the real domain.

### Phase 2 — LLM gateway + prompt lab (Week 2) 🟡 PARTIAL — backend done, frontend pending
- [x] `apps/llm-gateway`: full schema in §8.2.
- [x] LiteLLM integration with at least Anthropic + OpenAI configured.
- [x] `/v1/complete`, `/v1/complete/by-prompt`, `/v1/embed` (non-streaming first).
- [ ] Streaming via SSE.
- [x] Exact-match Redis cache.
- [x] Cost tracking + per-user budget enforcement.
- [x] Prompt CRUD + immutable versions.
- [ ] Frontend: `/prompts` page — list, edit, version, run with variables, see history of runs.
- [ ] Frontend: `/chat` page — multi-model dropdown, streaming UI, conversation export.

**Definition of done:** Owner can write a prompt, run it across two models side-by-side, see token costs, and have a working chat UI they'd actually use over claude.ai for some workflows (e.g., tools that hit their own data later).

### Phase 3 — Content service + public site (Week 3) ✅ DONE
- [x] `apps/content-svc`: full schema in §9.3.
- [x] MDX support in frontend with custom components: callouts, code blocks (with copy), images with captions.
- [x] Blog list, post page, RSS, JSON Feed, sitemap.
- [x] `/now` page reading from a `posts` row of kind=`page`, slug=`now`.
- [ ] Reading log: list public, write authed.
- [ ] Author the first 2 posts: "Why I built Polymath" and "The architecture".

**Definition of done:** Public blog is live, RSS validates, sitemap submitted to Google Search Console.

### Phase 4 — Notes + RAG (Week 4–5) 🟡 PARTIAL — CRUD done, RAG pipeline pending
- [x] `apps/notes-svc`: full schema in §9.1.
- [x] CRUD endpoints, FTS search, `[[wikilinks]]` parsing.
- [ ] Embeddings pipeline triggered by outbox event.
- [ ] Hybrid search (FTS + cosine + reciprocal rank fusion).
- [ ] Document ingestion: PDF (`pypdf`), web (`trafilatura`), arXiv (paper ID → metadata + text).
- [ ] RAG endpoint: retrieve top-k → llm-gateway with a registered prompt → cited answer.
- [x] Frontend: notes editor (markdown textarea + preview), backlinks panel.
- [ ] Frontend: `/rag` page — drop a file or URL, ask questions, see cited chunks.

**Definition of done:** Owner has dropped 20 documents (papers, articles), can ask "what did I read about MoE routing last month" and get a cited answer.

### Phase 5 — Habits, todos, analytics (Week 6) 🟡 PARTIAL — habits done, analytics pending
- [x] `apps/habits-svc`: full schema in §9.2, streaks materialized view.
- [ ] `apps/analytics-svc`: full schema in §9.4, beacon endpoint.
- [x] `apps/jobs-svc`: APScheduler skeleton (digest cron live). Outbox publisher, hourly rollups, nightly streak refresh, R2 backups still pending.
- [x] Frontend: `/habits` — list, today's check-ins, year heatmap.
- [ ] Frontend: `/todos` — Kanban or list, NL input via llm-gateway.
- [ ] Frontend: `/dashboard` — habits, streak, LLM spend, GitHub commits (via GH API, cached), reading log highlights.
- [ ] Frontend beacon firing pageviews; `/analytics` page shows last 7/30 days.

**Definition of done:** Owner has logged 1 week of habits, dashboard reflects activity, analytics shows real traffic.

### Phase 6 — Games + first agent (Week 7)
- [ ] `apps/games-svc`: full schema in §9.5, WebSocket support.
- [ ] First game: a daily Python-stdlib puzzle (or owner's choice). LLM-generated daily, owner reviews & approves.
- [ ] Multiplayer prototype: shared state via Redis pubsub, WebSocket fanout.
- [ ] First agent (in jobs-svc): `arxiv.daily_digest`. Pulls papers matching saved interests, summarizes via llm-gateway, drafts an email; owner gets it daily.
- [ ] Frontend: `/games`, `/games/[slug]`, leaderboard.

**Definition of done:** Daily puzzle goes live publicly, owner gets first arXiv digest email.

### Phase 4.5 — Daily Research Digest (autonomous agent) ✅ DONE

**Goal:** Every morning, the platform automatically finds the best new research papers, condenses each to a 5-minute read, and delivers them to the owner's dashboard. Zero manual effort.

**How it works:**
1. `jobs-svc` fires a cron job at 07:00 UTC daily.
2. `digest-svc` fetches the top 20 papers published in the last 24h from arXiv (via API) filtered by configurable topic tags (e.g. AI, ML, systems, biology).
3. For each paper: downloads abstract + intro, scores relevance (LLM call to llm-gateway), picks the top 5.
4. For each of the top 5: sends full abstract + intro to llm-gateway, gets back a structured 5-min summary (key insight, why it matters, one-sentence takeaway).
5. Stores the digest as a `digest` record in `digest-svc` DB. Emits a `digest.created` event via outbox.
6. Frontend `/digest` page shows today's digest and a calendar of past digests.

**New service: `digest-svc` (port 8015)**

Schema (`digest` schema):
```sql
CREATE TABLE digest.digests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  for_date DATE NOT NULL UNIQUE,
  topic_tags TEXT[] NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE digest.papers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  digest_id UUID NOT NULL REFERENCES digest.digests(id) ON DELETE CASCADE,
  arxiv_id TEXT NOT NULL,
  title TEXT NOT NULL,
  authors TEXT[] NOT NULL,
  abstract TEXT NOT NULL,
  arxiv_url TEXT NOT NULL,
  relevance_score INT NOT NULL,        -- 1–10 LLM score
  summary_headline TEXT NOT NULL,      -- one punchy sentence
  summary_body TEXT NOT NULL,          -- 5-min condensed read (markdown)
  key_insight TEXT NOT NULL,           -- single key finding
  why_it_matters TEXT NOT NULL,        -- relevance to owner's interests
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON digest.papers (digest_id);
```

Endpoints:
```
GET /v1/digests              # list past digests (date + paper count)
GET /v1/digests/today        # today's digest + papers
GET /v1/digests/{date}       # specific date (YYYY-MM-DD)
POST /v1/digests/run         # manually trigger a run (for testing)
GET /v1/digests/{date}/papers/{paper_id}   # single paper detail
```

**Jobs-svc integration:**
- Add `DigestJob` cron task: `0 7 * * *` (07:00 UTC daily)
- Calls `digest-svc POST /v1/digests/run`

**Topic tags** (configurable via env var `DIGEST_TOPICS`):
```
cs.AI, cs.LG, cs.CL, cs.CV, stat.ML
```

**LLM prompt design (in llm-gateway prompt registry):**
- `digest/relevance-score` — given abstract, score 1-10 for relevance to "software engineer interested in AI/ML, systems, and developer tools"
- `digest/summarise` — given abstract + intro, return structured JSON: `{headline, body_md, key_insight, why_it_matters}`

**Frontend `/digest` page (authed):**
- Today's date header with paper count
- Each paper card: title, authors, arXiv link, relevance score badge, 5-min summary, key insight callout, "why it matters" section
- Calendar sidebar to browse past digests
- "Run now" button (calls POST /v1/digests/run via gateway)

**Definition of done:**
- [ ] `digest-svc` scaffolded with schema, repos, service layer, routes, alembic migration
- [ ] arXiv fetch + LLM scoring + summarisation pipeline working end-to-end
- [ ] Cron job in jobs-svc fires daily at 07:00 UTC
- [ ] `/digest` frontend page shows today's papers with full summaries
- [ ] Past digests browsable by date
- [ ] Manual trigger button works from the dashboard

---

### Phase 7 — Polish & utility tools (Week 8+, ongoing)
- [ ] Token calculator (public utility)
- [ ] JSON / regex / base64 / JWT debugger pages (public)
- [ ] Pyodide-powered "live notebook" code blocks in blog posts
- [ ] Open-graph image generator
- [ ] Public API docs page (auto from OpenAPI)
- [ ] Status page (driven by synthetic checks in jobs-svc)

---

## 12. Operations

### 12.1 Environments
- `local`: docker-compose, all services on `localhost`.
- `prod`: Coolify on Hetzner CX22 (or CX32 if RAM tight), single VPS.
- No `staging` for v1. Use feature flags + `main` deploys. Add staging if shipping breaks prod >once/month.

### 12.2 Deployment flow
1. Push to `main` → CI runs.
2. CI builds Docker images, tagged with git SHA, pushed to GHCR.
3. CI calls Coolify webhook with new SHA per service.
4. Coolify pulls image, runs Alembic migrations (in init container), rolls service.
5. Synthetic check fires within 30s; rollback if `/readyz` fails.

### 12.3 Secrets
- Local: `.env` files, gitignored. `.env.example` checked in.
- Prod: Coolify environment variables (encrypted at rest).
- Rotation runbook: `docs/runbooks/rotate-secrets.md`. Rotate quarterly.
- Never log secrets. Pre-commit `gitleaks` blocks accidents.

### 12.4 Backups
- Postgres: nightly `pg_dump` (custom format) → R2, retained 30 days, monthly retained 1 year.
- R2 itself: versioning enabled.
- Quarterly restore drill: spin up empty Postgres locally, restore latest dump, run smoke tests. Logged in runbooks.

### 12.5 Observability
- **Traces:** OTel SDK in every service, exported to Grafana Cloud Tempo.
- **Logs:** structlog → stdout → Coolify log driver → Grafana Cloud Loki via `promtail` agent on the VPS.
- **Metrics:** prometheus-fastapi-instrumentator in every service → scraped by Grafana Agent → Grafana Cloud Mimir.
- **Errors:** Sentry for unhandled exceptions on backend + frontend.
- **Dashboards:** in `infra/grafana/`, provisioned as code. At minimum: per-service request rate / error rate / p95 latency, LLM cost per day, queue depth.
- **Alerts:** Grafana → email/Telegram. Page on: any service `/readyz` failing >2min; LLM daily spend >budget; Postgres disk >80%; backup job failure.

### 12.6 Performance budgets
- API p95: 300ms reads, 800ms writes (excluding LLM).
- LLM endpoints: passthrough latency overhead <100ms over provider time.
- Frontend Lighthouse: ≥95 perf, ≥100 a11y on public pages.
- Bundle size: <200KB JS gzipped on home page.

### 12.7 Cost target
- VPS: ~€5–8/mo
- Cloudflare, Clerk free tiers: $0
- Postgres backups in R2: ~$0
- Grafana Cloud free tier: $0
- LLM spend: budgeted via in-app limits, target <$30/mo personal use
- **Total: ~$10–40/mo all-in**

---

## 13. Architecture Decision Records (initial set)

Each ADR is a short markdown file in `docs/adr/`. Template:
```
# 000X — Title
Date: YYYY-MM-DD
Status: Proposed | Accepted | Superseded by 000Y
## Context
## Decision
## Consequences
```

Initial ADRs to write during Phase 0/1:
1. **0001** Monorepo over polyrepo
2. **0002** Single Postgres with schema-per-service
3. **0003** REST + OpenAPI over GraphQL/gRPC
4. **0004** Outbox pattern for cross-service events
5. **0005** Clerk for auth (revisit at year 1)
6. **0006** Coolify on Hetzner over managed PaaS
7. **0007** Next.js for frontend despite Python preference
8. **0008** pgvector over dedicated vector DB
9. **0009** Arq over Celery
10. **0010** No staging environment for v1

---

## 14. Security checklist

- [ ] All endpoints behind auth except explicit public allowlist (validated by middleware).
- [ ] CSRF: SameSite=Lax cookies; mutations require `Origin` check + Clerk session.
- [ ] CORS: gateway allows only `polymath.dev` and `localhost:3000`.
- [ ] Rate limits: per-user (Clerk ID) and per-IP (X-Forwarded-For from Cloudflare).
- [ ] SQL injection: only parameterized queries via SQLAlchemy.
- [ ] Pydantic validates all inputs; reject unknown fields.
- [ ] Output encoding: never reflect user input as HTML without sanitization (DOMPurify on frontend).
- [ ] Secrets: never in repo; gitleaks pre-commit; quarterly rotation.
- [ ] Dependencies: Renovate bot; CI fails on critical CVEs (`pip-audit`, `pnpm audit`).
- [ ] Headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options set in Next.js + gateway.
- [ ] LLM: prompt injection mitigations — never execute tool calls without explicit user confirmation; sanitize doc contents before including in prompts.
- [ ] PII: don't log request bodies; redact emails in logs.
- [ ] Backups: encrypted at rest in R2; restore drill documented.

---

## 15. Definition of Done — for any feature

A feature is done when:
1. ✅ Endpoints documented in OpenAPI, generated client updated.
2. ✅ Unit tests cover domain logic (≥80% on changed lines).
3. ✅ Integration test covers happy path + one error path against real Postgres/Redis (testcontainers).
4. ✅ Migration applied and rolls back cleanly.
5. ✅ Frontend has loading, empty, and error states.
6. ✅ Tracing visible in Grafana for the new endpoint.
7. ✅ At least one log line at INFO documenting the action.
8. ✅ Metric exposed if it's a meaningful operation.
9. ✅ Runbook updated if there's a new failure mode.
10. ✅ ADR written if a non-trivial design choice was made.
11. ✅ README of the service updated.
12. ✅ Owner has used it for at least one real task (not a demo).

---

## 16. Open questions for the owner (resolve before Phase 1)

1. **Domain name** — confirm `polymath.dev` is acquirable, or pick a backup.
2. **Email provider for outbound** — Resend ($) or AWS SES (cheaper, more setup)?
3. **Initial LLM providers** — Anthropic + OpenAI minimum; add Voyage (embeddings) and Groq (fast/cheap)?
4. **Public vs. private RAG** — keep RAG and notes strictly owner-only, or eventually allow shared corpora?
5. **Mobile app?** — out of scope for now; Next.js PWA covers mobile-web; revisit at year 1.
6. **Comments on blog?** — recommend no for v1 (Mastodon webmention as alternative).

---

## 17. First-week concrete checklist (kickoff)

```
Day 1
[ ] Buy domain. Set Cloudflare nameservers.
[ ] Create GitHub repo (private initially).
[ ] Provision Hetzner CX22, install Docker, install Coolify.
[ ] Sign up: Clerk, Sentry, Grafana Cloud, Cloudflare R2.
[ ] Copy this PLAN.md into the repo.

Day 2
[ ] Run scripts/bootstrap.sh (write it as you go).
[ ] Implement libs/polymath-core (config, logging, errors).
[ ] First passing test.

Day 3
[ ] Implement libs/polymath-db.
[ ] First Alembic migration creates schemas + extensions.
[ ] docker-compose up brings the stack up locally.

Day 4
[ ] apps/gateway skeleton, healthz/readyz/metrics.
[ ] Clerk JWT verification middleware.

Day 5
[ ] apps/web skeleton, public home page.
[ ] Clerk sign-up flow → authed /dashboard placeholder.
[ ] Wire OTel.

Day 6
[ ] CI green: lint, type, test, build images, push to GHCR.
[ ] Deploy to Coolify, verify polymath.dev resolves with TLS.

Day 7
[ ] Synthetic check job in jobs-svc skeleton.
[ ] Write ADRs 0001–0006.
[ ] Phase 1 review: what worked, what to adjust before Phase 2.
```

---

## 18. Final notes for Claude Code

- **Ask before adding dependencies.** Each new dep is debt; prefer stdlib + chosen stack.
- **Generate tests with the code, not after.** A function without a test is incomplete.
- **Keep PRs small.** One concern per PR. Don't mix refactors with features.
- **Prefer composition over inheritance.** Domain models are dataclasses; no deep class hierarchies.
- **Don't optimize prematurely.** Profile before adding caching beyond what's specified here.
- **When the spec is silent, prefer the most boring option.** Surface the gap by writing a short ADR draft for owner review.

End of plan.
