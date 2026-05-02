# Polymath

> Personal platform — many disciplines, one mind.

[![CI](https://github.com/luksz/polymath/actions/workflows/ci.yml/badge.svg)](https://github.com/luksz/polymath/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

Polymath is a single-domain personal platform: a portfolio and blog on the outside, and AI-powered productivity tools, analytics, games, and a RAG knowledge base on the inside. One domain, multiple focused services, a shared backbone.

## Quick start

```bash
git clone https://github.com/luksz/polymath
cd polymath
make bootstrap   # install deps, start Postgres/Redis/MinIO, copy .env
make dev         # start all services
```

See PLAN.md for the full architecture spec.

## Services

| Service | Port | Description |
|---|---|---|
| gateway | 8000 | BFF API gateway — all frontend traffic goes here |
| llm-gateway | 8001 | LLM provider routing, prompt registry, cost tracking |
| notes-svc | 8002 | Notes with wikilinks, FTS, semantic search, RAG |
| habits-svc | 8003 | Habits, todos, streaks, daily check-ins |
| content-svc | 8004 | Blog, learning log, reading list, RSS |
| analytics-svc | 8005 | Privacy-respecting site analytics |
| games-svc | 8006 | Daily puzzles, leaderboards, multiplayer |
| jobs-svc | 8007 | Arq workers, cron jobs, outbox publisher |

## Development

```bash
make help         # all available commands
make test         # run tests
make lint         # ruff lint
make typecheck    # mypy
make check        # lint + typecheck
make psql         # open psql shell
make new-service NAME=my-svc   # scaffold a new service
```

## Contributing

- Conventional Commits: `feat(notes): add semantic search`
- One concern per PR, squash merge
- See PLAN.md §15 for the Definition of Done

## License

MIT
