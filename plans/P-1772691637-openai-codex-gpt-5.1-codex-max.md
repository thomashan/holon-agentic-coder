# Plan for I-1771890389

**Plan ID:** P-1772691637-openai-codex-gpt-5.1-codex-max
**Parent Intent ID:** null
**Agent:** openai-codex/gpt-5.1-codex-max
**Created At:** 2026-03-05T06:20:37+11:00

## Planner Autonomy Summary

- Intent handling: ACCEPT_AS_IS
- Reframed intent (if applicable): n/a
- Exploration stance: balanced — mix of proven CLI patterns with targeted probes on sandbox bootstrapping to surface risks early.
- Safety priority level: elevated
- Priority Justification: Sandbox selection/execution is a core safety boundary (docs/safety.md), and the CLI will orchestrate sandboxed runs; elevated review keeps blast radius contained.

## Exploration

- Proportion of steps that are exploratory: 0.33
- Justification: Novel sandbox self-clone workflow and integration path need small exploratory spikes; remaining steps follow established repo patterns.

## Overall Plan Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.63  |
| entropy_pred        | 17.0  |
| impact_pred         | 78    |
| cost_pred           | 46    |
| learning_value_pred | 6.5   |
| ev_pred             | 32.7  |

### Strategy Rationale

We accept the intent as-is because building the `holon` CLI is prerequisite to self-orchestrated intents. Strategy is staged: capture requirements, design sandbox bootstrap, design CLI UX, then wire ledger/test scaffolds. Overall p_success is driven down by two bottlenecks: sandbox self-clone bootstrap (Step 4) and branch/intent wiring (Step 5). Entropy aggregates from step-level estimates (sum of key SSA/IRR components), with Step 4 contributing ~35% of predicted entropy. EV uses metrics formula in docs/metrics.md with λ=0.3, μ=0.5; high impact offsets moderate entropy and cost. Overall metrics are derived qualitatively from step-level predictions, weighted by criticality (bottleneck steps dominate success and entropy expectations).

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan: docs/safety.md (sandboxing, git isolation, entropy budgets), docs/metrics.md (metric semantics), docs/git_flow.md (parent-only merges).
- Potential violations or edge cases: sandbox escape risk during self-clone; branch naming drift from intent IDs; entropy overrun if CLI scaffolding touches many files.
- Mitigations built into the plan: explicit sandbox design review before implementation, branch naming checklist, isolate CLI surface area to new package to limit SSA, tests to validate container invocation without network.
- Residual risk accepted (and why): moderate novelty in sandbox bootstrap accepted for learning value and to unlock autonomy.
- Allocated Entropy Budget: not specified by parent; assume standard budget for root intent; predicted 17.0 stays within typical <30 threshold for container sandbox in safety.md.
- Predicted Plan Entropy: 17.0
- Budget Compliance: The strategy fits within budget

## Plan Description & Strategy

Deliver a first-version `holon` CLI that runs inside an isolated sandbox, clones the repo, checks out the correct branch, and scaffolds/executes intents. Work is sequenced to gather constraints, lock UX/acceptance, design the sandbox bootstrap flow, define CLI architecture, then wire branch/intent handling and tests. Exploratory probes focus on sandbox bootstrap and remote clone workflow; other steps exploit known patterns.

---

## Step 1: Map requirements & constraints

**Sub‑intent recommendation:** NO
**Reasoning:** Low risk documentation pass; no standalone value as sub-intent.
**Step Type:** INFO_GATHERING
**Exploration level:** EXPLOIT

- Hypothesis being tested: Project docs already describe intent creation flow and git rules; extracting them will reduce later rework.
- Learning target: Precise acceptance criteria, existing orchestrator hooks, entropy budget assumptions.
- Maximum acceptable cost for this learning: 4 cost units (short doc review window).

### Intent & Git Integration

**Step Intent:** Compile concrete requirements from docs (core_concepts, git_flow, metrics, safety) and any existing CLI-related code.
**Git branch:** I-1771890389-bootstrap-cli/step-1-notes
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

- Read docs: `docs/core_concepts.md`, `docs/git_flow.md`, `docs/metrics.md`, `docs/safety.md` for constraints on sandboxing and entropy.
- Scan repo for existing CLI or orchestration code (`orchestrate_intent.py`, `holon/` package) to understand current entry points.
- Summarise acceptance criteria and constraints in planner notes for downstream steps.

### Dependencies & Criticality

**Depends on:** NONE
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md (sandboxing), docs/git_flow.md (branch discipline).
- Potential failure modes: Missing key requirement leading to redesign later.
- Guardrails and early‑abort checks: Timebox review; if major gaps found, flag for scope adjustment.

### Success & Discard Criteria

**Success:** Requirements summary completed and shared with step owners; known constraints captured.
**Discard:** If constraints remain unclear after timebox, escalate for clarification before proceeding.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.9   |
| entropy_pred        | 2.0   |
| impact_pred         | 20    |
| cost_pred           | 6     |
| learning_value_pred | 3     |
| ev_pred             | 12.5  |

### Step Metrics Rationale

High success and low entropy because this is doc review; moderate impact as it de-risks later steps. Cost minimal; learning modest from clarifying constraints.

---

## Step 2: Define CLI scope, UX, and acceptance criteria

**Sub‑intent recommendation:** NO
**Reasoning:** Planning artifact; small scope; better kept within main branch flow.
**Step Type:** DOCUMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: A minimal command set (`init`, `plan`, `execute`, `status`) can cover intent lifecycle in sandboxed contexts.
- Learning target: Fit between desired UX and existing orchestrator capabilities; gaps needing future sub-intents.
- Maximum acceptable cost for this learning: 8 cost units.

### Intent & Git Integration

**Step Intent:** Produce a concise CLI spec (commands, flags, examples, acceptance tests) aligned with safety and git rules.
**Git branch:** I-1771890389-bootstrap-cli/step-2-cli-spec
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

- Draft command hierarchy and flag set (e.g., `holon intent create`, `holon intent checkout`, `holon sandbox run`).
- Define required behaviours: auto-clone into sandbox, branch naming from intent IDs, dual rebase gates, logging to ledger hooks.
- Write acceptance scenarios (Given/When/Then) for critical flows: create intent in sandbox, ensure correct branch checkout, dry-run mode.
- Validate feasibility against docs findings; adjust scope to stay within entropy budget.

### Dependencies & Criticality

**Depends on:** Step 1
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md (sandbox mandatory), docs/git_flow.md (branch naming), metrics.md (entropy budget awareness).
- Potential failure modes: Over-scoping commands; conflicting with future APIs.
- Guardrails and early‑abort checks: Keep MVP command set; defer advanced flags to follow-up intent if complexity grows.

### Success & Discard Criteria

**Success:** CLI spec drafted with acceptance criteria, reviewed against constraints, ready to guide implementation.
**Discard:** If command set balloons beyond MVP, pause and propose sub-intent for expansion.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.8   |
| entropy_pred        | 3.0   |
| impact_pred         | 40    |
| cost_pred           | 8     |
| learning_value_pred | 5     |
| ev_pred             | 22.0  |

### Step Metrics Rationale

Moderate success probability; entropy low as it is design-only. Impact higher because it shapes implementation; learning moderate due to UX validation.

---

## Step 3: Design CLI architecture and packaging

**Sub‑intent recommendation:** YES
**Reasoning:** Architectural decisions (module layout, packaging, entrypoint) are reusable and risky enough to merit isolation if complexity rises.
**Step Type:** DESIGN
**Exploration level:** BALANCED

- Hypothesis being tested: A Python-based CLI packaged under `holon` with `typer`/`click`-style interface can integrate with orchestrator and sandbox commands cleanly.
- Learning target: Module boundaries to separate sandbox orchestration from intent metadata handling; viability of dependency choices given sandbox restrictions.
- Maximum acceptable cost for this learning: 12 cost units.

### Intent & Git Integration

**Step Intent:** Produce architecture doc outlining CLI module structure, dependency choices, config resolution, and entrypoint wiring.
**Git branch:** I-1771890389-bootstrap-cli/step-3-arch
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

- Choose CLI framework (evaluate built-in argparse vs lightweight library respecting sandbox footprint).
- Define package layout (e.g., `holon/cli`, `holon/sandbox`, `holon/intent` helpers) and config discovery order.
- Specify how CLI will call sandbox bootstrapper and orchestrator, including interface contracts.
- Outline logging/telemetry hooks for ledger and dry-run behaviour.

### Dependencies & Criticality

**Depends on:** Step 2
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md (sandbox isolation), metrics.md (entropy via SSA if dependencies added).
- Potential failure modes: Heavy dependencies increasing SSA; architecture misaligned with sandbox network restrictions.
- Guardrails and early‑abort checks: Prefer stdlib; cap new deps; document rollback path if footprint grows.

### Success & Discard Criteria

**Success:** Architecture doc approved; dependency list minimal; interfaces defined for sandbox and intent modules.
**Discard:** If required deps violate sandbox policy or balloon SSA, escalate to sub-intent for alternative design.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.72  |
| entropy_pred        | 3.5   |
| impact_pred         | 55    |
| cost_pred           | 10    |
| learning_value_pred | 6     |
| ev_pred             | 25.6  |

### Step Metrics Rationale

Slightly lower success due to architectural choices and dependency risks; entropy remains moderate; impact significant because design guides code; learning notable from dependency evaluation.

---

## Step 4: Design sandbox bootstrap workflow (self-clone + branch checkout)

**Sub‑intent recommendation:** STRONGLY_YES
**Reasoning:** High criticality and moderate novelty; reusable across future intents; failure would block CLI usefulness.
**Step Type:** DESIGN
**Exploration level:** EXPLORATORY

- Hypothesis being tested: Containerised sandbox can self-clone repo, check out target branch, and run CLI with no host state leakage and no network (unless explicitly allowed).
- Learning target: Required bind mounts, credentials handling (read-only token or vendored repo), and deterministic branch checkout flow.
- Maximum acceptable cost for this learning: 18 cost units; abort if complexity exceeds or network policy prevents cloning.

### Intent & Git Integration

**Step Intent:** Specify sandbox bootstrap scripts/config (Dockerfile or wrapper) that handles repo acquisition, branch checkout, and environment preparation for `holon` CLI.
**Git branch:** I-1771890389-bootstrap-cli/step-4-sandbox-bootstrap
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Decide bootstrap source: `git clone` vs pre-baked archive; ensure reproducible source pinned to branch.
- Define container entrypoint workflow: fetch repo, checkout branch, install minimal deps, invoke CLI command passed in.
- Specify network policy: default `--network none`, allow opt-in for fetch via controlled token or pre-baked context.
- Outline caching strategy to reduce cost while respecting sandbox isolation.
- Document failure handling: clone failure, checkout failure, missing branch -> abort with clear exit codes.

### Dependencies & Criticality

**Depends on:** Step 1, Step 2
**Is Bottleneck:** YES

### Safety & Constraint Considerations

- Relevant rules: safety.md (sandbox types, escape detection), docs/git_flow.md (branch isolation).
- Potential failure modes: Network dependence breaks in offline sandbox; credential leakage; branch mismatch causing wrong checkout.
- Guardrails and early‑abort checks: Require token-less path (vendored archive) fallback; validate branch arg matches intent ID format before checkout; enforce read-only mount except workspace.

### Success & Discard Criteria

**Success:** Documented bootstrap flow with clear inputs/outputs, security posture, and error handling; path chosen (clone vs archive) validated in design.
**Discard:** Abort if secure repo acquisition cannot be defined without violating sandbox/network policy; escalate to parent for guidance.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.55  |
| entropy_pred        | 6.0   |
| impact_pred         | 70    |
| cost_pred           | 12    |
| learning_value_pred | 8     |
| ev_pred             | 20.5  |

### Step Metrics Rationale

Lower success due to novelty and security constraints; entropy higher from SSA/IRR of container scripts; impact high because sandbox bootstrap is foundational; learning high from exploring secure clone patterns.

---

## Step 5: Define intent/branch orchestration wiring and ledger touchpoints

**Sub‑intent recommendation:** YES
**Reasoning:** Cross-cutting integration with orchestrator and ledger; reusable and riskier than straightforward coding.
**Step Type:** DESIGN
**Exploration level:** BALANCED

- Hypothesis being tested: CLI can translate user commands into intent metadata, branch creation (`I-...`), and ledger-ready events without violating git flow.
- Learning target: Minimal interfaces required between CLI and existing orchestrate_intent code; metadata schema needed.
- Maximum acceptable cost for this learning: 10 cost units.

### Intent & Git Integration

**Step Intent:** Specify how CLI creates intents, names branches, records plan metadata, and interacts with ledger hooks and orchestrator.
**Git branch:** I-1771890389-bootstrap-cli/step-5-intent-wiring
**Sub‑intent** NEW

### Implementation Details (No code blocks, only logic/steps)

- Map command options to intent JSON schema (id, title, description, branch path).
- Define branch creation/checkout flow consistent with docs/git_flow.md (parent→child nesting, dual rebase gates). 
- Outline ledger/logging events the CLI should emit or queue for executor.
- Identify minimal storage for local state (e.g., `.holon/intent.json`) within sandbox.

### Dependencies & Criticality

**Depends on:** Steps 1–3
**Is Bottleneck:** YES (shared interface risk)

### Safety & Constraint Considerations

- Relevant rules: docs/git_flow.md (no merges to main), metrics.md (entropy tracking), safety.md (sandbox boundaries for logging).
- Potential failure modes: Incorrect branch paths; ledger schema drift; state leakage outside workspace.
- Guardrails and early‑abort checks: Validate branch names against intent ID regex; keep state under project root; design for dry-run mode before writing ledger entries.

### Success & Discard Criteria

**Success:** Documented wiring spec covering branch operations, intent metadata handling, and ledger touchpoints with clear contracts.
**Discard:** If orchestrator/ledger interfaces are too immature, pause and create follow-up intent to extend them.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.6   |
| entropy_pred        | 5.0   |
| impact_pred         | 65    |
| cost_pred           | 10    |
| learning_value_pred | 7     |
| ev_pred             | 23.5  |

### Step Metrics Rationale

Moderate success due to integration risk; entropy mid-level from branch/state handling; high impact because correctness here underpins all CLI operations; learning significant from defining interfaces.

---

## Step 6: Testing strategy, fixtures, and documentation plan

**Sub‑intent recommendation:** NO
**Reasoning:** Scoped to planning tests/docs; low risk.
**Step Type:** TEST
**Exploration level:** EXPLOIT

- Hypothesis being tested: We can cover sandbox bootstrap and CLI flows with containerised integration tests and lightweight unit tests.
- Learning target: Identify feasible test harness (pytest + docker), fixtures for sandboxed clone, and doc outputs.
- Maximum acceptable cost for this learning: 6 cost units.

### Intent & Git Integration

**Step Intent:** Define test matrix and documentation updates needed for CLI MVP.
**Git branch:** I-1771890389-bootstrap-cli/step-6-tests-docs
**Sub‑intent** NONE

### Implementation Details (No code blocks, only logic/steps)

- Outline unit tests for command parsing and branch-name validation.
- Plan integration test that spins container with pre-baked repo archive to validate clone/checkout flow and dry-run intent creation.
- Identify docs to update: README quickstart, new `docs/cli.md`, sandbox usage notes.
- Establish success metrics for tests (pass/fail, coverage targets where relevant).

### Dependencies & Criticality

**Depends on:** Steps 3, 4, 5
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md (sandboxed tests), metrics.md (entropy from SSA if fixtures large).
- Potential failure modes: Integration tests require network; fixtures too big; docs drift from behaviour.
- Guardrails and early‑abort checks: Use local archives instead of live network; keep fixtures small; align docs to acceptance criteria from Step 2.

### Success & Discard Criteria

**Success:** Test plan and doc update list ready; feasible to execute in container without network.
**Discard:** If integration testing cannot be sandboxed, flag need for alternate validation strategy.

### Metrics

| metric              | value |
|---------------------|-------|
| p_success_pred      | 0.78  |
| entropy_pred        | 2.5   |
| impact_pred         | 35    |
| cost_pred           | 6     |
| learning_value_pred | 4     |
| ev_pred             | 15.4  |

### Step Metrics Rationale

High success probability; low entropy; moderate impact by enabling regression protection; learning modest from test harness design.

---
