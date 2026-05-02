# Polymath Gateway

The API Gateway (BFF) is the single entry point for all frontend requests. It:

- Authenticates every request via **Clerk JWT** and injects `X-Polymath-User-Id` into downstream calls
- Proxies and fan-outs requests to internal microservices (llm-gateway, notes-svc, habits-svc, etc.)
- Enforces rate limiting via `slowapi`
- Exposes Prometheus metrics at `/metrics`
- Propagates OpenTelemetry traces to all downstream services

## How Auth Works

1. The Next.js frontend includes a Clerk session token either as `Authorization: Bearer <token>` or via the `__session` cookie.
2. The gateway fetches Clerk's JWKS endpoint, verifies the RS256 JWT signature, and extracts `sub` (the Clerk user ID).
3. The verified user ID is forwarded to downstream services as the `X-Polymath-User-Id` header.
4. Downstream services trust this header because they share the `POLYMATH_SERVICE_SECRET` HMAC secret (Phase 1+ will use full HMAC signing via `service_auth.py`).

**Dev bypass:** If `CLERK_SECRET_KEY` is not set, the gateway accepts `X-Dev-User-Id` directly (no JWT verification). Never use this in production.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/healthz` | none | Liveness probe |
| GET | `/readyz` | none | Readiness probe |
| GET | `/version` | none | Service version info |
| GET | `/metrics` | none | Prometheus metrics |
| POST | `/v1/llm/complete` | required | Proxy to llm-gateway `/v1/complete` |
| GET | `/v1/llm/prompts` | required | Proxy to llm-gateway `/v1/prompts` |
| GET | `/v1/llm/usage` | required | Proxy to llm-gateway `/v1/usage` |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLERK_SECRET_KEY` | `""` | Clerk secret key (omit for dev bypass) |
| `CLERK_PUBLISHABLE_KEY` | `""` | Clerk publishable key |
| `LLM_GATEWAY_URL` | `http://llm-gateway:8001` | Internal llm-gateway URL |
| `NOTES_SVC_URL` | `http://notes-svc:8002` | Internal notes service URL |
| `HABITS_SVC_URL` | `http://habits-svc:8003` | Internal habits service URL |
| `CONTENT_SVC_URL` | `http://content-svc:8004` | Internal content service URL |
| `ANALYTICS_SVC_URL` | `http://analytics-svc:8005` | Internal analytics service URL |
| `GAMES_SVC_URL` | `http://games-svc:8006` | Internal games service URL |
| `JOBS_SVC_URL` | `http://jobs-svc:8007` | Internal jobs service URL |
| `DEFAULT_TIMEOUT` | `5.0` | Default upstream call timeout (seconds) |
| `LLM_TIMEOUT` | `30.0` | LLM upstream call timeout (seconds) |
| `RATE_LIMIT_PER_MINUTE` | `60` | Max requests per IP per minute |
| `POLYMATH_SERVICE_SECRET` | `dev-secret-changeme` | Shared HMAC secret for inter-service auth |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | OpenTelemetry collector endpoint |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENVIRONMENT` | `development` | `development` or `production` |

## Running Locally

```bash
# From repo root (uv workspace)
uv run --package gateway uvicorn gateway.main:app --reload --port 8000
```

Or with Docker:

```bash
docker build -t polymath-gateway apps/gateway
docker run -p 8000:8000 -e CLERK_SECRET_KEY=your_key polymath-gateway
```

## Running Tests

```bash
# From repo root
uv run pytest apps/gateway/tests/
```
