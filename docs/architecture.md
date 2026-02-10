### architecture.md

This document describes the **Holon / FIEE (Fractal Intent Evolution Engine)** architecture: a self-evolving, git-native multi-agent system that plans competitively, executes in sandboxes, and improves via measured
feedback loops.

#### Scope

- What the system is made of (components + responsibilities)
- How work flows (intent → plans → execution → measurement → learning)
- Where invariants live (git discipline, metric “physics”, autonomy boundaries)
- How routing works (different models for different work, as a selection pressure)

---

### Core invariants (non-negotiable)

#### 1) Git is the universal state machine

- All intents, plans, executions, and outcomes are represented as git artifacts.
- Agents never “just do work”; they **propose diffs**.

#### 2) Fractal intent (infinite recursive depth)

- Any intent may spawn sub-intents recursively.
- Sub-intents are first-class and follow the same rules as root intents.

#### 3) Competitive planning variants per intent

- Multiple plan variants compete as hypotheses.
- Plans are scored using shared “physics” metrics (P(success), ΔS, EV, Cost, Impact).

#### 4) Strict rebase discipline; parent-only merges

- **Sub-intents rebase from parent before and after execution.**
- **Sub-intents may merge ONLY into their parent intent branch.**
- **No direct merges from sub-intents to `main`.**
- Human review happens at the **parent intent boundary** (configurable), not at every sub-intent.

#### 5) Sandboxed exploration is allowed (including risky)

- Risky exploration is allowed because it happens in disposable branches + sandboxes.
- The system is designed to **learn from failures**, not just avoid them.

#### 6) Metrics are “physics”

- Metric definitions are stable contracts.
- Estimators may evolve, but definitions, ranges, and ledger recording are immutable without explicit approval.

---

### High-level architecture

#### Component map

- **Intent Registry**
    - Stores intent metadata: IDs, parent/child links, state, constraints, trust requirements.
- **Planner (Variant Generator)**
    - Produces multiple candidate **Plan Graphs** for the same intent.
- **Plan Evaluator**
    - Scores plan variants using metrics + constraints.
- **Convergence Policy**
    - Decides when to stop generating new plan variants (EV plateau, entropy budget, dominant winner).
- **Router**
    - Selects model tiers per task (fast/cheap vs deep/careful), recorded as metadata.
- **Executor (Sandbox Runner)**
    - Runs a chosen plan variant in an isolated environment, producing artifacts + measurements.
- **Evolution Ledger (Write-once log)**
    - Append-only record of: predictions, actions, diffs, model routing decisions, outcomes, measured metrics.
- **Knowledge Base (Read/write store)**
    - Curated knowledge extracted from the ledger: patterns, reusable modules, known pitfalls, estimator proposals.
- **Meta-Agent / Orchestrator**
    - Watches for new work, dispatches planner/executor jobs, enforces git discipline and budgets.
- **Human Review Boundary**
    - Where humans approve promotions (typically parent intent → `main`).

---

### Data products: Ledger vs Knowledge Base

#### Evolution Ledger (append-only, forensic)

- Purpose: auditability and measurement.
- Stores:
    - intent_id, plan_id, variant_id
    - predicted metrics (P(success), ΔS, Impact, Cost, EV)
    - routing decision (model_id, tier, reason)
    - execution logs and outcomes
    - git commit SHAs / diffs
    - post-execution measurements + calibration errors

#### Knowledge Base (curated, reusable)

- Purpose: accelerate future planning and improve estimators.
- Stores:
    - proven tactics/patterns (“playbooks”)
    - common failure modes + mitigations
    - reusable code snippets/modules
    - estimator proposals, comparisons, and approvals
    - routing heuristics and observed ROI

---

### End-to-end lifecycle (intent → learning)

#### 1) Intent creation

An intent is created by one of:

- **Human root intent** (bootstrap and high-level goals)
- **Trusted agent root intent** (autonomous goal-setting; gated by trust)
- **Reactive/system intent** (triggered by failures, conflicts, regressions)

Each intent includes:

- goal statement
- constraints (entropy budget, cost budget, time budget, trust requirements)
- scope boundaries (allowed modules, forbidden modules, sandbox requirements)
- parent pointer (unless root)

#### 2) Competitive planning (plan variants)

For each intent, the planner generates plan variants:

- Each variant is a structured plan graph (steps + dependencies + sub-intents)
- Each variant includes predicted:
    - P(success)
    - ΔS (entropy)
    - Impact
    - Cost
    - EV

Variants are recorded even if rejected.

#### 3) Plan evaluation + selection

The evaluator:

- validates plan feasibility (dependency availability, tool availability, sandbox constraints)
- scores each variant via EV
- chooses the current best variant
- triggers **convergence** if further planning is unlikely to improve EV meaningfully

#### 4) Routing (model selection)

The router selects model tier per role/task:

- Low-entropy, low-novelty tasks → fast/cheap model (e.g., “Flash” class)
- High-entropy, high-novelty, high-impact tasks → deeper model (e.g., “DeepThink” class)

Routing decisions are logged:

- model_id, tier
- routing_reason
- expected benefit vs cost

Routing becomes a **selection pressure**: better routing improves ROI.

#### 5) Execution (sandboxed)

Executor:

- creates a sandbox environment
- checks out the correct branch
- enforces git discipline (rebase rules)
- runs plan steps (may spawn sub-intents where permitted)
- produces code changes, tests, artifacts, logs

#### 6) Measurement (post-execution)

After execution:

- measure actual P(success) (binary success/failure per intent definition)
- measure actual ΔS from diff + dependency changes + conflicts + coverage deltas
- measure actual Impact (domain-specific)
- compute calibration error for predictions

All results are appended to the ledger.

#### 7) Learning / KB update

Curate:

- if successful: extract reusable patterns into KB
- if failed: extract failure modes and mitigation steps
- if predictions were off: propose estimator improvements (requires approval)

---

### Branch topology and authority boundaries

#### Principle: merges flow up the intent tree

- Sub-intent branches merge into parent intent branches only.
- Parent intent branch is the integration surface.
- Only parent intent branches (or designated promotion branches) can merge into `main`.

#### Human review boundary

Human review occurs at:

- parent intent completion (promotion to `main`)
- estimator definition updates
- trust/autonomy level changes
- changes to “physics” or governance modules

---

### Planning convergence policy (architecture role)

Convergence prevents infinite planning loops.

Convergence triggers may include:

- **EV plateau:** incremental EV gains fall below threshold for N variants
- **entropy budget exhausted:** predicted ΔS exceeds remaining budget
- **dominant plan:** a plan wins by margin and confidence is high
- **planning cost cap:** planning spend exceeds configured cost/time limits

Convergence outcome:

- select best-known plan variant
- record convergence reason + final plan set

---

### Autonomy and trust levels (corrected: intent proposal is privileged)

Holon autonomy is staged such that **work is broadly allowed**, but **goal-setting is gated**.

#### Baseline (low trust / default agent)

- Agent can generate **plans** (variants) for assigned intents.
- Agent can execute **actions** inside sandbox for assigned intents, within budgets.
- Agent cannot create new root intents.
- Agent can propose sub-intents only if the parent intent policy allows it (often “no” at first).

Rationale: executing bounded work in a sandbox is safer than inventing new goals.

#### Medium trust (decomposition allowed)

- Agent can spawn **sub-intents** during planning/execution, subject to:
    - parent intent constraints
    - entropy/cost budgets
    - mandatory rebase + parent-only merge rules
- Agent still cannot propose new root intents.

#### High trust (autonomous goal-setting)

- Agent can propose **new root intents** (agent-generated intents) that enter the same validation pipeline:
    - predicted metrics (P(success), ΔS, Impact, Cost, EV)
    - justification + alignment constraints
    - explicit scope boundaries
- Root-intent proposals may still require human acceptance depending on configuration.

#### Highest trust (governance proposals; still human-approved)

- Agent can propose changes to:
    - estimator implementations
    - routing heuristics
    - governance policies
- Human approval remains required for any changes that affect metric definitions (“physics”) or system invariants.

#### Trust is earned via measurement

Trust level is influenced by:

- calibration quality (P(success), ΔS, Impact)
- rate of successful intent completion
- compliance with git discipline
- safety violations (immediate penalties)

---

### Minimal module map (conceptual)

- `core/`
    - intent model, plan model, IDs, invariants
- `planning/`
    - variant generation, plan graph, convergence policy
- `routing/`
    - model router, routing evaluation
- `execution/`
    - sandbox runner, tool adapters, rebase enforcer
- `metrics/`
    - estimators, post-measurement, calibration
- `ledger/`
    - append-only event logging, schemas
- `kb/`
    - curated knowledge, retrieval APIs, write rules
- `orchestrator/`
    - meta-agent loop, scheduling, work queue

---

### Interfaces (what components exchange)

#### Intent → Planner

- intent_id
- goal + constraints
- context pointers (KB refs + ledger summaries)
- allowed tool/model set

#### Planner → Evaluator

- plan_variants[] (each with predicted metrics + structure)

#### Evaluator → Router

- chosen plan variant + task decomposition with complexity/entropy cues

#### Router → Executor

- model assignments per subtask
- routing metadata

#### Executor → Ledger

- diffs, SHAs, logs
- predicted vs actual metrics
- outcomes and errors

#### Ledger/K.B. → Planner

- retrieved patterns
- prior similar intents + outcomes
- estimator versions and calibration stats

---

### Notes on extensibility

This architecture is intentionally modular:

- you can replace planners, routers, estimators without rewriting the whole system
- the ledger remains the stable audit backbone
- KB evolves slowly and deliberately to avoid poisoning

---

### What this architecture optimizes for

- auditability (every action has a trace)
- safety through containment (sandbox + branch discipline)
- continuous improvement (calibration + selection pressure)
- scalable delegation (fractal intent, authority boundaries)
- efficient inference spend (routing as evolution)
