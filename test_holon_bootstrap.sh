#!/usr/bin/env bash
# test_holon_bootstrap.sh - Automated end-to-end test for Holon agentic coder

set -euo pipefail

# Configuration
REPO_DIR=$(pwd)
INTENT_JSON="app/scripts/intent_bootstrap_cli.json"
ROOT_INTENT_BRANCH="I-001-bootstrap-cli"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        error "jq is not installed"
        exit 1
    fi

    if [ ! -f "$INTENT_JSON" ]; then
        error "Intent JSON file not found: $INTENT_JSON"
        exit 1
    fi

    log "All prerequisites satisfied"
}

# Build orchestrator
build_orchestrator() {
    log "Building orchestrator Docker image..."
    docker build --target holon-orchestrator -t holon/orchestrator . || {
        error "Failed to build orchestrator"
        exit 1
    }
    log "Orchestrator built successfully"
}

# Initialize ledger structure
init_ledger() {
    log "Initializing ledger structure..."
    mkdir -p app/ledger app/plans app/scripts
    touch app/ledger/intents.jsonl app/ledger/plans.jsonl app/ledger/events.jsonl
    log "Ledger structure initialized"
}

# Create root intent
create_intent() {
    log "Creating root intent..."
    ./holon create-intent "$INTENT_JSON" || {
        error "Failed to create intent"
        exit 1
    }

    # Verify intent was created
    if ! git show-ref --verify --quiet "refs/heads/$ROOT_INTENT_BRANCH"; then
        error "Intent branch $ROOT_INTENT_BRANCH was not created"
        exit 1
    fi

    log "Root intent created successfully"
}

# Generate competing plans
generate_plans() {
    log "Generating competing plans..."

    # Plan 1: Claude
    ./holon plan "$ROOT_INTENT_BRANCH" architect-agent claude-3.5-sonnet || {
        error "Failed to generate Claude plan"
        exit 1
    }

    # Plan 2: Gemini
    ./holon plan "$ROOT_INTENT_BRANCH" architect-agent gemini-2.0-flash || {
        error "Failed to generate Gemini plan"
        exit 1
    }

    log "Competing plans generated successfully"
}

# List and verify plan branches
list_plans() {
    log "Listing plan branches..."
    git branch | grep "$ROOT_INTENT_BRANCH/P-"
}

# Execute action on selected plan
execute_action() {
    local plan_branch
    plan_branch=$(git branch | grep "$ROOT_INTENT_BRANCH/P-" | head -n 1 | tr -d ' *')

    if [ -z "$plan_branch" ]; then
        error "No plan branches found"
        exit 1
    fi

    log "Executing action on plan: $plan_branch"
    ./holon execute "$plan_branch" coder-agent claude-3.5-sonnet init-project || {
        error "Failed to execute action"
        exit 1
    }

    log "Action executed successfully"
}

# List execution branches
list_executions() {
    log "Listing execution branches..."
    git branch | grep "$ROOT_INTENT_BRANCH/.*/E-"
}

# Merge execution to plan
merge_execution_to_plan() {
    local exec_branch
    local plan_branch

    exec_branch=$(git branch | grep "$ROOT_INTENT_BRANCH/.*/E-" | head -n 1 | tr -d ' *')
    plan_branch=$(echo "$exec_branch" | cut -d'/' -f1-4)

    if [ -z "$exec_branch" ] || [ -z "$plan_branch" ]; then
        error "Could not find execution or plan branch"
        exit 1
    fi

    log "Merging $exec_branch into $plan_branch"
    git checkout "$plan_branch" || {
        error "Failed to checkout plan branch"
        exit 1
    }

    git merge "$exec_branch" || {
        error "Failed to merge execution branch"
        exit 1
    }

    log "Execution merged to plan successfully"
}

# Merge plan to intent
merge_plan_to_intent() {
    local plan_branch
    plan_branch=$(git branch | grep "$ROOT_INTENT_BRANCH/P-" | head -n 1 | tr -d ' *')

    log "Merging $plan_branch into $ROOT_INTENT_BRANCH"
    git checkout "$ROOT_INTENT_BRANCH" || {
        error "Failed to checkout intent branch"
        exit 1
    }

    git merge "$plan_branch" || {
        error "Failed to merge plan branch"
        exit 1
    }

    log "Plan merged to intent successfully"
}

# Promote to main
promote_to_main() {
    log "Promoting intent to main"
    git checkout main || {
        error "Failed to checkout main branch"
        exit 1
    }

    git merge "$ROOT_INTENT_BRANCH" || {
        error "Failed to merge intent to main"
        exit 1
    }

    log "Intent promoted to main successfully"
}

# Cleanup ephemeral branches
cleanup() {
    log "Cleaning up ephemeral branches..."

    # Delete execution branches
    git branch | grep "$ROOT_INTENT_BRANCH/.*/E-" | tr -d ' *' | xargs -r git branch -D

    # Delete plan branches
    git branch | grep "$ROOT_INTENT_BRANCH/P-" | tr -d ' *' | xargs -r git branch -D

    # Delete intent branch
    git branch -D "$ROOT_INTENT_BRANCH"

    log "Cleanup completed"
}

# Verify ledger files
verify_ledger() {
    log "Verifying ledger files..."

    if [ -s "app/ledger/intents.jsonl" ]; then
        log "Intents ledger has entries:"
        jq . "app/ledger/intents.jsonl"
    else
        warn "Intents ledger is empty"
    fi

    if [ -s "app/ledger/plans.jsonl" ]; then
        log "Plans ledger has entries:"
        jq . "app/ledger/plans.jsonl"
    else
        warn "Plans ledger is empty"
    fi

    if [ -s "app/ledger/events.jsonl" ]; then
        log "Events ledger has entries:"
        jq . "app/ledger/events.jsonl"
    else
        warn "Events ledger is empty"
    fi
}

# Main test sequence
main() {
    log "Starting Holon bootstrap test..."

    check_prerequisites
    build_orchestrator
    init_ledger
    create_intent
    generate_plans
    list_plans
    execute_action
    list_executions
    merge_execution_to_plan
    merge_plan_to_intent
    verify_ledger

    log "Holon bootstrap test completed successfully!"
    log "To promote to main and cleanup, run:"
    echo "  ./test_holon_bootstrap.sh promote"
    echo "  ./test_holon_bootstrap.sh cleanup"
}

# Handle command line arguments
case "${1:-}" in
    promote)
        promote_to_main
        ;;
    cleanup)
        cleanup
        ;;
    verify)
        verify_ledger
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [promote|cleanup|verify]"
        echo "  (no args): Run full bootstrap test"
        echo "  promote:   Promote intent to main"
        echo "  cleanup:   Clean up ephemeral branches"
        echo "  verify:    Verify ledger files"
        exit 1
        ;;
esac
