# 0002 — Single Postgres, schema-per-service
**Date:** 2026-05-03
**Status:** Accepted

## Context
Running one Postgres instance per service would require 8+ databases on a single €5/mo VPS. Each service still needs isolation to prevent accidental cross-service SQL reads.

## Decision
One Postgres 16 instance with one schema per service (`auth`, `notes`, `habits`, `content`, `analytics`, `games`, `llm`, `jobs`). Each service gets its own DB user with `GRANT` access only to its schema. No foreign keys across schemas.

## Consequences
- Single DB process — low RAM usage.
- Schema-level isolation enforced at the DB user layer.
- Cross-service data access must go through APIs, not SQL joins.
- Migrations are per-service (each has its own Alembic env pointing at its schema).
- If a service ever needs to move to its own DB, the schema can be exported cleanly.
