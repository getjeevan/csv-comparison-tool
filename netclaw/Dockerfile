FROM node:20-bullseye-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git curl wget bash jq \
    build-essential libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install OpenClaw CLI globally
RUN npm install -g openclaw

# Install uv for fast Python package management (used by MCP servers)
RUN pip3 install --no-cache-dir uv

WORKDIR /netclaw

# Clone NetClaw at build time
RUN git clone https://github.com/automateyournetwork/netclaw.git .

# Make all scripts executable
RUN find scripts/ -name "*.sh" -exec chmod +x {} \;

# Persist OpenClaw config and workspace across container restarts
VOLUME ["/root/.openclaw", "/root/.config/openclaw"]

# OpenClaw gateway default port
EXPOSE 3000

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
