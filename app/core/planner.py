"""
Planner: generates competing plan variants for an intent,
selects the best by EV, and logs plans to the ledger.
"""

import json
from pathlib import Path
from typing import Optional

LEDGER_DIR = "holon-knowledge/ledger"


def _plans_path(ledger_dir: str) -> Path:
    p = Path(ledger_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p / "plans.jsonl"


def _append_plan(ledger_dir: str, entry: dict) -> None:
    path = _plans_path(ledger_dir)
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def generate_plans(
    intent_id: str,
    ledger_dir: str = LEDGER_DIR,
    max_variants: int = 3,
) -> list[dict]:
    """
    Generate competing plan variants for intent_id.
    Each variant is a dict with:
      - plan_id, intent_id, branch_name
      - steps (list of step dicts)
      - predicted metrics: p_success, entropy, impact, cost
      - ev (computed score)
    """
    plans = []
    base_branch = f"plans/{intent_id}"
    for i in range(1, max_variants + 1):
        plan = _build_variant(intent_id, i, base_branch)
        plans.append(plan)

    # Append all variants to the ledger
    for plan in plans:
        _append_plan(ledger_dir, plan)

    return plans


def select_best_plan_by_ev(
    intent_id: str,
    ledger_dir: str = LEDGER_DIR,
) -> dict:
    """
    Read plans.jsonl for intent_id, compute EV = P(success) - Entropy,
    return the highest-EV plan.
    """
    path = _plans_path(ledger_dir)
    if not path.exists():
        raise FileNotFoundError(f"No plans ledger at {path}")

    with open(path) as f:
        lines = [json.loads(line) for line in f if line.strip()]

    intent_plans = [p for p in lines if p.get("intent_id") == intent_id]
    if not intent_plans:
        raise ValueError(f"No plans found for intent {intent_id}")

    best = max(intent_plans, key=lambda p: _ev(p))
    print(f"[planner] Selected plan {best['plan_id']} with EV={_ev(best):.4f}")
    return best


# ------------------------------------------------------------------
# EV formula — pluggable via config in future
# ------------------------------------------------------------------
def _ev(plan: dict) -> float:
    """
    EV = P(success) * Impact - lambda * Entropy - Cost
    Currently: EV = p_success - entropy (no-op baseline).
    Replace with holon-config/metrics coefficients when ready.
    """
    p_success = float(plan.get("p_success", 0.5))
    entropy = float(plan.get("entropy", 0.0))
    impact = float(plan.get("impact", 1.0))
    cost = float(plan.get("cost", 0.0))

    # Simple baseline: maximise success prob, minimise entropy
    return p_success * impact - 0.1 * entropy - cost


def _build_variant(intent_id: str, variant_num: int, base_branch: str) -> dict:
    """
    Build a single plan variant (placeholder — replace with planner agent).
    This is the stub: real implementation calls an LLM via holon-config/prompts.
    """
    plan_id = f"{intent_id}-v{variant_num}"
    branch_name = f"{base_branch}/v{variant_num}"

    plan = {
        "plan_id": plan_id,
        "intent_id": intent_id,
        "branch_name": branch_name,
        "variant_num": variant_num,
        "status": "proposed",
        # Placeholder metrics — replace with model-predicted values
        "p_success": 0.5 + (variant_num * 0.05),   # optimistic v2/v3
        "entropy": 0.1 * variant_num,
        "impact": 1.0,
        "cost": 0.5 * variant_num,
        "steps": [],
    }
    plan["ev"] = _ev(plan)
    return plan