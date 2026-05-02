# 0006 — Coolify on Hetzner over managed PaaS
**Date:** 2026-05-03
**Status:** Accepted

## Context
Heroku is ~$25+/mo per dyno. Fly.io and Railway add per-service overhead that compounds with 8 services. A personal project budget target is <$10/mo infra.

## Decision
Self-host Coolify (open-source Heroku alternative) on a Hetzner CX22 VPS (~€4/mo). Coolify handles Docker-based deploys, env var management, and basic monitoring. Cloudflare sits in front for CDN and WAF.

## Consequences
- ~€4–8/mo total infra cost.
- Operational burden falls on the owner (one person).
- No SLA — acceptable for a personal project.
- If the VPS goes down, so does everything. Mitigated by Postgres backups to R2 and stateless services that restart quickly.
- Revisit if moving to a team or needing HA.
