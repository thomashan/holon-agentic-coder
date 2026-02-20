"""
Intent creation: branch lifecycle, git setup, ledger logging.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

LEDGER_DIR = "holon-knowledge/ledger"


def _run(cmd: list[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def _ledger_path(ledger_dir: str) -> Path:
    p = Path(ledger_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p / "intents.jsonl"


def _load_intent(intent_json_file: str) -> dict:
    with open(intent_json_file, "r") as f:
        return json.load(f)


def _append_intent(ledger_dir: str, entry: dict) -> None:
    path = _ledger_path(ledger_dir)
    path.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def create_intent(intent_json_file: str, ledger_dir: str = LEDGER_DIR) -> dict:
    """
    Load an intent from its JSON descriptor, create a git branch for it,
    and append the intent to the ledger.

    Returns the full intent dict (enriched with branch_name).
    """
    intent = _load_intent(intent_json_file)

    # Ensure ledger dir exists
    Path(ledger_dir).mkdir(parents=True, exist_ok=True)

    # Build branch name from intent_id + slug
    branch_name = _build_branch(intent)
    intent["branch_name"] = branch_name

    # Check if branch already exists (idempotent — safe to call twice)
    result = _run(["git", "rev-parse", "--verify", branch_name])
    if result.returncode == 0:
        print(f"[intent] Branch {branch_name} already exists, skipping creation.")
        # Still append to ledger so the record is complete
        intent["status"] = "created"
        _append_intent(ledger_dir, intent)
        return intent

    # Create the branch from the default base (main or origin/main)
    _run(["git", "checkout", "-b", branch_name])

    # Append intent to ledger
    intent["status"] = "created"
    _append_intent(ledger_dir, intent)

    print(f"[intent] Created branch: {branch_name}")
    return intent


def _build_branch(intent: dict) -> str:
    """Build a descriptive branch name from intent data."""
    base = "main"
    try:
        _run(["git", "rev-parse", "--verify", "origin/main"])
        base = "origin/main"
    except Exception:
        pass
    return f"{intent['intent_id']}-{intent.get('title', 'untitled')}/{_slugify(intent.get('branch', ''))}"


def _slugify(text: str) -> str:
    """Strip non-alphanumeric to dashes."""
    import re
    return re.sub(r"[^a-zA-Z0-9-_]", "-", text).strip("-") or " unnamed"