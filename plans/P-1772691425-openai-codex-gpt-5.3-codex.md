# Plan for I-1771890389

**Plan ID:** P-1772691425-openai-codex-gpt-5.3-codex
**Parent Intent ID:** null
**Agent:** openai-codex/gpt-5.3-codex
**Created At:** 2026-03-05T06:17:05.6NZ

## Planner Autonomy Summary

- Intent handling: SPLIT
- Reframed intent (if applicable): Keep the goal, but decompose into contract stabilisation, isolated workspace bootstrap, orchestration hardening, safety controls, and validation because current implementation has branch/arg/ledger mismatches that reduce EV if tackled as one unscoped execution.
- Exploration stance: balanced with targeted exploration. Most steps exploit known git/sandbox patterns, but selected low-probability tests are included to harvest failure-mode learning for future autonomous task spawning.
- Safety priority level: critical
- Priority Justification: `docs/safety.md` defines git isolation, sandboxing, trust boundaries, and entropy budget enforcement as invariants. This intent creates the mechanism that will spawn future work, so defects amplify system-wide risk.

## Exploration

- Proportion of steps that are exploratory: 0.25
- Justification: Two of eight steps are BALANCED/EXPLORATORY to validate uncertain clone/auth/branch-isolation behaviour and improve future planner calibration.

## Overall Plan Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.57                  |
| entropy_pred        | 48.5                  |
| impact_pred         | 96                    |
| cost_pred           | 39                    |
| learning_value_pred | 7.1                   |
| ev_pred             | 4.7                   |

### Strategy Rationale

The repo already contains a partial `holon` bootstrap (`holon`, `docker/files/entrypoints/*.sh`) but current state shows high-risk inconsistencies: root branch suffix duplication in intent creation, `execute` CLI arity mismatch with executor script, mixed ledger paths (`app/ledger/events.jsonl` vs `events.jsonl`), and non-deterministic runtime assumptions. A split strategy has higher EV than a monolithic execution because it isolates bottlenecks (workspace materialisation and orchestration contracts) into mergeable sub-intents with explicit quality gates.

Overall metrics were derived using bottleneck-aware aggregation, not simple averaging: `p_success_pred` is constrained by the lowest-confidence critical path steps (Steps 3-5). `entropy_pred` is the sum of step entropies. `impact_pred` is capped by end-state capability enablement rather than summed. `cost_pred` is critical-path cost with parallelizable sub-intent savings versus raw sum. `ev_pred` uses `EV = P(success)*Impact + 0.5*LearningValue - 0.3*Entropy - Cost` from `docs/metrics.md`.

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan:
- `world/ruleset.md` and `world/contraints.md` currently contain headings only; no additional enforceable rules discovered there
- `docs/safety.md` invariants: git safety boundary, sandbox mandatory execution, trust boundaries, entropy budget checks, parent-only promotion control
- `docs/git_flow.md` branch hierarchy (`/_`), pre/post parent rebase, and parent-only merge discipline
- Potential violations or edge cases:
- Branch suffix duplication from intent payload branch values already containing `/_`
- Container clone dependency on SSH and network when policy expects restricted networking
- CLI-to-entrypoint parameter mismatch causing incorrect execution context
- Sub-intent attempting direct merge to `main`
- Mitigations built into the plan:
- Contract tests and branch-shape validators before mutation operations
- Controlled sandbox policy for clone phase and explicit no-network runtime phase where possible
- Ledger path normalisation and execution provenance checks
- Explicit merge policy gates enforcing parent-only merges
- Residual risk accepted (and why): Bootstrap may initially require constrained network egress for `git clone` unless a local mirror strategy is implemented immediately; accepted due to high unblock impact, with hardening included as a follow-up gate.
- Allocated Entropy Budget: UNSPECIFIED in intent; provisional planning envelope assumed at 55 pending parent policy confirmation
- Predicted Plan Entropy: 48.5
- Budget Compliance: The strategy fits within budget under the provisional envelope; if final allocated budget is lower than 48.5, defer Step 7 exploratory load first.

## Plan Description & Strategy

Deliver `holon` as a reliable bootstrap CLI by first fixing contract ambiguity, then enforcing deterministic sandboxed repo materialisation and branch checkout, then aligning dispatch/execution/ledger flow to system invariants, and finally validating with both deterministic and exploratory tests. This sequencing minimises catastrophic integration failures while maximising reusable learning for future autonomous intent spawning.

---

## Step 1: Baseline Contract and Gap Audit

**Sub‑intent recommendation:** NO
**Reasoning:** Small, low-risk analysis step that should complete inside one execution branch and serves as prerequisite for all implementation steps.
**Step Type:** INFO_GATHERING
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Freeze authoritative command, branch, and ledger contracts by reconciling current scripts/docs before modifying runtime logic.
**Git branch:** I-1771890389-bootstrap-cli/P-1772691425-openai-codex-gpt-5.3-codex/E-1772691425-contract-audit
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

Audit `holon` wrapper, `docker/files/entrypoints/*`, and docs to document current vs intended behaviour.
Record canonical signatures for `create-intent`, `plan`, `execute` including argument ordering and required environment.
Define branch normalisation rules for payloads with/without `/_`.
Define canonical ledger paths and required event payload fields for intent/plan/execute lifecycle.
Produce acceptance checklist for Steps 2-8.

### Dependencies & Criticality

**Depends on:** NONE
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (Git boundary, sandboxing), `docs/git_flow.md` (branch hierarchy)
- Potential failure modes for this step:
- Hidden mismatch is missed and propagates into implementation
- Existing behaviour is assumed without proof from current scripts
- Guardrails and early‑abort checks:
- Do not start implementation until a single normalised contract is written and reviewed against docs
- Abort if unresolved contradictions remain after one reconciliation pass

### Success & Discard Criteria

**Success:** A single validated contract exists for commands, branch shape, and ledger paths.
**Discard:** Stop this step if contradictions cannot be resolved with available docs/repo state.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.95                  |
| entropy_pred        | 1.5                   |
| impact_pred         | 30                    |
| cost_pred           | 2                     |
| learning_value_pred | 4.0                   |
| ev_pred             | 28.1                  |

### Step Metrics Rationale

Low entropy and high success because this is a bounded alignment task with minimal state mutation, but impact is moderate because it prevents downstream rework.

---

## Step 2: Normalise `holon` CLI Surface

**Sub‑intent recommendation:** YES
**Reasoning:** Medium risk and reusable across all future intents; isolation as a sub-intent improves rollback and independent evaluation.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Make `holon` the stable user-facing entrypoint with validated command signatures and deterministic container invocation semantics.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691426-normalise-holon-cli/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Align `holon` subcommand argument parsing with dispatcher/entrypoint expectations.
Standardise error handling for missing/invalid arguments before any container action.
Separate role-specific runtime argument preparation from user command parsing.
Ensure intent JSON mount semantics are explicit for `create-intent` only.
Update command help text to match real runtime behaviour.

### Dependencies & Criticality

**Depends on:** Step 1
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` sandboxing mandatory; `docs/git_flow.md` lineage correctness
- Potential failure modes for this step:
- Backward-incompatible signature breakage in bootstrap scripts
- Silent argument shift causes incorrect role execution
- Guardrails and early‑abort checks:
- Require contract tests for each subcommand
- Abort if wrapper and dispatcher signatures diverge

### Success & Discard Criteria

**Success:** `holon` commands route correctly with validated args and deterministic role selection.
**Discard:** Stop if CLI normalisation cannot preserve required workflow semantics.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.82                  |
| entropy_pred        | 4.2                   |
| impact_pred         | 68                    |
| cost_pred           | 5                     |
| learning_value_pred | 4.5                   |
| ev_pred             | 51.8                  |

### Step Metrics Rationale

Moderate entropy due to integration touch points, high impact because CLI correctness is the control plane for future automated intents.

---

## Step 3: Deterministic Sandboxed Workspace Materialisation

**Sub‑intent recommendation:** STRONGLY_YES
**Reasoning:** High risk, high reusability, and hard bottleneck for autonomous spawning in isolated environments.
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: A containerised role can clone a clean repo copy and checkout the exact target branch lineage deterministically across repeated runs.
- Learning target: Identify failure modes in branch resolution, auth, network policy, and workspace hygiene that affect reproducibility.
- Maximum acceptable cost for this learning: Up to 1.3x of step cost because this is a foundational safety/performance bottleneck.

### Intent & Git Integration

**Step Intent:** Create a shared clone/checkout bootstrap mechanism used by all roles inside sandboxed runtime.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691427-sandbox-workspace-bootstrap/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Implement shared runtime bootstrap logic for clean workspace init per invocation.
Normalise branch inputs and enforce exact target branch checkout semantics.
Add explicit checks for branch existence, expected parent lineage, and non-detached state.
Harden cleanup to prevent cross-run state contamination in container filesystem.
Emit structured run metadata for repo URL, checked-out ref, and workspace path.

### Dependencies & Criticality

**Depends on:** Step 1, Step 2
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` sandboxing + git boundary; `docs/git_flow.md` rebase discipline
- Potential failure modes for this step:
- Wrong branch checkout contaminates unrelated intent state
- Clone/auth failures make autonomous execution non-operational
- Residual mutable state leaks between invocations
- Guardrails and early‑abort checks:
- Abort before mutations if branch resolution fails
- Abort when workspace root is outside allowed path
- Abort on detached or ambiguous HEAD states

### Success & Discard Criteria

**Success:** Each role starts from empty sandbox state, clones repo, checks out intended branch deterministically, and records provenance.
**Discard:** Stop if branch resolution or workspace isolation remains nondeterministic after repeated test runs.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.64                  |
| entropy_pred        | 8.8                   |
| impact_pred         | 95                    |
| cost_pred           | 8                     |
| learning_value_pred | 8.0                   |
| ev_pred             | 54.2                  |

### Step Metrics Rationale

Lower success probability reflects infra/auth variability; high learning value comes from discovering high-leverage failure modes in reproducibility.

---

## Step 4: Repair Role Dispatch, Execution Contract, and Ledger Paths

**Sub‑intent recommendation:** STRONGLY_YES
**Reasoning:** Large integration surface with cascading failure potential; strong candidate for independent branch/evaluation.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Align dispatcher and role scripts so execute/planner/intention contracts are consistent and all ledger writes use canonical paths.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691428-orchestration-contract-repair/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Resolve argument contract mismatch between `holon execute` and executor entrypoint.
Unify ledger write targets under `app/ledger/*.jsonl` and ensure all roles use same schema baseline.
Correct branch construction rules for intent and execution branches to prevent malformed refs.
Enforce deterministic commit metadata and event structure for traceability.
Add negative tests for malformed args, missing branch, and missing ledger path.

### Dependencies & Criticality

**Depends on:** Step 1, Step 2, Step 3
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` append-only trace + safety monitoring prerequisites; `docs/git_flow.md` hierarchy invariants
- Potential failure modes for this step:
- Ledger divergence breaks evaluator/calibration workflow
- Role contract drift causes silent incorrect behaviour
- Guardrails and early‑abort checks:
- Abort commit if ledger files are outside approved path
- Abort branch creation if naming violates hierarchy

### Success & Discard Criteria

**Success:** Role dispatch and role scripts are contract-consistent; lifecycle events land in canonical ledger paths.
**Discard:** Stop if event schema/path consistency cannot be guaranteed across roles.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.60                  |
| entropy_pred        | 9.5                   |
| impact_pred         | 92                    |
| cost_pred           | 8                     |
| learning_value_pred | 7.0                   |
| ev_pred             | 47.9                  |

### Step Metrics Rationale

This is an integration-heavy step with many interacting scripts, giving moderate success and high impact due to direct effect on traceability and correctness.

---

## Step 5: Action Execution Runtime for Autonomous Task Spawning

**Sub‑intent recommendation:** YES
**Reasoning:** High implementation value and moderate risk; reusable for all future execution actions.
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: The executor can reliably materialise an execution branch, run an action, and produce valid branch+ledger artifacts in isolated runtime.
- Learning target: Understand failure boundaries for agent invocation, action slugs, and branch lineage under real end-to-end load.
- Maximum acceptable cost for this learning: Medium; up to 1.2x step cost due to long-term platform leverage.

### Intent & Git Integration

**Step Intent:** Make `holon execute` produce correct `E-*` branches and action artifacts that can merge upward through plan and parent intent flow.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691429-execution-runtime-hardening/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Implement execution-branch creation from a validated plan branch using canonical naming.
Ensure executor operates within cloned sandbox workspace, not host mutable path assumptions.
Define a minimal action contract (inputs, outputs, commit scope, ledger event requirements).
Record success/failure with sufficient metadata for evaluator and trust scoring.
Add guardrails for invalid action slug, non-existent plan branch, and dirty workspace.

### Dependencies & Criticality

**Depends on:** Step 2, Step 3, Step 4
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` trust and sandbox boundaries; `docs/git_flow.md` execution branch lineage
- Potential failure modes for this step:
- Execution branch created from wrong base
- Agent action mutates unintended files or paths
- Insufficient metadata prevents post-execution audit
- Guardrails and early‑abort checks:
- Abort on branch ancestry mismatch
- Abort on writes outside repo workspace
- Abort if required ledger event fields are absent

### Success & Discard Criteria

**Success:** `holon execute` consistently generates valid execution branches and auditable action outputs.
**Discard:** Stop if action executions cannot satisfy lineage and auditability checks.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.58                  |
| entropy_pred        | 10.0                  |
| impact_pred         | 88                    |
| cost_pred           | 9                     |
| learning_value_pred | 8.5                   |
| ev_pred             | 43.3                  |

### Step Metrics Rationale

Higher entropy reflects runtime orchestration complexity; learning value is high because this step validates the core spawn-and-execute loop.

---

## Step 6: Safety Controls and Policy Gates

**Sub‑intent recommendation:** YES
**Reasoning:** Reusable and compliance-critical; moderate size and directly tied to world safety invariants.
**Step Type:** CONFIG
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Enforce explicit sandbox/network/credential boundaries and git discipline checks before execution and merge.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691430-safety-policy-gates/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Add policy gate checks for allowed filesystem scope, role permissions, and branch target validity.
Define clone-phase network allowance policy and execution-phase network restrictions.
Minimise credential exposure by limiting mounted key material and documenting least-privilege expectation.
Enforce pre/post parent rebase checks where sub-intent execution is involved.
Instrument early-abort events for policy violations.

### Dependencies & Criticality

**Depends on:** Step 3, Step 4, Step 5
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` sandbox escape response, entropy governance, trust model; `docs/git_flow.md` dual rebase
- Potential failure modes for this step:
- Overly strict policy blocks legitimate execution
- Under-constrained policy leaves escape or contamination paths
- Guardrails and early‑abort checks:
- Start with deny-by-default checks for critical boundaries
- Add controlled policy exceptions with explicit logging

### Success & Discard Criteria

**Success:** Runtime enforces policy gates and logs violations deterministically without blocking valid workflows.
**Discard:** Stop if policy cannot be enforced without repeated false positives that stall core flow.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.70                  |
| entropy_pred        | 6.2                   |
| impact_pred         | 80                    |
| cost_pred           | 6                     |
| learning_value_pred | 6.0                   |
| ev_pred             | 51.1                  |

### Step Metrics Rationale

Moderate cost with strong risk reduction and compliance impact; high EV due to preventing catastrophic violations.

---

## Step 7: End-to-End and Exploratory Validation Matrix

**Sub‑intent recommendation:** YES
**Reasoning:** Large test scope and high learning reuse for future intents; moderate risk if run in same branch as implementation.
**Step Type:** TEST
**Exploration level:** EXPLORATORY

- Hypothesis being tested: The full create-intent -> plan -> execute loop works reliably under nominal and adversarial edge conditions in isolated runtime.
- Learning target: Capture failure signatures (branch conflicts, missing refs, auth/network failures, malformed JSON) to improve future planning and calibration.
- Maximum acceptable cost for this learning: Medium-high but bounded to avoid delaying bootstrap release; cap at 1.25x step cost.

### Intent & Git Integration

**Step Intent:** Validate functionality, safety invariants, and observability using deterministic and low-probability test scenarios.
**Git branch:** I-1771890389-bootstrap-cli/I-1772691431-e2e-and-failure-matrix/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

Define acceptance suite for happy-path bootstrap and branch lineage checks.
Add negative-path tests for malformed intent payload, missing plan branch, and policy-gate denials.
Run repeated deterministic trials to detect nondeterministic checkout/ledger behaviour.
Capture and classify failure modes into reusable diagnostics.
Attach predicted vs observed metrics to improve estimator calibration baseline.

### Dependencies & Criticality

**Depends on:** Step 2, Step 3, Step 4, Step 5, Step 6
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` exploration safety model and monitoring triggers
- Potential failure modes for this step:
- Test coverage misses critical failure path
- Exploratory cases exceed entropy/cost envelope
- Guardrails and early‑abort checks:
- Predefine stop conditions for unstable exploratory runs
- Keep exploration within explicit entropy and runtime caps

### Success & Discard Criteria

**Success:** Test matrix demonstrates reliable nominal flow plus known behaviour under prioritised edge cases.
**Discard:** Stop exploratory subset if entropy/cost exceeds cap without proportional learning yield.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.73                  |
| entropy_pred        | 5.8                   |
| impact_pred         | 76                    |
| cost_pred           | 6                     |
| learning_value_pred | 7.5                   |
| ev_pred             | 51.5                  |

### Step Metrics Rationale

Exploratory tests intentionally increase uncertainty slightly, but produce strong reusable learning and confidence lift for production use.

---

## Step 8: Documentation, Merge Prep, and Operational Handover

**Sub‑intent recommendation:** NO
**Reasoning:** Low-risk closure step with limited implementation uncertainty; can run on parent execution branch after upstream sub-intents merge.
**Step Type:** DOCUMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Finalise operator docs and merge package for root-intent human review and promotion.
**Git branch:** I-1771890389-bootstrap-cli/P-1772691425-openai-codex-gpt-5.3-codex/E-1772691432-merge-prep
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

Document final CLI contract, expected sandbox behaviour, and branch/ledger invariants.
Summarise known limitations and deferred hardening items with rationale.
Prepare review package contents: metric deltas, test evidence, diff summary, and residual risks.
Define immediate follow-up intents for post-bootstrap hardening if needed.

### Dependencies & Criticality

**Depends on:** Step 7
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` human review boundaries; `docs/git_flow.md` root promotion path
- Potential failure modes for this step:
- Incomplete handover obscures residual risk
- Missing evidence blocks human review
- Guardrails and early‑abort checks:
- Require completion checklist before merge request
- Block promotion if safety/test evidence is incomplete

### Success & Discard Criteria

**Success:** Review package is complete and root intent is ready for human approval to merge.
**Discard:** Stop if required evidence for safety or correctness is missing.

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.90                  |
| entropy_pred        | 2.5                   |
| impact_pred         | 45                    |
| cost_pred           | 3                     |
| learning_value_pred | 4.0                   |
| ev_pred             | 38.8                  |

### Step Metrics Rationale

High confidence and low entropy because this step mostly packages decisions and evidence, while still adding meaningful operational impact.

---
