# Plan for I-1771890389

**Plan ID:** P-1772691637-opencode-opencode_big-pickle
**Parent Intent ID:** null
**Agent:** opencode/opencode_big-pickle
**Created At:** 2026-03-05T06:20:37.6NZ

## Planner Autonomy Summary

- Intent handling: ACCEPT_AS_IS
- Reframed intent (if applicable): N/A
- Exploration stance: balanced with 1–2 sentence justification.
- Safety priority level: standard
- Priority Justification: The intent is a bootstrap task to create a CLI tool. It does not involve production code changes, external API access, or security-sensitive operations. The sandbox model already supports container-based execution as specified.

## Exploration

- Proportion of steps that are exploratory: 0.1
- Justification: This is a bootstrap task with clear requirements. Most steps follow established patterns from existing code (holon script, docker files, entrypoints). Only Step 3 involves some exploration of agent capabilities within the sandbox.

## Overall Plan Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.85                  |
| entropy_pred        | 18.5                  |
| impact_pred         | 75                    |
| cost_pred           | 35                    |
| learning_value_pred | 5                     |
| ev_pred             | 48.45                 |

### Strategy Rationale

The plan follows a bottom-up approach: first establishing the foundational CLI tool, then enhancing it with agent capabilities, and finally validating the complete system. The overall metrics are derived from:
- p_success_pred: High because most steps involve modifying existing well-understood files (holon script, docker files). Step 3 has moderate uncertainty about agent behaviour.
- entropy_pred: Sum of step entropies (4 + 4 + 5.5 + 5 = 18.5) - moderate complexity from integration testing.
- impact_pred: Highest at 75 because this CLI enables the entire autonomous system to spawn future tasks.
- cost_pred: Sum of step costs (8 + 8 + 10 + 9 = 35) - reasonable for bootstrap work.
- learning_value_pred: Moderate at 5 - some novel integration patterns but mostly established code.

**EV Calculation (per metrics.md formula):**
- EV = P(success) * Impact + μ * LearningValue - λ * Entropy - Cost
- EV = 0.85 * 75 + 0.5 * 5 - 0.3 * 18.5 - 35 = 25.75

The bottleneck step (Step 3) has the lowest p_success_pred at 0.80 because git operations in containers can fail for various reasons.

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan:
  - safety.md#sandboxing: All execution must happen in sandboxed environments (containers)
  - safety.md#trust: Baseline agents cannot spawn sub-intents; the CLI enables this capability
  - git_flow.md: Branch naming uses `/_` suffix for terminal leaf nodes
  - architecture.md#fractal_intent: Sub-intents follow same rules as root intents

- Potential violations or edge cases:
  - Sandbox escape via git operations (mitigated by read-only except for intent workspace)
  - Intent branch naming conflicts (mitigated by timestamp-based IDs)

- Mitigations built into the plan:
  - All docker commands run with `--network none` for isolation
  - Git operations limited to the cloned workspace
  - No subprocess spawning except whitelisted tools (git, bash)

- Residual risk accepted (and why): Low - the CLI is a bootstrap tool that enables the system to function. Any failures are contained to intent branches.

- Allocated Entropy Budget: Not specified in intent - assuming moderate budget (30-40)
- Predicted Plan Entropy: 18.5
- Budget Compliance: The strategy fits within budget (18.5 < 30)

## Plan Description & Strategy

This plan creates a self-hosting holon CLI that can spawn its own future tasks. The CLI will:
1. Install the holon bash script into the docker container
2. Enhance the CLI with self-intent capabilities (create, plan, execute within sandbox)
3. Configure git access for the sandbox to clone and checkout branches
4. Validate the complete system by running a test intent

The approach is bottom-up, starting with the foundational CLI installation, then adding capabilities incrementally. This minimises risk and allows early detection of issues.

---

## Step 1: Install holon CLI into docker container

**Sub‑intent recommendation:** NO
**Reasoning:** This step is straightforward - copying an existing script to the container. No risk of significant blast radius if it fails. Cost is low (8).
**Step Type:** CONFIG
**Exploration level:** EXPLOIT

- Hypothesis being tested: N/A (exploitation step)
- Learning target: N/A
- Maximum acceptable cost for this learning: N/A

### Intent & Git Integration

**Step Intent:** Install the holon bash CLI script into the docker container so it can be used by agents running inside the sandbox.
**Git branch:** I-1771890389-bootstrap-cli/_/P-1772691637-opencode-opencode_big-pickle/E-1772691637-install-cli
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

1. Create a Dockerfile entry that copies the holon script to the orchestrator image
2. Modify the holon-orchestrator Dockerfile stage to include the holon CLI
3. Ensure the CLI is executable and in the PATH

### Dependencies & Criticality

**Depends on:** NONE
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md#sandboxing, safety.md#container_sandbox
- Potential failure modes:
  - Script not copied correctly
  - Permissions issues (not executable)
- Guardrails and early‑abort checks:
  - Verify script exists in container after build
  - Check execute permissions

### Success & Discard Criteria

**Success:** holon CLI is available in the docker container at /home/holon/holon and is executable
**Discard:** If docker build fails or CLI is not accessible

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.95                  |
| entropy_pred        | 4                     |
| impact_pred         | 60                    |
| cost_pred           | 8                     |
| learning_value_pred | 2                     |
| ev_pred             | 51.8                  |

### Step Metrics Rationale

- p_success_pred: 0.95 - High because this is a simple file copy operation with well-understood docker behaviour
- entropy_pred: 4 - Low complexity (one file modification in Dockerfile)
- impact_pred: 60 - Medium-high (enables CLI usage in sandbox)
- cost_pred: 8 - Low (docker build + copy operation)
- learning_value_pred: 2 - Low (standard docker operations)
- EV = 0.95*60 + 0.5*2 - 0.3*4 - 8 = 57 + 1 - 1.2 - 8 = 48.8

---

## Step 2: Add self-hosting commands to holon CLI

**Sub‑intent recommendation:** NO
**Reasoning:** This step extends existing CLI with new commands. Similar to Step 1 in complexity. Not risky enough to warrant sub-intent.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

- Hypothesis being tested: N/A
- Learning target: N/A
- Maximum acceptable cost for this learning: N/A

### Intent & Git Integration

**Step Intent:** Extend the holon CLI with commands that allow it to create intents, plan, and execute within the sandbox environment. This enables the system to spawn its own tasks.
**Git branch:** I-1771890389-bootstrap-cli/_/P-1772691637-opencode-opencode_big-pickle/E-1772691637-add-commands
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

1. Modify holon script to accept intent JSON and create intent branch
2. Add capability to run planner inside the container
3. Add capability to run executor inside the container
4. Ensure proper git configuration (user.email, user.name) for commits
5. Test that the CLI can be invoked from within the container

### Dependencies & Criticality

**Depends on:** Step 1 (CLI must be installed in container)
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md#git_discipline, git_flow.md#branch_naming
- Potential failure modes:
  - Git operations fail due to missing SSH keys
  - Intent JSON parsing errors
- Guardrails and early‑abort checks:
  - Validate intent JSON structure before processing
  - Check git status after each operation

### Success & Discard Criteria

**Success:** holon CLI can execute create-intent, plan, execute commands from within the container
**Discard:** If CLI commands fail or git operations cannot complete

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.90                  |
| entropy_pred        | 4                     |
| impact_pred         | 70                    |
| cost_pred           | 8                     |
| learning_value_pred | 3                     |
| ev_pred             | 58.3                  |

### Step Metrics Rationale

- p_success_pred: 0.90 - High because modifying existing well-tested script
- entropy_pred: 4 - Low complexity (adding ~30-50 lines to bash script)
- impact_pred: 70 - High (enables self-hosting capability)
- cost_pred: 8 - Low (bash scripting)
- learning_value_pred: 3 - Low-medium (extends existing patterns)
- EV = 0.90*70 + 0.5*3 - 0.3*4 - 8 = 63 + 1.5 - 1.2 - 8 = 55.3

---

## Step 3: Configure git access and branch checkout in sandbox

**Sub‑intent recommendation:** YES
**Reasoning:** This step involves configuring git access which is critical for the sandbox to function. It has higher uncertainty (will SSH keys work correctly? will branch checkout succeed?). It is also a reusable capability that other intents will need.
**Step Type:** CONFIG
**Exploration level:** BALANCED

- Hypothesis being tested: The sandbox environment can successfully clone the project repository and checkout the correct branch for the action it is taking.
- Learning target: Verify git operations work inside container with mounted SSH keys
- Maximum acceptable cost for this learning: 12 (cost_pred)

### Intent & Git Integration

**Step Intent:** Configure the docker container to have git access and the ability to checkout the correct branch. This is essential for the CLI to operate on its own copy of the project.
**Git branch:** I-1771890389-bootstrap-cli/_/P-1772691637-opencode-opencode_big-pickle/E-1772691637-configure-git
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

1. Ensure SSH keys are properly mounted into the container (verify in holon script)
2. Configure git to use SSH for remote operations
3. Test cloning the project repository in the sandbox
4. Test checkout of a specific branch
5. Ensure the workspace is writable for the agent to make commits

### Dependencies & Criticality

**Depends on:** Step 1, Step 2
**Is Bottleneck:** YES - Without git access, the CLI cannot function

### Safety & Constraint Considerations

- Relevant rules: safety.md#sandboxing, safety.md#process_sandbox (allowed tools: git)
- Potential failure modes:
  - SSH keys not available or incorrect permissions
  - Git clone fails due to network or authentication
  - Branch checkout fails
- Guardrails and early‑abort checks:
  - Verify SSH key file exists before running container
  - Check git remote -v shows correct URL
  - Verify branch exists before checkout

### Success & Discard Criteria

**Success:** Docker container can clone the repo and checkout any branch specified in the intent
**Discard:** If git clone or checkout fails after 2 attempts

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.80                  |
| entropy_pred        | 5.5                   |
| impact_pred         | 80                    |
| cost_pred           | 10                    |
| learning_value_pred | 5                     |
| ev_pred             | 53.85                 |

### Step Metrics Rationale

- p_success_pred: 0.80 - Moderate because git operations can fail due to various reasons (keys, network, permissions)
- entropy_pred: 5.5 - Medium (involves multiple git operations and potential error handling)
- impact_pred: 80 - Very high (critical for self-hosting capability)
- cost_pred: 10 - Moderate (testing git operations)
- learning_value_pred: 5 - Medium (understanding git access patterns in containers)
- EV = 0.80*80 + 0.5*5 - 0.3*5.5 - 10 = 64 + 2.5 - 1.65 - 10 = 54.85

---

## Step 4: Validate complete CLI system

**Sub‑intent recommendation:** NO
**Reasoning:** This is a validation step that tests the integrated system. Low risk - if it fails, we learn what needs to be fixed.
**Step Type:** TEST
**Exploration level:** EXPLOIT

- Hypothesis being tested: N/A (validation)
- Learning target: N/A
- Maximum acceptable cost for this learning: N/A

### Intent & Git Integration

**Step Intent:** Run a test intent through the complete holon CLI lifecycle to validate that the system can create, plan, and execute its own tasks.
**Git branch:** I-1771890389-bootstrap-cli/_/P-1772691637-opencode-opencode_big-pickle/E-1772691637-validate
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

1. Create a simple test intent (e.g., "echo hello" or create a small file)
2. Run holon create-intent with the test intent
3. Run holon plan to generate a plan
4. Run holon execute to carry out the plan
5. Verify the intended outcome was achieved
6. Clean up test artifacts

### Dependencies & Criticality

**Depends on:** Step 1, Step 2, Step 3
**Is Bottleneck:** NO (validation step)

### Safety & Constraint Considerations

- Relevant rules: safety.md#sandboxing
- Potential failure modes:
  - Test intent fails to create
  - Planning fails
  - Execution fails
- Guardrails and early‑abort checks:
  - Verify each step completes before proceeding
  - Log all output for debugging

### Success & Discard Criteria

**Success:** Test intent completes successfully - creates branch, generates plan, executes action
**Discard:** If any step in the lifecycle fails

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.75                  |
| entropy_pred        | 5                     |
| impact_pred         | 85                    |
| cost_pred           | 9                     |
| learning_value_pred | 5                     |
| ev_pred             | 56.95                 |

### Step Metrics Rationale

- p_success_pred: 0.75 - Moderate because this is an integration test with many dependencies
- entropy_pred: 5 - Medium (end-to-end test complexity)
- impact_pred: 85 - Highest (validates entire system works)
- cost_pred: 9 - Low-moderate (test execution)
- learning_value_pred: 5 - Medium (learns about integration issues)
- EV = 0.75*85 + 0.5*5 - 0.3*5 - 9 = 63.75 + 2.5 - 1.5 - 9 = 55.75

---

## Summary

The plan creates a self-hosting holon CLI in 4 steps:

1. **Install CLI** (p=0.95, E=4, cost=8) - Copy holon script to container
2. **Add commands** (p=0.90, E=4, cost=8) - Extend CLI with create-intent, plan, execute
3. **Configure git** (p=0.80, E=5.5, cost=10) - **Bottleneck step** - Enable git clone/checkout in sandbox
4. **Validate** (p=0.75, E=5, cost=9) - Test complete lifecycle

The bottleneck step (Step 3) has the lowest p_success_pred at 0.80 because git operations in containers can fail for various reasons. The overall plan has:
- p_success = 0.85 (weighted by step importance)
- Total entropy = 18.5 (within typical budget)
- High impact (75-85) because this enables autonomous task spawning
- EV = ~30 (acceptable for bootstrap work with high learning value)
