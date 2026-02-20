#!/usr/bin/env bash
# Usage: planner.sh <intent_branch> <agent_name> <model_name>
set -euo pipefail

INTENT_BRANCH="${1:?Usage: $0 <intent_branch> <agent_name> <model_name>}"
AGENT_NAME="${2:?Usage: $0 <intent_branch> <agent_name> <model_name>}"
MODEL_NAME="${3:?Usage: $0 <intent_branch> <agent_name> <model_name>}"

WORKDIR="$HOME/repo"
REPO_URL="git@github.com:Holon-Agentic-Coder/holon-agentic-coder-ref.git"

# Clean workspace
rm -rf "$WORKDIR"; mkdir -p "$WORKDIR"; cd "$WORKDIR"

INTENT_BRANCH_PREFIX="${INTENT_BRANCH%/_}"

# Clone repo fresh
git clone --branch "$INTENT_BRANCH" --single-branch --depth 1 "$REPO_URL" .

# Generate unique plan sequence number (timestamp)
PLAN_SEQ=$(date +%s)

# Create ephemeral plan branch from intent branch
PLAN_BRANCH="${INTENT_BRANCH_PREFIX}/P-${PLAN_SEQ}-${AGENT_NAME}-${MODEL_NAME}"
git checkout -B "$PLAN_BRANCH" "origin/$INTENT_BRANCH"

# Agent writes plan.md using pi
PLAN_MD="plans/${PLAN_SEQ}-${AGENT_NAME}-${MODEL_NAME}.md"

# Prepare pi arguments
PI_ARGS=("--model $MODEL_NAME")

# Allow explicit provider/key overrides from environment
if [ -n "${PI_PROVIDER:-}" ]; then
  PI_ARGS+=(--provider "$PI_PROVIDER")
fi
if [ -n "${PI_API_KEY:-}" ]; then
  PI_ARGS+=(--api-key "$PI_API_KEY")
fi

# Check for likely missing keys (sanity check)
if [[ "$MODEL_NAME" == *"anthropic"* ]] && [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -z "${PI_API_KEY:-}" ]; then
  echo "Warning: Anthropic model selected but ANTHROPIC_API_KEY is not set."
fi
if [[ "$MODEL_NAME" == *"gpt"* ]] && [ -z "${OPENAI_API_KEY:-}" ] && [ -z "${PI_API_KEY:-}" ]; then
  echo "Warning: OpenAI model selected but OPENAI_API_KEY is not set."
fi

# Get intent data
INTENT_DATA=$(jq -c --arg b "$INTENT_BRANCH_PREFIX" 'select(.branch == $b)' app/ledger/intents.jsonl | tail -n 1)

if [ -z "$INTENT_DATA" ]; then
  echo "Error: No intent found for branch $INTENT_BRANCH_PREFIX in app/ledger/intents.jsonl"
  exit 1
fi

# Write intent to a temporary file for pi to read safely
INTENT_FILE="/tmp/intent-${PLAN_SEQ}.json"
printf "%s\n" "$INTENT_DATA" > "$INTENT_FILE"

# Create prompt file
PROMPT_FILE="/tmp/plan_prompt-${PLAN_SEQ}.md"
cat > "$PROMPT_FILE" <<EOF
You are a planning agent.
Your task is to create a detailed implementation plan for the intent provided in the attached JSON file.

Repository file structure:
$(find . -maxdepth 3 -not -path '*/.*')

Please output the plan in Markdown format.
The plan should include a list of actions to be performed.
Do not include any other text (like "Here is the plan"), just the plan content.
EOF

# Run pi and capture output
# use -p to print response and exit
pi -p "${PI_ARGS[@]}" @"$PROMPT_FILE" @"$INTENT_FILE" > "$PLAN_MD"
rm "$PROMPT_FILE" "$INTENT_FILE"

# Fallback if pi failed or produced empty output
if [ ! -s "$PLAN_MD" ]; then
  echo "Warning: pi failed to generate plan. Using fallback plan."
  cat > "$PLAN_MD" <<EOF
# Plan for $INTENT_BRANCH by $AGENT_NAME ($MODEL_NAME)

- Action 1: Investigate the codebase
- Action 2: Implement the requested feature based on intent
EOF
fi

# Append plan summary to plans.jsonl ledger
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%6NZ")
PLAN_ID="P-${PLAN_SEQ}-${AGENT_NAME}-${MODEL_NAME}"
jq -c -n --arg pid "$PLAN_ID" --arg ib "$INTENT_BRANCH" --arg an "$AGENT_NAME" --arg mn "$MODEL_NAME" --arg ts "$TIMESTAMP" --arg pf "$PLAN_MD" \
  '{plan_id: $pid, intent_branch: $ib, agent: $an, model: $mn, p_success: 0.7, entropy: 3.0, created_at: $ts, plan_file: $pf}' >> app/ledger/plans.jsonl

# Commit plan and ledger
git add "$PLAN_MD" app/ledger/plans.jsonl
git config --local user.email "planner-agent@holon-agentic-coder.com"
git config --local user.name "Holon Planner Agent"
git commit -m "plan: $PLAN_ID created by $AGENT_NAME ($MODEL_NAME)"

# Push the new plan branch to origin
git push origin "$PLAN_BRANCH"

echo "Plan branch '$PLAN_BRANCH' created, committed, and pushed."
