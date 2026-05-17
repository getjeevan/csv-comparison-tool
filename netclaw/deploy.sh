#!/usr/bin/env bash
# NetClaw — one-shot deploy script for Hostinger
# Run this on your Hostinger server:
#   bash <(curl -fsSL https://raw.githubusercontent.com/getjeevan/csv-comparison-tool/claude/setup-grok-build-docker-GchPI/netclaw/deploy.sh)
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
info() { echo -e "${CYAN}[→]${NC} $1"; }

DEPLOY_DIR="$HOME/netclaw"
REPO="https://github.com/getjeevan/csv-comparison-tool.git"
BRANCH="claude/setup-grok-build-docker-GchPI"

# --- 1. Prerequisites ---
info "Checking prerequisites..."
for cmd in docker git curl; do
  command -v "$cmd" &>/dev/null || { warn "$cmd not found — installing..."; apt-get install -y "$cmd" 2>/dev/null || yum install -y "$cmd" 2>/dev/null || true; }
done
docker compose version &>/dev/null || { warn "Docker Compose v2 not found"; exit 1; }

# --- 2. Pull files ---
info "Fetching NetClaw Docker setup..."
if [ -d "$DEPLOY_DIR/.git" ]; then
  git -C "$DEPLOY_DIR" pull origin "$BRANCH"
else
  git clone --branch "$BRANCH" --depth 1 "$REPO" /tmp/netclaw-repo
  mkdir -p "$DEPLOY_DIR"
  cp -r /tmp/netclaw-repo/netclaw/. "$DEPLOY_DIR/"
  rm -rf /tmp/netclaw-repo
fi
log "Files ready at $DEPLOY_DIR"

# --- 3. .env setup ---
cd "$DEPLOY_DIR"
if [ ! -f .env ]; then
  cp .env.example .env
  warn ".env created from template."
  echo ""
  read -rp "  Enter your Anthropic API key: " AKEY
  sed -i "s|your_anthropic_api_key_here|$AKEY|" .env
  log "ANTHROPIC_API_KEY saved."
else
  log ".env already exists — skipping."
fi

# --- 4. Build & start ---
info "Building Docker image (this takes a few minutes)..."
docker compose build --no-cache
info "Starting NetClaw..."
docker compose up -d
log "Container started."

# --- 5. First-time setup wizard ---
echo ""
warn "NetClaw needs one-time configuration. Running setup wizard now..."
echo "  Follow the prompts to connect your Anthropic account and any integrations."
echo ""
docker exec -it netclaw bash -c 'cd /netclaw && ./scripts/install.sh'

# --- 6. Restart ---
info "Restarting so the gateway comes up..."
docker compose restart netclaw
sleep 5

STATUS=$(docker inspect --format='{{.State.Status}}' netclaw 2>/dev/null || echo "unknown")
log "NetClaw is $STATUS — running on port 3000"
echo ""
echo "  Logs:    docker compose -f $DEPLOY_DIR/docker-compose.yml logs -f"
echo "  Shell:   docker exec -it netclaw bash"
echo "  Stop:    docker compose -f $DEPLOY_DIR/docker-compose.yml down"
