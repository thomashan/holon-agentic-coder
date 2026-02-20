#!/usr/bin/env bash
# Usage: executor.sh <repo_path> <plan_branch> <agent_name> <model_name> <action_slug>
set -euo pipefail

REPO_PATH="${1:?Usage: $0 <repo_path> <plan_branch> <agent_name> <model_name> <action_slug>}"
PLAN_BRANCH="${2:?Usage: $0 <repo_path> <plan_branch> <agent_name> <model_name> <action_slug>}"
AGENT_NAME="${3:?Usage: $0 <repo_path> <plan_branch> <agent_name> <model_name> <action_slug>}"
MODEL_NAME="${4:?Usage: $0 <repo_path> <plan_branch> <agent_name> <model_name> <action_slug>}"
ACTION_SLUG="${5:?Usage: $0 <repo_path> <plan_branch> <agent_name> <model_name> <action_slug>}"

cd "$REPO_PATH"

# Generate unique execution sequence number
EXEC_SEQ=$(date +%s)

# Create ephemeral execution branch from plan branch
EXEC_BRANCH="${PLAN_BRANCH}/E-${EXEC_SEQ}-${AGENT_NAME}-${MODEL_NAME}-${ACTION_SLUG}"
git checkout -B "$EXEC_BRANCH" "$PLAN_BRANCH"

# Agent writes code and tests (simulate here)
CODE_FILE="src/${ACTION_SLUG}.py"
mkdir -p src
cat > "$CODE_FILE" <<EOF
# Auto-generated code for action $ACTION_SLUG
def feature():
    print("Feature $ACTION_SLUG implemented.")
EOF

# Append execution event to events.jsonl ledger
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%6NZ")
EXEC_ID="E-${EXEC_SEQ}-${AGENT_NAME}-${MODEL_NAME}-${ACTION_SLUG}"
jq -c -n --arg eid "$EXEC_ID" --arg pb "$PLAN_BRANCH" --arg an "$AGENT_NAME" --arg mn "$MODEL_NAME" --arg as "$ACTION_SLUG" --arg ts "$TIMESTAMP" \
  '{exec_id: $eid, plan_branch: $pb, agent: $an, model: $mn, action: $as, success: true, created_at: $ts}' >> events.jsonl

# Commit code and ledger
git add "$CODE_FILE" events.jsonl
git commit -m "exec: $EXEC_ID code for action $ACTION_SLUG by $AGENT_NAME ($MODEL_NAME)"

echo "Execution branch '$EXEC_BRANCH' created with code and logged."
