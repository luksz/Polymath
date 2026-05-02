# Deploy Runbook

## Prerequisites
- Hetzner VPS running with Coolify installed
- `polymath.dev` pointing to VPS IP via Cloudflare (proxied)
- GHCR credentials configured in Coolify
- All `COOLIFY_WEBHOOK_*` secrets set in GitHub repo settings

## Normal deploy flow

1. **Push to `main`** — any push (squash-merged PR) triggers CI.
2. **CI passes** — lint → test → build-images jobs run (~3–5 min).
3. **Deploy workflow fires** — on CI success, builds Docker images per service, pushes to `ghcr.io/OWNER/polymath/<svc>:SHA` and `:latest`.
4. **Coolify webhook** — each service notifies its Coolify webhook URL, which triggers a pull + restart.
5. **Health check** — Coolify waits for `/readyz` to return 200 before marking the deploy successful.
6. **Synthetic check** — `jobs-svc` health check fires within 5 min to confirm all services are up.

**Total time:** ~5–8 minutes from push to live.

## Rollback procedure

### Via Coolify UI
1. Open Coolify dashboard → select the failing service.
2. Click "Deployments" → find the last successful deployment SHA.
3. Click "Redeploy" on that deployment.

### Via CLI (manual)
```bash
# SSH into VPS
ssh root@<VPS_IP>

# Pull the previous image tag
docker pull ghcr.io/OWNER/polymath/<svc>:<PREVIOUS_SHA>

# Restart with that image (update docker-compose.prod.yml override)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d <svc>
```

## Emergency hotfix procedure

1. Create a branch from `main`.
2. Make the minimal fix.
3. Open a PR, get CI green, squash-merge.
4. Normal deploy flow runs automatically.

For a **true emergency** (prod is down, no time for CI):
1. SSH into VPS.
2. `docker exec -it <container> bash` to inspect.
3. Apply fix directly if it's config-only (env var change).
4. For code changes: deploy via Coolify using the last known-good image while you prepare the fix PR.

## Post-deploy checklist
- [ ] Check Grafana dashboard for error rate spike
- [ ] Verify `/readyz` on each service
- [ ] Check Sentry for new errors
- [ ] Confirm LLM spend did not spike unexpectedly
