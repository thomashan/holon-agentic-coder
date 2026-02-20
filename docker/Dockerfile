# Multi-stage Dockerfile for holon agent images
# Build targets: holon-base, agent-claude, agent-gemini, agent-opencode, holon-orchestrator

# --- Base Layer ---
FROM python:3.12-slim AS holon-base
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl jq build-essential ca-certificates npm nodejs ssh && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m holon
WORKDIR /home/holon
USER holon
ENV PATH="/home/holon/.local/bin:${PATH}"

# --- Claude Agent Layer ---
FROM holon-base AS agent-claude
USER root
RUN npm install -g @anthropic-ai/claude-code
USER holon

# --- Gemini Agent Layer ---
FROM holon-base AS agent-gemini
USER root
RUN npm install -g @google/gemini-cli
USER holon

# --- OpenCode Agent Layer (opencode) ---
FROM holon-base AS agent-opencode
USER root
RUN npm install -g opencode-ai
USER holon

# --- Pi Agent Layer ---
FROM holon-base AS agent-pi
USER root
RUN npm install -g @mariozechner/pi-coding-agent
USER holon

# --- Final Orchestrator Image ---
FROM holon-base AS holon-orchestrator

# Copy orchestrator entrypoints and scripts
COPY files/entrypoints/ /home/holon/entrypoints/

# Provide a lightweight entry that delegates to role-specific scripts
ENV LEDGER_PATH=/workspace/repo/holon/ledger

ENTRYPOINT ["/home/holon/entrypoints/role_dispatcher.sh"]
