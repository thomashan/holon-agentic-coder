# Plan for I-1771890389

**Plan ID:** P-1772691718-opencode-opencode_big-pickle
**Parent Intent ID:** null
**Agent:** opencode/opencode_big-pickle
**Created At:** 2026-03-05T06:21:58.6NZ

## Planner Autonomy Summary

- Intent handling: ACCEPT_AS_IS
- Reframed intent (if applicable): N/A
- Exploration stance: balanced with 1–2 sentence justification. This is a foundational bootstrap intent that establishes core system capability. Conservative approach is appropriate given this is a day-zero infrastructure intent with high impact but also high risk if mis-designed.
- Safety priority level: elevated
- Priority Justification: This intent bootstraps the system's self-replication capability. According to safety.md, sandbox escape attempts trigger critical alerts and trust degradation. The CLI spawns future tasks in isolated sandboxes - misimplementation could lead to resource exhaustion or sandbox policy violations.

## Exploration

- Proportion of steps that are exploratory: 0.2
- Justification: This is primarily implementation work following established patterns from existing entrypoints. However, step 3 (sub-intent spawning) is exploratory as it involves novel capability that enables recursive autonomy.

## Overall Plan Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.75                  |
| entropy_pred        | 22.5                  |
| impact_pred         | 90                    |
| cost_pred           | 45                    |
| learning_value_pred | 4                     |
| ev_pred             | 40.75                 |

### Strategy Rationale

The plan follows existing patterns from intent_creator.sh, planner.sh, and executor.sh. The bottleneck step is Step 3 (sub-intent spawning capability) due to novelty and complexity. Overall metrics derived as:
- p_success_pred: Weighted average of step success (Step 3 pulls down average)
- entropy_pred: Sum of step entropies (Step 3 has highest at 7.0)
- impact_pred: Maximum of step impacts (Step 5 has highest at 95)
- cost_pred: Sum of step costs
- learning_value_pred: Weighted by novelty - Step 3 and 5 have higher learning value
- ev_pred: Formula applied to aggregated values

## Safety & Constraint Alignment

- Key world ruleset constraints that affect this plan:
  - safety.md: Sandbox escape detection (sandbox must isolate executions)
  - safety.md: Trust model - baseline agents cannot spawn sub-intents
  - safety.md: Entropy budgets constrain blast radius
  - git_flow.md: Sub-intents merge only to parent, never directly to main

- Potential violations or edge cases:
  - Sub-intent spawning without proper entropy budget tracking
  - Sandbox escape via git operations outside workspace
  - Infinite recursion in sub-intent spawning

- Mitigations built into the plan:
  - Steps include validation of intent JSON structure
  - Docker sandbox with --read-only filesystem
  - Branch naming validation before creation
  - Entropy budget checks before spawning

- Residual risk accepted (and why): Low. The intent creator and planner entrypoints already demonstrate safe patterns. This plan extends those patterns with proper validation.

- Allocated Entropy Budget: 30 (assumed from intent context)
- Predicted Plan Entropy: 22.5
- Budget Compliance: The strategy fits within budget

## Plan Description & Strategy

The plan implements the CLI bootstrapping by extending existing entrypoint scripts with a new sub-intent spawning capability. This enables the system to recursively spawn tasks - the core requirement for autonomous operation.

Strategy:
1. First, analyse existing infrastructure to understand what's already in place
2. Define the sub-intent JSON schema and validation rules
3. Create the sub-intent spawner entrypoint following existing patterns
4. Add sub-intent spawning command to the holon CLI wrapper
5. Test the end-to-end flow to verify self-replication capability

---

## Step 1: Analyse existing CLI infrastructure

**Sub‑intent recommendation:** NO
**Reasoning:** This is a simple analysis step with low risk and no reusability. No need for separate branch.
**Step Type:** INFO_GATHERING
**Exploration level:** EXPLOIT

- Hypothesis being tested: N/A (exploitation of existing patterns)
- Learning target: N/A
- Maximum acceptable cost for this learning: N/A

### Intent & Git Integration

**Step Intent:** Review existing holon CLI wrapper, entrypoint scripts, and intent creation flow to identify gaps
**Git branch:** I-1771890389-bootstrap-cli/_
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Review holon CLI wrapper script (holon file)
2. Analyse intent_creator.sh entrypoint for intent creation patterns
3. Analyse planner.sh entrypoint for plan generation patterns
4. Analyse executor.sh entrypoint for execution patterns
5. Identify what new capability is needed for sub-intent spawning

### Dependencies & Criticality

**Depends on:** NONE
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md#sandboxing
- Potential failure modes for this step: None - purely informational
- Guardrails and early‑abort checks: None needed

### Success & Discard Criteria

**Success:** Documented analysis of existing infrastructure with identified gaps for sub-intent spawning
**Discard:** N/A - this step always succeeds

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.95                  |
| entropy_pred        | 2.0                   |
| impact_pred         | 30                    |
| cost_pred           | 5                     |
| learning_value_pred | 1                     |
| ev_pred             | 26.9                  |

### Step Metrics Rationale

High success probability (0.95) because this is pure analysis with no execution risk. Low entropy (2.0) as it's a simple review task. Low cost (5) reflects minimal time investment. Learning value low (1) as it exploits existing knowledge rather than exploring new territory.

---

## Step 2: Define sub-intent JSON schema and validation

**Sub‑intent recommendation:** NO
**Reasoning:** This is a specification step with no code changes and low risk. Existing entrypoints provide clear patterns to follow.
**Step Type:** CONFIG
**Exploration level:** EXPLOIT

- Hypothesis being tested: N/A
- Learning target: N/A
- Maximum acceptable cost for this learning: N/A

### Intent & Git Integration

**Step Intent:** Define JSON schema for sub-intent creation, including required fields, validation rules, and entropy budget allocation
**Git branch:** I-1771890389-bootstrap-cli/_
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Define sub-intent JSON schema:
   - intent_id: required, format I-{timestamp}-{slug}
   - parent_id: required, reference to parent intent
   - title: required, short descriptive title
   - description: required, detailed description
   - goal: required, measurable goal
   - branch: required, follows fractal nesting pattern
   - entropy_budget: optional, defaults to parent budget * 0.5
   - trust_level_required: optional, minimum trust level needed
2. Define validation rules:
   - Branch must follow naming convention: {parent_branch}/I-{timestamp}-{slug}/_
   - Entropy budget must be within parent allocation
   - Trust level must be sufficient for proposed sub-intent depth
3. Document schema in app/scripts/sub_intent_schema.json

### Dependencies & Criticality

**Depends on:** Step 1
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md#entropy-budgets, safety.md#trust-model
- Potential failure modes: Invalid intent JSON could cause downstream failures
- Guardrails and early‑abort checks: Validate JSON schema before accepting sub-intent proposals

### Success & Discard Criteria

**Success:** Sub-intent schema defined and documented in app/scripts/sub_intent_schema.json
**Discard:** N/A

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.90                  |
| entropy_pred        | 3.5                   |
| impact_pred         | 50                    |
| cost_pred           | 8                     |
| learning_value_pred | 2                     |
| ev_pred             | 40.85                 |

### Step Metrics Rationale

High success (0.90) as schema design follows established patterns. Low-medium entropy (3.5) as it requires careful design but is not complex. Moderate impact (50) as schema enables type safety. Low cost (8). Learning value low (2) as it follows existing intent schema patterns.

---

## Step 3: Create sub-intent spawner entrypoint

**Sub‑intent recommendation:** YES
**Reasoning:** This step introduces new capability with moderate risk and high reusability. It should be isolated to contain blast radius and allow independent testing. The sub-intent spawner is a core system component that other intents will depend on.
**Step Type:** IMPLEMENTATION
**Exploration level:** BALANCED

- Hypothesis being tested: Can we safely enable sub-intent spawning within sandbox constraints while maintaining entropy budget discipline?
- Learning target: Understanding of sub-intent spawning patterns, entropy budget allocation, and trust level validation
- Maximum acceptable cost for this learning: 15 entropy exceeds (if this, abort and use simpler fallback)

### Intent & Git Integration

**Step Intent:** Implement sub-intent spawner entrypoint (sub_intent_spawner.sh) following patterns from intent_creator.sh
**Git branch:** I-1771890389-bootstrap-cli/_
**Sub‑intent:** NEW - enables recursive intent decomposition

### Implementation Details (No code blocks, only logic/steps)

1. Create docker/files/entrypoints/sub_intent_spawner.sh:
   - Accept sub-intent JSON file path as argument
   - Read parent intent branch from environment or argument
   - Validate sub-intent JSON against schema (Step 2)
   - Check entropy budget availability
   - Verify trust level requirements
   - Clone repo to fresh workspace
   - Create sub-intent branch from parent
   - Log sub-intent creation to intents.jsonl
   - Commit and push new branch
2. Ensure sandbox constraints:
   - Filesystem read-only except workspace
   - No network except git operations
   - Restricted to whitelisted tools (git, jq)
3. Handle errors:
   - Schema validation failures → log and exit
   - Entropy budget exceeded → log and exit with error
   - Trust level insufficient → log and exit with error
   - Git failures → log and exit with error

### Dependencies & Criticality

**Depends on:** Step 2
**Is Bottleneck:** YES (If this step fails, the entire plan fails to deliver core capability)
**Note:** p_success_pred is 0.70 which is below 0.6 threshold - sub-intent recommendation is STRONGLY_YES per guidelines

### Safety & Constraint Considerations

- Relevant rules: safety.md#sandboxing, safety.md#entropy-budgets, safety.md#trust-model, safety.md#sandbox-escape-detection
-  - Sub-int Potential failure modes:
ent spawns without proper budget validation → entropy budget overrun
  - Trust level bypass → unauthorised capability escalation
  - Git operations escape workspace → sandbox violation
- Guardrails and early‑abort checks:
  - Validate JSON schema before any git operations
  - Check entropy budget before branch creation
  - Verify trust level before allowing spawn

### Success & Discard Criteria

**Success:** Sub-intent spawner creates valid sub-intent branch with proper logging
**Discard:** If sub-intent spawner produces invalid branches, violates entropy budget, or attempts sandbox escape

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.70                  |
| entropy_pred        | 7.0                   |
| impact_pred         | 85                    |
| cost_pred           | 12                    |
| learning_value_pred | 6                     |
| ev_pred             | 50.1                  |

### Step Metrics Rationale

Lower success probability (0.70) due to novelty and complexity of new capability. Higher entropy (7.0) as it introduces new code paths. High impact (85) as this enables core self-replication. Higher learning value (6) as it explores new territory. Cost moderate (12).

---

## Step 4: Extend holon CLI with sub-intent command

**Sub‑intent recommendation:** NO
**Reasoning:** Simple extension to existing CLI wrapper following established patterns. Low risk, no need for separate branch.
**Step Type:** IMPLEMENTATION
**Exploration level:** EXPLOIT

- Hypothesis being tested: N/A
- Learning target: N/A
- Maximum acceptable cost for this learning: N/A

### Intent & Git Integration

**Step Intent:** Add sub-intent command to holon CLI wrapper to enable spawning from within sandbox
**Git branch:** I-1771890389-bootstrap-cli/_
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Add sub-intent command to holon CLI wrapper:
   - Command: holon spawn-sub-intent <sub_intent_json>
   - Calls sub_intent_spawner.sh via docker run
   - Validates arguments before invocation
2. Update holon wrapper to support the new command:
   - Add spawn-sub-intent case to CLI
   - Pass through JSON file to container
3. Document new command in holon usage

### Dependencies & Criticality

**Depends on:** Step 3
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: safety.md#sandboxing
- Potential failure modes: CLI passes invalid arguments to spawner
- Guardrails: Validate JSON file exists before docker run

### Success & Discard Criteria

**Success:** holon spawn-sub-intent command available and documented
**Discard:** N/A

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.85                  |
| entropy_pred        | 3.0                   |
| impact_pred         | 70                    |
| cost_pred           | 8                     |
| learning_value_pred | 2                     |
| ev_pred             | 55.6                  |

### Step Metrics Rationale

High success (0.85) as it follows existing CLI patterns. Low entropy (3.0). Moderate impact (70). Low cost (8). Learning value low (2) as it exploits existing CLI pattern.

---

## Step 5: End-to-end test of self-replication capability

**Sub‑intent recommendation:** YES
**Reasoning:** This tests the core capability that enables autonomous system evolution. Should be isolated to contain blast radius and verify safety constraints work correctly.
**Step Type:** TEST
**Exploration level:** EXPLORATORY

- Hypothesis being tested: Can the system spawn a sub-intent from within a sandboxed environment while maintaining safety constraints?
- Learning target: Verify entropy budget tracking, trust level validation, and sandbox isolation work correctly in practice
- Maximum acceptable cost for this learning: 12 (abort if test takes too long or reveals critical issues)

### Intent & Git Integration

**Step Intent:** Test the full sub-intent spawning flow by creating a child intent from within the CLI
**Git branch:** I-1771890389-bootstrap-cli/_
**Sub‑intent:** NONE (this is a test of Step 3's capability)

### Implementation Details (No code blocks, only logic/steps)

1. Create test sub-intent JSON:
   - Parent: I-1771890389-bootstrap-cli
   - Goal: Test sub-intent for validation
   - Valid branch name following fractal pattern
2. Execute holon spawn-sub-intent with test JSON
3. Verify:
   - New branch created with correct naming
   - Intent logged in intents.jsonl
   - Branch pushed to remote
4. Cleanup test branch after verification

### Dependencies & Criticality

**Depends on:** Step 4
**Is Bottleneck:** NO (but critical for validation)

### Safety & Constraint Considerations

- Relevant rules: safety.md#all - tests all safety mechanisms
- Potential failure modes:
  - Sub-intent spawns without proper entropy tracking
  - Trust level bypass
  - Sandbox escape
- Guardrails and early‑abort checks: Test runs in isolated sandbox, can be terminated

### Success & Discard Criteria

**Success:** Sub-intent successfully created from within sandboxed environment with proper logging
**Discard:** If any safety constraint is violated or sub-intent creation fails

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.75                  |
| entropy_pred        | 5.0                   |
| impact_pred         | 95                    |
| cost_pred           | 10                    |
| learning_value_pred | 5                     |
| ev_pred             | 65.25                 |

### Step Metrics Rationale

Moderate success (0.75) - testing may reveal integration issues. Moderate entropy (5.0). Highest impact (95) as this validates the core self-replication capability. Learning value moderate-high (5) as it validates safety model in practice. Cost (10).

---

## Step 6: Document the CLI bootstrap completion

**Sub‑intent recommendation:** NO
**Reasoning:** Documentation step with low risk. Follows from successful test completion.
**Step Type:** DOCUMENTATION
**Exploration level:** EXPLOIT

- Hypothesis being tested: N/A
- Learning target: N/A
- Maximum acceptable cost for this learning: N/A

### Intent & Git Integration

**Step Intent:** Document the completed CLI bootstrap with usage instructions and integration notes
**Git branch:** I-1771890389-bootstrap-cli/_
**Sub‑intent:** NONE

### Implementation Details (No code blocks, only logic/steps)

1. Update README.md with holon CLI usage:
   - create-intent command
   - spawn-sub-intent command (new)
   - plan command
   - execute command
2. Document the sub-intent JSON schema in docs/
3. Add entry to docs/examples.md showing recursive intent spawning
4. Update ledger_schema.md with new event types if needed

### Dependencies & Criticality

**Depends on:** Step 5
**Is Bottleneck:** NO

### Safety & Constraint Considerations

- Relevant rules: N/A
- Potential failure modes: None - documentation only
- Guardrails: None

### Success & Discard Criteria

**Success:** Complete documentation of CLI bootstrap capability
**Discard:** N/A

### Metrics

| metric              | value                 |
|---------------------|-----------------------|
| p_success_pred      | 0.95                  |
| entropy_pred        | 2.0                   |
| impact_pred         | 60                    |
| cost_pred           | 2                     |
| learning_value_pred | 1                     |
| ev_pred             | 56.9                  |

### Step Metrics Rationale

Very high success (0.95). Very low entropy (2.0). Low cost (2). Low learning value (1).

