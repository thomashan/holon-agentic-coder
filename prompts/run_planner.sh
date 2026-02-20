#!/bin/bash
set -e

# Get the directory of the script and the project root
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --model) MODEL="$2"; shift ;;
        --command) COMMAND="$2"; shift ;;
        --intent_file) INTENT_FILE="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [ -z "$MODEL" ] || [ -z "$COMMAND" ] || [ -z "$INTENT_FILE" ]; then
    echo "Error: --model, --command, and --intent_file are mandatory parameters."
    echo "Usage: $0 --model <model_name> --command <command_name> --intent_file <path>"
    exit 1
fi

# 1. Agent mapping (needed for PLAN_ID and filename)
case $COMMAND in
    gemini)   AGENT="gemini-cli" ;;
    claude)   AGENT="claude-code" ;;
    codex)    AGENT="openai-codex" ;;
    pi)       AGENT="pi-coding-agent" ;;
    opencode) AGENT="opencode" ;;
    *)
        echo "Error: Unknown command $COMMAND"
        exit 1
        ;;
esac

TEMPLATE_FILE="$PROJECT_ROOT/prompts/planner.template.md"

# 2. Extract metadata and generate PLANNER_PROMPT
if [ ! -f "$INTENT_FILE" ]; then
    if [ -f "$PROJECT_ROOT/$INTENT_FILE" ]; then
        INTENT_FILE="$PROJECT_ROOT/$INTENT_FILE"
    else
        echo "Error: $INTENT_FILE not found."
        exit 1
    fi
fi

INTENT_ID=$(jq -r '.intent_id' "$INTENT_FILE")
DESCRIPTION=$(jq -r '.description' "$INTENT_FILE")
INTENT_JSON_CONTENT=$(cat "$INTENT_FILE")
TIMESTAMP=$(date +%s)
DATE=$(date -u +"%Y-%m-%dT%H:%M:%S.%6NZ")

# Replace slashes in model name for filename safety
SAFE_MODEL=$(echo "$MODEL" | tr '/' '_')
PLAN_ID="P-${TIMESTAMP}-${AGENT}-${SAFE_MODEL}"

PLANNER_PROMPT=$(python3 -c "
import json, sys, os
template_path = sys.argv[1]
with open(template_path, 'r') as f:
    template = f.read()

replacements = {
    '{timestamp}': sys.argv[2],
    '{agent}': sys.argv[3],
    '{model}': sys.argv[4],
    '{intent_id}': sys.argv[5],
    '{description}': sys.argv[6],
    '{plan_id}': sys.argv[7],
    '{date}': sys.argv[8],
    '{intent_json}': sys.argv[9],
    '{safe_model}': sys.argv[10]
}

for k, v in replacements.items():
    template = template.replace(k, v)

print(template)
" "$TEMPLATE_FILE" "$TIMESTAMP" "$AGENT" "$MODEL" "$INTENT_ID" "$DESCRIPTION" "$PLAN_ID" "$DATE" "$INTENT_JSON_CONTENT" "$SAFE_MODEL")

# 3. Configure command execution with generated prompt
# We use an array for the full command to handle spaces and quoting correctly
CMD_ARGS=()

case $COMMAND in
    gemini)
        CMD_ARGS+=("gemini" "--model" "$MODEL" "--yolo" "--prompt" "$PLANNER_PROMPT")
        ;;
    claude)
        CMD_ARGS+=("claude" "--model" "$MODEL" "--dangerously-skip-permissions" "-p" "--settings" "$HOME/.claude/lmstudio.settings.json" "$PLANNER_PROMPT")
        ;;
    codex)
        CMD_ARGS+=("codex" "exec" "--model" "$MODEL" "--dangerously-bypass-approvals-and-sandbox" "$PLANNER_PROMPT")
        ;;
    pi)
        CMD_ARGS+=("pi" "--model" "$MODEL" "-p" "$PLANNER_PROMPT")
        ;;
    opencode)
        CMD_ARGS+=("opencode" "run" "--model" "$MODEL" "$PLANNER_PROMPT")
        ;;
esac

# 4. Execute from project root
echo "Executing: ${CMD_ARGS[*]}"
cd "$PROJECT_ROOT"


echo executing: "${CMD_ARGS[@]}"
time "${CMD_ARGS[@]}"
