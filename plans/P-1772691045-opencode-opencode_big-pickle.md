# Plan for I-1771890389

**Plan ID:** P-1772691045-opencode-opencode_big-pickle
**Parent Intent ID:** null (root intent)
**Agent:** opencode/opencode/big-pickle
**Created At:** 2026-03-05T06:10:45.6NZ

## Planner Autonomy Summary

- Intent handling: ACCEPT_AS_IS
- Reframed intent (if applicable): None
- Exploration stance: balanced with 1–2 sentence justification.
- Safety priority level: elevated (new capability bootstrapping with git isolation)
- Priority Justification: This is a root intent that bootstraps the system's self-reproduction capability. The intent involves modifying the CLI and sandbox environment - both critical paths. However, git isolation and container sandboxing provide safety boundaries per safety.md §1-2.

## Exploration

- Proportion of steps that are exploratory: 0.15
- Justification: Most steps are exploitation of known patterns (CLI design, Docker setup). Step 3 (self-spawning capability) is exploratory as it involves recursive intent creation which has no prior KB patterns.

## Overall Plan Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.75                  |
| entropy_pred        | 22.5                  |
| impact_pred         | 95                    |
| cost_pred           | 50                    |
| learning_value_pred | 13.0                  |
| ev_pred             | 21.0                  |

### Strategy Rationale

The intent is to bootstrap a CLI that can spawn its own future tasks. The existing `holon` CLI wrapper already exists at `/holon` and Docker infrastructure is partially set up. The key gaps are: (1) adding self-spawning capability to the CLI, (2) ensuring the isolated environment can clone and checkout branches correctly.

**Overall metrics derivation:**
- p_success_pred: Weighted average of step success probabilities weighted by cost, bottleneck at Step 3 (self-spawning)
- entropy_pred: Sum of step entropies = 1.5 + 5.0 + 8.0 + 4.0 + 2.0 = 20.5 ≈ 22.5 (with safety margin)
- impact_pred: System-level impact = 95 (enables self-reproduction capability)
- cost_pred: Sum of step costs = 50
- learning_value_pred: Sum of step learning values = 1.0 + 2.5 + 5.0 + 3.0 + 1.5 = 13.0
- ev_pred: P(success) × Impact + μ × LearningValue - λ × Entropy - Cost
  = 0.75 × 95 + 0.5 × 13 - 0.3 × 22.5 - 50
  = 71.25 + 6.5 - 6.75 - 50
  = 21.0

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan:
  - safety.md §1: Git is the safety boundary - all execution in isolated branches
  - safety.md §2: Sandboxing mandatory - Docker containers with restricted access
  - safety.md §4: Entropy is a safety signal - high entropy = deeper review
  - Git discipline: Sub-intents never merge directly to main

- Potential violations or edge cases:
  - Sandbox escape attempts during self-cloning (mitigated by Docker isolation)
  - Infinite recursion in self-spawning (mitigated by depth limits in entrypoints)
  - Rebase conflicts from concurrent branch operations

- Mitigations built into the plan:
  - Step-by-step execution with verification at each stage
  - Container sandbox as per safety.md §2 (medium entropy)
  - Testing self-spawn in isolation before production use

- Residual risk accepted (and why): Low. Docker sandboxing and git branch isolation provide containment. The CLI modifications are additive only.

- Allocated Entropy Budget: Not specified in intent, using default for root intents
- Predicted Plan Entropy: 22.5
- Budget Compliance: Assumed sufficient for root intent

## Plan Description & Strategy

The plan creates a self-reproducing CLI capability. Key strategy:
1. **Leverage existing infrastructure** - The `holon` CLI wrapper and Docker files already exist
2. **Add self-spawning capability** - Extend CLI to programmatically create new intents
3. **Verify isolation** - Ensure the sandbox can clone and operate on its own branch
4. **Test the闭环** - Verify the system can spawn and execute a follow-up intent

The plan treats Steps 1-2 as low-risk exploitation of existing patterns, and Step 3 as the novel capability that justifies the learning value component.

---

## Step 1: Analyse existing CLI and Docker infrastructure

**Sub‑intent recommendation:** NO
**Reasoning:** Simple analysis task with low risk, no code changes, reusability value is low
**Step Type:** INFO_GATHERING
**Exploration level:** EXPLOIT

- Hypothesis being tested: N/A (exploitation of known patterns)
- Learning target: N/A
- Maximum acceptable cost: N/A

### Intent & Git Integration

**Step Intent:** Understand what already exists in the codebase for the holon CLI and Docker orchestration to identify gaps
**Git branch:** I-1771890389-bootstrap-cli/_ (same as intent branch)
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Read existing holon CLI wrapper script at project root
2. Read Docker files: Dockerfile, build scripts, entrypoint scripts
3. Read orchestrate_intent.py orchestration script
4. Read existing intent_bootstrap_cli.json for expected format
5. Identify what gaps exist for self-spawning capability
6. Document findings in a summary

### Dependencies & Criticality

**Depends on:** NONE (first step)
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md §1 (git isolation), no code changes
- Potential failure modes for this step: None - this is a read-only analysis
- Guardrails and early‑abort checks: N/A

### Success & Discard Criteria

**Success:** Written summary of existing infrastructure and identified gaps for self-spawning
**Discard:** N/A (cannot fail read-only analysis)

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.95                  |
| entropy_pred        | 1.5                   |
| impact_pred         | 10                    |
| cost_pred           | 5                     |
| learning_value_pred | 1.0                   |
| ev_pred             | 9.5                   |

### Step Metrics Rationale

p_success_pred=0.95: High because this is purely reading existing files with no execution
entropy_pred=1.5: Very low - simple file reads with well-defined structure
impact_pred=10: Low - informational only, doesn't enable new capabilities
cost_pred=5: Low - minimal effort to read files
learning_value_pred=1.0: Low - known patterns, no novel information expected

---

## Step 2: Design and implement self-spawning CLI commands

**Sub‑intent recommendation:** NO
**Reasoning:** Implementation follows standard CLI patterns already present in holon wrapper
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

- Hypothesis being tested: N/A
- Learning target: N/A  
- Maximum acceptable cost: N/A

### Intent & Git Integration

**Step Intent:** Extend the holon CLI to support programmatic intent creation and self-spawning
**Git branch:** I-1771890389-bootstrap-cli/_ (execution branch)
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Extend holon CLI wrapper to add `spawn-intent` subcommand
2. Add `spawn-intent <intent_json_path>` that:
   - Validates intent JSON structure (intent_id, title, description, branch, goal)
   - Creates a new git branch for the intent
   - Logs the intent to the ledger
   - Optionally triggers planning for the new intent
3. Add environment variable support for sandbox configuration (BRANCH_NAME, REPO_URL)
4. Document the new commands in the CLI help

### Dependencies & Criticality

**Depends on:** Step 1 (analysis of existing infrastructure)
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md §2 (sandboxing), git discipline (branch naming)
- Potential failure modes for this step:
  - Invalid intent JSON causing parse errors
  - Branch name conflicts
  - SSH key access issues for git push
- Guardrails and early‑abort checks:
  - Validate intent JSON schema before creating branch
  - Check branch doesn't already exist
  - Verify SSH keys are mounted in container

### Success & Discard Criteria

**Success:** 
- `holon spawn-intent --help` shows new command
- Can create a new intent branch via dockerised holon CLI
- Intent appears in ledger

**Discard:** 
- If CLI command fails to parse intent JSON
- If branch creation fails

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.80                  |
| entropy_pred        | 5.0                   |
| impact_pred         | 40                    |
| cost_pred           | 15                    |
| learning_value_pred | 2.5                   |
| ev_pred             | 30.5                  |

### Step Metrics Rationale

p_success_pred=0.80: Moderate - CLI implementation is straightforward but may have edge cases
entropy_pred=5.0: Low-medium - familiar CLI patterns, some file I/O
impact_pred=40: Medium-high - enables programmatic intent creation
cost_pred=15: Low-medium - straightforward CLI additions
learning_value_pred=2.5: Low - follows established CLI patterns

---

## Step 3: Implement sandbox self-cloning and branch checkout

**Sub‑intent recommendation:** YES
**Reasoning:** This is the novel capability - the sandbox must clone the repo and checkout the correct branch. High learning value and risk. If this step fails, the entire self-spawning loop fails.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLORATORY

- Hypothesis being tested: Can an isolated Docker container clone the project and checkout the correct branch for execution?
- Learning target: Understand self-referential git operations in sandboxed environment
- Maximum acceptable cost: 20 tokens / 10 minutes wall time

### Intent & Git Integration

**Step Intent:** Ensure the Docker sandbox can clone the project and checkout the branch specified by the intent
**Git branch:** I-1771890389-bootstrap-cli/_ (execution branch)
**Sub‑intent:** NEW - Create sub-intent for sandbox self-cloning capability

### Implementation Details (No code blocks, only logic/steps)

1. Modify Docker entrypoint (intent_creator.sh or create new entrypoint) to:
   - Accept environment variables: REPO_URL, BRANCH_NAME
   - Clone repository to fresh directory
   - Checkout specified branch
   - Verify clone was successful
2. Add self-clone logic to holon CLI spawn command:
   - Detect if running in container
   - If in container, clone fresh; otherwise use mounted volume
3. Test the self-clone in isolation:
   - Create test intent
   - Run holon spawn-intent in Docker
   - Verify new branch has correct code

### Dependencies & Criticality

**Depends on:** Step 2 (CLI spawn command must exist before self-spawn can work)
**Is Bottleneck:** YES - This is the critical path for self-reproduction

### Safety & Constraint Considerations

- Relevant rules: safety.md §2 (sandbox isolation), §3 (trust model - baseline agent)
- Potential failure modes for this step:
  - Network unavailable in sandbox (blocked by --network none)
  - SSH key not mounted correctly
  - Branch doesn't exist remotely
  - Infinite recursion if spawn triggers spawn
- Guardrails and early‑abort checks:
  - Verify network isolation is intentional per intent spec
  - Add depth limit to prevent infinite spawn loops
  - Validate branch exists before checkout

### Success & Discard Criteria

**Success:**
- Docker container can clone repo and checkout branch
- Branch contains correct code at specified commit
- Multiple sequential spawns work correctly

**Discard:**
- Network permanently blocked and cannot clone
- SSH key authentication fails repeatedly
- Branch checkout fails for valid branch names

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.70                  |
| entropy_pred        | 8.0                   |
| impact_pred         | 50                    |
| cost_pred           | 15                    |
| learning_value_pred | 5.0                   |
| ev_pred             | 36.5                  |

### Step Metrics Rationale

p_success_pred=0.70: Lower because this is novel - network isolation in sandbox may be unexpected
entropy_pred=8.0: Higher - involves git operations, network, new code paths
impact_pred=50: High - core capability for self-reproduction
cost_pred=15: Medium - git clone and checkout operations
learning_value_pred=5.0: High - unknown failure modes, will populate KB

---

## Step 4: Test end-to-end self-spawning loop

**Sub‑intent recommendation:** NO
**Reasoning:** Integration testing to verify the complete loop works
**Step Type:** TEST
**Exploration level:** EXPLOIT

- Hypothesis being tested: The complete self-spawn loop functions correctly
- Learning target: Verify all components work together
- Maximum acceptable cost: 30 tokens / 15 minutes

### Intent & Git Integration

**Step Intent:** Verify the CLI can spawn a new intent and the sandbox can execute it
**Git branch:** I-1771890389-bootstrap-cli/_ (execution branch)
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Create a test intent JSON (e.g., "echo test intent")
2. Run holon spawn-intent with the test intent in Docker
3. Verify new branch was created
4. Verify intent was logged to ledger
5. Optionally trigger planning on the new intent
6. Verify plan was generated
7. Document the complete flow

### Dependencies & Criticality

**Depends on:** Steps 2 and 3 (CLI and self-clone must work)
**Is Bottleneck:** NO (but if this fails, the goal isn't achieved)

### Safety & Constraint Considerations

- Relevant rules: safety.md §1-2 (git isolation, sandboxing)
- Potential failure modes:
  - Test intent creation fails
  - Ledger write fails
  - Planning doesn't trigger
- Guardrails: Test with harmless intent first

### Success & Discard Criteria

**Success:**
- Complete loop executes without error
- New branch created and contains code
- Intent appears in ledger
- Can trigger follow-on actions

**Discard:**
- Any step in the loop fails
- Ledger not updated correctly

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.75                  |
| entropy_pred        | 4.0                   |
| impact_pred         | 30                    |
| cost_pred           | 10                    |
| learning_value_pred | 3.0                   |
| ev_pred             | 26.5                  |

### Step Metrics Rationale

p_success_pred=0.75: Integration testing has moderate complexity
entropy_pred=4.0: Medium - orchestration of multiple components
impact_pred=30: Validates the system works but doesn't add new capability
cost_pred=10: Test execution
learning_value_pred=3.0: Moderate - confirms expected behaviour

---

## Step 5: Document CLI usage and finalise

**Sub‑intent recommendation:** NO
**Reasoning:** Documentation is low-risk, completes the intent
**Step Type:** DOCUMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Document the CLI commands and usage for future agents
**Git branch:** I-1771890389-bootstrap-cli/_ (execution branch)
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Update holon CLI help text with all available commands
2. Document the spawn-intent command format
3. Document sandbox environment variables
4. Add examples to README or create docs/cli.md

### Dependencies & Criticality

**Depends on:** Step 2 (CLI must be implemented)
**Is Bottleneck:** NO

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.90                  |
| entropy_pred        | 2.0                   |
| impact_pred         | 15                    |
| cost_pred           | 5                     |
| learning_value_pred | 1.5                   |
| ev_pred             | 14.0                  |

### Step Metrics Rationale

p_success_pred=0.90: Documentation is straightforward
entropy_pred=2.0: Very low - text writing only
impact_pred=15: Improves usability but not core capability
cost_pred=5: Low effort
learning_value_pred=1.5: Low - standard documentation

---

## Overall Plan Summary

The plan creates a self-reproducing CLI that enables the Holon system to spawn its own future tasks:

1. **Analyse** existing infrastructure (read-only, low risk)
2. **Implement** spawn-intent CLI command (exploitation of known patterns)
3. **Implement** sandbox self-cloning (novel capability, highest entropy, sub-intent recommended)
4. **Test** the complete self-spawn loop (integration verification)
5. **Document** CLI usage (completion)

The bottleneck is Step 3 - sandbox self-cloning - which has the lowest p_success_pred (0.70) and highest entropy (8.0). This step justifies the sub-intent recommendation because:
- It's the critical path for self-reproduction
- It involves novel git operations in isolated environments
- Failure here fails the entire goal
- Learning value is high (will expose failure modes for KB)
