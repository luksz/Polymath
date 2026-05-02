# 0010 — No staging environment for v1
**Date:** 2026-05-03
**Status:** Accepted

## Context
A staging environment would double the VPS cost and require maintaining config parity. The project has one user (the owner) and low traffic. The risk of a bad prod deploy is recoverable (Postgres backup, fast rollback via Coolify).

## Decision
No staging environment for v1. All deploys go directly to production from `main`. Risky changes use feature flags or are developed behind `/experimental` routes. If production breaks more than once per month, add staging.

## Consequences
- Occasional prod breakage risk.
- Offset by: fast deploy pipeline (~3 min), Coolify one-click rollback, nightly Postgres backups to R2.
- Forces discipline: no "it works in staging" — everything is tested locally + CI.
- Trigger to add staging: prod breaks >1×/month OR a second user is onboarded.
