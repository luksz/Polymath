# 0005 — Clerk for managed auth
**Date:** 2026-05-03
**Status:** Accepted

## Context
Building auth from scratch (password hashing, JWT rotation, OAuth flows, MFA, session management) is a multi-sprint project. Polymath is a personal platform with one user. The cost of a security mistake in custom auth is high.

## Decision
Use Clerk as a managed auth provider for v1. Clerk handles sign-up, sign-in, OAuth, session tokens, and webhooks. The gateway validates Clerk JWTs on every request and injects `X-Polymath-User-Id` for downstream services.

## Consequences
- Vendor dependency on Clerk. Free tier covers personal use.
- Clerk webhooks mirror user events into `auth.users` for FK references.
- Revisit at year 1: migrate to self-hosted if Clerk pricing changes or feature needs require it.
- No auth code to maintain, test, or audit.
