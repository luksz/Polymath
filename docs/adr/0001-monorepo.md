# 0001 — Monorepo over polyrepo
**Date:** 2026-05-03
**Status:** Accepted

## Context
Polymath is built by one developer. Services share types, migrations, and tooling. Cross-service changes (e.g., adding a field that flows from gateway → notes-svc → frontend) are common during early development.

## Decision
Use a single Git repository with `uv` workspaces for Python packages and `pnpm` workspaces for the frontend. All services and shared libs live under one repo root.

## Consequences
- One CI pipeline, one clone, one set of tooling to maintain.
- Atomic commits that span multiple services.
- Repo grows over time — manage with clear directory conventions.
- No need for a service mesh to share types; shared libs are workspace dependencies.
