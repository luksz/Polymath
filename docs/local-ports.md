# Local Dev Ports

All Polymath services use non-default ports to avoid conflicts with other local projects.

| Service      | Local Port | Notes                              |
|--------------|-----------|-------------------------------------|
| Postgres     | 5434      | Default 5432 taken by other project |
| Redis        | 6380      | Default 6379 taken by other project |
| MinIO API    | 9002      | Default 9000 taken by other project |
| MinIO UI     | 9003      | Default 9001 taken by other project |
| llm-gateway  | 8011      | Default 8001 taken by other project |
| gateway      | 8010      | Default 8000 taken by PokerNow      |
| notes-svc    | 8012      | Default 8002 taken by other project |
| habits-svc   | 8013      | Default 8003 taken by other project |
| web          | 3000      | —                                   |

## Connection strings (local dev)

```
DATABASE_URL=postgresql+asyncpg://polymath:polymath@localhost:5434/polymath
REDIS_URL=redis://localhost:6380/0
S3_ENDPOINT_URL=http://localhost:9002
NEXT_PUBLIC_GATEWAY_URL=http://localhost:8010
```

## MinIO Console

Open http://localhost:9003 — login: `minioadmin` / `minioadmin`

## Run order (local, outside Docker)

```bash
# Terminal 1 — infra
make dev-backend

# Terminal 2
cd apps/llm-gateway && uv run uvicorn llm_gateway.main:app --reload --port 8011

# Terminal 3
cd apps/notes-svc && uv run uvicorn notes_svc.main:app --reload --port 8012

# Terminal 4
cd apps/habits-svc && uv run uvicorn habits_svc.main:app --reload --port 8013

# Terminal 5
cd apps/gateway && uv run uvicorn gateway.main:app --reload --port 8010

# Terminal 6
cd apps/web && pnpm dev
```
