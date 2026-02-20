# Plan for I-1771890389

**Plan ID:** P-1772691663-gemini-cli-gemini-3.1-pro-preview
**Parent Intent ID:** None
**Agent:** gemini-cli/gemini-3.1-pro-preview
**Created At:** 2026-03-05T06:21:03.6NZ

## Planner Autonomy Summary

- Intent handling: ACCEPT_AS_IS
- Reframed intent (if applicable): N/A
- Exploration stance: balanced. We need to implement a standard CLI tool but ensure it correctly integrates with the Docker sandbox and Git workflows described in the architecture constraints.
- Safety priority level: standard
- Priority Justification: The creation of a CLI tool does not inherently violate any strict safety boundaries as it primarily reads/writes to the local ledger and initiates sandboxed execution. It aligns with the baseline trust model.

## Exploration

- Proportion of steps that are exploratory: 0.2
- Justification: Most of the work is standard implementation (CLI parsing, JSON writing). A small exploratory portion is needed to correctly map the CLI's execution model to the existing Docker setup and ensure seamless Git cloning/branching from within the container.

## Overall Plan Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.90                  |
| entropy_pred        | 15.0                  |
| impact_pred         | 80                    |
| cost_pred           | 30                    |
| learning_value_pred | 4                     |
| ev_pred             | 39.5                  |

### Strategy Rationale

The strategy is to build a Python-based CLI named `holon` that provides a command interface for intent creation. It will manage generating intent IDs, constructing the intent JSON payload, and appending it to `app/ledger/intents.jsonl`. We will also include the functionality for the CLI to be executed within the Docker container, pulling the repository and checking out the correct branch as specified in the intent description. 

Overall metrics derivation: 
- `p_success_pred` (0.90) is derived qualitatively from the lowest step probability (bottleneck is Step 2 at 0.85, but Step 1 is straightforward, bringing overall confidence slightly up).
- `entropy_pred` (15.0) is the sum of step entropies (5.0 + 10.0).
- `impact_pred` (80) is the sum of step impacts (40 + 40), as both steps are required to fulfill the full intent value.
- `cost_pred` (30) is the sum of step costs (10 + 20).
- `learning_value_pred` (4) is the sum of step learning values (1 + 3).
- `ev_pred` (39.5) is calculated using the EV formula: (0.90 * 80) + (0.5 * 4) - (0.3 * 15) - 30 = 72 + 2 - 4.5 - 30 = 39.5.

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan: `docs/safety.md#2-sandboxing-is-mandatory-for-execution`, `docs/safety.md#1-git-is-the-safety-boundary`
- Potential violations or edge cases: The CLI might fail to properly sandbox execution or might execute destructive git commands outside of the intended isolated branch.
- Mitigations built into the plan: The CLI will strictly use the standard Docker mechanisms defined in the sandbox model to spawn environments, and Git operations will be strictly parameterised to the intent's branch.
- Residual risk accepted (and why): Minimal. The CLI itself is a tool; the actual risk comes when it spawns agents, which will be constrained by the Docker sandboxes.
- Allocated Entropy Budget: 50
- Predicted Plan Entropy: 15.0
- Budget Compliance: The strategy fits within budget

## Plan Description & Strategy

The plan involves creating a core `holon` Python script in the project root. This script will implement the `intent create` command to generate an intent ID, prompt for/accept arguments (title, description), and append the record to the ledger. A second step will ensure the CLI can bootstrap its own environment inside Docker: we'll implement a workspace setup logic that the Docker entrypoint can call to clone the repo and checkout the target branch before executing the agent.

---

## Step 1: Implement `holon` CLI Core and Intent Creation

**Sub‑intent recommendation:** NO
**Reasoning:** This is a straightforward Python script implementation using standard libraries for CLI parsing and JSON file appending. It poses very low risk.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Create the executable `holon` CLI tool with the `intent create` command to append valid JSON records to the intent ledger.
**Git branch:** I-1771890389-bootstrap-cli/step-1-core-cli
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Create a Python executable file named `holon` in the root directory (with `#!/usr/bin/env python3` shebang and execution permissions).
2. Use `argparse` to set up subcommands, starting with `intent`.
3. Under the `intent` subcommand, create a `create` action.
4. The `create` action should accept arguments: `--title`, `--description`, and optionally `--parent-id`.
5. Generate a unique `intent_id` (e.g., `I-<timestamp>`).
6. Construct the intent dictionary conforming to the schema.
7. Append this JSON string as a new line to `app/ledger/intents.jsonl`.

### Dependencies & Criticality

**Depends on:** NONE
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: implied schema adherence for ledger.
- Potential failure modes for this step: Malformed JSON written to the ledger; incorrect ID formatting.
- Guardrails and early‑abort checks: Validate the JSON structure against the expected schema before appending to the file.

### Success & Discard Criteria

**Success:** Running `./holon intent create --title "Test" --description "Desc"` successfully appends a well-formed JSON line to `app/ledger/intents.jsonl`.
**Discard:** If file I/O permissions repeatedly block execution or if Python 3 is not available in the base environment.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.95                  |
| entropy_pred        | 5.0                   |
| impact_pred         | 40                    |
| cost_pred           | 10                    |
| learning_value_pred | 1                     |
| ev_pred             | 27.0                  |

### Step Metrics Rationale

Very high success probability and low entropy due to standard file I/O and CLI parsing. High impact as it is the foundational interface for the system. EV = (0.95 * 40) + (0.5 * 1) - (0.3 * 5) - 10 = 38 + 0.5 - 1.5 - 10 = 27.0.

---

## Step 2: Implement Isolated Environment Bootstrap Logic

**Sub‑intent recommendation:** YES
**Reasoning:** Interacting with Docker and Git to ensure proper sandboxing and branch isolation carries higher risk and complexity, making it suitable for a sub-intent to isolate failure.
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: The CLI can reliably set up its workspace by cloning the repository and checking out the correct intent branch from within a minimal Docker container without leaking host state.
- Learning target: Identify any permission issues or missing dependencies when cloning the git repo inside the Docker container.
- Maximum acceptable cost for this learning: 20

### Intent & Git Integration

**Step Intent:** Extend the CLI (or its Docker entrypoints) to support bootstrapping: cloning the repository and checking out the intent's branch inside the Docker sandbox.
**Git branch:** I-1771890389-bootstrap-cli/step-2-sandbox-bootstrap
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

1. Add a command to the `holon` CLI, e.g., `holon workspace setup --intent-id <id>`.
2. This command should read the intent from `app/ledger/intents.jsonl` to find the target `branch`.
3. Execute `git clone` to retrieve a clean copy of the project within the isolated environment.
4. Execute `git checkout <branch>` to move to the branch associated with the intent.
5. Ensure this logic is invoked properly by the Docker entrypoints.

### Dependencies & Criticality

**Depends on:** Step 1
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md#2-sandboxing-is-mandatory-for-execution`, `docs/safety.md#1-git-is-the-safety-boundary`
- Potential failure modes for this step: Network restrictions in Docker preventing `git clone`; Git credentials leaking into the sandbox.
- Guardrails and early‑abort checks: Verify the target directory is empty before cloning; ensure the branch name matches the isolated branch naming convention.

### Success & Discard Criteria

**Success:** The CLI can be invoked in a Docker container, successfully clones the repo, and checks out the specific branch for an intent.
**Discard:** If the Docker container fails to build or lacks Git, or if cloning fails consistently due to network/auth issues.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.85                  |
| entropy_pred        | 10.0                  |
| impact_pred         | 40                    |
| cost_pred           | 20                    |
| learning_value_pred | 3                     |
| ev_pred             | 12.5                  |

### Step Metrics Rationale

Lower success probability due to environmental variables (Docker, Git auth inside containers). Higher entropy due to filesystem/process operations. EV = (0.85 * 40) + (0.5 * 3) - (0.3 * 10) - 20 = 34 + 1.5 - 3 - 20 = 12.5.
