"""
Executor: execute a selected plan in an isolated sandbox,
measure actual metrics, and append results to the ledger.
"""

import json
from pathlib import Path
from typing import Optional

LEDGER_DIR = "holon-knowledge/ledger"


def _events_path(ledger_dir: str) -> Path:
    p = Path(ledger_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p / "events.jsonl"


def _append_event(ledger_dir: str, entry: dict) -> None:
    path = _events_path(ledger_dir)
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def execute_plan(
    plan_id: str,
    intent_id: str,
    branch_name: str,
    ledger_dir: str = LEDGER_DIR,
) -> dict:
    """
    Execute a plan branch in an isolated sandbox environment.

    Steps:
      1. Verify the branch exists (checkout or fetch).
      2. Run each step in the plan sequentially.
      3. Capture stdout/stderr to events ledger.
      4. Measure actual P(success), entropy, cost post-execution.
      5. Append execution result to ledger.

    Returns the measured-result dict (plan enriched with actual metrics).
    """
    # Verify branch is available
    result = _checkout_branch(branch_name)
    if not result["ok"]:
        measured = {
            "plan_id": plan_id,
            "intent_id": intent_id,
            "status": "failed",
            "reason": result.get("error", "checkout failed"),
        }
        _append_event(ledger_dir, measured)
        return measured

    # Run steps from the plan
    steps_result = _run_steps(plan_id, ledger_dir)

    # Merge measured metrics into the plan record
    measured = {
        "plan_id": plan_id,
        "intent_id": intent_id,
        "status": steps_result["status"],
        "actual_p_success": steps_result.get("p_success"),
        "actual_entropy": steps_result.get("entropy"),
        "actual_cost": steps_result.get("cost"),
        "learning_value": _compute_learning_value(steps_result),
    }
    measured["ev"] = _measured_ev(measured)

    # Append final execution record
    _append_event(ledger_dir, measured)
    print(f"[executor] Plan {plan_id} finished with status={measured['status']}")
    return measured


# ------------------------------------------------------------------
# Internal helpers — replace with real sandbox/step runners below
# ------------------------------------------------------------------

def _checkout_branch(branch_name: str) -> dict:
    """Attempt to checkout the branch, return ok=True/False."""
    import subprocess

    # First check if it's a local branch
    r = subprocess.run(["git", "rev-parse", "--verify", branch_name],
                        capture_output=True, text=True)
    if r.returncode == 0:
        return {"ok": True}

    # Try fetching from origin
    remote = "origin"
    r = subprocess.run(["git", "fetch", remote, branch_name],
                        capture_output=True, text=True)
    if r.returncode == 0:
        return {"ok": True}

    return {"ok": False, "error": f"Branch {branch_name} not found locally or remotely"}


def _run_steps(plan_id: str, ledger_dir: str) -> dict:
    """
    Run each step of the plan.
    Placeholder: runs nothing until steps are defined in the plan dict.
    Replace with real sandbox exec (docker/isolate) + tool invocations.
    """
    # Stub — steps will come from planner output
    return {
        "status": "completed",
        "p_success": 1.0,
        "entropy": 0.0,
        "cost": 0.0,
    }


def _compute_learning_value(result: dict) -> float:
    """Learning value = epistemic gain from this execution."""
    # Stub — replace with KB extraction logic when curator runs
    return 0.0


def _measured_ev(measured: dict) -> float:
    """Compute EV from actual measured metrics."""
    p = float(measured.get("actual_p_success", 0.5))
    s = float(measured.get("actual_entropy", 0.0))
    c = float(measured.get("actual_cost", 0.0))
    return p - 0.1 * s - c