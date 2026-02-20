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

# Agent writes plan.md and action breakdown (simulate here)
PLAN_MD="plans/${PLAN_SEQ}-${AGENT_NAME}-${MODEL_NAME}.md"
cat > "$PLAN_MD" <<EOF
# Plan for $INTENT_BRANCH by $AGENT_NAME ($MODEL_NAME)

- Action 1: Implement feature X
- Action 2: Refactor module Y
EOF

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
