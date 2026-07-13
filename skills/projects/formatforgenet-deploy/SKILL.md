---
name: "formatforgenet-deploy"
description: "FormatForgeNet SaaS deployment: split-topology deploy with JP frontend node + local backend Docker containers via Tailscale. 前后端分离部署, 日本节点前端, 本机Docker后端, Tailscale隧道, docker compose, scp, deploy-frontend.sh."
revision: 1
---

# FormatForgeNet Production Deployment

> Crystallized from: repeated deployment confusion across deai-review integration, daily-stats-report, and prior feature rollouts
> Date: 2026-04-16
> Trigger: T3 (user explicitly requested crystallization)

## When to Use

- Deploying any code change to FormatForgeNet production (new feature, bugfix, config change)
- Adding a new Docker service to the stack
- Updating frontend components that need to reach production users
- Any plan task labeled "生产部署" / "production deployment"

## When NOT to Use

- Local development/testing only (use `docker compose up -d --build` directly)
- Changes to de-ai-fier, FormatForge, or pdf2md repos that don't affect FormatForgeNet SaaS
- Database migrations (require separate Alembic workflow, not covered here)

## Architecture

```
Users (internet)
  │
  ▼
┌─────────────────────────────────────┐
│  Japan Node (100.82.241.21)         │
│  - System nginx (not Docker)        │
│  - Serves static frontend from      │
│    /var/www/formatforge/             │
│  - Proxies /api/ and /docconv-files/│
│    to local machine via Tailscale   │
│  - Domain: formatforge.dev (HTTPS)  │
└──────────┬──────────────────────────┘
           │ Tailscale tunnel
           ▼
┌─────────────────────────────────────┐
│  Local Machine (gw-Precision-5820)  │
│  - ALL Docker containers:           │
│    backend, worker-cpu, celery-beat │
│    nginx(:28080), minio, postgres   │
│    redis, formatforge-api           │
│    pdf2md-api, deai-review-api      │
│  - Docker nginx is internal only    │
│    (not exposed to internet)        │
│  - .env at docconv-saas/.env        │
└─────────────────────────────────────┘
```

Key facts:
- **No Docker on Japan node.** Frontend is plain static files served by system nginx.
- **No git remote for FormatForgeNet.** Code lives only on local machine. No `git push` needed for backend.
- **Docker build contexts reference local paths** (e.g., `/home/gw/opt/de-ai-fier` for deai-review-api). These paths exist on the build machine.
- **Tailscale SSH** to Japan node may require browser authentication. Watch for `# Tailscale SSH requires an additional check` in terminal output.

## Workflow

### Step 1: Identify what changed

Determine which components need redeployment:

| Change location | Action needed |
|----------------|---------------|
| `backend/app/` (routers, schemas, workers, config, services) | Rebuild: `backend`, `worker-cpu` |
| `backend/app/workers/celery_app.py` or beat schedules | Rebuild: `worker-cpu`, `celery-beat` |
| New Docker service in `docker-compose.yml` | Rebuild: the new service + `worker-cpu` (if new queue) + `backend` (if new routes) |
| `frontend/src/` | Run `deploy-frontend.sh` |
| `nginx/nginx.conf` | Rebuild: `nginx` (local Docker nginx, NOT Japan node) |
| `.env` changes | Rebuild: affected containers |
| External repo used as build context (e.g., de-ai-fier) | Rebuild: the service that references it |

### Step 2: Rebuild backend containers (local)

```bash
cd /home/gw/opt/FormatForgeNet/docconv-saas
docker compose up -d --build <service1> <service2> ...
```

Common patterns:
```bash
# Feature touching routes + worker:
docker compose up -d --build backend worker-cpu

# New service added:
docker compose up -d --build backend worker-cpu <new-service>

# Beat schedule changed:
docker compose up -d --build worker-cpu celery-beat

# Everything:
docker compose up -d --build
```

After rebuild, verify:
```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep docconv
```
All containers must show `(healthy)`. If a container shows `(health: starting)`, wait 30s and check again.

### Step 3: Deploy frontend to Japan node

Only needed if `frontend/src/` files changed.

```bash
cd /home/gw/opt/FormatForgeNet/docconv-saas
bash scripts/deploy-frontend.sh
```

This script:
1. Runs `npm run build` in `frontend/`
2. SSHs to `root@100.82.241.21` (Japan node via Tailscale)
3. Clears old assets: `rm -rf /var/www/formatforge/assets/*`
4. Copies `dist/*` and logos to `/var/www/formatforge/`

**Tailscale auth interruption**: If you see `Tailscale SSH requires an additional check`, the user must authenticate in browser. Pause and inform the user with the auth URL.

### Step 4: Verify production

```bash
# Check backend health
curl -s https://formatforge.dev/api/health | python3 -m json.tool

# Check new service health (if applicable, via Docker internal)
docker exec docconv-<new-service> curl -sf http://localhost:8000/health

# Quick E2E: login + create job + verify
TOKEN=$(curl -s -X POST https://formatforge.dev/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"<test-email>","password":"<test-pass>"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Login OK: token obtained"
```

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Code changes in FormatForgeNet/docconv-saas | Local git repo on development machine |
| Code changes in external build-context repos (de-ai-fier, etc.) | Local git repos; push to GitHub if collaboration needed |
| `.env` configuration | `docconv-saas/.env` |

| Output | Format |
|--------|--------|
| Running Docker containers | Verified via `docker ps` (all healthy) |
| Updated static frontend | Files at Japan node `/var/www/formatforge/` |
| Production service | Accessible at `https://formatforge.dev` |

## Common Pitfalls

- **"No git push needed for backend"**: FormatForgeNet has no git remote. Code is executed directly on the local machine. Do NOT suggest `git push` + `ssh server && git pull` — that workflow does not apply here.
- **Docker build context paths are absolute**: `docker-compose.yml` may reference paths like `/home/gw/opt/de-ai-fier`. These only work on this specific machine. If the repo ever moves, update compose file.
- **Vale binary for deai-review-api**: The Dockerfile COPYs a `vale` binary from the repo root. Before first build: `cp $(which vale) /home/gw/opt/de-ai-fier/vale`. The binary is gitignored.
- **Tailscale SSH auth**: `deploy-frontend.sh` uses `ssh root@100.82.241.21` (Tailscale IP). Periodic re-authentication is required. If the script hangs at SSH, check terminal for auth URL.
- **Japan node nginx is NOT in Docker**: Do not try to `docker compose restart nginx` expecting it to affect production routing. The local Docker nginx (port 28080) is for local testing only. Japan node runs system nginx.
- **Frontend-only changes still need local build**: Even though frontend runs on Japan, `npm run build` runs locally and `scp`s the artifacts. The Japan node has no Node.js / npm.
- **Do NOT use `docker compose down -v`**: This deletes volumes (postgres data, minio files). Use `scripts/safe-compose.sh` wrapper which guards against this.
- **Presigned URLs use `formatforge.dev` domain**: MinIO presigned URLs are signed for `formatforge.dev`. When testing locally, you cannot reuse production presigned URLs with `localhost` — the signature will fail. Use `docker exec docconv-minio mc cp` for local testing.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-16 | Initial crystallization | deai-review-integration deployment + prior deployment confusion across multiple sessions |
