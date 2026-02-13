# core_concepts.md

This document defines the fundamental concepts, terminology, and core metrics used throughout the Holon self-evolving AI agent system. It establishes a shared vocabulary and formalizes the contracts that govern agent
behavior and system operation.

---

## The Project as a Unique World

Each project is effectively its own **unique world** defined by a specific **rule set** and **constraints** that govern how work is done, how code behaves, and how the system evolves.

### Rule Set

The rule set includes the "language" of the project — not just programming languages, but also:

- Language versions and dialects (e.g., Python 3.9 vs 3.11, TypeScript strictness levels)
- Coding conventions and style guides
- API contracts and data schemas
- Testing frameworks and coverage requirements
- Deployment environments and runtime assumptions
- Implicit domain-specific protocols and workflows

These rules shape what is valid, safe, and effective within the project world.

### Constraints

Constraints are the boundaries and policies that must be respected, such as:

- Security policies and access controls
- Architectural patterns and design principles (e.g., microservices, event-driven)
- Performance and scalability requirements
- Compliance and regulatory mandates
- Team workflows and review processes

Constraints limit the space of acceptable changes and exploration, ensuring stability and compliance.

### Why This Matters

Foundational models provide broad priors but cannot fully capture the infinite variety of these project-specific rule sets and constraints. Each project world is unique and dynamic, evolving over time as rules and
constraints change.

Holon’s agents must therefore **learn, adapt, and evolve within the context of these unique worlds**. They do this by generating hypotheses (plans and intents) that test assumptions about the rule set and constraints,
learning from outcomes, and updating their internal models accordingly.

This recursive, fractal-like exploration and adaptation is the core mechanism that enables Holon to bridge the gap between general foundational knowledge and project-specific expertise, delivering solutions tailored to
the unique physics of each project world.

---

## 1) Intent Ontology

### 1.1 Intent

An **Intent** is a discrete unit of work or goal that an agent or the system aims to accomplish. It encapsulates a specific task, objective, or problem to solve.

- Each intent has a unique identifier.
- Each intent corresponds to a dedicated Git branch.
- Intents can be decomposed into smaller intents to manage complexity.

### 1.2 Root Intent

A **Root Intent** is a top-level intent created either by a human or an autonomous agent with earned autonomy.

- It represents a major goal or project.
- Requires human review before merging into the canonical `main` branch.
- All other intents in its hierarchy eventually merge into it.

### 1.3 Parent Intent

A **Parent Intent** is the immediate parent of a sub-intent in the intent hierarchy.

- Receives automatic merges from its sub-intents.
- May itself be a sub-intent of a higher-level intent.
- Exists at any depth except the root level.

### 1.4 Sub-Intent

A **Sub-Intent** is an intent spawned by another intent to break down complex work into manageable parts.

- Merges automatically into its parent intent based on evaluation.
- Can have its own sub-intents, forming a fractal hierarchy.

---

## 2) The Value Calculus

### 2.1 Probability of Success ($P(success)$)

- The estimated likelihood that an intent or plan will achieve its goal.
- Calculated pre-execution using a weighted combination of plan features.
- Updated post-execution based on actual outcomes for calibration.

### 2.2 Impact

- The expected positive effect or benefit delivered by completing the intent.
- Measured in domain-specific units (e.g., performance gain, cost savings).
- Used to prioritize intents with higher value.

### 2.3 Cost

- The resources, time, or effort required to execute the intent.
- Includes computational cost, human review time, and entropy introduced.
- Helps balance benefit against expenditure.

---

## 3) The Entropy Framework

### 3.1 Intent Entropy ($\Delta S_{intent}$)

- A measure of disorder, uncertainty, or risk **introduced by a single intent or action**.
- Quantifies how much an intent’s changes increase unpredictability or instability locally.
- Examples include:
    - Code complexity added by the intent
    - Risk of conflicts or rebase failures caused by the intent
    - Novelty or unpredictability of the changes
- Used to evaluate and rank intents during planning and merging.

### 3.2 System Entropy ($S_{system}$)

- A global measure of disorder or instability **across the entire system state**.
- Aggregates entropy contributions from all active intents, branches, and unresolved conflicts.
- Reflects the overall health and stability of the system.
- High system entropy indicates a fragmented, unstable, or risky state that requires maintenance.
- Managed by:
    - Pruning or discarding high-entropy intents
    - Merging completed intents to reduce branch divergence
    - Resolving conflicts and rebasing frequently
    - Enforcing entropy budgets to limit exploration risk

### 3.3 Relationship Between Intent and System Entropy

- System entropy is the **sum or aggregation** of all individual intent entropies plus additional systemic factors (e.g., unresolved conflicts, stale branches).
- Controlling system entropy requires managing the entropy of individual intents and their interactions.
- Agents must balance exploration (which increases intent entropy) with system stability (which requires keeping system entropy within bounds).

### 3.4 Entropy Budget

- A predefined limit on allowable system entropy.
- Ensures the system remains stable and manageable.
- Intents that would cause system entropy to exceed the budget may be:
    - Pruned or discarded
    - Delayed until entropy is reduced
    - Broken down into smaller, lower-entropy sub-intents

---

## 4) The Decision Engine

### 4.1 Expected Value ($EV$)

- Combines $P(success)$, Impact, Cost, and Entropy into a single metric.
- Formula (conceptual):

$$
EV = P(success) \times Impact - Cost - \Delta S
$$

- Guides autonomous decision-making, planning, and merging.

---

## 5) The Intent Lifecycle State Machine

### 5.1 States

| State     | Description                                   |
|-----------|-----------------------------------------------|
| Proposed  | Intent has been created but not yet executed. |
| Executing | Intent is currently being worked on.          |
| Completed | Intent execution finished successfully.       |
| Failed    | Intent execution finished with failure.       |
| Merged    | Intent changes merged into parent or main.    |
| Discarded | Intent abandoned and branch closed.           |

### 5.2 Transitions

- **Proposed → Executing**: When an agent starts working on the intent.
- **Executing → Completed/Failed**: Based on execution outcome.
- **Completed → Merged**: Automatic for sub-intents; human-reviewed for root intents.
- **Failed → Discarded**: Failed intents are pruned but may contribute learnings.
- **Any → Discarded**: Intent may be discarded due to low value or high entropy.

## 6) Convergence

In this system, **convergence** of a plan or intent means that the planning process has reached a point where further generation and evaluation of new plan variants is no longer expected to yield significantly better
options. In other words, the planner and evaluator agree that the current best plan(s) are good enough to proceed to execution.

### Key points about convergence:

- **Stopping Criterion:**  
  Convergence is a formal stopping condition for the planning phase. It signals that the system should stop exploring new plan variants and select the best candidate for execution.

- **Based on Metrics:**  
  Convergence decisions rely on metrics like Expected Value (EV), entropy, planning cost, and improvement trends. For example, if the EV improvements between new variants become negligible (an EV plateau), or if one plan
  clearly dominates others by a significant margin, the system considers the plan converged.

- **Entropy and Budget Constraints:**  
  Convergence also occurs if the planning process risks exceeding entropy or resource budgets, preventing runaway exploration that could destabilize the system.

- **Types of Convergence Triggers:**
    - **Dominant Plan:** One plan’s EV is sufficiently higher than all others.
    - **EV Plateau:** Recent new plans do not improve EV meaningfully.
    - **Budget Exhaustion:** Planning cost or entropy budget is reached.
    - **Max Variants or Time Limit:** Hard limits on planning iterations or duration.

- **Outcome:**  
  Once converged, the best plan is selected and passed to the executor agent for sandboxed execution.

### Why is convergence important?

- **Efficiency:** Prevents endless planning loops, saving compute and time.
- **Stability:** Avoids excessive entropy and system instability from over-exploration.
- **Decision Confidence:** Provides a principled way to decide when enough information is available to act.

---

## 7) Summary Table of Core Terms

| Term                  | Definition                                                            | Role in System                                           |
|-----------------------|-----------------------------------------------------------------------|----------------------------------------------------------|
| Intent                | Unit of work or goal                                                  | Basic building block                                     |
| Root Intent           | Top-level intent requiring human review                               | Human review boundary                                    |
| Parent Intent         | Immediate parent of a sub-intent                                      | Receives automatic merges                                |
| Sub-Intent            | Intent spawned by another intent                                      | Automatic merging and evaluation                         |
| $P(success)$          | Probability intent will succeed                                       | Guides planning and merging decisions                    |
| Impact                | Expected benefit delivered                                            | Prioritization metric                                    |
| Cost                  | Resources required                                                    | Balances benefit vs expenditure                          |
| Entropy ($\Delta S$)  | Measure of disorder or risk introduced                                | Controls system stability                                |
| Expected Value ($EV$) | Combined metric for decision-making                                   | Drives autonomous agent behavior                         |
| Convergence           | Condition when planning sufficiently explores and selects a best plan | Signals planning termination and readiness for execution |

---

This document forms the semantic foundation for the Holon system. All agents and humans should refer to it to ensure consistent understanding and operation.

---
