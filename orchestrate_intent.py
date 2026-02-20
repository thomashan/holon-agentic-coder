#!/usr/bin/env python3
"""
orchestrate_intent.py
Orchestrates the full intent lifecycle: create → plan → execute
Usage: python orchestrate_intent.py <ledger_dir> <intent_json_file> <repo_path>
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run_entrypoint(script_name, *args):
    """Run an entrypoint script with given arguments"""
    cmd = ["bash", f"entrypoints/{script_name}"] + list(args)
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {script_name}: {result.stderr}")
        sys.exit(1)
    print(result.stdout)
    return result.stdout


def read_jsonl_file(filepath):
    """Read a JSONL file and return list of JSON objects"""
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return [json.loads(line) for line in f if line.strip()]


def select_best_plan(plans_file, intent_id):
    """Select the best plan based on Expected Value (P(success) - Entropy)"""
    plans = read_jsonl_file(plans_file)
    intent_plans = [p for p in plans if p.get('intent_id') == intent_id]

    if not intent_plans:
        raise ValueError(f"No plans found for intent {intent_id}")

    # Calculate EV for each plan and select the best one
    best_plan = max(intent_plans, key=lambda p: p['p_success'] - p['entropy'])
    return best_plan['plan_id']


def main():
    if len(sys.argv) != 4:
        print("Usage: python orchestrate_intent.py <ledger_dir> <intent_json_file> <repo_path>")
        sys.exit(1)

    ledger_dir = sys.argv[1]
    intent_json_file = sys.argv[2]
    repo_path = sys.argv[3]

    # Create ledger directory if it doesn't exist
    Path(ledger_dir).mkdir(parents=True, exist_ok=True)

    # Read intent ID from the JSON file
    with open(intent_json_file, 'r') as f:
        intent_data = json.load(f)
        intent_id = intent_data['intent_id']

    print("=== Holon Intent Orchestration ===")
    print(f"Intent ID: {intent_id}")
    print(f"Ledger Directory: {ledger_dir}")
    print(f"Repository Path: {repo_path}")
    print()

    # Step 1: Create Intent
    print("Step 1: Creating Intent...")
    run_entrypoint("intent_creator.sh", ledger_dir, intent_json_file)
    print()

    # Step 2: Generate Plans
    print("Step 2: Generating Plans...")
    run_entrypoint("planner.sh", ledger_dir, intent_id, "bootstrap-planner")
    print()

    # Step 3: Select Best Plan by Expected Value (EV = P(success) - Entropy)
    print("Step 3: Selecting Best Plan...")
    plans_file = os.path.join(ledger_dir, "plans.jsonl")
    best_plan = select_best_plan(plans_file, intent_id)
    print(f"Selected Plan: {best_plan}")
    print()

    # Step 4: Execute Selected Plan
    print("Step 4: Executing Plan...")
    run_entrypoint("executor.sh", ledger_dir, intent_id, best_plan, repo_path)
    print()

    print("=== Orchestration Complete ===")
    print(f"Intent {intent_id} has been processed.")


if __name__ == "__main__":
    main()
