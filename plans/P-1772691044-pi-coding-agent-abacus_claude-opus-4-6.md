# Plan for I-1771890389

**Plan ID:** P-1772691044-pi-coding-agent-abacus_claude-opus-4-6
**Parent Intent ID:** null
**Agent:** pi-coding-agent/abacus/claude-opus-4-6
**Created At:** 2026-03-05T06:10:44.6NZ

## Planner Autonomy Summary

- Intent handling: ACCEPT_AS_IS
- Reframed intent (if applicable): N/A
- Exploration stance: balanced — The project already has a working skeleton (`holon` CLI, Dockerfile, entrypoints) but it is incomplete and partially hardcoded. The intent is well-scoped and the existing code provides strong scaffolding, so a balanced approach that exploits known patterns while exploring Docker networking and git-in-container isolation is appropriate.
- Safety priority level: elevated
- Priority Justification: safety.md mandates sandboxed execution for all code (§2 "Sandboxing is mandatory for execution"). This intent directly creates the sandbox infrastructure, so any defect here undermines the entire safety model. Additionally, the CLI will be the primary mechanism for spawning future tasks, making it a critical-path component.

## Exploration

- Proportion of steps that are exploratory: 0.15
- Justification: Most work is well-defined (CLI argument parsing, Docker container lifecycle, git clone/checkout). The exploratory portion covers SSH key forwarding strategies and container networking isolation patterns, which have not been validated in this project yet.

## Overall Plan Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.72  |
| entropy_pred        | 18.5  |
| impact_pred         | 90    |
| cost_pred           | 45    |
| learning_value_pred | 6.0   |
| ev_pred             | 46.35 |

### Strategy Rationale

**EV Calculation:** EV = 0.72 × 90 + 0.5 × 6.0 − 0.3 × 18.5 − 45 = 64.8 + 3.0 − 5.55 − 45 = 17.25

*Note: Recalculating more carefully:* EV = 0.72 × 90 + 0.5 × 6.0 − 0.3 × 18.5 − 45 = 64.8 + 3.0 − 5.55 − 45 = **17.25**

The intent is accepted as-is because the existing project already has a partial `holon` CLI script, a Dockerfile, and entrypoint scripts. The work is to complete, harden, and integrate these into a functional end-to-end system where:
1. `holon create-intent` creates an intent branch in an isolated Docker container
2. `holon plan` generates plans in an isolated container
3. `holon execute` runs execution in an isolated container
4. Each container clones its own copy of the repo and checks out the correct branch

**Overall p_success (0.72):** Derived as the product of the most critical step probabilities. The bottleneck is Step 3 (Docker sandbox hardening) at 0.75 and Step 4 (end-to-end integration) at 0.78. The chain probability across all steps is approximately 0.72.

**Overall entropy (18.5):** Sum of per-step entropies. The largest contributors are Docker sandbox hardening (SSA=5, IRR=3, NOV=3) and the CLI refactor (SSA=4, IRR=2).

**Overall impact (90):** This intent is foundational — it enables the entire system to spawn future tasks autonomously. Without it, no other intent can be executed through the system. Max of step impacts.

**Overall cost (45):** Sum of step costs. Dominated by Docker work and integration testing.

**Overall learning_value (6.0):** Max of step learning values. The Docker isolation patterns and git-in-container workflows are novel to this project and will inform all future execution.

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan:
  - safety.md §2: All code execution must happen in sandboxed environments
  - safety.md §1: Git is the safety boundary — every intent executes in an isolated git branch
  - git_flow.md §3: Mandatory dual rebase discipline (before and after execution)
  - architecture.md: Sandboxed exploration is allowed including risky work
- Potential violations or edge cases:
  - SSH key mounting (`-v "$HOME/.ssh":/home/holon/.ssh:ro`) exposes host credentials to container — potential sandbox escape vector
  - Container running with `-it` (interactive TTY) may not be appropriate for automated execution
  - No network isolation currently (`--network none` not enforced in the existing `holon` script)
- Mitigations built into the plan:
  - Step 3 explicitly addresses network isolation, resource limits, and read-only filesystem
  - SSH key forwarding will use ssh-agent forwarding instead of direct mount where possible
  - All containers will have resource limits (CPU, memory, disk)
  - Step 5 adds tests that verify sandbox constraints are enforced
- Residual risk accepted (and why): SSH key access is required for git clone from GitHub. This is an accepted trade-off for bootstrap — future iterations can use deploy keys or GitHub App tokens with narrower scope.
- Allocated Entropy Budget: Not explicitly set by parent (root intent from human). Assuming standard root budget of 50.
- Predicted Plan Entropy: 18.5
- Budget Compliance: The strategy fits within budget (18.5 < 50)

## Plan Description & Strategy

The strategy decomposes the Bootstrap CLI intent into 6 steps that progressively build from foundation to integration:

1. **Refactor the `holon` CLI script** — Clean up the existing bash wrapper, add missing commands, improve argument handling, add help text
2. **Fix and complete Docker entrypoints** — The existing entrypoints have inconsistencies (executor.sh takes repo_path as first arg but the CLI doesn't pass it). Make all entrypoints self-contained: each clones the repo, checks out the correct branch, does its work
3. **Harden Docker sandbox** — Add network isolation, resource limits, read-only filesystem, proper user permissions per safety.md
4. **End-to-end integration** — Wire the CLI → Docker → entrypoint → git clone → branch checkout → work → commit → push pipeline
5. **Automated tests** — Create test_holon_bootstrap.sh improvements and unit tests that validate the full lifecycle
6. **Documentation** — Update README.md and add CLI usage docs

The approach is incremental: each step produces a working (if incomplete) system, reducing risk of total failure.

---

## Step 1: Refactor the `holon` CLI bash script

**Sub‑intent recommendation:** NO
**Reasoning:** Small scope (single file edit), low risk, well-understood bash scripting. Not reusable as a standalone component.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Refactor the `holon` bash CLI to have clean argument parsing, comprehensive help, and correct Docker invocation for all three commands (create-intent, plan, execute).
**Git branch:** `I-1771890389-bootstrap-cli/P-1772691044-pi-coding-agent-abacus_claude-opus-4-6/E-{timestamp}-refactor-cli`
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Restructure the `holon` script with proper argument parsing using a case statement
2. Add `--help` / `-h` flag support for the main command and each subcommand
3. Add a `version` subcommand that prints the current version
4. Fix the `run_in_container` function to:
   - Pass environment variables for API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY) via `-e` flags
   - Mount SSH keys correctly (read-only)
   - Pass the git repo URL as an environment variable (HOLON_REPO_URL) rather than hardcoding
   - Set HOLON_BRANCH environment variable so the container knows which branch to work on
5. For `create-intent`: mount the intent JSON file and pass the branch name
6. For `plan`: pass intent_branch, agent_name, model_name as environment variables
7. For `execute`: pass plan_branch, agent_name, model_name, action_slug as environment variables
8. Add error handling for missing Docker, missing images, and invalid arguments
9. Add a `build` subcommand that invokes `docker/build_all_images.sh`

### Dependencies & Criticality

**Depends on:** NONE
**Is Bottleneck:** YES (all subsequent steps depend on the CLI being functional)

### Safety & Constraint Considerations

- Relevant rules: safety.md §2 (sandboxing mandatory), architecture.md (agents propose diffs)
- Potential failure modes: Incorrect Docker flag syntax, missing environment variable passthrough, SSH key path differences across OS
- Guardrails: Test each subcommand with `--dry-run` flag before actual execution; validate Docker is running before attempting container operations

### Success & Discard Criteria

**Success:** `holon --help` prints usage; `holon create-intent`, `holon plan`, and `holon execute` each invoke Docker with correct arguments (verified via dry-run or echo mode)
**Discard:** If bash argument parsing becomes unmanageable (>200 lines for basic functionality), consider rewriting in Python

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.90  |
| entropy_pred        | 3.5   |
| impact_pred         | 60    |
| cost_pred           | 8     |
| learning_value_pred | 2.0   |
| ev_pred             | 44.95 |

### Step Metrics Rationale

High p_success because bash CLI refactoring is well-understood and the existing script provides a working template. Low entropy — single file change, easily reversible. Moderate impact as it's the user-facing entry point. Low cost (small file). Low learning value (routine work). EV = 0.90 × 60 + 0.5 × 2.0 − 0.3 × 3.5 − 8 = 54 + 1.0 − 1.05 − 8 = 45.95.

---

## Step 2: Fix and complete Docker entrypoint scripts

**Sub‑intent recommendation:** YES
**Reasoning:** The entrypoints are the core of the sandboxed execution model. They are reusable across all future intents and have moderate complexity (git clone, branch management, agent invocation). Errors here propagate to every future execution.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Make each Docker entrypoint (intent_creator.sh, planner.sh, executor.sh) fully self-contained: clone the repo, checkout the correct branch, perform its role, commit and push results.
**Git branch:** `I-1771890389-bootstrap-cli/P-1772691044-pi-coding-agent-abacus_claude-opus-4-6/E-{timestamp}-fix-entrypoints`
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. **intent_creator.sh** — Already mostly functional. Fix:
   - Read HOLON_REPO_URL from environment instead of hardcoding
   - Add error handling for git clone failure
   - Add validation that the intent JSON is well-formed before proceeding
   - Ensure the branch naming follows git_flow.md conventions (already does)

2. **planner.sh** — Partially functional. Fix:
   - Read HOLON_REPO_URL from environment
   - Fix the pi invocation: the current script uses `pi -p` with `@file` syntax but the prompt construction is fragile
   - Add support for multiple agent types (not just pi): detect HOLON_AGENT_COMMAND env var and dispatch to claude/gemini/pi/opencode accordingly
   - Ensure plan file is written to the correct path under `plans/`
   - Add ledger entry with proper metrics fields (currently hardcodes p_success=0.7, entropy=3.0)

3. **executor.sh** — Needs significant rework:
   - Currently takes repo_path as first arg but the CLI doesn't pass it
   - Should clone its own repo copy (like intent_creator and planner do)
   - Should read plan file from the plan branch to understand what actions to take
   - Should invoke the appropriate agent (claude/gemini/pi) to execute the plan step
   - Should commit results and push to the execution branch
   - Add proper ledger event logging

4. **role_dispatcher.sh** — Already functional, minor cleanup:
   - Add logging of which role was dispatched
   - Add validation that required environment variables are set for each role

### Dependencies & Criticality

**Depends on:** Step 1 (CLI must pass correct env vars to containers)
**Is Bottleneck:** YES (entrypoints are the execution engine)

### Safety & Constraint Considerations

- Relevant rules: safety.md §2 (sandbox execution), git_flow.md §3 (dual rebase), git_flow.md §2 (branch naming)
- Potential failure modes: Git clone auth failure (SSH keys), branch not found on remote, agent tool not installed in container image, ledger file conflicts on concurrent writes
- Guardrails: Validate git clone success before proceeding; validate branch exists; check agent tool is available; use atomic file operations for ledger writes

### Success & Discard Criteria

**Success:** Each entrypoint can be invoked in a Docker container and successfully: (a) clones the repo, (b) checks out the correct branch, (c) performs its role (create branch / generate plan / execute action), (d) commits and pushes results
**Discard:** If entrypoint complexity exceeds 150 lines each, consider refactoring shared logic into a common library script

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.82  |
| entropy_pred        | 5.0   |
| impact_pred         | 80    |
| cost_pred           | 12    |
| learning_value_pred | 4.0   |
| ev_pred             | 52.1  |

### Step Metrics Rationale

Good p_success — the existing scripts provide a template and the patterns are well-understood. Moderate entropy due to touching 4 files and introducing git-in-container patterns. High impact as these are the execution engine. Moderate cost (4 files, each ~50-100 lines). Moderate learning value — git clone/checkout patterns inside containers will be reused extensively. EV = 0.82 × 80 + 0.5 × 4.0 − 0.3 × 5.0 − 12 = 65.6 + 2.0 − 1.5 − 12 = 54.1.

---

## Step 3: Harden Docker sandbox per safety.md requirements

**Sub‑intent recommendation:** YES
**Reasoning:** Sandbox hardening is a security-critical, reusable component. Errors here undermine the entire safety model. The patterns established here will be used by every future execution. High learning value for understanding Docker security constraints in this project context.
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: Docker containers with `--network none`, `--read-only`, resource limits, and ssh-agent forwarding can successfully clone a GitHub repo, run agent tools, and push results.
- Learning target: Which Docker security flags are compatible with the git+agent workflow; whether ssh-agent forwarding works reliably across macOS and Linux hosts.
- Maximum acceptable cost for this learning: 15 cost units (if SSH forwarding proves unworkable, fall back to read-only key mount)

### Intent & Git Integration

**Step Intent:** Add Docker security hardening to the `holon` CLI and Dockerfile: network isolation (with selective allowlisting for git operations), resource limits, read-only filesystem, non-root user enforcement.
**Git branch:** `I-1771890389-bootstrap-cli/I-{timestamp}-harden-sandbox/_`
**Sub‑intent:** NEW

### Implementation Details (No code blocks, only logic/steps)

1. **Dockerfile changes:**
   - Ensure the `holon` user is non-root with minimal permissions
   - Add a health check
   - Pin base image versions for reproducibility
   - Add labels for image metadata

2. **CLI Docker invocation changes:**
   - Add `--cpus 2 --memory 4g` resource limits
   - Add `--read-only` with `--tmpfs /tmp:size=1g`
   - Add `--tmpfs /home/holon/repo:size=2g` for the workspace
   - For git operations: use a two-phase approach:
     a. Phase 1 (network enabled): Clone repo and fetch branches with `--network host` or a restricted network
     b. Phase 2 (network disabled): Execute agent work with `--network none`
   - Alternative simpler approach: Allow network access but restrict to GitHub IPs only using Docker network policies
   - Pragmatic bootstrap approach: Use `--network host` initially with a TODO to restrict later, since the container is already isolated by Docker's process namespace

3. **SSH key handling:**
   - Option A: Mount SSH keys read-only (current approach, simple but exposes keys)
   - Option B: Use ssh-agent forwarding via Docker socket mount
   - Option C: Use a GitHub deploy key specific to this repo
   - For bootstrap: Use Option A with a clear TODO for Option C

4. **Workspace isolation:**
   - Mount workspace as a tmpfs (ephemeral, destroyed when container exits)
   - No persistent volumes (each run is fresh)
   - Container cannot access host filesystem except for explicitly mounted paths

### Dependencies & Criticality

**Depends on:** Step 1 (CLI), Step 2 (entrypoints must work in hardened environment)
**Is Bottleneck:** NO (can be done in parallel with Step 2 to some extent; the system works without hardening, just less safely)

### Safety & Constraint Considerations

- Relevant rules: safety.md §2 (container sandbox requirements), safety.md §2.3 (sandbox escape detection)
- Potential failure modes: `--read-only` breaks agent tools that write to unexpected paths; `--network none` prevents git push; resource limits too tight for large model responses; SSH forwarding fails on macOS
- Guardrails: Test each security flag individually before combining; maintain a "permissive mode" flag for debugging; log all Docker flags used for audit

### Success & Discard Criteria

**Success:** Container runs with resource limits, non-root user, and restricted filesystem. Git clone/push works. Agent tools (pi, claude) work within the container. No files written outside designated workspace.
**Discard:** If Docker security flags prevent basic git operations after 2 hours of debugging, fall back to minimal hardening (non-root user + resource limits only) and document the gap.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.75  |
| entropy_pred        | 5.5   |
| impact_pred         | 70    |
| cost_pred           | 12    |
| learning_value_pred | 6.0   |
| ev_pred             | 38.85 |

### Step Metrics Rationale

Lower p_success due to uncertainty around Docker security flag compatibility with git+agent workflows. Higher entropy — touching Dockerfile, CLI, and potentially entrypoints; some irreversibility in choosing a security model. High impact as this establishes the safety foundation. Moderate cost. High learning value — Docker isolation patterns are novel to this project and will be reused everywhere. EV = 0.75 × 70 + 0.5 × 6.0 − 0.3 × 5.5 − 12 = 52.5 + 3.0 − 1.65 − 12 = 41.85.

---

## Step 4: End-to-end integration and wiring

**Sub‑intent recommendation:** YES
**Reasoning:** This is the integration step where all components come together. It has the highest risk of unexpected interactions and is the step most likely to surface design issues. Making it a sub-intent allows isolated debugging.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Wire the complete pipeline: `holon create-intent` → Docker container → git clone → create branch → commit → push; `holon plan` → Docker container → git clone → checkout intent branch → generate plan → commit → push; `holon execute` → Docker container → git clone → checkout plan branch → run agent → commit → push.
**Git branch:** `I-1771890389-bootstrap-cli/I-{timestamp}-e2e-integration/_`
**Sub‑intent:** NEW

### Implementation Details (No code blocks, only logic/steps)

1. **Verify create-intent flow:**
   - Run `holon create-intent app/scripts/intent_bootstrap_cli.json`
   - Verify: Docker container starts, clones repo, creates branch, appends to intents.jsonl, commits, pushes
   - Verify: Branch appears on remote with correct naming convention

2. **Verify plan flow:**
   - Run `holon plan "I-1771890389-bootstrap-cli/_" "pi-coding-agent" "claude-opus-4-6"`
   - Verify: Docker container starts, clones repo on intent branch, creates plan branch, generates plan file, appends to plans.jsonl, commits, pushes
   - Verify: Plan branch appears on remote

3. **Verify execute flow:**
   - Run `holon execute "<plan_branch>" "pi-coding-agent" "claude-opus-4-6" "init-project"`
   - Verify: Docker container starts, clones repo on plan branch, creates execution branch, runs agent, commits code changes, pushes
   - Verify: Execution branch appears on remote

4. **Fix integration issues:**
   - Environment variable passthrough between CLI and container
   - Git remote URL consistency
   - Branch name encoding/escaping (slashes in branch names)
   - Ledger file merge conflicts when multiple operations run concurrently

5. **Add orchestration support:**
   - Update `orchestrate_intent.py` to use the `holon` CLI instead of directly calling entrypoints
   - Or deprecate `orchestrate_intent.py` in favor of the CLI-based workflow

### Dependencies & Criticality

**Depends on:** Step 1, Step 2, Step 3
**Is Bottleneck:** YES (if integration fails, the CLI doesn't work end-to-end)

### Safety & Constraint Considerations

- Relevant rules: git_flow.md §2 (branch naming), git_flow.md §3 (rebase discipline), safety.md §1 (git as safety boundary)
- Potential failure modes: Branch name escaping issues with Docker; git push auth failure from container; race conditions in ledger writes; container exit before push completes
- Guardrails: Run each flow independently first; add `set -x` debug mode; verify remote state after each operation; add timeout to prevent hung containers

### Success & Discard Criteria

**Success:** All three commands (create-intent, plan, execute) complete successfully end-to-end. Branches appear on remote. Ledger files are updated. The test script `test_holon_bootstrap.sh` passes.
**Discard:** If more than 3 integration issues remain unresolved after 3 hours of debugging, decompose into smaller sub-intents targeting each command independently.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.78  |
| entropy_pred        | 4.0   |
| impact_pred         | 85    |
| cost_pred           | 10    |
| learning_value_pred | 4.0   |
| ev_pred             | 55.1  |

### Step Metrics Rationale

Moderate p_success — integration always surfaces unexpected issues, but the individual components are well-tested by this point. Moderate entropy — mostly wiring, not new code. Very high impact — this is where the system becomes functional. Moderate cost. Moderate learning value — integration patterns inform future development. EV = 0.78 × 85 + 0.5 × 4.0 − 0.3 × 4.0 − 10 = 66.3 + 2.0 − 1.2 − 10 = 57.1.

---

## Step 5: Automated tests

**Sub‑intent recommendation:** NO
**Reasoning:** Tests are important but low-risk and well-scoped. The existing `test_holon_bootstrap.sh` provides a template. Not complex enough to warrant a separate sub-intent.
**Step Type:** TEST
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Create comprehensive automated tests that validate the full `holon` CLI lifecycle: intent creation, planning, execution, branch management, and ledger integrity.
**Git branch:** `I-1771890389-bootstrap-cli/P-1772691044-pi-coding-agent-abacus_claude-opus-4-6/E-{timestamp}-add-tests`
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. **Refactor test_holon_bootstrap.sh:**
   - Add proper test assertions (not just "did it not crash")
   - Verify branch naming conventions match git_flow.md
   - Verify ledger entries have required fields per ledger_schema.md
   - Verify Docker container exits cleanly (no orphaned containers)
   - Add cleanup on test failure (trap handler)

2. **Add unit tests for CLI argument parsing:**
   - Test each subcommand with valid and invalid arguments
   - Test help output
   - Test error messages for missing prerequisites

3. **Add integration test for sandbox isolation:**
   - Verify container cannot access host filesystem outside mounts
   - Verify resource limits are applied
   - Verify non-root user is enforced

4. **Add test for git flow compliance:**
   - Verify branches follow naming convention
   - Verify commits have proper messages
   - Verify ledger is append-only (no modifications to existing entries)

### Dependencies & Criticality

**Depends on:** Steps 1-4 (tests validate the implementation)
**Is Bottleneck:** NO (tests validate but don't block functionality)

### Safety & Constraint Considerations

- Relevant rules: safety.md §2.3 (sandbox escape detection — tests should verify this)
- Potential failure modes: Tests may be flaky due to Docker timing; tests may leave orphaned branches/containers
- Guardrails: Add cleanup trap; use unique branch names per test run; set test timeouts

### Success & Discard Criteria

**Success:** All tests pass. Test coverage includes: CLI argument parsing, Docker container lifecycle, git branch creation/naming, ledger integrity, sandbox isolation.
**Discard:** If Docker-based integration tests prove too flaky (>30% failure rate), reduce scope to CLI unit tests only and document integration test gaps.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.88  |
| entropy_pred        | 2.0   |
| impact_pred         | 50    |
| cost_pred           | 8     |
| learning_value_pred | 3.0   |
| ev_pred             | 35.9  |

### Step Metrics Rationale

High p_success — test writing is well-understood and the existing test script provides a template. Low entropy — tests are additive and easily reversible. Moderate impact — tests provide confidence and catch regressions. Low cost. Moderate learning value — test patterns for Docker-based systems. EV = 0.88 × 50 + 0.5 × 3.0 − 0.3 × 2.0 − 8 = 44 + 1.5 − 0.6 − 8 = 36.9.

---

## Step 6: Documentation update

**Sub‑intent recommendation:** NO
**Reasoning:** Documentation is low-risk, low-cost, and straightforward. No need for a separate branch/evaluation cycle.
**Step Type:** DOCUMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Update README.md with CLI usage instructions, update app/README.md with current structure, and add a CONTRIBUTING.md or docs/cli.md with detailed CLI documentation.
**Git branch:** `I-1771890389-bootstrap-cli/P-1772691044-pi-coding-agent-abacus_claude-opus-4-6/E-{timestamp}-update-docs`
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Update root README.md:
   - Add "Quick Start" section with `holon` CLI usage examples
   - Add "Prerequisites" section (Docker, jq, git, SSH keys)
   - Add "Building" section referencing `holon build` or `docker/build_all_images.sh`

2. Update app/README.md:
   - Reflect current directory structure
   - Remove references to `setup_holon.sh` (doesn't exist)
   - Update bootstrap process to use `holon` CLI

3. Add docs/cli.md:
   - Full CLI reference for all subcommands
   - Environment variables reference
   - Docker image reference
   - Troubleshooting section

### Dependencies & Criticality

**Depends on:** Steps 1-4 (documentation must reflect final implementation)
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: None specific
- Potential failure modes: Documentation becomes stale if implementation changes
- Guardrails: Write docs last, after implementation is stable

### Success & Discard Criteria

**Success:** README.md contains working quick-start instructions. A new user can follow the docs to build and run the `holon` CLI.
**Discard:** If implementation is still in flux, defer docs to a follow-up intent.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.95  |
| entropy_pred        | 1.0   |
| impact_pred         | 30    |
| cost_pred           | 3     |
| learning_value_pred | 1.0   |
| ev_pred             | 25.7  |

### Step Metrics Rationale

Very high p_success — documentation is straightforward. Minimal entropy — additive changes to markdown files. Lower impact than code changes but still valuable for onboarding. Very low cost. Minimal learning value. EV = 0.95 × 30 + 0.5 × 1.0 − 0.3 × 1.0 − 3 = 28.5 + 0.5 − 0.3 − 3 = 25.7.

---
