# 0003 — REST + OpenAPI over GraphQL or gRPC
**Date:** 2026-05-03
**Status:** Accepted

## Context
The frontend is a single consumer. Internal service-to-service calls are infrequent and go through the gateway. Developer is comfortable with REST; GraphQL and gRPC add tooling and cognitive overhead.

## Decision
REST with FastAPI (OpenAPI auto-generated from Pydantic schemas). A TypeScript client is generated from the merged OpenAPI spec via `openapi-typescript` and checked into `apps/web/lib/api-client/`.

## Consequences
- HTTP is easy to debug with curl, browser devtools, and Postman.
- OpenAPI gives a self-documenting, type-safe client for free.
- Slight N+1 risk on complex screens mitigated by gateway fan-out (the BFF aggregates multiple service calls before responding to frontend).
- No GraphQL resolver complexity or gRPC proto management.
