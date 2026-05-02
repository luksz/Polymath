# 0009 — Arq over Celery for background jobs
**Date:** 2026-05-03
**Status:** Accepted

## Context
Background jobs are needed for: re-embedding notes, outbox publishing, arXiv digests, analytics rollups, and backups. Celery is the traditional choice but requires a broker (Redis or RabbitMQ) and has a heavier API surface.

## Decision
Use Arq (async Redis queue) for job execution and APScheduler for cron-style schedules, both running inside `jobs-svc`. Redis is already a project dependency, so no new infrastructure is needed.

## Consequences
- Lighter API than Celery — job functions are plain async Python functions.
- Redis-only broker (no RabbitMQ option) — acceptable since Redis is already required.
- Smaller ecosystem than Celery; less documentation.
- All scheduled and async work is centralised in `jobs-svc`, making it easy to inspect the job catalog.
