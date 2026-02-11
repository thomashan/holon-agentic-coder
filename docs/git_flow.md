# git_flow.md

This document defines the **Git branching, rebasing, and merging discipline** for Holon.

---

## 1) Core Principles

### 1.1 Git as Universal State Machine

- Every intent gets its own branch
- All work happens in branches, never directly on `main`
- `main` is the canonical "promoted" state
- Branches are cheap; exploration is encouraged

### 1.2 Fractal Intent Hierarchy

- Intents can spawn sub-intents recursively
- Each sub-intent gets a branch nested under its parent's branch
- Depth is unlimited (but entropy budgets constrain practical depth)

### 1.3 Human Review Boundary

- **Root intents** (top-level intents) require human review before merging to `main`
- **Sub-intents** (at any depth) merge automatically to their parent based on evaluation
- This applies recursively: sub-sub-intents merge to sub-intents, which merge to root intents

### 1.4 Terminology

- **Root Intent**: Top-level intent that will eventually merge to `main` (requires human review)
- **Parent Intent**: Immediate parent of a sub-intent in the tree (may itself be a sub-intent)
- **Sub-Intent**: Any intent spawned by another intent (can have its own sub-intents)

---

## 2) Branch Naming Convention

### 2.1 Root Intent Branch

```
intent/I-root-{seq}-{slug}
```

Example:

```
intent/I-root-050-refactor-metrics
```

### 2.2 Sub-Intent Branch (Nested)

```
intent/I-root-{seq}-{slug}/I-root-{seq}-{sub-seq}-{sub-slug}
```

Example:

```
intent/I-root-050-refactor-metrics/I-root-050-001-improve-estimators
```

### 2.3 Sub-Sub-Intent Branch (Deeper Nesting)

```
intent/I-root-{seq}-{slug}/I-root-{seq}-{sub-seq}-{sub-slug}/I-root-{seq}-{sub-seq}-{subsub-seq}-{subsub-slug}
```

Example:

```
intent/I-root-050-refactor-metrics/I-root-050-001-improve-estimators/I-root-050-001-001-p-success
```

**Pattern:** Each level appends to the path, creating a filesystem-like hierarchy.

---

## 3) Mandatory Rebase Discipline

### 3.1 Dual Rebase Rule

Every sub-intent **must rebase from its immediate parent**:

1. **Before execution** (to get latest parent state)
2. **After execution** (to ensure clean merge)

### 3.2 Rebase Commands

**Before execution:**

```bash
$ git checkout intent/I-root-050-refactor-metrics/I-root-050-001-improve-estimators
$ git fetch origin
$ git rebase intent/I-root-050-refactor-metrics
```

**After execution:**

```bash
$ git fetch origin
$ git rebase intent/I-root-050-refactor-metrics
```

### 3.3 Conflict Handling

If rebase fails:

1. Log conflict to ledger
2. Spawn reactive intent to resolve conflict
3. If unresolvable automatically, escalate to human

---

## 4) Merge Rules

### 4.1 Sub-Intent → Parent Merge (Automatic)

**Trigger:** Sub-intent execution completes successfully

**Process:**

1. Evaluate all completed sub-intents under the same parent
2. Compute `merge_value` for each:
   ```python
   merge_value = impact_actual - conflict_risk - entropy_actual - redundancy_penalty
   ```
3. Filter by success (`success_actual == 1`)
4. Sort by `merge_value` (descending)
5. Merge sequentially or in parallel (based on conflict detection)

**Example:**

```bash
# Sub-intent completes
$ git checkout intent/I-root-050-refactor-metrics
$ git merge intent/I-root-050-refactor-metrics/I-root-050-001-improve-estimators
# Automatic, no human review
```

**Ledger event:**

```json
{
  "event_type": "git_merge_attempted",
  "payload": {
    "intent_id": "I-root-050-001-improve-estimators",
    "from_branch": "intent/I-root-050-refactor-metrics/I-root-050-001-improve-estimators",
    "to_branch": "intent/I-root-050-refactor-metrics",
    "status": "success",
    "merge_type": "automatic_sub_intent",
    "human_review_required": false
  }
}
```

### 4.2 Root Intent → Main Merge (Human Review Required)

**Trigger:** All sub-intents merged, root intent ready for promotion

**Process:**

1. Generate review package:
    - Intent goal and constraints
    - Predicted vs actual metrics
    - Diff summary
    - Test results
    - Calibration errors
2. Request human review
3. Human approves or rejects
4. If approved, merge to `main`

**Example:**

```bash
# Human reviews
$ holon review approve I-root-050-refactor-metrics

# System merges
$ git checkout main
$ git merge intent/I-root-050-refactor-metrics
$ git push origin main
```

**Ledger event:**

```json
{
  "event_type": "intent_promoted_to_main",
  "payload": {
    "intent_id": "I-root-050-refactor-metrics",
    "merge_sha": "abc123",
    "reviewer": "human@example.com"
  }
}
```

### 4.3 Merge Constraints

**Forbidden:**

- Sub-intent merging directly to `main` (must go through root intent)
- Merging without prior rebase
- Merging failed intents (unless explicitly overridden by human)

**Allowed:**

- Discarding sub-intents (close branch without merging)
- Multiple sub-intents merging to same parent
- Recursive sub-intent trees of arbitrary depth

---

## 5) Automatic Merge Evaluation

### 5.1 Merge Value Calculation

```python
def compute_merge_value(sub_intent):
    return (
            sub_intent.impact_actual
            - estimate_conflict_risk(sub_intent)
            - sub_intent.entropy_actual
            - compute_redundancy_penalty(sub_intent)
    )
```

### 5.2 Conflict Risk Estimation

```python
def estimate_conflict_risk(sub_intent):
    # Check file overlap with other pending sub-intents
    overlapping_files = find_overlapping_files(sub_intent)

    # Check if files are "hot" (frequently modified)
    hot_file_penalty = sum(is_hot_file(f) for f in sub_intent.files_modified)

    return len(overlapping_files) * 5.0 + hot_file_penalty * 2.0
```

### 5.3 Redundancy Detection

```python
def compute_redundancy_penalty(sub_intent):
    # Check if another sub-intent already solved the same problem
    siblings = get_sibling_intents(sub_intent)

    for sibling in siblings:
        if solves_same_problem(sub_intent, sibling):
            if sibling.merge_value > sub_intent.merge_value:
                return 1000.0  # High penalty, discard this one

    return 0.0
```

---

## 6) Merge Strategies

### 6.1 Sequential Merge (Safe Default)

```python
def sequential_merge(sub_intents, parent_branch):
    # Sort by merge_value descending
    sorted_subs = sorted(sub_intents, key=lambda s: s.merge_value, reverse=True)

    for sub in sorted_subs:
        rebase_from_parent(sub, parent_branch)
        if rebase_successful():
            merge_to_parent(sub, parent_branch)
            log_merge(sub, "automatic_sequential")
        else:
            handle_conflict(sub)
```

### 6.2 Parallel Merge (Optimized)

```python
def parallel_merge(sub_intents, parent_branch):
    # Cluster by file overlap
    clusters = cluster_by_file_overlap(sub_intents)

    for cluster in clusters:
        if cluster.no_internal_conflicts():
            # Merge all in parallel
            for sub in cluster:
                rebase_and_merge(sub, parent_branch)
        else:
            # Fall back to sequential within cluster
            sequential_merge(cluster, parent_branch)
```

---

## 7) Branch Lifecycle

### 7.1 Creation

```bash
# Root intent
$ git checkout main
$ git checkout -b intent/I-root-050-refactor-metrics

# Sub-intent
$ git checkout intent/I-root-050-refactor-metrics
$ git checkout -b intent/I-root-050-refactor-metrics/I-root-050-001-improve-estimators
```

### 7.2 Execution

- Work happens in the branch
- Commits are made
- Tests run in sandbox
- Metrics measured

### 7.3 Rebase (Post-Execution)

```bash
$ git rebase intent/I-root-050-refactor-metrics
```

### 7.4 Merge (Automatic for Sub-Intents)

```bash
$ git checkout intent/I-root-050-refactor-metrics
$ git merge intent/I-root-050-refactor-metrics/I-root-050-001-improve-estimators
```

### 7.5 Promotion (Human Review for Root Intents)

```bash
$ holon review approve I-root-050-refactor-metrics
$ git checkout main
$ git merge intent/I-root-050-refactor-metrics
$ git push origin main
```

### 7.6 Cleanup

```bash
# Delete merged branches
$ git branch -d intent/I-root-050-refactor-metrics/I-root-050-001-improve-estimators
$ git branch -d intent/I-root-050-refactor-metrics
```

---

## 8) Example: Multi-Level Intent Tree

### Intent Hierarchy

```
I-root-050-refactor-metrics (root)
├── I-root-050-001-improve-estimators (sub, depth 1)
│   ├── I-root-050-001-001-p-success (sub-sub, depth 2)
│   ├── I-root-050-001-002-entropy (sub-sub, depth 2)
│   └── I-root-050-001-003-impact (sub-sub, depth 2)
├── I-root-050-002-add-logging (sub, depth 1)
└── I-root-050-003-add-tests (sub, depth 1)
```

### Git Branch Structure

```
main
└── intent/I-root-050-refactor-metrics
    ├── intent/.../I-root-050-001-improve-estimators
    │   ├── intent/.../I-root-050-001-001-p-success
    │   ├── intent/.../I-root-050-001-002-entropy
    │   └── intent/.../I-root-050-001-003-impact
    ├── intent/.../I-root-050-002-add-logging
    └── intent/.../I-root-050-003-add-tests
```

### Merge Flow

1. **Depth 2 → Depth 1** (automatic):
    - `I-root-050-001-001` → `I-root-050-001`
    - `I-root-050-001-002` → `I-root-050-001`
    - `I-root-050-001-003` → `I-root-050-001`

2. **Depth 1 → Root** (automatic):
    - `I-root-050-001` → `I-root-050`
    - `I-root-050-002` → `I-root-050`
    - `I-root-050-003` → `I-root-050`

3. **Root → Main** (human review):
    - `I-root-050` → `main` (after human approval)

---

## 9) Conflict Resolution

### 9.1 Automatic Resolution (Attempted First)

```python
def auto_resolve_conflict(sub_intent, parent_branch):
    # Try simple strategies
    if conflict_is_whitespace_only():
        accept_parent_version()
        return True

    if conflict_is_import_order():
        sort_imports()
        return True

    if conflict_is_non_overlapping():
        accept_both_changes()
        return True

    return False  # Escalate
```

### 9.2 Reactive Intent (If Auto-Resolution Fails)

```python
def handle_conflict(sub_intent):
    spawn_intent({
        "intent_id": f"{sub_intent.intent_id}-R001-resolve-conflict",
        "parent_intent_id": sub_intent.intent_id,
        "goal": f"Resolve rebase conflict in {sub_intent.conflict_files}",
        "intent_type": "reactive",
        "trigger": "rebase_conflict"
    })
```

---

## 10) Ledger Events

All Git operations are logged to the ledger:

```json
{
  "event_type": "git_branch_created",
  "payload": {
    "branch": "intent/I-root-050-refactor-metrics"
  }
}
{
  "event_type": "git_rebase_completed",
  "payload": {
    "status": "success",
    "conflict_files": []
  }
}
{
  "event_type": "git_merge_attempted",
  "payload": {
    "status": "success",
    "merge_type": "automatic_sub_intent"
  }
}
{
  "event_type": "intent_promoted_to_main",
  "payload": {
    "merge_sha": "abc123"
  }
}
```

---

## 11) Discard Policy

### 11.1 When to Discard Sub-Intents

Sub-intents should be discarded (branch closed without merging) when:

1. **Execution failed** (`success_actual == 0`)
2. **Negative merge value** (`merge_value < 0`)
3. **Redundant with higher-value sibling** (another sub-intent solved the same problem better)
4. **Conflicts with higher-value sibling** (unresolvable conflict, lower-value intent discarded)
5. **Entropy budget exceeded** (sub-intent consumed too much entropy)

### 11.2 Discard Process

```python
def discard_sub_intent(sub_intent, reason):
    # Log to ledger
    ledger.log({
        "event_type": "sub_intent_discarded",
        "payload": {
            "intent_id": sub_intent.intent_id,
            "reason": reason,
            "merge_value": sub_intent.merge_value,
            "success_actual": sub_intent.success_actual
        }
    })

    # Extract KB learnings (even from failures)
    if sub_intent.kb_entries_created > 0:
        extract_kb_learnings(sub_intent)

    # Close branch
    git.branch_delete(sub_intent.branch_name)
```

### 11.3 Learning from Discarded Intents

Even discarded intents provide value:

- **Failure modes** extracted to KB
- **Calibration data** (predicted vs actual metrics)
- **Negative examples** (what not to do)

---

## 12) Summary Table

| Operation                 | Automatic? | Human Review? | Rebase Required?       |
|---------------------------|------------|---------------|------------------------|
| Sub-intent → Parent merge | ✓ Yes      | ✗ No          | ✓ Yes (before & after) |
| Root intent → Main merge  | ✗ No       | ✓ Yes         | ✓ Yes (before)         |
| Branch creation           | ✓ Yes      | ✗ No          | N/A                    |
| Conflict resolution       | Attempted  | If fails      | N/A                    |
| Sub-intent discard        | ✓ Yes      | ✗ No          | N/A                    |

**Key insight:** Human review is only required at the root intent level. All sub-intent merges are automatic and evaluation-based.

---

## 13) Edge Cases

### 13.1 Root Intent with No Sub-Intents

If a root intent has no sub-intents (leaf intent):

- Execute directly in root intent branch
- Still requires human review before merging to `main`

### 13.2 All Sub-Intents Fail

If all sub-intents under a parent fail:

- Parent intent is marked as failed
- If parent is root intent, human review requested (may choose to retry or abandon)
- If parent is sub-intent, it is discarded automatically

### 13.3 Partial Sub-Intent Success

If some sub-intents succeed and others fail:

- Successful sub-intents merge automatically
- Failed sub-intents discarded
- Parent intent continues with merged work

### 13.4 Long-Running Root Intent

If a root intent remains open for extended period (e.g., weeks):

- Periodic rebase from `main` recommended
- System entropy monitoring triggers maintenance
- Human may choose to merge incrementally or wait for completion

---

## 14) Best Practices

### 14.1 Keep Sub-Intents Focused

- Each sub-intent should have a single, clear goal
- Avoid "mega sub-intents" that do too much
- Better to have more sub-intents with smaller scope

### 14.2 Monitor File Overlap

- Track which files are "hot" (frequently modified)
- Consider sequential execution for sub-intents touching hot files
- Use finer-grained decomposition to reduce overlap

### 14.3 Rebase Frequently

- Don't let branches diverge too far
- Rebase from parent regularly, not just before/after execution
- Reduces conflict resolution cost

### 14.4 Prune Aggressively

- Discard low-value sub-intents early
- Don't wait for all sub-intents to complete before merging high-value ones
- Keep branch count low to reduce system entropy

---

## Related Documents

- [`metrics.md`](metrics.md) — merge value calculation, entropy formulas
- [`examples.md`](examples.md) — concrete examples of merge flows
- [`ledger_schema.md`](ledger_schema.md) — event logging for Git operations
- [`architecture.md`](architecture.md) — overall system design
