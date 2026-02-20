# Plan for I-1771890389

**Plan ID:** P-1772691068-openai-codex-gpt-5.3-codex
**Parent Intent ID:** null
**Agent:** openai-codex/gpt-5.3-codex
**Created At:** 2026-03-05T06:11:08.6NZ

## Planner Autonomy Summary

- Intent handling: SPLIT
- Reframed intent (if applicable): Keep goal unchanged, but decompose into contract-first bootstrap + isolated runtime foundation + safety/merge compliance + validation so the CLI can reliably spawn future work.
- Exploration stance: balanced with one high-entropy validation slice. Most steps are exploitative implementation; one targeted exploratory stress-test is included to maximise learning around sandbox isolation failure modes.
- Safety priority level: critical
- Priority Justification: `docs/safety.md` defines sandboxing, git isolation, and trust boundaries as hard invariants; this intent directly touches all three and is a root capability that can amplify future blast radius if implemented incorrectly.

## Exploration

- Proportion of steps that are exploratory: 0.25
- Justification: Bootstrap infrastructure has unknowns around clone/checkout flow inside containerised isolation. Limited exploration is justified to reduce repeated future failures while preserving delivery speed.

## Overall Plan Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.71                  |
| entropy_pred        | 33.7                  |
| impact_pred         | 92                    |
| cost_pred           | 48                    |
| learning_value_pred | 7.4                   |
| ev_pred             | 11.6                  |

### Strategy Rationale

The strategy splits the intent into reusable sub-intents where risk and reusability are high (workspace isolation, orchestration contract, safety enforcement, and end-to-end validation). This minimises integration entropy while preserving forward progress toward the goal: autonomous task spawning. Overall metrics are derived using qualitative aggregation anchored by bottlenecks: Step 3 (self-clone + branch materialisation in sandbox) and Step 4 (CLI-orchestrator argument/flow contract) are primary success bottlenecks. Overall `p_success_pred` is constrained by those bottlenecks rather than averaged; overall entropy and cost are summed from step estimates; overall impact is capped near the maximum of major enabling steps with slight additive uplift for integration completeness; overall EV uses `EV = p*Impact + 0.5*Learning - 0.3*Entropy - Cost` from `docs/metrics.md`.

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan:
- `world/ruleset.md` (currently empty placeholder; no explicit project-local overrides found)
- `world/contraints.md` (currently empty placeholder; no explicit additional constraints found)
- `docs/safety.md` sandboxing, trust, entropy budget, and git-discipline invariants
- `docs/git_flow.md` parent-only merge and dual rebase rules
- Potential violations or edge cases:
- Branch naming mismatch (`/_` suffix duplication risk in `intent_creator.sh`)
- CLI/entrypoint argument mismatch (`holon execute` vs `executor.sh` signature)
- Inconsistent ledger path writes (`events.jsonl` vs `app/ledger/events.jsonl`)
- Unsafe assumptions about host-mounted credentials and remote clone failure modes
- Guardrails and early-abort checks:
- Enforce branch-shape validation before mutating git state
- Fail closed when target branch cannot be fetched/checked out inside sandbox
- Reject execution if pre/post rebase discipline cannot be satisfied
- Block merge promotion when required ledger events are missing
- Residual risk accepted (and why): Initial bootstrap may still rely on SSH key mounting for private clone access; accepted temporarily to unlock core capability, with explicit hardening follow-up.
- Allocated Entropy Budget: UNSPECIFIED in intent; provisional planning budget assumed at 40 pending explicit parent allocation
- Predicted Plan Entropy: 33.7
- Budget Compliance: The strategy fits within budget (under the provisional 40 assumption); if parent budget is lower, Step 7 should be deferred first.

## Plan Description & Strategy

Build a robust `holon` bootstrap path in four layers: contract, isolated execution substrate, safety-integrated orchestration, and validation. Start by freezing command and branch semantics to remove ambiguity. Then implement deterministic workspace materialisation in sandbox (fresh clone + exact branch checkout + immutable base assumptions), followed by strict orchestration contracts that align CLI arguments, role dispatch, and ledger writes. Add explicit git discipline and safety instrumentation before running hard end-to-end validation, including one exploratory stress slice to discover isolation edge cases early. Finalise with docs and operator guidance so future intents can reliably spawn sub-work in the same model.

---

## Step 1: Define CLI and Runtime Contract Baseline

**Sub‑intent recommendation:** NO
**Reasoning:** Small but mandatory alignment step; low implementation risk and high leverage for downstream clarity.
**Step Type:** INFO_GATHERING
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Freeze the authoritative command contract for `holon` bootstrap (`create-intent`, `plan`, `execute`) and normalise branch/ledger/path semantics before implementation changes.
**Git branch:** I-1771890389-bootstrap-cli/P-1772691068-openai-codex-gpt-5.3-codex/E-1772691068-contract-baseline
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

Audit current wrapper and entrypoints to enumerate argument signatures and path assumptions.
Document canonical mapping from CLI args to role dispatcher and role-specific scripts.
Define branch-shape rules for intent/plan/execution paths, including `/_` handling to prevent suffix duplication.
Define required ledger write locations and event minimums for create/plan/execute phases.
Record acceptance criteria that all later steps must satisfy.

### Dependencies & Criticality

**Depends on:** NONE
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (Git as safety boundary, sandboxing mandatory), `docs/git_flow.md` (branch naming, merge discipline)
- Potential failure modes for this step:
- Contract remains ambiguous and downstream changes diverge
- Existing subtle mismatches are missed and become latent failures
- Guardrails and early‑abort checks:
- Abort planning branch if branch format and CLI signature cannot be made internally consistent
- Require explicit acceptance checklist before moving to Step 2

### Success & Discard Criteria

**Success:** A single unambiguous contract exists for commands, branch naming, ledger paths, and role arguments.
**Discard:** Stop if unresolved contradictions remain between docs and executable scripts after one reconciliation pass.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.96                  |
| entropy_pred        | 1.8                   |
| impact_pred         | 35                    |
| cost_pred           | 3                     |
| learning_value_pred | 4.0                   |
| ev_pred             | 32.5                  |

### Step Metrics Rationale

High success and low entropy because this is predominantly analysis and specification. Impact is moderate due to defect-prevention leverage across all later implementation steps.

---

## Step 2: Normalise `holon` CLI Surface and Invocation Semantics

**Sub‑intent recommendation:** YES
**Reasoning:** Reusable command-surface work with medium integration risk; isolation into a sub-intent simplifies rollback if command contracts break existing flows.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Ensure the user-facing tool is `holon`, exposes stable subcommands, and forwards validated arguments to containerised role execution.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691201-normalise-holon-cli/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Refactor command parsing so `holon` is the single canonical entrypoint and command names match docs/examples.
Validate argument counts and structured error messaging per subcommand.
Unify `execute` argument structure with executor expectations, eliminating current arity mismatch.
Pin deterministic container invocation flags for isolation and reproducibility.
Ensure intent JSON mounting behaviour is explicit and safe for `create-intent`.

### Dependencies & Criticality

**Depends on:** Step 1
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` sandboxing mandatory, trust boundary; `docs/examples.md` command expectations
- Potential failure modes for this step:
- Backward-incompatible CLI changes break bootstrap scripts
- Wrapper still leaks inconsistent runtime assumptions into entrypoints
- Guardrails and early‑abort checks:
- Add compatibility checks against existing bootstrap test workflow
- Fail fast on invalid command signature before container startup

### Success & Discard Criteria

**Success:** `holon` command layer consistently invokes intended role with validated parameters and no signature ambiguity.
**Discard:** Abort if command normalisation introduces unresolved incompatibility with required root workflow.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.82                  |
| entropy_pred        | 4.9                   |
| impact_pred         | 72                    |
| cost_pred           | 7                     |
| learning_value_pred | 5.0                   |
| ev_pred             | 52.0                  |

### Step Metrics Rationale

Moderate entropy due to interface changes across wrapper and automation scripts. High impact because this creates the operator interface for all future intent spawning.

---

## Step 3: Implement Deterministic Sandbox Workspace Materialisation

**Sub‑intent recommendation:** STRONGLY_YES
**Reasoning:** High-risk, high-reusability foundation; failure blocks the core intent goal and affects all future autonomous executions.
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: A containerised role can safely clone a fresh repo copy and checkout exact intent/plan/execution branches without relying on mutable host workspace state.
- Learning target: Identify edge cases in remote auth, shallow clone behaviour, and branch materialisation under isolated runtime constraints.
- Maximum acceptable cost for this learning: Medium-high; up to 1.3x planned cost is acceptable because this is a platform bottleneck.

### Intent & Git Integration

**Step Intent:** Build a reliable per-run sandbox workspace bootstrap path that clones repository state and checks out the correct branch lineage for each role.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691202-sandbox-workspace-bootstrap/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Centralise clone/checkout logic shared by intent creator, planner, and executor entrypoints.
Guarantee clean workspace initialisation for each invocation and eliminate implicit dependence on previous runs.
Validate branch existence and lineage before checkout; provide explicit fallback/error behaviour when branch is missing.
Resolve `/_` suffix handling consistently so input branch values do not duplicate or truncate hierarchy.
Standardise repository remote configuration and shallow/full clone policy based on operation needs.
Emit structured runtime metadata for workspace root, checked-out ref, and source remote.

### Dependencies & Criticality

**Depends on:** Step 1
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` sandboxing model and git isolation; `docs/git_flow.md` branch hierarchy and rebase discipline
- Potential failure modes for this step:
- Wrong branch checkout causes cross-intent contamination
- Clone fails in isolated environment, making system non-operational
- Incomplete cleanup leaks state across runs
- Guardrails and early‑abort checks:
- Abort before write operations if expected ref does not resolve to remote branch
- Abort if workspace path escapes allowed root
- Abort if clone/checkout produces detached or ambiguous branch state

### Success & Discard Criteria

**Success:** Each role can start from an empty sandbox, clone the repo, checkout the intended branch deterministically, and proceed with no host-state dependency.
**Discard:** Abort when branch resolution fails repeatedly or checkout behaviour is nondeterministic across repeated runs.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.63                  |
| entropy_pred        | 8.4                   |
| impact_pred         | 95                    |
| cost_pred           | 11                    |
| learning_value_pred | 8.5                   |
| ev_pred             | 50.4                  |

### Step Metrics Rationale

Lower success probability reflects integration and environment dependencies. Entropy is high due to git/runtime boundary complexity. Learning value is high because failure data here materially improves future autonomous reliability.

---

## Step 4: Repair Role Orchestration and Ledger Contract

**Sub‑intent recommendation:** STRONGLY_YES
**Reasoning:** Large integration surface and direct correctness risk; reusable by all future intents and a likely source of cascading failures if not isolated.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Align wrapper, role dispatcher, and role entrypoints so arguments, ledger writes, and commit flows are consistent and auditable.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691203-orchestration-contract-fix/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Unify expected argument order between CLI wrapper and `executor.sh`/`planner.sh`/`intent_creator.sh`.
Correct ledger path usage to consistently target `app/ledger/*.jsonl` and include required fields.
Standardise role-specific git identity, commit message structure, and push behaviour.
Ensure dispatcher default behaviour does not accidentally run arbitrary commands in production workflows.
Add deterministic failure propagation so container exit codes map cleanly to CLI outcomes.

### Dependencies & Criticality

**Depends on:** Step 1, Step 2, Step 3
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` append-only auditability expectations, sandbox boundaries; `docs/ledger_schema.md` event integrity
- Potential failure modes for this step:
- Silent partial failures leave branch state inconsistent with ledger
- Incorrect ledger paths break observability and calibration
- Dispatcher fallback enables unsafe invocation paths
- Guardrails and early‑abort checks:
- Require atomic role completion criteria (branch mutation + ledger event + commit)
- Abort and emit explicit error if any required ledger write fails

### Success & Discard Criteria

**Success:** End-to-end role invocations produce correct branch mutations and ledger artifacts with consistent argument semantics.
**Discard:** Stop if any role can mutate git state without corresponding ledger trace.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.66                  |
| entropy_pred        | 7.1                   |
| impact_pred         | 90                    |
| cost_pred           | 10                    |
| learning_value_pred | 7.5                   |
| ev_pred             | 50.6                  |

### Step Metrics Rationale

This is a high-risk integration bottleneck with broad systemic effect; success probability is moderate, while impact and learning value are both high.

---

## Step 5: Enforce Git Discipline and Safety Gates in Execution Path

**Sub‑intent recommendation:** YES
**Reasoning:** Policy-critical and reusable, with moderate risk; isolating this as a sub-intent supports independent evaluation and safer rollout.
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: Embedding explicit pre/post rebase and parent-merge rules in execution flow will materially reduce conflict entropy and unsafe merges.
- Learning target: Measure where automated rebase policy fails under realistic branch topology.
- Maximum acceptable cost for this learning: Medium; do not exceed planned cost by more than 20%.

### Intent & Git Integration

**Step Intent:** Apply mandatory rebase checks, parent-only merge boundaries, and safety aborts before promotion actions.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691204-git-safety-gates/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Add pre-execution rebase from immediate parent branch and enforce clean state before action execution.
Add post-execution rebase before merge attempts and block merge on unresolved conflicts.
Reject direct merge attempts from sub-intent to `main` by construction.
Emit ledger events for rebase attempts, conflicts, and gate decisions.
Tie gate outcomes to clear CLI exit behaviour for operator visibility.

### Dependencies & Criticality

**Depends on:** Step 3, Step 4
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/git_flow.md` dual rebase and merge constraints; `docs/safety.md` Git discipline invariant
- Potential failure modes for this step:
- Gate logic deadlocks normal flow on benign branch states
- Missing parent detection causes false policy violations
- Guardrails and early‑abort checks:
- Explicit parent-branch derivation validation from branch path
- Escape hatch limited to human-reviewed override intent (not default flow)

### Success & Discard Criteria

**Success:** Execution pipeline consistently enforces rebase and merge policy with observable ledger traces and safe failure modes.
**Discard:** Stop if policy automation cannot determine parent branch reliably from branch topology.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.74                  |
| entropy_pred        | 4.6                   |
| impact_pred         | 82                    |
| cost_pred           | 6                     |
| learning_value_pred | 6.0                   |
| ev_pred             | 56.7                  |

### Step Metrics Rationale

Balanced step with moderate novelty around automated rebase behaviour. Strong impact due to direct reduction in merge and governance risk.

---

## Step 6: Add Safety and Sandbox Observability Events

**Sub‑intent recommendation:** NO
**Reasoning:** Medium-small implementation with low standalone risk; tightly coupled to execution path and can be done on the same execution branch as Step 5.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Improve safety observability by emitting sandbox lifecycle, policy violation, and trust-relevant events needed for future calibration.
**Git branch:** I-1771890389-bootstrap-cli/P-1772691068-openai-codex-gpt-5.3-codex/E-1772691205-safety-observability
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

Emit `sandbox_created`, `sandbox_violation`, and relevant execution lifecycle events with stable schemas.
Capture clone/checkout/rebase failure reasons as structured fields, not only plain text logs.
Ensure events append to ledger atomically and preserve append-only semantics.
Add minimal validation for required event fields at write time.

### Dependencies & Criticality

**Depends on:** Step 4, Step 5
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` sandbox escape detection and monitoring; `docs/ledger_schema.md` event semantics
- Potential failure modes for this step:
- Event schema drift reduces future calibration utility
- Excessive logging leaks sensitive runtime details
- Guardrails and early‑abort checks:
- Validate event schema against documented required keys
- Redact secrets/tokens from emitted diagnostic fields

### Success & Discard Criteria

**Success:** Execution produces a complete, schema-consistent safety trace enabling trust and calibration workflows.
**Discard:** Abort if event logging cannot be made append-only and deterministic.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.84                  |
| entropy_pred        | 2.8                   |
| impact_pred         | 58                    |
| cost_pred           | 4                     |
| learning_value_pred | 6.5                   |
| ev_pred             | 47.0                  |

### Step Metrics Rationale

Low-to-moderate entropy and high success probability; impact is moderate because this is enabling observability rather than core behaviour change.

---

## Step 7: Execute E2E and Exploratory Isolation Stress Validation

**Sub‑intent recommendation:** YES
**Reasoning:** High test complexity and reusable across future intents; exploratory and potentially time-consuming, so independent execution/evaluation is valuable.
**Step Type:** TEST
**Exploration level:** EXPLORATORY

- Hypothesis being tested: The bootstrap CLI remains correct under adverse but realistic conditions (missing branch, stale refs, shallow clone constraints, credential unavailability, repeated sandbox runs).
- Learning target: Discover failure clusters early and codify mitigations for future autonomous spawning reliability.
- Maximum acceptable cost for this learning: High but bounded; up to 1.5x planned test cost if new high-value failure modes are discovered.

### Intent & Git Integration

**Step Intent:** Validate happy-path and adversarial scenarios in sandbox to prove the system can reliably spawn future tasks.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691206-bootstrap-e2e-validation/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Expand bootstrap test coverage to include create/plan/execute lifecycle in clean containers.
Add adversarial tests for branch-not-found, malformed branch path, and clone/auth degradation.
Validate that each run starts from fresh workspace state and cannot read/write outside intended mount points.
Verify ledger completeness after success and failure paths.
Use repeat-run checks to detect nondeterminism and flaky orchestration behaviour.

### Dependencies & Criticality

**Depends on:** Step 2, Step 3, Step 4, Step 5, Step 6
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` sandboxing, failure containment, monitoring alerts
- Potential failure modes for this step:
- False confidence from shallow happy-path coverage
- Test harness mutates host repo state unexpectedly
- Exploratory cases consume excessive entropy/cost without actionable learning
- Guardrails and early‑abort checks:
- Run in disposable branches/workspaces only
- Stop exploratory expansion when marginal learning value drops below threshold
- Enforce explicit pass/fail gates tied to core invariants

### Success & Discard Criteria

**Success:** Reproducible evidence that `holon` can spawn lifecycle tasks in sandboxed clones with correct branch and ledger behaviour across both nominal and adverse cases.
**Discard:** Stop if exploratory cost exceeds threshold without uncovering actionable failure modes.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.57                  |
| entropy_pred        | 3.9                   |
| impact_pred         | 78                    |
| cost_pred           | 6                     |
| learning_value_pred | 9.0                   |
| ev_pred             | 40.6                  |

### Step Metrics Rationale

Lower success prediction reflects intentional adversarial testing and discovery risk. Learning value is very high by design, which justifies exploratory cost.

---

## Step 8: Document Operational Playbook and Promotion Checklist

**Sub‑intent recommendation:** NO
**Reasoning:** Small, low-risk finalisation step; best kept close to integrated execution result to avoid documentation drift.
**Step Type:** DOCUMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Provide clear operator documentation for bootstrap usage, constraints, and merge-review evidence expected at root intent boundary.
**Git branch:** I-1771890389-bootstrap-cli/P-1772691068-openai-codex-gpt-5.3-codex/E-1772691207-docs-and-checklist
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

Update docs with canonical `holon` command usage and argument contracts.
Document sandbox assumptions, branch topology requirements, and failure handling guidance.
Add reviewer checklist mapping safety invariants to observable artifacts (tests, ledger events, branch graph).
Include troubleshooting matrix for top bootstrap failure classes discovered in Step 7.

### Dependencies & Criticality

**Depends on:** Step 7
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` human review boundary and invariants; `docs/git_flow.md` merge requirements
- Potential failure modes for this step:
- Docs diverge from implementation and mislead future operators
- Missing checklist items weaken root-intent human review quality
- Guardrails and early‑abort checks:
- Tie checklist entries directly to test artifacts and ledger evidence
- Require doc examples to match validated CLI signatures

### Success & Discard Criteria

**Success:** Documentation accurately reflects the implemented bootstrap flow and enables consistent human review decisions.
**Discard:** Stop if docs cannot be validated against implemented behaviour.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.91                  |
| entropy_pred        | 0.2                   |
| impact_pred         | 32                    |
| cost_pred           | 1                     |
| learning_value_pred | 3.0                   |
| ev_pred             | 29.6                  |

### Step Metrics Rationale

Very high success and low entropy due to limited scope; impact is supportive but important for governance and repeatable operations.

---
