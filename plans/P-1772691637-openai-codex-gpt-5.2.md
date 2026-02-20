# Plan for I-1771890389

**Plan ID:** P-1772691637-openai-codex-gpt-5.2
**Parent Intent ID:** null
**Agent:** openai-codex/gpt-5.2
**Created At:** 2026-03-05T06:20:37.6NZ

## Planner Autonomy Summary

- Intent handling: REFRAME
- Reframed intent (if applicable): Create a minimal-but-correct `holon` CLI focused on **intent creation** that always runs intent mutations inside a container sandbox that **clones its own repo copy** and **checks out the correct branch**, while reusing (and hardening) existing `docker/` entrypoints where possible.
- Exploration stance: balanced — a small amount of exploration is required to reconcile the existing Bash CLI + Docker entrypoints with the documented safety model, but implementation should converge quickly to a deterministic workflow.
- Safety priority level: elevated
- Priority Justification: `docs/safety.md` defines sandboxing + Git isolation as mandatory for execution-capable tooling; this intent creates the mechanism that can spawn future tasks, so mistakes here have systemic blast-radius.

## Exploration

- Proportion of steps that are exploratory: 0.22
- Justification: The repo already contains partial CLI/orchestrator scaffolding; short exploratory probes are needed to map gaps (e.g., argument mismatches, ledger paths, auth assumptions) before locking in interfaces.

## Overall Plan Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.68                  |
| entropy_pred        | 22                    |
| impact_pred         | 120                   |
| cost_pred           | 60                    |
| learning_value_pred | 7                     |
| ev_pred             | 18.5                  |

### Strategy Rationale

This plan maximises EV by **hardening existing scaffolding** (`holon` Bash wrapper + `docker/files/entrypoints/*.sh`) rather than replacing it, while meeting the explicit requirement that the sandbox clones/checkout happen inside the isolated environment. Overall `p_success_pred` is bottlenecked by getting Git auth + clone/checkout correct in a network-restricted container without leaking host secrets; entropy is dominated by changes across CLI + Docker entrypoints + tests; impact is high because it unlocks the system’s ability to create future intent branches; cost is moderate due to integration work. `ev_pred` uses the bootstrap formula and coefficients in `docs/metrics.md` (λ=0.3, μ=0.5).

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan:
  - `docs/safety.md` (Git as safety boundary, mandatory sandboxing, entropy budgets, trust boundaries).
  - `docs/git_flow.md` (branch naming and rebase/merge discipline).
  - `docs/ledger_schema.md` (event/ledger contracts; avoid ad-hoc JSONL drift).
  - `world/ruleset.md` and `world/contraints.md` exist but are currently placeholders; treat `docs/*` as the operative constraints until the world ruleset is populated.
- Potential violations or edge cases:
  - Leaking host credentials into containers (e.g., mounting `$HOME/.ssh`) beyond minimum necessary.
  - Container cloning requiring network access when sandbox policy expects `--network none`.
  - Creating branches that violate the `.../_` naming convention or accidentally writing to `main`.
  - Ledger writes going to inconsistent paths (`app/ledger/*` vs repo root).
- Mitigations built into the plan:
  - Prefer token-based HTTPS auth passed as ephemeral env/secret; avoid mounting full host SSH directories.
  - Support offline/no-network integration tests by cloning from a mounted local bare repo (`file://`), so sandbox networking can remain disabled in tests.
  - Centralise “clone + checkout + branch create” logic in one place and validate branch patterns before pushing.
  - Align all ledger writes to a single configured ledger root and validate schema envelopes where feasible.
- Residual risk accepted (and why): Some parts of plan/execute may remain “stub/experimental” after intent-creation MVP if they exceed entropy/cost budgets; acceptable because the stated intent is intent creation, and follow-on intents can safely evolve execution.
- Allocated Entropy Budget: Not specified in intent JSON; assume root intent budget target `<= 30` for bootstrap stability.
- Predicted Plan Entropy: 22
- Budget Compliance: The strategy fits within budget.

## Plan Description & Strategy

Deliver an MVP `holon` CLI that reliably creates new intent branches from a specified repo/branch inside a Docker sandbox that clones the repository and checks out the correct branch before mutating state. Treat existing Bash scripts as prototypes: standardise interfaces, eliminate argument mismatches, make repo/auth configurable, and add an offline integration test path that simulates “clone inside container” without requiring external network access. Defer non-essential planner/executor sophistication to follow-on sub-intents to keep entropy bounded.

---

## Step 1: Confirm Current-State Gaps and Acceptance Criteria

**Sub‑intent recommendation:** NO
**Reasoning:** Small, low-risk discovery needed to lock MVP scope and prevent wasteful re-implementation.
**Step Type:** INFO_GATHERING
**Exploration level:** BALANCED

- Hypothesis being tested: Existing `holon` + `docker/files/entrypoints/*` already implement most of intent-creation workflow but have interface and safety gaps that can be corrected with minimal surface-area changes.
- Learning target: Identify exact mismatches (CLI args vs entrypoints), hardcoded repo/auth assumptions, ledger path inconsistencies, and test harness expectations.
- Maximum acceptable cost for this learning: Low (timeboxed to < 2 hours equivalent effort).

### Intent & Git Integration

**Step Intent:** Convert repo reconnaissance into an explicit MVP contract: which commands, which required flags/env vars, and what “success” means for intent creation.
**Git branch:** I-1771890389-bootstrap-cli/_
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

- Inventory the existing CLI entry (`holon`) and Docker entrypoints (`intent_creator.sh`, `planner.sh`, `executor.sh`) and map expected arguments.
- Identify where the repo URL is hard-coded and where credentials are assumed (SSH keys, env vars).
- Trace ledger write locations and compare against `docs/ledger_schema.md` expectations.
- Review `test_holon_bootstrap.sh` and decide whether it targets a “local git” workflow or a “remote clone inside container” workflow; capture required adjustments.
- Define acceptance criteria for this intent as: “`holon create-intent <intent.json>` deterministically creates/pushes the intent branch and appends a ledger event/record in the correct place, without requiring host repo mutation.”

### Dependencies & Criticality

**Depends on:** NONE
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (sandbox mandatory, Git boundary), `docs/git_flow.md` (branch naming).
- Potential failure modes for this step:
  - Mis-scoping the MVP and accidentally committing to executing unbounded code inside the container.
  - Missing an implicit requirement (e.g., no-network mode) that later forces rework.
- Guardrails and early‑abort checks:
  - If the MVP contract cannot be stated in 5-8 bullet requirements, stop and re-scope to “intent create only”.

### Success & Discard Criteria

**Success:** Written MVP acceptance criteria + a list of concrete gaps to fix.
**Discard:** If discovery reveals no coherent path without broad refactor, defer to sub-intents and propose a narrower MVP (intent creation only).

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.93  |
| entropy_pred        | 2     |
| impact_pred         | 25    |
| cost_pred           | 7     |
| learning_value_pred | 4     |
| ev_pred             | 17.0  |

### Step Metrics Rationale

High probability and low entropy; moderate learning value because it reduces downstream rework and prevents unsafe interface decisions.

---

## Step 2: Specify the `holon` CLI Contract (MVP + Stable Interfaces)

**Sub‑intent recommendation:** NO
**Reasoning:** Primarily design/documentation; keeping it in the parent intent reduces coordination overhead.
**Step Type:** DOCUMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Define the CLI’s stable user-facing interface and the internal container contract for intent creation.
**Git branch:** I-1771890389-bootstrap-cli/_
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

- Define canonical subcommand and flags for intent creation (either keep `create-intent` or introduce `intent create`, but choose one and treat the other as compatibility alias).
- Define required inputs:
  - intent JSON path (host file, mounted read-only into container)
  - repo URL (default to current project remote, overrideable)
  - base branch (default `main`)
  - target intent branch (from JSON `branch`, enforce `.../_`)
- Define required outputs:
  - pushed intent branch exists on remote
  - local ledger record appended and committed on that intent branch
  - printed summary containing intent_id, branch, commit SHA, and ledger path.
- Define a Git auth strategy matrix:
  - primary: HTTPS + token via env var/secret
  - fallback: SSH deploy key mounted as a single file (not full `$HOME/.ssh`)
  - explicitly disallow “mount full host SSH directory” in default docs.
- Define sandbox constraints:
  - for offline tests: container runs with `--network none` and clones from a mounted bare repo using `file://`
  - for real remote runs: container may require network; if enabled, it should be explicit and logged (ledger event).

### Dependencies & Criticality

**Depends on:** Step 1
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (sandboxing + trust), `docs/ledger_schema.md` (ledger integrity).
- Potential failure modes for this step:
  - Designing an interface that forces unsafe secret mounting.
  - Overcommitting to networked cloning without an offline test path.
- Guardrails and early‑abort checks:
  - Require that every secret input has a “least privilege” delivery method described.

### Success & Discard Criteria

**Success:** A concrete CLI + container contract that can be implemented without further ambiguities.
**Discard:** If contract requires major ledger schema redesign, split that redesign into a separate root intent (out of scope).

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.85  |
| entropy_pred        | 2     |
| impact_pred         | 35    |
| cost_pred           | 9     |
| learning_value_pred | 3     |
| ev_pred             | 21.8  |

### Step Metrics Rationale

Low entropy but high leverage: a clear contract materially increases success probability for implementation steps.

---

## Step 3: Build a Reusable “Sandbox Clone + Checkout” Primitive (Auth + Branch Validation)

**Sub‑intent recommendation:** YES
**Reasoning:** Medium risk, reusable across planner/executor, and the most failure-prone part of the workflow (auth + branch correctness).
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: A single shared “clone/checkout/push” implementation reduces defects versus duplicating Git logic across entrypoints.
- Learning target: Determine the minimum viable Git auth mechanism that works in containers and supports both offline tests and real remotes.
- Maximum acceptable cost for this learning: Medium; stop if it expands into full secret-management design.

### Intent & Git Integration

**Step Intent:** Implement and validate a shared cloning/checkout layer used by the intent-creator container role.
**Git branch:** I-1771890389-bootstrap-cli/I-<ts>-sandbox-clone-checkout/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Introduce a single shared script/module used by Docker entrypoints to:
  - validate target branch pattern (`.../_`)
  - clone repo (supports `file://` and `https://`)
  - checkout base branch deterministically
  - create target branch and push upstream
  - configure Git identity locally for agent commits
- Implement least-privilege auth:
  - if token env var present: configure HTTPS remote with token
  - else if a deploy key file is mounted: use `GIT_SSH_COMMAND` pointing at that file
  - else: fail with actionable error.
- Add guardrails:
  - refuse to push if target branch already exists unless `--force` (default off)
  - refuse to write outside workspace root
  - log clone mode (offline file:// vs networked remote) to ledger.

### Dependencies & Criticality

**Depends on:** Step 2
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (sandboxing, escape detection principles), `docs/git_flow.md` (branch naming).
- Potential failure modes for this step:
  - Accidentally persisting secrets into git config or logs.
  - Branch validation too lax, allowing writes to unintended refs.
  - File:// clone path assumptions that break on CI.
- Guardrails and early‑abort checks:
  - Ensure token never printed; redact in logs.
  - Unit-test branch validation logic with reject cases.

### Success & Discard Criteria

**Success:** Container role can clone/checkout/create/push branches with a single entrypoint call, in both offline (`file://`) and remote modes.
**Discard:** If auth cannot be made to work without mounting broad host secrets, stop and escalate design decision (safety boundary risk).

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.62  |
| entropy_pred        | 7     |
| impact_pred         | 55    |
| cost_pred           | 18    |
| learning_value_pred | 6     |
| ev_pred             | 18.4  |

### Step Metrics Rationale

This is the highest-risk step (auth + Git correctness in sandbox), hence lower p_success and higher entropy; learning value is high because it establishes a durable primitive used across future intents.

---

## Step 4: Harden the Host `holon` CLI Wrapper (Intent Creation End-to-End)

**Sub‑intent recommendation:** YES
**Reasoning:** Medium scope with user-facing UX; benefits from isolated evaluation and fast iteration without entangling other pipeline parts.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Make `holon` reliably invoke the intent-creator container role with correct mounts/args and clear errors.
**Git branch:** I-1771890389-bootstrap-cli/I-<ts>-holon-cli-intent-create/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Update `holon` to:
  - expose the MVP interface defined in Step 2
  - mount the intent JSON read-only into the container
  - pass repo URL/base branch/auth mode via env/args
  - optionally enable/disable networking explicitly.
- Ensure CLI prints deterministic outputs for scripting:
  - intent_id, branch, upstream remote, resulting commit SHA
  - location of ledger record produced.
- Add a “preflight”/“doctor” check path (even if minimal):
  - docker present
  - image present (or instruct build command)
  - required env vars present for chosen auth mode.

### Dependencies & Criticality

**Depends on:** Step 2, Step 3
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (sandboxing, secrets), `docs/git_flow.md` (branch naming).
- Potential failure modes for this step:
  - CLI passes wrong arguments (regression) causing unsafe container behaviour.
  - CLI mounts sensitive host paths by default.
- Guardrails and early‑abort checks:
  - Default mounts limited to intent JSON and (optionally) a single deploy-key file.
  - Refuse to run if asked to mount a directory known to contain broad secrets.

### Success & Discard Criteria

**Success:** Running `holon` intent creation from a clean host state creates the intent branch via container-only cloning/checkout, with no host repo modification required.
**Discard:** If the wrapper requires major rewrite to meet contract, defer to a Python-based CLI in a separate intent (higher cost/entropy).

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.74  |
| entropy_pred        | 5     |
| impact_pred         | 60    |
| cost_pred           | 16    |
| learning_value_pred | 4     |
| ev_pred             | 27.3  |

### Step Metrics Rationale

Moderate entropy (user-facing CLI changes) but higher p_success because it composes the shared clone/checkout primitive rather than inventing new Git behaviour.

---

## Step 5: Reconcile Docker Entrypoint Interfaces and Ledger Paths (Intent-Creation First)

**Sub‑intent recommendation:** YES
**Reasoning:** Touches multiple entrypoints and the ledger; medium conflict likelihood and needs isolated testing.
**Step Type:** REFACTOR
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Ensure entrypoints accept consistent arguments and write ledger updates to a single canonical location.
**Git branch:** I-1771890389-bootstrap-cli/I-<ts>-entrypoints-contract-ledger/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Standardise entrypoint argument conventions:
  - `intent_creator` consumes only the mounted intent JSON plus config env vars; avoid positional overload.
  - planner/executor entrypoints may remain experimental, but must not conflict with the CLI contract (fail fast if called incorrectly).
- Align ledger paths:
  - pick a single ledger root (likely `app/ledger/`) and ensure all writes go there
  - ensure ledger writes happen on the correct branch and are committed before push.
- Introduce minimal ledger envelope compliance checks (lightweight validation) for any new events added by the intent-creation flow.

### Dependencies & Criticality

**Depends on:** Step 3, Step 4
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/ledger_schema.md` (append-only integrity), `docs/safety.md` (Git boundary).
- Potential failure modes for this step:
  - Breaking existing bootstrap scripts (`test_holon_bootstrap.sh`) by changing assumptions.
  - Ledger drift creating non-comparable records.
- Guardrails and early‑abort checks:
  - Keep compatibility aliases where feasible; otherwise update tests/docs in the same sub-intent.

### Success & Discard Criteria

**Success:** Intent creation flow produces ledger entries in the canonical path and pushes a branch that includes the ledger commit.
**Discard:** If ledger schema alignment requires a systemic redesign, stop and propose a separate root intent targeting ledger governance.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.70  |
| entropy_pred        | 4     |
| impact_pred         | 45    |
| cost_pred           | 12    |
| learning_value_pred | 3     |
| ev_pred             | 18.9  |

### Step Metrics Rationale

Refactor-focused, moderate risk of regressions, but bounded scope because it targets interfaces and paths rather than adding new capabilities.

---

## Step 6: Add an Offline End-to-End Test That Proves “Clone Happens Inside the Container”

**Sub‑intent recommendation:** YES
**Reasoning:** Integration testing across Docker + Git is moderately complex and highly reusable for future pipeline intents.
**Step Type:** TEST
**Exploration level:** BALANCED

- Hypothesis being tested: A no-network, local-bare-repo test can reliably validate clone/checkout correctness without depending on GitHub availability or credentials.
- Learning target: Determine the minimal test harness that exercises containerised cloning, branch creation, ledger commit, and push.
- Maximum acceptable cost for this learning: Medium; stop if test harness becomes a full CI system.

### Intent & Git Integration

**Step Intent:** Provide a deterministic, credential-free regression test for the intent-creation CLI behaviour.
**Git branch:** I-1771890389-bootstrap-cli/I-<ts>-offline-e2e-test/_
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Create a local bare Git repo fixture during the test run and seed it with the current project state on `main`.
- Run the orchestrator container with:
  - `--network none`
  - a volume mount exposing the bare repo fixture
  - `HOLON_REPO_URL=file:///...` pointing to the mounted bare repo
  - a temp workspace volume for the clone.
- Execute `holon` intent creation against that fixture and assert:
  - the bare repo has the new intent branch ref
  - the branch contains an appended ledger record
  - output contains expected summary fields.
- Ensure the test is self-cleaning and does not depend on host-global git config.

### Dependencies & Criticality

**Depends on:** Step 4, Step 5
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (sandboxing, no-network mode), `docs/git_flow.md` (branch naming).
- Potential failure modes for this step:
  - Flaky tests due to platform-specific path handling.
  - Implicit network dependencies sneaking back in.
- Guardrails and early‑abort checks:
  - Require `--network none` as the default test mode.
  - Fail test if remote URL is not `file://` for the offline harness.

### Success & Discard Criteria

**Success:** A single command (script) passes locally and demonstrates that the container can clone + create/push the intent branch without network or host repo mutation.
**Discard:** If offline cloning cannot be made to work reliably, fall back to a mocked Git remote in tests and explicitly require networked CI later.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.60  |
| entropy_pred        | 6     |
| impact_pred         | 50    |
| cost_pred           | 16    |
| learning_value_pred | 7     |
| ev_pred             | 16.7  |

### Step Metrics Rationale

Lower p_success due to Docker/Git integration complexity; high learning value because it creates a durable regression harness for future sandbox workflows.

---

## Step 7: Document Operational Use and Safety Posture (MVP)

**Sub‑intent recommendation:** NO
**Reasoning:** Low risk; keeping docs in the parent makes review simpler and prevents drift.
**Step Type:** DOCUMENTATION
**Exploration level:** EXPLOIT

### Intent & Git Integration

**Step Intent:** Provide clear instructions for running `holon` intent creation safely (auth, sandbox networking, offline test mode).
**Git branch:** I-1771890389-bootstrap-cli/_
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

- Update README/docs to reflect the chosen CLI contract and configuration env vars.
- Document:
  - recommended auth method (token-based HTTPS or single deploy key file)
  - how to run in offline mode (file:// bare repo) vs remote mode
  - expected branch naming (`.../_`) and ledger behaviour.
- Add a short troubleshooting section (“common failure modes”): missing docker, missing token, branch exists, non-fast-forward push, ledger path mismatch.

### Dependencies & Criticality

**Depends on:** Step 4, Step 6
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: `docs/safety.md` (least privilege, sandbox boundaries).
- Potential failure modes for this step:
  - Docs encourage unsafe practices (mounting broad secrets, enabling network by default).
- Guardrails and early‑abort checks:
  - Explicitly mark any unsafe legacy behaviours as “deprecated / not recommended”.

### Success & Discard Criteria

**Success:** A new contributor can run the offline E2E test and understand how to create an intent branch safely.
**Discard:** If implementation details are still in flux, document only the MVP path and defer advanced options.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.92  |
| entropy_pred        | 1     |
| impact_pred         | 25    |
| cost_pred           | 7     |
| learning_value_pred | 2     |
| ev_pred             | 16.4  |

### Step Metrics Rationale

Very low entropy and cost; improves operational safety and reduces future support burden.

