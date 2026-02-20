# Plan for I-1771890389

**Plan ID:** P-1772691637-openai-codex-gpt-5.1-codex-mini
**Parent Intent ID:** null
**Agent:** openai-codex/gpt-5.1-codex-mini
**Created At:** 2026-03-05T07:10:00.0NZ

## Planner Autonomy Summary

- Intent handling: SPLIT
- Reframed intent (if applicable): Root goal preserved; decomposed the bootstrap CLI work into contract stabilisation, CLI surface hardening, sandbox/bootstrap plumbing, execution orchestration, safety policy controls, and validation because each core capability has distinct risk/learning profiles and deserves targeted instrumentation.
- Exploration stance: balanced with explicit exploratory probes around sandbox determinism and failure-mode validation to grow future estimator accuracy while still prioritising production-grade CLI behaviour.
- Safety priority level: elevated
- Priority Justification: `docs/safety.md` enforces sandbox-only execution, strict git isolation, entropy budgets, and human review boundaries; this intent bootstraps the CLI that will spawn downstream intents, so any regression has outsised systemic impact.

## Exploration

- Proportion of steps that are exploratory: 0.43
- Justification: Three of seven steps (sandbox bootstrap, execution runtime hardening, validation matrix) are tagged BALANCED/EXPLORATORY to surface unknowns in deterministic cloning and runtime branching while the rest exploit established operational patterns.

## Overall Plan Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.58                  |
| entropy_pred        | 41.2                  |
| impact_pred         | 90                    |
| cost_pred           | 32                    |
| learning_value_pred | 6.8                   |
| ev_pred             | 15.9                  |

### Strategy Rationale

By splitting the work, we keep the contract, CLI surface, sandbox init, execution orchestration, safety automation, and validation loops each on their own branches while still converging to the ultimate holon CLI capability. Overall metrics use a bottleneck-aware aggregation: `p_success_pred` reflects the lowest-confidence critical implementation steps (3–5), `entropy_pred` is the sum of step entropies since risks compound, `impact_pred` stays at the high end because delivering a safe autonomous CLI unlocks future agentic work, `cost_pred` is reduced from the raw sum via parallelizable sub-intent assumptions, `learning_value_pred` tracks the mean of exploratory steps, and `ev_pred` applies `EV = P(success)·Impact + 0.5·LearningValue - 0.3·Entropy - Cost` from `docs/metrics.md` against the aggregated numbers, yielding positive EV because sandbox determinism plus safety gating outweigh the entropy/cost.

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan:
  - `world/ruleset.md` (basic git discipline and constraints headings exist even if empty)
  - `world/contraints.md` (same)
  - `docs/safety.md` (sandbox mandate, git isolation, entropy budgeting, trust gating, failure containment)
  - `docs/git_flow.md` (implicit in git isolation requirement: dual rebases, parent-only merges, branch naming)
- Potential violations or edge cases:
  - Container needs to clone the repo; uncontrolled network usage may violate sandbox assumptions if not documented.
  - New CLI automation might accidentally create branches outside the intent hierarchy or push directly to `main`.
  - Ledger writes could be inconsistent across roles if ledger paths remain ambiguous.
- Mitigations built into the plan:
  - Explicit documentation and gating for allowed network operations, plus staged clones that drop network after fetching origin.
  - Branch normalisation logic aligned to `I-*/_*` naming and forced parent rebase checks before pushing.
  - Shared ledger path constants and pre-flight validation that all roles append to the same files.
- Residual risk accepted (and why): Remote cloning still requires network access for the initial bootstrap; we accept that risk because the CLI cannot materialise intent branches without a remote origin, but we cap entropy downstream by isolating the clone phase.
- Allocated Entropy Budget: UNSPECIFIED (assume at least 50 given root-level intent; confirm before execution).
- Predicted Plan Entropy: 41.2
- Budget Compliance: The strategy fits within the assumed budget (41.2 < 50); if the official allocation is lower, deprioritise the exploratory validation suite (Step 7) and re-calibrate.

## Plan Description & Strategy

Deliver a trustworthy `holon` CLI that can be invoked both locally and inside the mandated container sandbox. Start by freezing contracts (commands, branches, ledger paths), then harden the CLI surface, bootstrap deterministic sandbox cloning and branching, orchestrate execution roles with precise branch/ledger behaviour, add safety/policy gates, and finally validate/document the loop so future intent spawning inherits a reproducible foundation.

---

## Step 1: Contract Mapping and Ambiguity Resolution

**Sub‑intent recommendation:** NO
**Reasoning:** Minimal state mutation; purely informational and necessary to avoid misaligned implementation.
**Step Type:** INFO_GATHERING
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Identify the actual CLI contracts (commands, args, branch expectations, ledger locations) that the current shim scripts, docs, and orchestrator enforce.
**Git branch:** I-1771890389-bootstrap-cli/P-1772691637-openai-codex-gpt-5.1-codex-mini/E-1772691637-contract-audit
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

- Inventory existing entrypoints, orchestrator flows, and CLI wrapper behaviour to understand what currently happens versus desired behaviour in the intent description.
- Confirm branch naming (especially `/I-*/_/` suffixes), ledger file targets (`app/ledger/*.jsonl` vs root `events.jsonl`), and expected file locations after sandboxed execution.
- Capture the canonical command signatures for `create-intent`, `plan`, `execute`, and the new CLI role logic, then publish a short checklist the subsequent steps must satisfy before touching code.

### Dependencies & Criticality

**Depends on:** NONE
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (git/sandbox boundaries), `docs/git_flow.md` (branch hierarchy)
- Potential failure modes for this step:
  - Misinterpreting current behaviour and propagating incorrect assumptions.
  - Overlooking existing ledger conventions, leading to inconsistent documentation.
- Guardrails and early‑abort checks:
  - Stop before implementation begins until the checklist is reviewed by another agent or documented for redundant verification.

### Success & Discard Criteria

**Success:** Produce an agreed-upon matrix of CLI commands, branch names, and ledger paths with no open contradictions.
**Discard:** Abandon deeper work until outstanding contradictions are resolved or more data is gathered.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.95                  |
| entropy_pred        | 1.2                   |
| impact_pred         | 25                    |
| cost_pred           | 1.5                   |
| learning_value_pred | 3.8                   |
| ev_pred             | 22.0                  |

### Step Metrics Rationale

High success and low entropy because this is a bounded audit; moderate impact and EV stem from preventing downstream misalignment.

---

## Step 2: Stabilise the `holon` CLI Surface

**Sub‑intent recommendation:** YES
**Reasoning:** The CLI surface is the future interface for every intent creation; isolating it in its own branch allows independent validation and rollback.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Make `holon` the deterministic entrypoint with validated argument parsing, help text, and container role dispatch without touching `holon-cli` artifacts.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691638-cli-surface/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Update `holon` to parse commands/args, validate required payloads, give precise error messages, and produce help text aligned with documented contracts.
- Factor `run_in_container` (or equivalent) so it can be re-used by future `holon` commands without duplicating env handling and ensures SSH keys/mounts behave consistently.
- Ensure CLI never references uncontrolled `holon-cli` names and that container role selection maps directly to orchestrator entrypoints plus eventual sandbox bootstrap logic.

### Dependencies & Criticality

**Depends on:** Step 1
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (sandbox invocation must be explicit, no stray environment escapes).
- Potential failure modes for this step:
  - New CLI signature deviates from orchestrator expectations causing runtime failures.
  - Path/role combinations allow commands to mutate unauthorised areas.
- Guardrails and early‑abort checks:
  - Validate CLI parsing with unit tests that run the wrapper (without executing docker) to ensure argument flows are predictable.

### Success & Discard Criteria

**Success:** `holon` provides stable help text, enforces argument counts, and routes requests through a shared container runner.
**Discard:** Stop and revert if container role dispatch becomes ambiguous or misaligns with documented contracts.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.85                  |
| entropy_pred        | 4.0                   |
| impact_pred         | 70                    |
| cost_pred           | 4                     |
| learning_value_pred | 4.2                   |
| ev_pred             | 56.0                  |

### Step Metrics Rationale

Moderate entropy due to CLI/entrypoint touch points; high impact because this command is the control plane for every future intent.

---

## Step 3: Deterministic Sandbox Workspace Bootstrap

**Sub‑intent recommendation:** STRONGLY_YES
**Reasoning:** This is a foundational bottleneck for reproducible CLI execution; isolating it lets us stress-test clone/branch behaviour without contaminating other work.
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: A containerised role can clone the repo, enforce branch lineage, and drop to a clean workspace reproducibly even when run multiple times or on different machines.
- Learning target: Discover failure modes in branch resolution, git auth handling, and workspace cleanup that currently manifest as nondeterministic results.
- Maximum acceptable cost for this learning: 1.3x the expected step cost because deterministic cloning is critical for trust and cannot be deferred.

### Intent & Git Integration

**Step Intent:** Build reusable sandbox bootstrap logic that clones the repository, checks out the exact intent/plan/execution branch, and exposes metadata to invoking roles.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691639-sandbox-init/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Create shared bootstrap code (bash script or Python helper) invoked by every role to clone the canonical repository, fetch required refs, and verify the requested branch before execution.
- Enforce normalisation rules (strip trailing `/_`, re-attach expected suffixes, refuse to push to `main`, check parent branch ancestry) and emit structured metadata (cloned URL, checked-out SHA, workspace path).
- Harden workspace cleanup so successive runs start from a known state (remove /tmp artifacts, limit mounts, enforce `git status` clean before mutations).

### Dependencies & Criticality

**Depends on:** Steps 1, 2
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md#Sandbox selection policy` (sandbox must do network-limited clone), `docs/git_flow.md` (parent rebase requirements).
- Potential failure modes for this step:
  - Clone fails over the network or leaves remnant credentials in container.
  - Branch checkout resolves to the wrong ref/parent lineage, invalidating future merges.
  - Workspace cleanup is incomplete, leading to unexpected sandbox state corruption.
- Guardrails and early‑abort checks:
  - Abort before mutating the workspace if branch validation fails (`git rev-parse` mismatch or HEAD not on expected ref).
  - After clone, run `git status --short` and abort if the working tree is dirty.

### Success & Discard Criteria

**Success:** Every role begins from a clean clone anchored on the expected branch and emits metadata proving it, while failing fast on mis-specified refs.
**Discard:** Stop and revert this sub-intent if deterministic checkout cannot be achieved after two iterations.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.62                  |
| entropy_pred        | 9.0                   |
| impact_pred         | 95                    |
| cost_pred           | 9                     |
| learning_value_pred | 8.5                   |
| ev_pred             | 51.0                  |

### Step Metrics Rationale

Lower success probability reflects infra variability; high learning value arises from surfacing edge cases around branch resolution and workspace hygiene.

---

## Step 4: Holon-Orchestrated Execution Contract

**Sub‑intent recommendation:** YES
**Reasoning:** Execution orchestration touches ledger, branch creation, and agent metadata; isolating it avoids regressing existing lifecycle data.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Align `holon execute` with orchestrator logic so the CLI can spawn plan/execution branches inside the sandbox while keeping ledger writes consistent and traceable.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691640-command-orchestration/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Wire `holon execute` through the new sandbox bootstrap helper so the execution role derives the correct plan branch, creates an `E-*` branch, and records `exec` events in `app/ledger/events.jsonl` with canonical schema.
- Ensure execution branch naming follows the hierarchical pattern and that cloning/orchestrator steps enforce parent ancestry checks (plan -> intent -> main).
- Capture metadata (agent, model, action slug, origin branch, checked-out SHA) and return it to the caller for logging/monitoring.

### Dependencies & Criticality

**Depends on:** Steps 2, 3
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (append-only ledger, sandbox isolation), `docs/git_flow.md` (execution branches only merge to plan branch, not main).
- Potential failure modes for this step:
  - Ledger writes race or get lost if file paths aren't shared across roles.
  - Execution branches might accidentally be created off `main` if parent lineage validation fails.
  - Execution metadata is incomplete, preventing traceability.
- Guardrails and early‑abort checks:
  - Validate branch ancestry before commit and abort if parent branch does not exist locally.
  - Reject execution if `ACTION_SLUG` or other required metadata is missing or malformed.

### Success & Discard Criteria

**Success:** Execution branch creation, code mutation (placeholder or real), and ledger logging happen deterministically with canonical metadata.
**Discard:** Abort if the branch ancestry or ledger schema cannot be satisfied after multiple attempts.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.60                  |
| entropy_pred        | 10.0                  |
| impact_pred         | 90                    |
| cost_pred           | 10                    |
| learning_value_pred | 7.5                   |
| ev_pred             | 44.0                  |

### Step Metrics Rationale

This is a high-integration step with moderate success confidence; EV remains positive because execution correctness unlocks autonomous task creation.

---

## Step 5: Execution Runtime Hardening and Metadata

**Sub‑intent recommendation:** YES
**Reasoning:** Hardening the executor is reusable for every future action and worth its own branch to calibrate runtime behaviour.
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: The executor can run in the isolated sandbox, respect workspace boundaries, and produce action artifacts (code, events) that pass downstream reviews without manual cleanup.
- Learning target: Identify failure conditions around action slugs, dirty worktrees, and metadata emission that could derail future autonomous runs.
- Maximum acceptable cost for this learning: 1.2x of the expected step cost because this path is critical for enabling future intents with acceptable trust profiles.

### Intent & Git Integration

**Step Intent:** Harden the execution role so it records structured metadata, validates action slugs, and cleans artifacts before publishing execution branches.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691641-execution-runtime/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Validate action slug inputs and guard against directory traversal or missing plans before mutating the workspace.
- Improve metadata logging (timestamps, success flags, delta metrics) into the ledger so downstream evaluators can compute success/entropy.
- Ensure the runtime removes temporary files, runs `git status` before commits, and surfaces failure diagnostics to the caller.

### Dependencies & Criticality

**Depends on:** Steps 3, 4
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (failure containment, metadata for trust), `docs/git_flow.md` (execution branches commit only intended files).
- Potential failure modes for this step:
  - Dirty workspace commits slip into execution branch, causing future conflicts.
  - Missing diagnostics make bounding-box debugging impossible.
- Guardrails and early‑abort checks:
  - Abort on `git status --porcelain` if there are staged changes beyond the expected ones.
  - Emit structured failure events if metadata cannot be written.

### Success & Discard Criteria

**Success:** Execution runs complete with clean artifacts and ledger metadata; downstream evaluators can compute success and entropy.
**Discard:** Stop if instrumentation cannot guarantee workspace cleanliness or metadata completeness.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.57                  |
| entropy_pred        | 8.5                   |
| impact_pred         | 85                    |
| cost_pred           | 8                     |
| learning_value_pred | 8.0                   |
| ev_pred             | 42.0                  |

### Step Metrics Rationale

Entropy is high because the executor touches runtime boundaries; learning value is high as we calibrate failure-handling metadata.

---

## Step 6: Safety and Policy Gates

**Sub‑intent recommendation:** YES
**Reasoning:** Enforcing sandbox/network/git policies is reusable and compliance-critical; manage it on an isolated branch to avoid blocking lower-risk work.
**Step Type:** CONFIG
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Add guardrails for allowed mounts, network usage epochs, credential exposure, and pre/post parent rebase validation so the CLI cannot violate `docs/safety.md` invariants.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691642-safety-gates/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Extend sandboxes to document when network access is permitted (clone phase only) and ensure execution phases have explicit NO_NETWORK policies after cloning.
- Check branch ancestry before pushing and enforce pre/post execution rebases to prevent merges with stale parent state.
- Limit mounted secrets/ssh keys and log policy violations as structured telemetry events (to support guardrail automation in future).

### Dependencies & Criticality

**Depends on:** Steps 3, 4, 5
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (entropy budgets, sandbox escape handling, trust scoring), `docs/git_flow.md` (dual rebase)
- Potential failure modes for this step:
  - Policy checks become too brittle, blocking valid operations.
  - Logging misses violations, hiding safety breaches.
- Guardrails and early‑abort checks:
  - Provide a configuration toggle to relax non-critical policies temporarily during debugging with explicit logging.

### Success & Discard Criteria

**Success:** Sandbox/network/git policies are enforced without false positives, and violations emit structured diagnostics.
**Discard:** Back out policy gates if they repeatedly block valid flows for more than one business day.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.71                  |
| entropy_pred        | 5.5                   |
| impact_pred         | 70                    |
| cost_pred           | 6                     |
| learning_value_pred | 5.8                   |
| ev_pred             | 45.0                  |

### Step Metrics Rationale

Lower entropy because this is mostly policy validation and gating; impact remains high due to compliance gains.

---

## Step 7: End-to-End Validation Matrix and Documentation

**Sub‑intent recommendation:** YES
**Reasoning:** Large, reusable test suite and documentation bundle that should be validated independently before merging parent intent.
**Step Type:** TEST
**Exploration level:** EXPLORATORY

- Hypothesis being tested: The full create-intent → plan → execute lifecycle works in the isolated sandbox and behaves well under nominal and adversarial edge cases.
- Learning target: Capture failure modes (branch conflicts, missing refs, corrupted intent payloads) to improve future estimators and calibrate entropy budgets.
- Maximum acceptable cost for this learning: 1.25x expected step cost to keep the verification loop manageable while still exercising high-entropy paths.

### Intent & Git Integration

**Step Intent:** Build deterministic integration tests plus exploratory edge cases, document the final CLI contract, and package evidence for human review.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691643-validation/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Define a matrix covering happy-path commands, branch lineage checks, ledger writes, and failure injections (missing action slug, invalid branch, policy violations).
- Automate the validation matrix inside the sandbox, capturing logs/metrics for each scenario and recording any deviations for the ledger.
- Update documentation (README, doc bits) to describe the runtime contract, known limitations, and required safety steps for the new CLI.

### Dependencies & Criticality

**Depends on:** Steps 2–6
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (exploration allowances, entropy monitoring), `docs/git_flow.md` (branch shaping for tests)
- Potential failure modes for this step:
  - Tests fail intermittently due to nondeterminism in cloning or branch creation.
  - Documentation lags actual behaviour, misleading future agents.
- Guardrails and early‑abort checks:
  - Cap exploratory trials per test run to keep entropy below budget (e.g., limit to three high-risk cases).

### Success & Discard Criteria

**Success:** Test matrix runs reliably with documented failure boundaries and supporting docs prepared for review.
**Discard:** Stop if exploratory cases consume too much time/entropy without new learning after two iterations.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.88                  |
| entropy_pred        | 3.2                   |
| impact_pred         | 50                    |
| cost_pred           | 4                     |
| learning_value_pred | 6.5                   |
| ev_pred             | 42.0                  |

### Step Metrics Rationale

Lower entropy and high p_success because the verification suite focuses on well-understood scenarios; learning value remains due to the curated failure catalogue.

---
