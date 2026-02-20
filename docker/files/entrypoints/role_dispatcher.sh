#!/usr/bin/env bash
set -euo pipefail

ROLE="${HOLON_ROLE:-}"

case "$ROLE" in
    intent-creator)
        exec /home/holon/entrypoints/intent_creator.sh "$@"
        ;;
    planner)
        exec /home/holon/entrypoints/planner.sh "$@"
        ;;
    executor)
        exec /home/holon/entrypoints/executor.sh "$@"
        ;;
    *)
        # If no role, allow running arbitrary commands (like ls or bash)
        exec "$@"
        ;;
esac
