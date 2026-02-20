"""
Ledger utilities: append-only JSONL storage for intents, plans, events.
"""

import json
from pathlib import Path
from typing import Optional


class LedgerError(Exception):
    """Raised on ledger read/write failures."""


def append_ledger(ledger_dir: str, ledger_file: str, entry: dict) -> None:
    """
    Append a single JSON dict to <ledger_dir>/<ledger_file>.jsonl.
    Creates parent dir if missing. Silently ignores duplicate writes (idempotent).
    """
    p = Path(ledger_dir)
    p.mkdir(parents=True, exist_ok=True)
    path = p / f"{ledger_file}.jsonl"
    try:
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError as e:
        raise LedgerError(f"Could not write to {path}: {e}") from e


def read_ledger(ledger_dir: str, ledger_file: str) -> list[dict]:
    """
    Read all entries from <ledger_dir>/<ledger_file>.jsonl.
    Returns [] if file does not exist (empty ledger is valid).
    """
    path = Path(ledger_dir) / f"{ledger_file}.jsonl"
    if not path.exists():
        return []
    try:
        with open(path) as f:
            return [json.loads(line) for line in f if line.strip()]
    except OSError as e:
        raise LedgerError(f"Could not read {path}: {e}") from e


def query_ledger(ledger_dir: str, ledger_file: str, **filters) -> list[dict]:
    """
    Read ledger and return only entries matching the given key=val filters.
    e.g. query_ledger(led, "plans", intent_id="I-42") -> [plan dicts]
    """
    entries = read_ledger(ledger_dir, ledger_file)
    return [
        e for e in entries
        if all(e.get(k) == v for k, v in filters.items())
    ]


def latest_ledger_entry(ledger_dir: str, ledger_file: str) -> Optional[dict]:
    """Return the last entry in a ledger (most recent), or None if empty."""
    entries = read_ledger(ledger_dir, ledger_file)
    return entries[-1] if entries else None