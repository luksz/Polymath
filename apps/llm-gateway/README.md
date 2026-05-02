# llm-gateway

LLM Gateway service for Polymath. All AI calls go through here — never directly to LLM providers.

## What it does

- **Provider routing** — Anthropic and OpenAI via LiteLLM, with fallback support
- **Prompt registry** — versioned, immutable prompt templates (Jinja2)
- **Cost tracking** — every call logged with token counts and micro-USD cost
- **Exact-match caching** — Redis, 24h TTL, key = `sha256(model + messages + params)`
- **Budget enforcement** — per-user daily/monthly $ caps; returns 429 if exceeded
- **Streaming** — SSE passthrough via `/v1/complete/stream`

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/v1/complete` | Non-streaming completion |
| POST | `/v1/complete/stream` | SSE streaming completion |
| POST | `/v1/embed` | Batch embeddings |
| GET | `/v1/prompts` | List prompts |
| POST | `/v1/prompts` | Create prompt |
| POST | `/v1/prompts/{slug}/versions` | Add prompt version |
| GET | `/v1/prompts/{slug}/versions/{v}` | Get prompt version |
| GET | `/v1/usage` | Cost usage for current user |
| GET | `/healthz` | Liveness |
| GET | `/readyz` | Readiness (checks DB) |
| GET | `/metrics` | Prometheus metrics |
| GET | `/version` | Service version |

## Run locally

```bash
cd apps/llm-gateway
uv run uvicorn llm_gateway.main:app --reload --port 8001
```

## Key env vars

```
DATABASE_URL        Postgres connection string
REDIS_URL           Redis connection string
ANTHROPIC_API_KEY   Anthropic API key
OPENAI_API_KEY      OpenAI API key
```

## Design decisions

- Costs stored as `BIGINT` micro-USD (integer arithmetic only, no floats for money)
- Cache key is `sha256(model + sorted_messages + params)` — deterministic, no collisions
- Budget check happens before the LLM call using worst-case token estimate
- All LLM calls logged to `llm.runs` regardless of cache hit
