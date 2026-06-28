# Appendix: Key Terminology and Metrics

This document provides a reference for the core mathematical and operational terms used across the Holon system
documentation.

## Core Metrics

### Expected Value ($EV$)

The primary selection objective used to compare competing plan variants for the same intent. Formula:
$$EV = P(success)\cdot Impact + \mu\cdot LearningValue - \lambda \cdot \Delta S_{intent} - Cost$$

### Success ($success_{actual}$)

A binary outcome representing whether an executed intent satisfied its acceptance criteria.

- $success_{actual} = 1$: The intent's acceptance criteria were fully met (all tests pass, lint requirements satisfied,
  no sandbox violations, no merge conflicts).
- $success_{actual} = 0$: Otherwise.

### $P(success)$ / $P(success)_{pred}$

The predicted probability (between $0.0$ and $1.0$) that executing a plan will successfully meet the intent's acceptance
criteria.

### Learning Value

The epistemic gain delivered to the system by executing an intent, independent of its success or failure (e.g.,
discovery of new failure modes, creation of reusable knowledge base entries, or exploration of novel solutions).

### Impact

An estimate of the utility or benefit delivered if the intent succeeds. Measured on a normalized scale (typically
0–100).

### Cost

The expected resource consumption (time, compute, tokens, developer review time) required to execute the plan.

---

## Entropy Framework

### Entropy

A measure of disorder, uncertainty, and stability within the project world. In Holon, it represents the risk of
introducing instability or unpredictable behaviors.

### Per-Intent Entropy ($\Delta S_{intent}$ or $\Delta S$)

An estimate of the local disorder and risk introduced by executing a specific plan. It acts as a risk/complexity proxy
computed using five primary factors (SSA, IRR, CL, SER, NOV):
$$\Delta S_{intent,pred} = w_1\cdot SSA + w_2\cdot IRR + w_3\cdot CL + w_4\cdot SER + w_5\cdot NOV$$

### System Entropy ($S_{system}$)

A global measure of disorder across the entire system state, aggregating the contributions of all active intents,
branches, and unresolved conflicts.

---

## Intent Entropy Components

### State Surface Area (SSA)

The physical footprint of the change. This includes the expected number of files modified, lines of code changed, and
the configuration surface area (such as dependency manifests or build scripts).

### Irreversibility (IRR)

The difficulty or risk associated with rolling back the changes if execution fails. High-irreversibility changes include
database schema migrations, data-destructive operations, or major public API contract updates.

### Conflict Likelihood (CL)

The probability of rebase or merge conflicts. Factors include file overlap with concurrent tasks, modifications to
highly active files ("hot files"), and branch divergence from the parent commit.

### Sandbox Escape Risk (SER)

The probability that executing the plan will violate sandbox constraints. This includes executing untrusted shell
commands, making unexpected network calls, writing outside the sandbox directory, or accessing environment secrets.

### Novelty (NOV)

The degree of unfamiliarity of the approach, technologies, or code paths relative to the Knowledge Base and historical
ledger data.
