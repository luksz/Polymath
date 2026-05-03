# Local Dev Ports

All Polymath services use non-default ports to avoid conflicts with other local projects.

| Service     | Local Port | Notes                        |
|-------------|-----------|------------------------------|
| Postgres    | 5434      | Default 5432 was taken       |
| Redis       | 6380      | Default 6379 was taken       |
| MinIO API   | 9002      | Default 9000 was taken       |
| MinIO UI    | 9003      | Default 9001 was taken       |
| llm-gateway | 8001      | —                            |
| gateway     | 8000      | —                            |
| web         | 3000      | —                            |

## Connection strings (local dev)

```
DATABASE_URL=postgresql+asyncpg://polymath:polymath@localhost:5434/polymath
REDIS_URL=redis://localhost:6380/0
S3_ENDPOINT_URL=http://localhost:9002
```

## MinIO Console

Open http://localhost:9003 — login: `minioadmin` / `minioadmin`
