# Polymath

> Personal platform — many disciplines, one mind.

[![CI](https://github.com/luksz/polymath/actions/workflows/ci.yml/badge.svg)](https://github.com/luksz/polymath/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## What is this?

Polymath is a self-hosted personal OS. A portfolio and blog on the outside — AI tools, productivity, and a daily research digest on the inside. One domain, one codebase, owned by you.

## What's built

| Layer | Status | What |
|---|---|---|
| **Public site** | ✅ shipped | Home, `/blog`, `/projects`, `/now` |
| **Notes** | ✅ CRUD + FTS | Create, edit, search personal notes (semantic search via pgvector pending) |
| **Habits** | ✅ shipped | Daily habit tracking with streaks + to-do list |
| **Writing** | ✅ shipped | Private MDX editor — drafts → publish to public blog |
| **Daily Digest** | ✅ shipped | Runs every morning at 07:00 UTC, finds top arXiv papers, LLM-condenses each to a 5-min read |
| **LLM routing** | ✅ shipped | All AI calls flow through `llm-gateway` — cost tracking, caching, budget caps |
| **Chat / Prompts UI** | 🚧 backend only | `/chat` + `/prompts` frontend pages not built yet |
| **Analytics** | 🚧 stub | `analytics-svc` scaffolded, no pipeline yet |
| **Games** | 🚧 stub | `games-svc` scaffolded, no puzzles yet |
| **Notes RAG** | 🚧 pending | Embedding + retrieval pipeline not wired |

## Services

| Service | Local Port | Description |
|---|---|---|
| `gateway` | 8010 | BFF — Clerk auth, routes all frontend traffic |
| `llm-gateway` | 8011 | LLM routing (Anthropic + OpenAI), cost tracking, Redis cache |
| `notes-svc` | 8012 | Notes CRUD, full-text search, pgvector semantic search |
| `habits-svc` | 8013 | Habits, check-ins, streaks, todos |
| `content-svc` | 8014 | Blog posts, projects, now page, RSS feed |
| `digest-svc` | 8015 | Daily research paper fetcher + LLM summariser |
| `analytics-svc` | 8016 | Privacy-respecting page analytics (no cookies) |
| `games-svc` | 8017 | Daily puzzles, leaderboards |
| `jobs-svc` | 8018 | Cron scheduler, outbox publisher, background workers |
| `web` | 3000 | Next.js 15 App Router frontend |

> See [docs/local-ports.md](docs/local-ports.md) for the full port map.

## Quick start

```bash
git clone https://github.com/luksz/polymath
cd polymath
make bootstrap        # install Python + Node deps, copy .env, start infra
make dev-backend      # start Postgres (5434), Redis (6380), MinIO (9002)
```

Create a root `.env` before running anything that calls the LLM:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...          # optional
```

Then in separate terminals:
```bash
cd apps/gateway   && uv run uvicorn gateway.main:app      --reload --port 8010
cd apps/web       && pnpm dev
```

Full run order in [docs/local-ports.md](docs/local-ports.md).

## Tech stack

| Concern | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Alembic |
| Frontend | Next.js 15 App Router, Tailwind CSS, shadcn/ui |
| Auth | Clerk (managed) |
| Database | Postgres 16 + pgvector |
| Cache | Redis 7 |
| Storage | Cloudflare R2 (MinIO locally) |
| AI | LiteLLM → Anthropic + OpenAI |
| Deploy | Docker Compose locally, Coolify on Hetzner in prod |

## Development

```bash
make help                        # all commands
make test                        # run all tests
make lint                        # ruff check
make typecheck                   # mypy
make check                       # lint + typecheck
make migrate SVC=notes-svc       # run alembic upgrade head for a service
make new-service NAME=my-svc     # scaffold a new service
```

## License

MIT
