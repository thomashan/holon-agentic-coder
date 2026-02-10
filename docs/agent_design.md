# agent_design.md

This document provides a high-level architectural overview and behavioral design principles for the autonomous agents within the Holon system. It defines the governance framework, trust and autonomy models, and
interaction protocols that guide agent behavior and system integration.

---

## 1) Agent Ecosystem Overview

The Holon system consists of multiple autonomous agents collaborating to plan, execute, learn, and evolve. Agents operate within a fractal intent hierarchy and adhere to strict safety, trust, and operational contracts.

### Key Components

- **Meta-Agent (Orchestrator):** Coordinates intent lifecycle, agent dispatch, and system state.
- **Worker Agents:** Specialized agents (Planner, Executor, Curator, Evaluator, Researcher) performing domain-specific tasks.
- **Knowledge Base (KB):** Shared repository of patterns, tactics, estimators, and failure modes.
- **Ledger:** Immutable event log capturing all agent actions, decisions, and system state changes.

---

## 2) Agent Roles and Responsibilities

| Agent Type | Primary Role                                  | Autonomy Scope                   |
|------------|-----------------------------------------------|----------------------------------|
| Meta-Agent | Orchestrates intent lifecycle and agent tasks | System-wide coordination         |
| Planner    | Generates and evaluates plan variants         | Intent-level planning            |
| Executor   | Executes plans in sandboxed environments      | Intent-level execution           |
| Curator    | Extracts patterns and failure modes           | Knowledge base curation          |
| Evaluator  | Selects best plans and manages convergence    | Planning evaluation              |
| Researcher | Proposes estimator and policy improvements    | System-level learning and tuning |

---

## 3) Trust and Autonomy Model

Agents operate under a **trust-bounded autonomy** framework, where capabilities expand with demonstrated reliability.

| Trust Level   | Capabilities                                                        | Autonomy Examples                         |
|---------------|---------------------------------------------------------------------|-------------------------------------------|
| Baseline      | Execute assigned tasks, generate basic plans                        | Execute plans, generate simple variants   |
| Medium        | Spawn sub-intents, propose patterns and tactics                     | Decompose intents, propose KB entries     |
| High          | Propose root intents, novel plans, and advanced tactics             | Autonomous goal-setting, complex planning |
| Highest       | Propose estimator improvements, routing policies, and system tuning | Meta-learning, policy refinement          |
| Full (Future) | Modify core invariants and safety policies (with human approval)    | System governance and evolution           |

---

## 4) Behavioral Contracts and Safety

Agents must adhere to the following immutable contracts unless explicitly overridden by human review:

- **Sandboxing:** Agents execute only within isolated environments; no sandbox escape allowed.
- **Git Discipline:** Agents must follow mandatory rebase and merge rules.
- **Metric-Driven Decisions:** Agents use defined metrics (P(success), Entropy, Impact, Cost, EV) for all planning and execution.
- **No Core Invariant Modification:** Agents cannot autonomously change core system invariants or safety policies.
- **Human Review Boundary:** Root intents require human approval before promotion; sub-intents merge automatically based on evaluation.
- **Communication via Ledger:** All inter-agent communication and state changes are logged in the ledger; no direct agent-to-agent messaging.

---

## 5) Agent Interaction Protocols

### 5.1 Intent Lifecycle Management

- Meta-Agent creates and tracks intents.
- Planner agents generate multiple plan variants per intent.
- Evaluator agents select plans based on Expected Value and convergence policies.
- Executor agents run selected plans in sandboxes.
- Curator agents extract learnings and update the KB.
- Researcher agents propose system-level improvements.

### 5.2 Model Routing

- Agents select models dynamically based on intent complexity and entropy.
- Routing tiers (Flash, Medium, Deep) balance speed, cost, and capability.
- Routing decisions are logged and influence agent trust and evolution.

### 5.3 Trust Updates

- Agent trust levels are updated based on execution success, calibration accuracy, and adherence to contracts.
- Trust changes affect autonomy scope and task assignments.

---

## 6) Autonomy Escalation and Earned Autonomy

Agents start with limited capabilities and earn higher autonomy by demonstrating:

- Consistent success in assigned tasks.
- Accurate metric predictions and low calibration error.
- Responsible spawning and merging of sub-intents.
- Compliance with safety and operational contracts.

Autonomy escalation enables:

- Recursive intent decomposition without human intervention.
- Autonomous root intent generation (subject to trust gates).
- Proposal of estimator and policy improvements.

---

## 7) Agent Lifecycle

1. **Creation:** Agents are instantiated with assigned trust levels and models.
2. **Task Assignment:** Meta-Agent dispatches intents and plans based on agent capabilities.
3. **Execution:** Agents perform tasks, log results, and update metrics.
4. **Learning:** Agents update internal models and propose KB entries or system improvements.
5. **Trust Evaluation:** Agent trust is recalculated and autonomy adjusted.
6. **Retirement:** Agents may be retired or upgraded based on performance and system needs.

---

## 8) Summary

This design framework ensures that Holon’s agents operate safely, efficiently, and collaboratively within a governed ecosystem. Trust-bounded autonomy and rigorous behavioral contracts enable scalable, recursive, and
self-improving AI agent behavior while maintaining human oversight where necessary.

---

## Related Documents

- [`agents.md`](agents.md) — Detailed agent type specifications and code examples
- [`git_flow.md`](git_flow.md) — Git branching and merging discipline
- [`core_concepts.md`](core_concepts.md) — Fundamental terminology and metrics
- [`safety.md`](safety.md) — Safety policies and sandboxing
- [`ledger_schema.md`](ledger_schema.md) — Event logging and communication protocols
- [`architecture.md`](architecture.md) — Overall system architecture and data flow
