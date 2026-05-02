# 0004 — Outbox pattern for cross-service events
**Date:** 2026-05-03
**Status:** Accepted

## Context
Services need to notify each other (e.g., notes-svc tells jobs-svc to re-embed a note). A direct Redis publish in the same DB transaction is not atomic — the publish can succeed while the DB write fails, or vice versa.

## Decision
Each service that emits events writes to a `<schema>.outbox` table within the same DB transaction as the business operation. A background worker in `jobs-svc` polls all outbox tables, publishes to Redis pub/sub, and marks rows as published. This is the transactional outbox pattern.

Event envelope format:
```json
{ "event_id": "uuid", "event_type": "notes.note.created", "version": 1, "occurred_at": "...", "actor": {...}, "data": {...} }
```

## Consequences
- At-least-once delivery (safe because consumers are idempotent on `event_id`).
- No distributed transactions required.
- Slight latency (up to outbox poll interval, default 1s).
- The outbox table doubles as an event log for debugging.
