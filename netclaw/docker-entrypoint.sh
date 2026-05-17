#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}[netclaw]${NC} $1"; }
warn() { echo -e "${YELLOW}[netclaw]${NC} $1"; }
info() { echo -e "${CYAN}[netclaw]${NC} $1"; }

cd /netclaw

# Pull latest NetClaw on every start
log "Pulling latest NetClaw..."
git pull origin main 2>/dev/null || warn "Could not pull updates (offline?)"

CONFIG_FILE="/root/.openclaw/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    warn "NetClaw is not configured yet."
    echo ""
    echo "  Run the interactive setup wizard:"
    echo "    docker exec -it netclaw bash -c 'cd /netclaw && ./scripts/install.sh'"
    echo ""
    echo "  Then restart the container:"
    echo "    docker compose restart netclaw"
    echo ""
    # Keep container alive so the user can exec into it
    exec tail -f /dev/null
fi

log "Starting OpenClaw gateway..."
exec openclaw
