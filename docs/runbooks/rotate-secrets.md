# Secret Rotation Runbook

Rotate all secrets quarterly (every 3 months). Last rotation: (fill in date).

## Rotation checklist

### `POLYMATH_SERVICE_SECRET`
Internal HMAC secret used for gateway → service auth.
1. Generate new secret: `openssl rand -hex 32`
2. Update in Coolify env vars for ALL services simultaneously (gateway, llm-gateway, notes-svc, habits-svc, content-svc, analytics-svc, games-svc, jobs-svc).
3. Redeploy all services.
4. Verify inter-service calls still work (smoke test each service's `/readyz`).

### `CLERK_SECRET_KEY` and `CLERK_WEBHOOK_SECRET`
1. Go to Clerk dashboard → API Keys.
2. Rotate the secret key (Clerk allows both old and new to be active briefly).
3. Update `CLERK_SECRET_KEY` in Coolify for `gateway` service.
4. Update `CLERK_WEBHOOK_SECRET` for webhooks.
5. Redeploy gateway.
6. Test: sign in via the app and confirm session works.

### `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`
1. Go to Anthropic/OpenAI console → API Keys.
2. Create a new key.
3. Update in Coolify env for `llm-gateway`.
4. Redeploy `llm-gateway`.
5. Test: run a prompt from the /prompts UI and confirm a successful response.
6. Delete the old key from the provider console.

### `RESEND_API_KEY`
1. Go to Resend dashboard → API Keys.
2. Create a new key.
3. Update in Coolify env for `jobs-svc`.
4. Redeploy `jobs-svc`.
5. Trigger an arXiv digest manually and confirm email arrives.

### Postgres passwords (`*_DEV` service users)
1. For each service user: `ALTER USER <svc>_svc WITH PASSWORD '<new_password>';`
2. Update corresponding `DATABASE_URL` in Coolify for that service.
3. Redeploy the service.
4. Verify `/readyz` returns healthy.

### `SENTRY_DSN`
Sentry DSNs don't need regular rotation but rotate if compromised:
1. Sentry dashboard → Project Settings → Client Keys → Add new DSN.
2. Update in Coolify for all services.
3. Redeploy all services.
4. Trigger a test error and confirm it appears in Sentry.

## Post-rotation verification
- [ ] All service `/readyz` endpoints return 200
- [ ] Authentication flow (sign-in) works end-to-end
- [ ] One LLM completion succeeds (checks API keys)
- [ ] Check Grafana for any error spike post-rotation
- [ ] Update "Last rotation" date at top of this file
