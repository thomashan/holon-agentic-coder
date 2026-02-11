# examples.md

This document provides **concrete examples** of how Holon operates in practice, from simple single-intent executions to complex multi-level recursive decompositions.

These examples illustrate:

- **Intent creation and planning**
- **Competitive planning with multiple variants**
- **Metric estimation and EV calculation**
- **Execution in sandboxes**
- **Git flow (rebase, merge)**
- **Recursive sub-intent spawning**
- **Human review and promotion**
- **KB extraction and learning**
- **Failure handling and recovery**

---

## Example 1: Simple root intent (bootstrap P(success) estimator)

### Scenario

Human wants to bootstrap the naive P(success) estimator as the first intent in the system.

### Step-by-step execution

#### 1) Intent creation (human-initiated)

```bash
$ holon intent create \
--goal "Implement naive P(success) estimator" \
--constraints '{"entropy_budget": 50, "cost_budget": 200, "time_budget_sec": 3600}' \
--scope '{"allowed_paths": ["holon/metrics/"], "sandbox_required": true}'
```

**Ledger event:**

```json
{
  "event_type": "intent_created",
  "ts": "2026-02-10T10:00:00Z",
  "seq": 1,
  "payload": {
    "intent_id": "I-root-001-bootstrap-p-success",
    "parent_intent_id": null,
    "goal": "Implement naive P(success) estimator",
    "constraints": {
      "entropy_budget": 50,
      "cost_budget": 200,
      "time_budget_sec": 3600
    },
    "scope": {
      "allowed_paths": [
        "holon/metrics/"
      ],
      "sandbox_required": true
    }
  }
}
```

**Git:**

```bash
$ git checkout -b intent/I-root-001-bootstrap-p-success
```

---

#### 2) Planning phase (agent generates variants)

**Meta-agent dispatches to planner agent:**

- Agent: `agent-planner-01` (Gemini Flash, baseline trust)
- Task: Generate 3 plan variants

**Planner agent generates variants:**

**Variant 1: Weighted feature sum**

```json
{
  "plan_id": "P-I-root-001-bootstrap-p-success-v1-flash",
  "variant_id": "v1",
  "model": {
    "provider": "gemini",
    "model_id": "gemini-2.0-flash",
    "tier": "flash"
  },
  "plan_graph": {
    "steps": [
      {
        "id": 1,
        "description": "Define feature extraction (coverage, dependencies, novelty, depth)",
        "tool": "python"
      },
      {
        "id": 2,
        "description": "Assign bootstrap weights (0.3, 0.3, -0.2, -0.1)",
        "tool": "python"
      },
      {
        "id": 3,
        "description": "Implement weighted sum formula",
        "tool": "python"
      },
      {
        "id": 4,
        "description": "Clamp to [0, 1]",
        "tool": "python"
      },
      {
        "id": 5,
        "description": "Write unit tests",
        "tool": "pytest"
      }
    ],
    "sub_intents": []
  },
  "predicted": {
    "p_success": 0.75,
    "entropy": 12.0,
    "impact": 80,
    "cost": 50,
    "ev": "0.75 * 80 - 0.3 * 12.0 - 50 = 6.4",
    "lambda": 0.3
  }
}
```

**Variant 2: Lookup table**

```json
{
  "plan_id": "P-I-root-001-bootstrap-p-success-v2-flash",
  "variant_id": "v2",
  "model": {
    "provider": "gemini",
    "model_id": "gemini-2.0-flash",
    "tier": "flash"
  },
  "plan_graph": {
    "steps": [
      {
        "id": 1,
        "description": "Define intent type categories",
        "tool": "python"
      },
      {
        "id": 2,
        "description": "Create lookup table (type → base P(success))",
        "tool": "python"
      },
      {
        "id": 3,
        "description": "Implement lookup with fallback",
        "tool": "python"
      },
      {
        "id": 4,
        "description": "Write unit tests",
        "tool": "pytest"
      }
    ],
    "sub_intents": []
  },
  "predicted": {
    "p_success": 0.65,
    "entropy": 8.0,
    "impact": 60,
    "cost": 30,
    "ev": "0.65 * 60 - 0.3 * 8.0 - 30 = 6.6",
    "lambda": 0.3
  }
}
```

**Variant 3: Hybrid (lookup + adjustment)**

```json
{
  "plan_id": "P-I-root-001-bootstrap-p-success-v3-flash",
  "variant_id": "v3",
  "model": {
    "provider": "gemini",
    "model_id": "gemini-2.0-flash",
    "tier": "flash"
  },
  "plan_graph": {
    "steps": [
      {
        "id": 1,
        "description": "Define intent type categories with base scores",
        "tool": "python"
      },
      {
        "id": 2,
        "description": "Extract plan features (novelty, depth)",
        "tool": "python"
      },
      {
        "id": 3,
        "description": "Adjust base score with feature penalties",
        "tool": "python"
      },
      {
        "id": 4,
        "description": "Clamp to [0, 1]",
        "tool": "python"
      },
      {
        "id": 5,
        "description": "Write unit tests",
        "tool": "pytest"
      }
    ],
    "sub_intents": []
  },
  "predicted": {
    "p_success": 0.80,
    "entropy": 15.0,
    "impact": 85,
    "cost": 60,
    "ev": "0.80 * 85 - 0.3 * 15.0 - 60 = 3.5",
    "lambda": 0.3
  }
}
```

**Ledger events:**

```json
{
  "event_type": "plan_variant_created",
  "seq": 2,
  "payload": {
    "plan_id": "P-I-root-001-bootstrap-p-success-v1-flash",
    ...
  }
}
{
  "event_type": "plan_variant_created",
  "seq": 3,
  "payload": {
    "plan_id": "P-I-root-001-bootstrap-p-success-v2-flash",
    ...
  }
}
{
  "event_type": "plan_variant_created",
  "seq": 4,
  "payload": {
    "plan_id": "P-I-root-001-bootstrap-p-success-v3-flash",
    ...
  }
}
```

---

#### 3) Plan evaluation and selection

**Evaluator agent ranks by EV:**

1. v2: EV = 6.6 (winner)
2. v1: EV = 6.4
3. v3: EV = 3.5

**Convergence check:**

- EV gap between v2 and v1: 0.2 (< dominant_plan_threshold of 5.0)
- Only 3 variants generated (< max_variants of 5)
- Planning cost: 140 (< planning_budget of 200)

**Decision:** Generate one more variant to check for improvement.

**Variant 4: Simple heuristic**

```json
{
  "plan_id": "P-I-root-001-bootstrap-p-success-v4-flash",
  "variant_id": "v4",
  "predicted": {
    "p_success": 0.60,
    "entropy": 5.0,
    "impact": 50,
    "cost": 20,
    "ev": "0.60 * 50 - 0.3 * 5.0 - 20 = 8.5"
  }
}
```

**Re-rank:**

1. **v4: EV = 8.5 (new winner)**
2. v2: EV = 6.6
3. v1: EV = 6.4
4. v3: EV = 3.5

**Convergence check:**

- EV gap between v4 and v2: 1.9 (< dominant_plan_threshold)
- 4 variants generated
- Planning cost: 160

**Decision:** EV improvement from v2 to v4 is 1.9. This is significant, but not dominant. Generate one more variant.

**Variant 5: Constant baseline**

```json
{
  "plan_id": "P-I-root-001-bootstrap-p-success-v5-flash",
  "variant_id": "v5",
  "predicted": {
    "p_success": 0.55,
    "entropy": 3.0,
    "impact": 40,
    "cost": 15,
    "ev": "0.55 * 40 - 0.3 * 3.0 - 15 = 6.1"
  }
}
```

**Final rank:**

1. **v4: EV = 8.5 (winner)**
2. v2: EV = 6.6
3. v1: EV = 6.4
4. v3: EV = 3.5
5. v5: EV = 6.1

**Convergence check:**

- EV improvement from v4 to v5: -2.4 (negative, no improvement)
- **Convergence reason: EV plateau** (last variant did not improve)

**Ledger events:**

```json
{
  "event_type": "planning_converged",
  "seq": 9,
  "payload": {
    "intent_id": "I-root-001-bootstrap-p-success",
    "variants_considered": [
      "v1",
      "v2",
      "v3",
      "v4",
      "v5"
    ],
    "winner_plan_id": "P-I-root-001-bootstrap-p-success-v4-flash",
    "reason": "ev_plateau"
  }
}
{
  "event_type": "plan_selected",
  "seq": 10,
  "payload": {
    "plan_id": "P-I-root-001-bootstrap-p-success-v4-flash",
    "predicted": {
      "p_success": 0.60,
      "entropy": 5.0,
      "impact": 50,
      "cost": 20,
      "ev": 8.5
    }
  }
}
```

---

#### 4) Execution phase

**Rebase from parent (main) before execution:**

```bash
$ git fetch origin
$ git rebase origin/main
# No conflicts (first intent)
```

**Ledger event:**

```json
{
  "event_type": "git_rebase_completed",
  "seq": 11,
  "payload": {
    "intent_id": "I-root-001-bootstrap-p-success",
    "branch": "intent/I-root-001-bootstrap-p-success",
    "status": "success",
    "conflict_files": []
  }
}
```

**Executor agent executes plan v4:**

**Sandbox creation:**

```bash
$ docker run --rm --network none -v $(pwd):/workspace holon-sandbox:latest
```

**Ledger event:**

```json
{
  "event_type": "sandbox_created",
  "seq": 12,
  "payload": {
    "sandbox_id": "S-20260210-1005-a3f2",
    "sandbox_type": "container"
  }
}
```

**Execute steps:**

```python
# Step 1: Implement simple heuristic
def estimate_p_success_v1(plan, ledger):
    
    # Simple heuristic: base 0.6, adjust for novelty
    base = 0.6
    novelty_penalty = 0.2 * plan.novelty
    return max(0.0, min(1.0, base - novelty_penalty))
    
# Step 2: Write to file
with open('holon/metrics/p_success.py', 'w') as f:
        f.write(code)

# Step 3: Write unit tests
# ... test code ...

# Step 4: Run tests
$ pytest
holon / metrics / test_p_success.py
# All tests pass
```

**Ledger events:**

```json
{
  "event_type": "tool_call",
  "seq": 13,
  "payload": {
    "tool_name": "python",
    "exit_code": 0
  }
}
{
  "event_type": "tool_call",
  "seq": 14,
  "payload": {
    "tool_name": "pytest",
    "exit_code": 0
  }
}
```

**Measure actual metrics:**

```python
actual_p_success = 1.0  # Success (tests passed)
actual_entropy = 4.2  # Measured: 1 file modified, 45 lines added, 0 conflicts
actual_impact = 55  # Measured: estimator now callable, tests pass
actual_cost = 18  # Measured: 3 minutes execution time
```

**Ledger event:**

```json
{
  "event_type": "execution_completed",
  "seq": 15,
  "payload": {
    "intent_id": "I-root-001-bootstrap-p-success",
    "status": "success",
    "actual": {
      "p_success": 1.0,
      "entropy": 4.2,
      "impact": 55,
      "cost": 18
    },
    "calibration": {
      "p_success_error": 0.40,
      "entropy_error": 0.8,
      "impact_error": 5.0
    },
    "metadata": {
      "note": "Errors calculated as |predicted - actual|. Predicted values were: p_success: 0.60, entropy: 5.0, impact: 50"
    }
  }
}
```

**Rebase from parent (main) after execution:**

```bash
$ git fetch origin
$ git rebase origin/main
# No conflicts
```

**Ledger event:**

```json
{
  "event_type": "git_rebase_completed",
  "seq": 16,
  "payload": {
    "status": "success"
  }
}
```

---

#### 5) Human review

**Review package generated:**

```json
{
  "intent_id": "I-root-001-bootstrap-p-success",
  "goal": "Implement naive P(success) estimator",
  "status": "awaiting_review",
  "branch": "intent/I-root-001-bootstrap-p-success",
  "predicted_metrics": {
    "p_success": 0.60,
    "entropy": 5.0,
    "impact": 50,
    "ev": 8.5
  },
  "actual_metrics": {
    "p_success": 1.0,
    "entropy": 4.2,
    "impact": 55,
    "ev": 11.8
  },
  "calibration": {
    "p_success_error": 0.40,
    "entropy_error": 0.8,
    "impact_error": 5.0
  },
  "diff_summary": {
    "files_modified": 2,
    "lines_added": 45,
    "lines_deleted": 0
  },
  "test_results": {
    "passed": 5,
    "failed": 0,
    "coverage": 0.92
  }
}
```

**Ledger event:**

```json
{
  "event_type": "human_review_requested",
  "seq": 17,
  "payload": {
    "intent_id": "I-root-001-bootstrap-p-success",
    "review_kind": "promotion"
  }
}
```

**Human reviews and approves:**

```bash
$ holon review approve I-root-001-bootstrap-p-success
```

**Ledger event:**

```json
{
  "event_type": "human_review_decision",
  "seq": 18,
  "payload": {
    "intent_id": "I-root-001-bootstrap-p-success",
    "decision": "approved",
    "reviewer": "human@example.com"
  }
}
```

---

#### 6) Merge to main

```bash
$ git checkout main
$ git merge intent/I-root-001-bootstrap-p-success
$ git push origin main
```

**Ledger event:**

```json
{
  "event_type": "intent_promoted_to_main",
  "seq": 19,
  "payload": {
    "intent_id": "I-root-001-bootstrap-p-success",
    "merge_sha": "def456"
  }
}
```

---

## Example 2: Recursive sub-intent decomposition

### Scenario

Human creates a root intent to "Implement metrics module". Agent decomposes into sub-intents.

### Intent hierarchy

```
I-root-002-implement-metrics-module (parent)
├── I-root-002-001-implement-p-success (sub-intent, depth 1)
├── I-root-002-002-implement-entropy (sub-intent, depth 1)
│   ├── I-root-002-002-001-define-entropy-sources (sub-sub-intent, depth 2)
│   └── I-root-002-002-002-implement-entropy-formula (sub-sub-intent, depth 2)
├── I-root-002-003-implement-impact (sub-intent, depth 1)
└── I-root-002-004-implement-ev (sub-intent, depth 1)
```

### Git branch structure

```
main
└── intent/I-root-002-implement-metrics-module
├── intent/I-root-002-implement-metrics-module/I-root-002-001-implement-p-success
├── intent/I-root-002-implement-metrics-module/I-root-002-002-implement-entropy
│   ├── .../I-root-002-002-001-define-entropy-sources
│   └── .../I-root-002-002-002-implement-entropy-formula
├── intent/I-root-002-implement-metrics-module/I-root-002-003-implement-impact
└── intent/I-root-002-implement-metrics-module/I-root-002-004-implement-ev
```

### Execution flow

#### 1) Root intent created (human)

```bash
$ holon intent create --goal "Implement metrics module" --constraints '{"entropy_budget": 150}'
```

**Intent ID:** `I-root-002-implement-metrics-module`

**Git:**

```bash
$ git checkout -b intent/I-root-002-implement-metrics-module
```

---

#### 2) Planning phase (agent decomposes)

**Planner agent (medium trust) generates plan with sub-intents:**

```json
{
  "plan_id": "P-I-root-002-implement-metrics-module-v1-medium",
  "plan_graph": {
    "steps": [
      {
        "id": 1,
        "description": "Create module structure",
        "tool": "bash"
      },
      {
        "id": 2,
        "description": "Spawn sub-intents for each estimator",
        "tool": "meta"
      }
    ],
    "sub_intents": [
      {
        "intent_id": "I-root-002-001-implement-p-success",
        "goal": "Implement P(success) estimator"
      },
      {
        "intent_id": "I-root-002-002-implement-entropy",
        "goal": "Implement entropy estimator"
      },
      {
        "intent_id": "I-root-002-003-implement-impact",
        "goal": "Implement impact estimator"
      },
      {
        "intent_id": "I-root-002-004-implement-ev",
        "goal": "Implement EV calculator"
      }
    ]
  },
  "predicted": {
    "p_success": 0.85,
    "entropy": 45.0,
    "impact": 200,
    "cost": 150,
    "ev": "0.85 * 200 - 0.3 * 45.0 - 150 = 6.5"
  }
}
```

**Plan selected:** v1 (only variant, EV positive)

---

#### 3) Execution: Create module structure

```bash
$ mkdir -p holon/metrics
$ touch holon/metrics/__init__.py
$ git add holon/metrics
$ git commit -m "Create metrics module structure"
```

---

#### 4) Spawn sub-intent 1: Implement P(success)

**Intent created:**

```json
{
  "intent_id": "I-root-002-001-implement-p-success",
  "parent_intent_id": "I-root-002-implement-metrics-module",
  "goal": "Implement P(success) estimator",
  "constraints": {
    "entropy_budget": 37.5
  }
  // 150 * 0.25 (fraction of parent)
}
```

**Git:**

```bash
$ git checkout -b intent/I-root-002-implement-metrics-module/I-root-002-001-implement-p-success
```

**Rebase from parent before execution:**

```bash
$ git rebase intent/I-root-002-implement-metrics-module
```

**Execute:** (similar to Example 1)

**Rebase from parent after execution:**

```bash
$ git rebase intent/I-root-002-implement-metrics-module
```

**Merge to parent (no human review for sub-intent):**

```bash
$ git checkout intent/I-root-002-implement-metrics-module
$ git merge intent/I-root-002-implement-metrics-module/I-root-002-001-implement-p-success
```

**Ledger event:**

```json
{
  "event_type": "git_merge_attempted",
  "seq": 45,
  "payload": {
    "intent_id": "I-root-002-001-implement-p-success",
    "from_branch": "intent/I-root-002-implement-metrics-module/I-root-002-001-implement-p-success",
    "to_branch": "intent/I-root-002-implement-metrics-module",
    "status": "success"
  }
}
```

---

#### 5) Spawn sub-intent 2: Implement entropy (with further decomposition)

**Intent created:**

```json
{
  "intent_id": "I-root-002-002-implement-entropy",
  "parent_intent_id": "I-root-002-implement-metrics-module",
  "goal": "Implement entropy estimator"
}
```

**Planner agent (medium trust) decomposes further:**

```json
{
  "plan_graph": {
    "sub_intents": [
      {
        "intent_id": "I-root-002-002-001-define-entropy-sources",
        "goal": "Define entropy sources"
      },
      {
        "intent_id": "I-root-002-002-002-implement-entropy-formula",
        "goal": "Implement entropy formula"
      }
    ]
  }
}
```

**Git branches:**

```
intent/I-root-002-implement-metrics-module/I-root-002-002-implement-entropy
├── .../I-root-002-002-001-define-entropy-sources
└── .../I-root-002-002-002-implement-entropy-formula
```

**Each sub-sub-intent:**

1. Rebases from parent (`I-root-002-002-implement-entropy`) before execution
2. Executes
3. Rebases from parent after execution
4. Merges to parent (no human review)

**After both sub-sub-intents complete:**

```bash
$ git checkout intent/I-root-002-implement-metrics-module
$ git merge intent/I-root-002-implement-metrics-module/I-root-002-002-implement-entropy
```

---

#### 6) Complete remaining sub-intents

Sub-intents 3 and 4 execute similarly, merging to parent.

---

#### 7) Parent intent complete

**All sub-intents merged to parent branch.**

**Rebase from main:**

```bash
$ git checkout intent/I-root-002-implement-metrics-module
$ git rebase origin/main
```

**Human review requested** (parent intent).

**Human approves.**

**Merge to main:**

```bash
$ git checkout main
$ git merge intent/I-root-002-implement-metrics-module
$ git push origin main
```

**Ledger event:**

```json
{
  "event_type": "intent_promoted_to_main",
  "seq": 89,
  "payload": {
    "intent_id": "I-root-002-implement-metrics-module",
    "merge_sha": "abc789"
  }
}
```

---

## Example 3: Rebase conflict and resolution

### Scenario

Two sub-intents modify the same file concurrently, causing a rebase conflict.

### Setup

**Parent intent:** `I-root-003-refactor-metrics`

**Sub-intents (concurrent):**

- `I-root-003-001-add-caching` (modifies `holon/metrics/p_success.py`)
- `I-root-003-002-add-logging` (modifies `holon/metrics/p_success.py`)

### Execution

#### 1) Sub-intent 001 completes first

```bash
$ git checkout intent/I-root-003-refactor-metrics
$ git merge intent/I-root-003-refactor-metrics/I-root-003-001-add-caching
# Merge successful
```

---

#### 2) Sub-intent 002 attempts rebase after execution

```bash
$ git checkout intent/I-root-003-refactor-metrics/I-root-003-002-add-logging
$ git rebase intent/I-root-003-refactor-metrics
# CONFLICT in holon/metrics/p_success.py
```

**Ledger event:**

```json
{
  "event_type": "git_rebase_completed",
  "seq": 102,
  "payload": {
    "intent_id": "I-root-003-002-add-logging",
    "status": "conflict",
    "conflict_files": [
      "holon/metrics/p_success.py"
    ]
  }
}
```

---

#### 3) Agent detects conflict

**Executor agent logs conflict and aborts rebase:**

```bash
$ git rebase --abort
```

**Agent spawns reactive intent:**

```json
{
  "intent_id": "I-root-003-002-R001-resolve-conflict",
  "parent_intent_id": "I-root-003-002-add-logging",
  "goal": "Resolve rebase conflict in p_success.py",
  "intent_type": "reactive",
  "trigger": "rebase_conflict"
}
```

---

#### 4) Conflict resolution intent executes

**Planner agent generates plan:**

```json
{
  "plan_graph": {
    "steps": [
      {
        "id": 1,
        "description": "Fetch parent changes",
        "tool": "git"
      },
      {
        "id": 2,
        "description": "Identify conflict regions",
        "tool": "git"
      },
      {
        "id": 3,
        "description": "Apply logging changes to updated file",
        "tool": "python"
      },
      {
        "id": 4,
        "description": "Run tests",
        "tool": "pytest"
      },
      {
        "id": 5,
        "description": "Commit resolution",
        "tool": "git"
      }
    ]
  }
}
```

**Executor agent resolves conflict:**

```bash
$ git rebase intent/I-root-003-refactor-metrics
# Manual conflict resolution by agent
$ git add holon/metrics/p_success.py
$ git rebase --continue
$ pytest holon/metrics/test_p_success.py
# Tests pass
```

**Ledger event:**

```json
{
  "event_type": "git_rebase_completed",
  "seq": 108,
  "payload": {
    "intent_id": "I-root-003-002-R001-resolve-conflict",
    "status": "success",
    "conflict_files": []
  }
}
```

---

#### 5) Sub-intent 002 merges to parent

```bash
$ git checkout intent/I-root-003-refactor-metrics
$ git merge intent/I-root-003-refactor-metrics/I-root-003-002-add-logging
# Merge successful (conflict already resolved)
```

---

## Example 4: Agent proposes new intent (autonomous goal-setting)

### Scenario

Agent (high trust) notices calibration error increasing and proposes an intent to improve the estimator.

### Execution

#### 1) Agent monitors calibration

**Curator agent scans ledger:**

```python
recent_executions = ledger.query_executions(since=now() - timedelta(days=7))
mean_p_success_error = mean(e.calibration.p_success_error for e in recent_executions)
# mean_p_success_error = 0.42 (high!)
```

---

#### 2) Agent proposes intent

```json
{
  "proposed_intent": {
    "intent_id": "I-root-010-improve-p-success-estimator",
    "goal": "Improve P(success) estimator to reduce calibration error",
    "rationale": "Mean calibration error over last 7 days is 0.42, exceeding threshold of 0.30",
    "evidence": {
      "ledger_refs": [
        "I-root-005-001",
        "I-root-006-002",
        "I-root-007-001"
      ],
      "mean_error": 0.42,
      "sample_size": 15
    }
  },
  "proposed_by": "agent-curator-05",
  "trust_level": "high"
}
```

**Ledger event:**

```json
{
  "event_type": "intent_proposed",
  "seq": 150,
  "payload": {
    "intent_id": "I-root-010-improve-p-success-estimator",
    "proposed_by": "agent-curator-05",
    "quality_score": 0.78
  }
}
```

---

#### 3) Intent quality scoring

```python
quality_score = score_intent_quality(proposed_intent, "agent-curator-05", ledger, kb)
# quality_score = 0.78
# - Addresses calibration error: +0.3
# - Fills KB gap: +0.0 (estimator already exists)
# - Responds to failure: +0.0
# - Novelty: +0.2 (improvement, not new)
# - Agent trust: +0.18 (trust_score = 0.9)
# - Predicted EV: +0.1 (EV = 45)
```

---

#### 4) Approval gate

```python
approval = approve_intent_proposal(proposed_intent, "agent-curator-05", quality_score=0.78)
# approval = "auto_approved" (high trust + quality > 0.6)
```

**Ledger event:**

```json
{
  "event_type": "intent_approved",
  "seq": 151,
  "payload": {
    "intent_id": "I-root-010-improve-p-success-estimator",
    "approval_type": "auto_approved",
    "quality_score": 0.78
  }
}
```

---

#### 5) Intent executes

Intent proceeds through normal lifecycle:

- Planning (generate variants)
- Execution (implement improved estimator)
- Measurement (backtest on historical data)
- Human review (estimator change requires human approval)
- Promotion to main (if approved)

---

## Example 5: KB extraction (pattern learning)

### Scenario

After 5 successful intents with similar structure, curator agent extracts a pattern.

### Execution

#### 1) Curator scans ledger

```python
intents = ledger.query_intents(status="success", since=now() - timedelta(days=14))
# Found 5 intents with similar structure:
# - I-root-001-001, I-root-002-003, I-root-005-002, I-root-007-001, I-root-008-001
# All implement estimators with similar steps
```

---

#### 2) Extract common structure

```python
pattern = extract_common_structure(intents)
# Pattern:
# 1. Define feature extraction
# 2. Assign weights
# 3. Implement formula
# 4. Clamp to valid range
# 5. Write unit tests
```

---

#### 3) Validate evidence threshold

```python
validate_evidence(pattern, intents)
# success_count = 5 (>= 3, threshold met)
# failure_count = 0
# avg_p_success = 0.88
# avg_entropy = 14.2
```

---

#### 4) Propose KB entry

```json
{
  "kb_id": "KB-pattern-001",
  "kb_type": "pattern",
  "version": "1.0",
  "status": "proposed",
  "evidence": {
    "ledger_refs": [
      "I-root-001-001",
      "I-root-002-003",
      "I-root-005-002",
      "I-root-007-001",
      "I-root-008-001"
    ],
    "success_count": 5,
    "failure_count": 0,
    "avg_p_success": 0.88,
    "avg_entropy": 14.2
  },
  "payload": {
    "name": "Weighted Feature Sum for Estimators",
    "description": "Implement estimators as weighted sums of features with clamping",
    "structure": {
      "steps": [
        "Define feature extraction",
        "Assign weights",
        "Implement formula",
        "Clamp to valid range",
        "Write unit tests"
      ]
    }
  }
}
```

**Ledger event:**

```json
{
  "event_type": "kb_entry_proposed",
  "seq": 200,
  "payload": {
    "kb_id": "KB-pattern-001",
    "kb_type": "pattern",
    "proposed_by": "agent-curator-03"
  }
}
```

---

#### 5) Human approval

```bash
$ holon kb approve KB-pattern-001
```

**KB entry status changed to "active".**

**Ledger event:**

```json
{
  "event_type": "kb_entry_approved",
  "seq": 201,
  "payload": {
    "kb_id": "KB-pattern-001",
    "approved_by": "human@example.com"
  }
}
```

---

#### 6) Pattern used in future planning

**Next time an agent plans an estimator intent:**

```python
patterns = kb.find_similar_intents(intent.goal, intent.constraints)
# Returns: [KB-pattern-001]

# Agent uses pattern to generate plan
plan = generate_plan_from_pattern(intent, patterns[0])
# Plan follows proven structure, higher predicted P(success)
```

---

## Example 6: Model routing based on complexity

### Scenario

Two intents with different complexity levels are routed to different model tiers.

### Intent A: Low complexity (familiar work)

**Intent:** "Add docstrings to existing functions"

**Predicted metrics:**

- `entropy = 5.0` (low)
- `novelty = 0.2` (familiar)
- `complexity = 0.3` (simple)

**Routing decision:**

```python
model = router.select_model(predicted_entropy=5.0, novelty=0.2, complexity=0.3)
# Returns: gemini-2.0-flash (flash tier)
# Reason: "Low entropy and familiar work, fast model sufficient"
```

**Ledger event:**

```json
{
  "event_type": "model_routed",
  "seq": 250,
  "payload": {
    "intent_id": "I-root-015-add-docstrings",
    "model": {
      "provider": "gemini",
      "model_id": "gemini-2.0-flash",
      "tier": "flash"
    },
    "routing_reason": "Low entropy and familiar work"
  }
}
```

**Execution cost:** 10 units (fast, cheap)

**Actual outcome:** Success, EV = 8.5

**Routing ROI:** `(8.5 - 10) / 10 = -0.15` (negative, but acceptable for low-risk work)

---

### Intent B: High complexity (novel problem)

**Intent:** "Design new entropy estimation algorithm"

**Predicted metrics:**

- `entropy = 45.0` (high)
- `novelty = 0.9` (novel)
- `complexity = 0.8` (complex)

**Routing decision:**

```python
model = router.select_model(predicted_entropy=45.0, novelty=0.9, complexity=0.8)
# Returns: gemini-2.0-flash-thinking (deep tier)
# Reason: "High entropy and novel problem, deep reasoning required"
```

**Ledger event:**

```json
{
  "event_type": "model_routed",
  "seq": 275,
  "payload": {
    "intent_id": "I-root-020-design-entropy-algorithm",
    "model": {
      "provider": "gemini",
      "model_id": "gemini-2.0-flash-thinking",
      "tier": "deep"
    },
    "routing_reason": "High entropy and novel problem"
  }
}
```

**Execution cost:** 120 units (slow, expensive)

**Actual outcome:** Success, EV = 85.0

**Routing ROI:** `(85.0 - 120) / 120 = -0.29` (negative cost, but high impact justifies it)

---

## Example 7: Failure mode extraction and mitigation

### Scenario

After 3 intents fail with rebase conflicts, curator extracts a failure mode.

### Execution

#### 1) Curator detects repeated failures

```python
failures = ledger.query_intents(status="failure", since=now() - timedelta(days=7))
conflict_failures = [f for f in failures if "rebase_conflict" in f.failure_reason]
# Found 3 failures: I-root-012-002, I-root-013-001, I-root-014-003
```

---

#### 2) Analyze root cause

```python
root_cause = analyze_root_cause(conflict_failures)
# Root cause: "Concurrent sub-intents modifying same file (holon/metrics/p_success.py)"
```

---

#### 3) Identify mitigations

```python
mitigations = [
    {"strategy": "Sequential merges", "effectiveness": 0.95},
    {"strategy": "Finer-grained decomposition", "effectiveness": 0.85},
    {"strategy": "Conflict-aware entropy estimation", "effectiveness": 0.70}
]
```

---

#### 4) Propose failure mode KB entry

```json
{
  "kb_id": "KB-failure-001",
  "kb_type": "failure_mode",
  "payload": {
    "name": "Rebase Conflict from Concurrent File Edits",
    "symptoms": [
      "rebase_conflict",
      "file_overlap > 0.5"
    ],
    "root_causes": [
      "Insufficient work decomposition",
      "No coordination between sub-intents"
    ],
    "mitigations": [
      ...
    ]
  }
}
```

---

#### 5) Future intents use mitigation

**Next time planner generates plan with concurrent sub-intents:**

```python
failure_modes = kb.find_failure_modes(module_path="holon/metrics/p_success.py")
# Returns: [KB-failure-001]

# Planner adjusts plan:
# - Increase predicted entropy (conflict risk)
# - Add sequential merge constraint
# - Or decompose more finely to avoid file overlap
```

---

## Summary of examples

| Example | Demonstrates                                                                          |
|---------|---------------------------------------------------------------------------------------|
| 1       | Simple root intent, competitive planning, human review, promotion to main             |
| 2       | Recursive sub-intent decomposition, git branch hierarchy, automatic sub-intent merges |
| 3       | Rebase conflict detection, reactive intent spawning, conflict resolution              |
| 4       | Autonomous intent generation, quality scoring, approval gates                         |
| 5       | KB pattern extraction, evidence validation, pattern reuse in future planning          |
| 6       | Model routing based on complexity, ROI measurement                                    |
| 7       | Failure mode extraction, mitigation identification, failure avoidance                 |

---

## Related documents

- [`architecture.md`](architecture.md) — system architecture
- [`agents.md`](agents.md) — agent types and capabilities
- [`git_flow.md`](git_flow.md) — git discipline and rebase rules
- [`metrics.md`](metrics.md) — metric definitions and EV calculation
- [`ledger_schema.md`](ledger_schema.md) — event logging
- [`kb_schema.md`](kb_schema.md) — knowledge base structure
- [`safety.md`](safety.md) — sandboxing, trust levels, entropy budgets
