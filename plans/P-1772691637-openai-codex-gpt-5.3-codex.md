# Plan for I-1771890389

**Plan ID:** P-1772691637-openai-codex-gpt-5.3-codex
**Parent Intent ID:** null
**Agent:** openai-codex/gpt-5.3-codex
**Created At:** 2026-03-05T06:20:37.6NZ

## Planner Autonomy Summary

- Intent handling: SPLIT
- Reframed intent (if applicable): Keep the intent goal unchanged, but decompose into contract hardening, sandbox bootstrap reliability, orchestration correctness, and validation tracks to maximise EV and reduce systemic bootstrap risk.
- Exploration stance: balanced with targeted exploration. Most steps exploit known repository patterns, while one explicit failure-injection step is exploratory to harvest high-value learning for future autonomous spawning.
- Safety priority level: critical
- Priority Justification: `docs/safety.md` defines git isolation, sandboxing, and trust boundaries as hard invariants; this intent creates the mechanism that can spawn future work, so defects amplify blast radius.

## Exploration

- Proportion of steps that are exploratory: 0.25
- Justification: Two of eight steps are BALANCED/EXPLORATORY to reduce uncertainty around clone/checkout behaviour in isolated runtime and to improve future estimator calibration.

## Overall Plan Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.59                  |
| entropy_pred        | 42.6                  |
| impact_pred         | 98                    |
| cost_pred           | 40                    |
| learning_value_pred | 7.6                   |
| ev_pred             | 8.8                   |

### Strategy Rationale

The codebase already has a `holon` wrapper and role entrypoints, but there are correctness gaps that lower EV if handled monolithically: `create-intent` unconditionally appends `/_` to branch input, `execute` argument contracts are inconsistent between wrapper and executor, and ledger path usage diverges (`app/ledger/events.jsonl` vs `events.jsonl`). Splitting into focused sub-intents yields better rollback boundaries and cleaner evaluation while keeping the root goal intact.

Overall metrics were derived with bottleneck-aware aggregation. `p_success_pred` is constrained by the critical path (Steps 3, 5, and 7). `entropy_pred` is the sum of step entropies. `impact_pred` is capped near the highest enabling capability with integration uplift, not simple sum. `cost_pred` is critical-path weighted rather than strict sum due to potential sub-intent parallelism. `ev_pred` follows `EV = P(success)*Impact + 0.5*LearningValue - 0.3*Entropy - Cost` from `docs/metrics.md`.

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan:
- `world/ruleset.md` exists but currently contains only a heading, so no additional enforceable rules are available there
- `world/contraints.md` exists but currently contains only a heading, so no additional enforceable constraints are available there
- `docs/safety.md`: git safety boundary, sandbox mandatory execution, trust limits, entropy budget discipline
- `docs/git_flow.md`: `/_` branch hierarchy, parent-only merge flow, dual rebase rule
- Potential violations or edge cases:
- Branch-shape corruption when incoming intent branch already ends with `/_`
- Incorrect checkout lineage in sandbox leading to cross-intent contamination
- Executor writes outside canonical ledger path, weakening auditability
- Root/sub-intent merge boundaries being bypassed in test flows
- Mitigations built into the plan:
- Explicit branch normalisation and branch-shape validation gates
- Shared deterministic clone/checkout bootstrap with fail-closed checks
- Canonical ledger path enforcement and schema-level event checks
- Pre/post rebase and parent-only merge guardrails in runtime and tests
- Residual risk accepted (and why): Initial bootstrap may still require controlled network access for `git clone` in containerised execution; accepted because the feature is otherwise blocked and follow-up hardening is included.
- Allocated Entropy Budget: UNSPECIFIED in intent; provisional planning envelope assumed at 50
- Predicted Plan Entropy: 42.6
- Budget Compliance: The strategy fits within budget under the provisional envelope.

## Plan Description & Strategy

Deliver a reliable `holon` bootstrap CLI through staged hardening: first stabilise contract surfaces, then implement deterministic isolated workspace materialisation, then align planner/executor orchestration and ledger invariants, and finally validate with both deterministic and exploratory tests. This preserves safety constraints while enabling the system to spawn future tasks with traceable lineage.

---

## Step 1: Freeze Bootstrap Contracts and Acceptance Matrix

**Sub‑intent recommendation:** NO
**Reasoning:** Small, low-risk analysis prerequisite that should remain in the execution branch for fast alignment.
**Step Type:** INFO_GATHERING
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Establish one authoritative contract for CLI signatures, branch shapes, and ledger paths before changing runtime behaviour.
**Git branch:** I-1771890389-bootstrap-cli/P-1772691637-openai-codex-gpt-5.3-codex/E-1772691637-contract-baseline
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

Audit `holon`, `docker/files/entrypoints/intent_creator.sh`, `planner.sh`, and `executor.sh` to enumerate current signatures and path assumptions.
Define canonical branch normalisation rules for both raw intent branches and already-normalised `/_` branches.
Define expected ledger output locations and required minimum fields for intent, plan, and execution events.
Create an acceptance matrix used as pass/fail criteria for all implementation steps.

### Dependencies & Criticality

**Depends on:** NONE
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` core principles 1 and 2, `docs/git_flow.md` sections 2 and 3
- Potential failure modes for this step:
- Contract ambiguity persists and propagates to implementation
- Mismatch between docs and scripts is not detected
- Guardrails and early‑abort checks:
- Do not proceed to implementation until branch and signature rules are conflict-free
- Abort if unresolved contradictions remain after one reconciliation pass

### Success & Discard Criteria

**Success:** A single explicit contract baseline exists and is referenced by subsequent steps.
**Discard:** Stop if no internally consistent contract can be produced from current repo state.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.96                  |
| entropy_pred        | 1.2                   |
| impact_pred         | 28                    |
| cost_pred           | 2                     |
| learning_value_pred | 3.5                   |
| ev_pred             | 26.3                  |

### Step Metrics Rationale

Very high success and low entropy because this is bounded analysis with minimal mutation risk; moderate impact comes from reducing downstream rework.

---

## Step 2: Normalise `holon` CLI Surface and Argument Validation

**Sub‑intent recommendation:** YES
**Reasoning:** Medium integration risk with reusable value across all future intents; isolated evaluation improves rollback safety.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Make `holon` the stable public entrypoint with deterministic per-command argument contracts.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691638-normalise-holon-cli-surface/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Align subcommand signatures and usage output with actual role-entrypoint expectations.
Validate argument counts and required values before any container run.
Ensure `create-intent` mounts exactly one intent JSON and no unrelated host paths.
Ensure `plan` and `execute` pass arguments in canonical order expected by downstream runtime.

### Dependencies & Criticality

**Depends on:** Step 1
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` sandboxing mandatory, `docs/examples.md` command behaviour expectations
- Potential failure modes for this step:
- Backward-incompatible command behaviour breaks bootstrap flows
- Silent argument shuffling causes wrong role behaviour
- Guardrails and early‑abort checks:
- Require command-level contract tests for all subcommands
- Fail fast on invalid args before runtime side effects

### Success & Discard Criteria

**Success:** All commands invoke intended role paths with validated deterministic arguments.
**Discard:** Stop if command normalisation cannot preserve required root workflow behaviour.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.84                  |
| entropy_pred        | 4.8                   |
| impact_pred         | 66                    |
| cost_pred           | 6                     |
| learning_value_pred | 4.5                   |
| ev_pred             | 50.3                  |

### Step Metrics Rationale

Moderate entropy due to wrapper/runtime coupling; high impact because CLI correctness is the control plane for all future autonomous task creation.

---

## Step 3: Build Deterministic Sandbox Workspace Bootstrap (Clone + Checkout)

**Sub‑intent recommendation:** STRONGLY_YES
**Reasoning:** High-risk, high-reusability platform bottleneck; failure blocks the root goal.
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: Isolated runtime can reproducibly clone fresh repository state and checkout the exact target branch lineage for each role.
- Learning target: Branch resolution, clone/auth behaviour, and workspace hygiene failure modes under container isolation.
- Maximum acceptable cost for this learning: Up to 1.3x of predicted step cost because this bottleneck dominates future execution reliability.

### Intent & Git Integration

**Step Intent:** Replace implicit host-state dependence with explicit per-run repository materialisation inside sandbox.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691639-sandbox-workspace-bootstrap/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Introduce shared bootstrap flow used by intent-creator, planner, and executor roles for workspace initialisation.
Clone repository into a clean runtime path on each run and verify remote ref availability before checkout.
Normalise branch values so `/_` is handled once and nested plan/execution paths resolve correctly.
Record provenance metadata for remote, ref, HEAD, and workspace root.
Abort mutation steps when checkout state is detached, ambiguous, or outside allowed runtime path.

### Dependencies & Criticality

**Depends on:** Step 1, Step 2
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` sandboxing model and git boundary, `docs/git_flow.md` hierarchy semantics
- Potential failure modes for this step:
- Wrong branch materialisation causes cross-intent state contamination
- Clone/auth failure blocks autonomous execution end-to-end
- Residual workspace state leaks between runs
- Guardrails and early‑abort checks:
- Abort before writes when remote ref cannot be resolved exactly
- Abort if runtime workspace path is not under approved root
- Abort on detached or non-deterministic HEAD state

### Success & Discard Criteria

**Success:** Repeated runs in isolated runtime produce deterministic branch checkout and clean workspace provenance.
**Discard:** Stop if branch checkout remains non-deterministic after repeated controlled runs.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.62                  |
| entropy_pred        | 8.9                   |
| impact_pred         | 95                    |
| cost_pred           | 10                    |
| learning_value_pred | 8.0                   |
| ev_pred             | 50.2                  |

### Step Metrics Rationale

Success is constrained by infra variability and auth dependencies; impact and learning are high because this directly enables safe autonomous branch execution.

---

## Step 4: Repair Planner Branching and Plan Artifact Contract

**Sub‑intent recommendation:** YES
**Reasoning:** Medium-large surface and reusable behaviour; isolating this improves traceability and rollback.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Ensure planner branch naming, plan IDs, and ledger entries are consistent with intent branch hierarchy and evaluation expectations.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691640-planner-contract-alignment/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Align plan branch derivation with root intent prefix semantics and avoid accidental duplicate suffix behaviour.
Ensure planner can locate intent ledger entries using canonical branch keys.
Standardise plan artifact naming and ledger payload fields to include required predicted metrics keys.
Ensure planner pushes branch and artifacts consistently from isolated clone context.

### Dependencies & Criticality

**Depends on:** Step 1, Step 3
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/metrics.md` canonical predicted metric names, `docs/git_flow.md` branch naming
- Potential failure modes for this step:
- Planner creates orphaned or malformed plan branches
- Ledger entries become non-comparable due to key mismatch
- Guardrails and early‑abort checks:
- Validate branch pattern before create/push
- Validate ledger payload fields against minimal schema before append

### Success & Discard Criteria

**Success:** Planner emits correctly named plan branches and valid plan ledger entries from sandboxed runs.
**Discard:** Stop if planner output cannot satisfy canonical branch and metric contracts together.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.74                  |
| entropy_pred        | 5.6                   |
| impact_pred         | 78                    |
| cost_pred           | 8                     |
| learning_value_pred | 5.5                   |
| ev_pred             | 50.8                  |

### Step Metrics Rationale

This is a tractable integration correction with moderate entropy and high practical impact on plan comparability and branch lineage.

---

## Step 5: Repair Executor Contract, Execution Branch Flow, and Ledger Writes

**Sub‑intent recommendation:** STRONGLY_YES
**Reasoning:** High-risk integration bottleneck with direct effect on whether autonomous execution works at all.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Align executor invocation contract with `holon execute` and enforce canonical execution branch and ledger behaviour.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691641-executor-contract-alignment/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Remove the current repo-path argument mismatch by defining one canonical executor signature across wrapper and entrypoint.
Derive execution branch under plan branch using documented hierarchy and unique execution ID semantics.
Write execution events to canonical ledger location consistent with intent/planner flow.
Ensure commit metadata and branch push behaviour are deterministic in isolated runtime.

### Dependencies & Criticality

**Depends on:** Step 1, Step 2, Step 3, Step 4
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` git safety boundary and auditability, `docs/git_flow.md` execution branch hierarchy
- Potential failure modes for this step:
- Execution never starts due to argument mismatch
- Execution writes outside canonical ledger path
- Execution branch does not map cleanly to parent plan branch
- Guardrails and early‑abort checks:
- Validate argument contract at wrapper and entrypoint boundaries
- Abort if execution branch does not satisfy expected path pattern
- Abort if ledger target path is unavailable or outside approved workspace

### Success & Discard Criteria

**Success:** `holon execute` reliably creates execution branch, records events in canonical ledger path, and preserves intent-plan-execution lineage.
**Discard:** Stop if canonical signature and branch lineage cannot be simultaneously enforced.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.68                  |
| entropy_pred        | 7.4                   |
| impact_pred         | 88                    |
| cost_pred           | 9                     |
| learning_value_pred | 6.5                   |
| ev_pred             | 51.9                  |

### Step Metrics Rationale

This is high-impact with non-trivial entropy because CLI-wrapper-runtime alignment errors can silently break execution lineage.

---

## Step 6: Enforce Safety Gates (Rebase Discipline, Parent-Only Merge, Fail-Closed Runtime)

**Sub‑intent recommendation:** YES
**Reasoning:** Reusable control-plane safeguards with medium implementation risk and high long-term safety value.
**Step Type:** CONFIG
**Exploration level:** BALANCED

- Hypothesis being tested: Explicit runtime guardrails can block unsafe lineage and merge behaviour without materially degrading execution throughput.
- Learning target: Tradeoff between strict safety checks and operational friction in autonomous flows.
- Maximum acceptable cost for this learning: Moderate; do not exceed 1.2x step cost.

### Intent & Git Integration

**Step Intent:** Add mandatory preflight checks so unsafe branch/merge behaviour is rejected before mutation.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691642-safety-gates-enforcement/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Require pre-execution parent synchronisation checks aligned with dual-rebase policy.
Block direct merge paths that bypass parent intent boundaries.
Define explicit runtime modes for clone-time network access versus execution-time restricted behaviour.
Emit failure events when guardrails trigger, preserving audit trail for trust scoring.

### Dependencies & Criticality

**Depends on:** Step 3, Step 4, Step 5
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` core principles 1, 2, and 5; `docs/git_flow.md` sections 3 and 4
- Potential failure modes for this step:
- Overly strict checks block valid runs
- Guardrails are incomplete and allow unsafe merge paths
- Guardrail failures are not logged for audit/trust
- Guardrails and early‑abort checks:
- Roll out checks with explicit failure diagnostics
- Abort execution immediately on lineage policy violations
- Verify failure events are always appended on guardrail-triggered aborts

### Success & Discard Criteria

**Success:** Unsafe lineage and merge operations are prevented with auditable fail-closed behaviour.
**Discard:** Stop if safety enforcement causes persistent false positives that outweigh risk reduction.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.65                  |
| entropy_pred        | 5.9                   |
| impact_pred         | 72                    |
| cost_pred           | 7                     |
| learning_value_pred | 6.8                   |
| ev_pred             | 41.4                  |

### Step Metrics Rationale

Moderate success due to balancing strictness vs usability; strong learning from guardrail-triggered failures improves future policy calibration.

---

## Step 7: End-to-End and Failure-Injection Validation in Isolated Runtime

**Sub‑intent recommendation:** STRONGLY_YES
**Reasoning:** Large, risky, and highly reusable verification harness; critical for confidence before parent merge.
**Step Type:** TEST
**Exploration level:** EXPLORATORY

- Hypothesis being tested: The end-to-end bootstrap path remains correct under both nominal and adversarial conditions in isolated execution.
- Learning target: High-value failure modes (missing branch, clone/auth failure, malformed inputs, stale parent state) and their observability quality.
- Maximum acceptable cost for this learning: High but bounded; up to 1.4x predicted step cost.

### Intent & Git Integration

**Step Intent:** Validate create-intent → plan → execute flow and confirm guardrail behaviour under intentional fault cases.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691643-bootstrap-e2e-validation/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Run deterministic e2e scenario for root intent creation, plan generation, and execution branch creation in isolated environment.
Add negative-path validation for invalid branch shapes, missing refs, and invalid argument contracts.
Add controlled clone/auth failure simulation and verify fail-closed outcomes with ledger traces.
Validate that merge path remains parent-only and that branch naming hierarchy is preserved.
Measure predicted vs observed entropy signals to improve future planning calibration.

### Dependencies & Criticality

**Depends on:** Step 2, Step 3, Step 4, Step 5, Step 6
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` sandbox and trust implications, `docs/metrics.md` predicted vs actual calibration, `docs/git_flow.md` merge discipline
- Potential failure modes for this step:
- False confidence from weak assertions
- Test harness bypasses realistic isolated runtime assumptions
- Exploratory faults consume excessive cost without actionable learning
- Guardrails and early‑abort checks:
- Require explicit assertions for branch lineage, ledger location, and failure-event logging
- Abort exploratory matrix expansion if learning signal saturates or cost exceeds threshold
- Stop if repeated sandbox policy violations indicate unsafe configuration

### Success & Discard Criteria

**Success:** Nominal flow passes and failure-injection paths are correctly blocked and logged with actionable diagnostics.
**Discard:** Stop if test expansion exceeds 1.4x cost prediction without reducing key uncertainty.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.58                  |
| entropy_pred        | 6.7                   |
| impact_pred         | 82                    |
| cost_pred           | 11                    |
| learning_value_pred | 8.8                   |
| ev_pred             | 39.0                  |

### Step Metrics Rationale

Lower success reflects intentionally adversarial coverage; high learning value justifies entropy because discovered failure modes directly improve future autonomous reliability.

---

## Step 8: Operational Documentation and Rollout Criteria

**Sub‑intent recommendation:** NO
**Reasoning:** Small finishing step with low risk and moderate reuse; can remain in parent execution branch.
**Step Type:** DOCUMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Document final bootstrap flow, guardrails, and rollout boundaries for human reviewers and future agents.
**Git branch:** I-1771890389-bootstrap-cli/P-1772691637-openai-codex-gpt-5.3-codex/E-1772691637-docs-rollout
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

Document canonical `holon` command contracts and argument examples.
Document branch lineage expectations and forbidden merge paths.
Document runtime prerequisites, sandbox assumptions, and known residual risks.
Document acceptance checklist for root-intent promotion readiness.

### Dependencies & Criticality

**Depends on:** Step 1, Step 2, Step 3, Step 4, Step 5, Step 6, Step 7
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` human review boundary and safety principles, `docs/git_flow.md` merge constraints
- Potential failure modes for this step:
- Documentation diverges from implemented contracts
- Reviewers cannot verify safety boundaries quickly
- Guardrails and early‑abort checks:
- Cross-check docs against test outcomes and final contract matrix
- Abort publish if unresolved contract discrepancies remain

### Success & Discard Criteria

**Success:** Concise runbook exists and reflects verified behaviour and constraints.
**Discard:** Stop if documentation cannot be reconciled with verified runtime behaviour.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.90                  |
| entropy_pred        | 2.1                   |
| impact_pred         | 40                    |
| cost_pred           | 3                     |
| learning_value_pred | 3.0                   |
| ev_pred             | 33.9                  |

### Step Metrics Rationale

Low entropy and high success due to bounded scope; impact comes from reducing operational ambiguity and improving reviewer throughput.

---
