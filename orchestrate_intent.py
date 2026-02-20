"""
orchestrate_intent.py
Orchestrates the full intent lifecycle: create → plan → execute.

Each step is delegated to a testable Python module.
Usage:
    python orchestrate_intent.py <ledger_dir> <intent_json_file> <repo_path>
"""

import sys
from pathlib import Path

# These must be importable — relative to this file's location.
from app.core.intent import create_intent
from app.core.planner import generate_plans, select_best_plan_by_ev
from app.core.executor import execute_plan


LEDGER_DIR = "holon-knowledge/ledger"


def main() -> None:
    if len(sys.argv) < 3:
        print(
            "Usage: python orchestrate_intent.py "
            "<ledger_dir> <intent_json_file> [repo_path]"
        )
        sys.exit(1)

    ledger_dir = sys.argv[1] if len(sys.argv) > 1 else LEDGER_DIR
    intent_json_file = sys.argv[2]
    repo_path = sys.argv[3] if len(sys.argv) > 3 else "."

    # Ensure ledger dir
    Path(ledger_dir).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Step 1: Create Intent — branch + ledger entry
    # ------------------------------------------------------------------
    print("=== Orchestrate Intent ===")
    print(f"Ledger dir : {ledger_dir}")
    print(f"Intent file: {intent_json_file}")
    print()

    intent = create_intent(intent_json_file, ledger_dir)
    print(f"[orchestrator] Intent created: {intent['intent_id']}")

    # ------------------------------------------------------------------
    # Step 2: Generate Plans — competitive planning (v1, v2, ...)
    # ------------------------------------------------------------------
    print("Step 2: Generate competing plan variants...")
    plans = generate_plans(intent["intent_id"], ledger_dir)
    print(f"[orchestrator] Generated {len(plans)} plan variants")

    # ------------------------------------------------------------------
    # Step 3: Select Best Plan by EV
    # ------------------------------------------------------------------
    print("Step 3: Evaluate and select best plan by Expected Value...")
    best_plan = select_best_plan_by_ev(intent["intent_id"], ledger_dir)
    print(f"[orchestrator] Selected plan: {best_plan['plan_id']} "
          f"(EV={best_plan.get('ev', 0):.4f})")

    # ------------------------------------------------------------------
    # Step 4: Execute Selected Plan
    # ------------------------------------------------------------------
    print("Step 4: Execute plan in sandbox...")
    result = execute_plan(
        best_plan["plan_id"],
        intent["intent_id"],
        best_plan["branch_name"],
        ledger_dir,
    )
    print(f"[orchestrator] Execution result: status={result.get('status')}")

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    print()
    print("=== Orchestration Complete ===")
    print(f"Intent : {intent['intent_id']}")
    print(f"Plan   : {best_plan['plan_id']}")
    print(f"Status : {result.get('status')}")


if __name__ == "__main__":
    main()