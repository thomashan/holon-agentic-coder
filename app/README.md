# Holon System

This directory contains the core files for the holon agentic coding system.

## Structure

- `ledger/` - Contains the JSONL files that track intents, plans, and events
- `core/` - Core Python modules (to be implemented)
- `scripts/` - Utility scripts for system management

## Ledger Files

- `intents.jsonl` - Tracks all intents in the system
- `plans.jsonl` - Tracks competing plans for each intent
- `events.jsonl` - Logs all events and inner-loop failures

## Bootstrap Process

1. Run `setup_holon.sh` to initialize the directory structure
2. Run `python orchestrate_intent.py holon/ledger holon/scripts/intent_bootstrap_cli.json repo/` to start the first intent
