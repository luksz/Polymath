# Polymath — Claude Code Guide

## Project overview

Polymath is a personal web platform: portfolio + blog publicly, AI tools + productivity + analytics + games privately.

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0 async, Alembic, Pydantic v2
- **Frontend**: Next.js 15 App Router, Tailwind CSS 4, shadcn/ui
- **Auth**: Clerk (managed)
- **Data**: Postgres 16 + pgvector, Redis 7, Cloudflare R2 (MinIO locally)
- **Deploy**: Docker Compose locally, Coolify on Hetzner in prod
- **AI**: LiteLLM routing Anthropic + OpenAI, polymath-llm lib, llm-gateway service

Full spec: see PLAN.md.

## Critical rules

1. **Follow §11 build order in PLAN.md strictly.** Current phase: **Phase 0**. Do not work on Phase 1 features until Phase 0 definition of done is met.
2. **Every service follows the template in §6 of PLAN.md.** Use `make new-service NAME=foo` to scaffold.
3. **ADRs in `docs/adr/` are binding.** If a decision seems wrong, write a draft ADR and surface it before deviating.
4. **Every function must have a test.** Coverage gate: 70% for services, 90% for shared libs.
5. **Observability from day one.** Every service must emit OTel traces, structlog logs, and Prometheus metrics.
6. **Frontend never calls internal services directly.** All traffic goes through `apps/gateway`.
7. **Services don't call each other synchronously** unless there is an ADR documenting the exception.
8. **No shared ORM models across services.** Shared types live in the generated OpenAPI client.
9. **Ask before adding a dependency.** Each new dep is debt. Prefer stdlib + the locked stack.
10. **All commits: Conventional Commits format.** E.g. `feat(notes): add semantic search`, `fix(gateway): retry on 502`.

## Current phase

**Phase 0 — Repo & local dev**

Definition of done:
- `make bootstrap && make dev` starts Postgres, Redis, MinIO
- `make test` passes (framework is working, even if no tests yet)

Next: Phase 1 — Foundation services (polymath-core, polymath-db, polymath-events, gateway skeleton, web skeleton, OTel).

## Dev workflow

```bash
make bootstrap    # first-time setup
make dev          # daily: start all infra + services
make test         # run tests
make lint         # ruff check
make format       # ruff format
make typecheck    # mypy
make check        # lint + typecheck combined
```

## Adding a service

```bash
make new-service NAME=my-svc
# Then: add "apps/my-svc" to pyproject.toml workspace members
# Add service to docker-compose.yml
```

## Key files

| File | Purpose |
|---|---|
| PLAN.md | Source of truth — full spec, architecture, build order |
| docs/adr/ | Architectural decision records — all binding |
| Makefile | All development commands |
| docker-compose.yml | Local dev stack |
| scripts/new-service.sh | Service scaffolder |
| libs/polymath-core/ | Shared config, logging, errors, OTel |
| libs/polymath-db/ | SQLAlchemy base, session factory |
| libs/polymath-events/ | Event envelope, outbox writer, Redis publisher |
| apps/llm-gateway/ | LLM routing, prompt registry, cost tracking |

## Definition of Done (for any feature)

A feature is done when ALL of the following are true:

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

## Open questions (resolve before Phase 1)

1. **Domain name** — confirm `polymath.dev` is acquirable, or pick a backup (Atlas, Lighthouse, Forge).
2. **Email provider** — Resend or AWS SES for outbound email?
3. **LLM providers** — Anthropic + OpenAI minimum; add Voyage AI (embeddings) and Groq (fast/cheap)?
4. **RAG visibility** — keep notes and RAG strictly owner-only, or allow shared corpora later?
5. **Mobile app** — Next.js PWA covers mobile-web for now; revisit at year 1.
6. **Blog comments** — recommend none for v1; Mastodon webmention as alternative?
