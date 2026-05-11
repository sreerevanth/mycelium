#!/usr/bin/env bash
# MYCELIUM bootstrap script
# Usage: ./infra/scripts/bootstrap.sh

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${CYAN}[MYCELIUM]${NC} $1"; }
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERR]${NC} $1"; exit 1; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

log "Bootstrapping MYCELIUM monorepo..."

# ─── CHECK PREREQUISITES ──────────────────────────────────────────────────────
command -v docker &>/dev/null || err "Docker not found. Install Docker Desktop."
command -v docker &>/dev/null && docker compose version &>/dev/null || err "Docker Compose v2 not found."

# ─── ENVIRONMENT ──────────────────────────────────────────────────────────────
if [[ ! -f ".env" ]]; then
    log "Creating .env from .env.example..."
    cp .env.example .env
    ok ".env created"
else
    warn ".env already exists, skipping."
fi

# ─── PULL BASE IMAGES ─────────────────────────────────────────────────────────
log "Pulling base images..."
docker pull python:3.12-slim --quiet
docker pull node:22-alpine --quiet
docker pull postgres:16-alpine --quiet
docker pull redis:7-alpine --quiet
ok "Base images ready"

# ─── BUILD SERVICES ───────────────────────────────────────────────────────────
log "Building MYCELIUM services..."
docker compose build --parallel
ok "Services built"

# ─── START INFRASTRUCTURE ─────────────────────────────────────────────────────
log "Starting infrastructure (postgres, redis)..."
docker compose up -d postgres redis

log "Waiting for postgres to be ready..."
for i in $(seq 1 30); do
    if docker compose exec -T postgres pg_isready -U mycelium &>/dev/null; then
        ok "Postgres ready"
        break
    fi
    if [[ $i -eq 30 ]]; then
        err "Postgres did not become ready in time"
    fi
    sleep 1
done

# ─── RUN MIGRATIONS ───────────────────────────────────────────────────────────
log "Running database migrations..."
docker compose run --rm backend \
    bash -c "cd /app && alembic upgrade head 2>/dev/null || python -c 'import asyncio; from app.db import init_db; asyncio.run(init_db())'"
ok "Migrations applied"

# ─── START ALL SERVICES ───────────────────────────────────────────────────────
log "Starting all MYCELIUM services..."
docker compose up -d
ok "All services started"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     MYCELIUM RUNTIME BOOTSTRAPPED        ║${NC}"
echo -e "${CYAN}╠══════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║${NC}  Frontend:   ${GREEN}http://localhost:3000${NC}       ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  API:        ${GREEN}http://localhost:8000${NC}       ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  API Docs:   ${GREEN}http://localhost:8000/docs${NC}  ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}  WS Events:  ${GREEN}ws://localhost:8000/ws/events${NC}${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""
log "Tail logs: docker compose logs -f"
