#!/usr/bin/env bash
set -euo pipefail

# Resolve the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Help menu
show_help() {
  cat <<EOF
Usage: $(basename "$0") [options]

Builds all Docker images for the Holon agentic environments (base, agents, and orchestrator).

Options:
  -h, --help      Show this help message and exit
  --no-cache      Build Docker images without using the cache (forces fresh packages/dependencies)
EOF
}

# Check command line arguments
NO_CACHE_FLAG=""
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  show_help
  exit 0
elif [[ "${1:-}" == "--no-cache" ]]; then
  NO_CACHE_FLAG="--no-cache"
fi

# 1. Build and tag the shared base layer first
echo "Building shared base image (holon/base)..."
docker build $NO_CACHE_FLAG --target holon-base -t holon/base "$SCRIPT_DIR"

# 2. Build the agents and orchestrator inheriting from the pre-built base image
echo "Building agent images using pre-built base..."
docker build $NO_CACHE_FLAG --target agent-claude --build-arg AGENT_BASE=holon/base -t holon/agent-claude "$SCRIPT_DIR"
docker build $NO_CACHE_FLAG --target agent-codex --build-arg AGENT_BASE=holon/base -t holon/agent-codex "$SCRIPT_DIR"
docker build $NO_CACHE_FLAG --target agent-gemini --build-arg AGENT_BASE=holon/base -t holon/agent-gemini "$SCRIPT_DIR"
docker build $NO_CACHE_FLAG --target agent-hermes --build-arg AGENT_BASE=holon/base -t holon/agent-hermes "$SCRIPT_DIR"
docker build $NO_CACHE_FLAG --target agent-opencode --build-arg AGENT_BASE=holon/base -t holon/agent-opencode "$SCRIPT_DIR"
docker build $NO_CACHE_FLAG --target agent-open-codex --build-arg AGENT_BASE=holon/base -t holon/agent-open-codex "$SCRIPT_DIR"
docker build $NO_CACHE_FLAG --target agent-pi --build-arg AGENT_BASE=holon/base -t holon/agent-pi "$SCRIPT_DIR"
docker build $NO_CACHE_FLAG --target agent-antigravity --build-arg AGENT_BASE=holon/base -t holon/agent-antigravity "$SCRIPT_DIR"
docker build $NO_CACHE_FLAG --target holon-orchestrator --build-arg AGENT_BASE=holon/base -t holon/orchestrator "$SCRIPT_DIR"

echo "All images built successfully!"
