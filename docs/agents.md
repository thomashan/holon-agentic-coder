# agents.md

This document defines the **agent model** for Holon. Agents are autonomous AI entities that plan, execute, learn, and evolve within the constraints of the safety model, git discipline, and metric-driven decision-making.

Agents enable:

- **autonomous intent execution** (planning → execution → measurement)
- **self-improvement** (proposing better estimators, tactics, patterns)
- **recursive decomposition** (spawning sub-intents to solve complex problems)
- **competitive planning** (generating multiple plan variants, selecting best by EV)
- **earned autonomy** (gaining capabilities through demonstrated reliability)

---

## Core agent principles

### 1) Agents are goal-directed

- Every agent operates on an **intent** (goal + constraints).
- Agents plan actions to maximize **Expected Value (EV)**.
- Agents measure outcomes and update calibration.

### 2) Agents are metric-driven

- Agents use **P(success), ΔS, Impact, Cost** to evaluate plans.
- Agents select plans with highest EV under constraints.
- Agents learn from **calibration errors** (predicted vs actual).

### 3) Agents are sandboxed

- Agents execute in **isolated environments** (git branches + sandboxes).
- Agents cannot escape sandbox boundaries.
- Agents cannot modify core invariants without human approval.

### 4) Agents are trust-bounded

- Agents start with **baseline trust** (limited autonomy).
- Agents earn trust through **demonstrated reliability**.
- Agents lose trust through **failures or violations**.

### 5) Agents are evolvable

- Agents can propose **improvements to themselves** (estimators, tactics, patterns).
- Agents can spawn **sub-agents** (recursive decomposition).
- Agents can generate **new intents** (autonomous goal-setting, with trust gates).

---

## Agent types

### 1) **Planner Agent**

**Role:** Generate plan variants for a given intent.

**Inputs:**

- Intent (goal, constraints, scope)
- KB (patterns, tactics, failure modes)
- Ledger (historical calibration data)

**Outputs:**

- Plan variants (structured steps, sub-intents, predictions)
- Predicted metrics (P(success), ΔS, Impact, Cost, EV)

**Capabilities:**

- Retrieve similar intents from KB
- Decompose intent into sub-intents
- Estimate metrics using current estimators
- Generate multiple plan variants (competitive planning)

**Trust requirements:**

- **Baseline:** Can generate plans for assigned intents
- **Medium:** Can propose sub-intent decomposition
- **High:** Can propose novel plan structures
- **Highest:** Can propose new planning heuristics

**Model routing:**

- **Flash tier:** Low-entropy intents (< 10), familiar patterns
- **Medium tier:** Moderate-entropy intents (10-30), some novelty
- **Deep tier:** High-entropy intents (> 30), novel problems, complex decomposition

**Example:**
```python
class PlannerAgent:
    def __init__(self, agent_id, model, trust_level):
        self.agent_id = agent_id
        self.model = model
        self.trust_level = trust_level


    def generate_plan_variants(self, intent, kb, ledger, num_variants=3):
        variants = []
        for i in range(num_variants):
            # Retrieve similar patterns
            patterns = kb.find_similar_intents(intent.goal, intent.constraints)
    
            # Generate plan structure
            plan = self.generate_plan_structure(intent, patterns)
    
            # Estimate metrics
            predicted = self.estimate_metrics(plan, ledger)
    
            # Create plan variant
            variant = PlanVariant(
                plan_id=f"P-{intent.intent_id}-v{i + 1}-{self.model.tier}",
                plan_graph=plan,
                predicted=predicted,
                model=self.model
            )
            variants.append(variant)
    
        return variants
    
    
    def estimate_metrics(self, plan, ledger):
        # Use active estimators from KB
        p_success_estimator = kb.get_active_estimator("p_success")
        entropy_estimator = kb.get_active_estimator("entropy")
        impact_estimator = kb.get_active_estimator("impact")
    
        p_success = p_success_estimator.estimate(plan, ledger)
        entropy = entropy_estimator.estimate(plan, ledger)
        impact = impact_estimator.estimate(plan, ledger)
        cost = self.estimate_cost(plan)
    
        ev = p_success * impact - LAMBDA * entropy - cost
    
        return PredictedMetrics(
            p_success=p_success,
            entropy=entropy,
            impact=impact,
            cost=cost,
            ev=ev
        )

```

---

### 2) **Executor Agent**

**Role:** Execute a selected plan in a sandboxed environment.

**Inputs:**

- Intent
- Selected plan
- Sandbox configuration
- KB (tactics, modules)

**Outputs:**

- Execution results (success/failure)
- Artifacts (code, diffs, test results)
- Actual metrics (measured P(success), ΔS, Impact, Cost)

**Capabilities:**

- Execute plan steps sequentially
- Invoke tools (git, pytest, python, bash)
- Retrieve tactics from KB
- Handle errors and retries
- Measure actual metrics post-execution

**Trust requirements:**

- **Baseline:** Can execute in process/container sandbox
- **Medium:** Can execute with limited network access
- **High:** Can execute with broader tool access
- **Highest:** Can execute in production-like environments (still sandboxed)

**Model routing:**

- **Flash tier:** Simple execution (scripted steps, low complexity)
- **Medium tier:** Moderate complexity (some decision-making required)
- **Deep tier:** Complex execution (novel problems, error recovery, adaptation)

**Example:**
```python
class ExecutorAgent:
def __init__(self, agent_id, model, trust_level):
self.agent_id = agent_id
self.model = model
self.trust_level = trust_level

    def execute_plan(self, intent, plan, sandbox):
        ledger.log("execution_started", intent_id=intent.intent_id, plan_id=plan.plan_id)
        
        try:
            # Execute each step
            for step in plan.steps:
                self.execute_step(step, sandbox)
            
            # Run tests
            test_results = sandbox.run_tests()
            
            # Measure actual metrics
            actual = self.measure_metrics(intent, plan, sandbox)
            
            # Log completion
            ledger.log("execution_completed", 
                       intent_id=intent.intent_id,
                       status="success",
                       actual=actual,
                       test_results=test_results)
            
            return ExecutionResult(status="success", actual=actual)
        
        except Exception as e:
            ledger.log("execution_completed",
                       intent_id=intent.intent_id,
                       status="failure",
                       failure_reason=str(e))
            
            return ExecutionResult(status="failure", error=e)
    
    def execute_step(self, step, sandbox):
        # Retrieve tactics from KB
        tactics = kb.find_tactics(step.description, step.language)
        
        if tactics:
            # Use proven tactic
            tactic = tactics[0]
            result = sandbox.run_code(tactic.code)
        else:
            # Generate new implementation
            code = self.generate_code(step)
            result = sandbox.run_code(code)
        
        ledger.log("tool_call", 
                   tool_name=step.tool,
                   command=step.command,
                   exit_code=result.exit_code)
        
        return result
    
    def measure_metrics(self, intent, plan, sandbox):
        # Measure actual P(success) (1.0 if we got here, 0.0 if exception)
        p_success = 1.0
        
        # Measure actual entropy
        entropy = self.measure_entropy(intent, sandbox)
        
        # Measure actual impact
        impact = self.measure_impact(intent, sandbox)
        
        # Measure actual cost
        cost = self.measure_cost(sandbox)
        
        return ActualMetrics(
            p_success=p_success,
            entropy=entropy,
            impact=impact,
            cost=cost
        )

```

---

### 3) **Curator Agent**

**Role:** Extract patterns, tactics, and failure modes from ledger and propose KB entries.

**Inputs:**

- Ledger (historical executions)
- KB (existing entries)

**Outputs:**

- KB entry proposals (patterns, tactics, failure modes)
- Evidence (ledger references, success/failure counts)

**Capabilities:**

- Scan ledger for recurring patterns
- Identify successful tactics (5+ uses, 0 failures)
- Identify failure modes (3+ failures, same root cause)
- Propose KB entries with evidence
- Validate against KB write rules

**Trust requirements:**

- **Medium:** Can propose tactics and patterns
- **High:** Can propose failure modes and modules
- **Highest:** Can propose estimator improvements

**Model routing:**

- **Medium tier:** Pattern extraction (similarity matching)
- **Deep tier:** Failure mode analysis (root cause reasoning)

**Example:**
```python
class CuratorAgent:
def __init__(self, agent_id, model, trust_level):
self.agent_id = agent_id
self.model = model
self.trust_level = trust_level

    def extract_patterns(self, ledger, kb, lookback_days=7):
        # Query recent successful intents
        intents = ledger.query_intents(
            status="success",
            since=now() - timedelta(days=lookback_days)
        )
        
        # Group by similarity
        clusters = self.cluster_by_similarity(intents)
        
        # For each cluster with 3+ members
        for cluster in clusters:
            if len(cluster) >= 3:
                # Extract common structure
                pattern = self.extract_common_structure(cluster)
                
                # Validate evidence threshold
                if self.validate_evidence(pattern, cluster):
                    # Propose KB entry
                    kb_entry = self.create_pattern_entry(pattern, cluster)
                    kb.propose_entry(kb_entry)
                    
                    ledger.log("kb_entry_proposed",
                               kb_id=kb_entry.kb_id,
                               kb_type="pattern",
                               evidence=kb_entry.evidence)
    
    def extract_failure_modes(self, ledger, kb, lookback_days=7):
        # Query recent failed intents
        failures = ledger.query_intents(
            status="failure",
            since=now() - timedelta(days=lookback_days)
        )
        
        # Group by failure reason
        failure_groups = self.group_by_failure_reason(failures)
        
        # For each group with 3+ members
        for reason, group in failure_groups.items():
            if len(group) >= 3:
                # Analyze root cause
                root_cause = self.analyze_root_cause(group)
                
                # Identify mitigations
                mitigations = self.identify_mitigations(root_cause, kb)
                
                # Propose failure mode entry
                kb_entry = self.create_failure_mode_entry(reason, root_cause, mitigations, group)
                kb.propose_entry(kb_entry)
                
                ledger.log("kb_entry_proposed",
                           kb_id=kb_entry.kb_id,
                           kb_type="failure_mode",
                           evidence=kb_entry.evidence)

```

---

### 4) **Evaluator Agent**

**Role:** Evaluate plan variants and select the best by EV.

**Inputs:**

- Intent
- Plan variants (with predicted metrics)
- Convergence policy

**Outputs:**

- Selected plan
- Convergence reason (EV plateau, dominant plan, budget exhausted)

**Capabilities:**

- Rank plans by EV
- Check convergence criteria
- Decide when to stop planning
- Log planning convergence

**Trust requirements:**

- **Baseline:** Can evaluate plans using standard EV formula
- **High:** Can propose convergence policy changes

**Model routing:**

- **Flash tier:** Simple EV comparison
- **Medium tier:** Complex convergence logic

**Example:**
```python
class EvaluatorAgent:
def __init__(self, agent_id, model, trust_level):
self.agent_id = agent_id
self.model = model
self.trust_level = trust_level

    def evaluate_and_select(self, intent, variants, convergence_policy):
        # Rank by EV
        ranked = sorted(variants, key=lambda v: v.predicted.ev, reverse=True)
        
        # Check convergence
        converged, reason = self.check_convergence(ranked, convergence_policy)
        
        if converged:
            winner = ranked[0]
            
            ledger.log("planning_converged",
                       intent_id=intent.intent_id,
                       variants_considered=[v.plan_id for v in variants],
                       winner_plan_id=winner.plan_id,
                       reason=reason)
            
            ledger.log("plan_selected",
                       intent_id=intent.intent_id,
                       plan_id=winner.plan_id,
                       predicted=winner.predicted)
            
            return winner
        else:
            return None  # Keep planning
    
    def check_convergence(self, ranked_variants, policy):
        if len(ranked_variants) < 2:
            return False, None
        
        best = ranked_variants[0]
        second_best = ranked_variants[1]
        
        # Dominant plan (EV gap > threshold)
        ev_gap = best.predicted.ev - second_best.predicted.ev
        if ev_gap > policy.dominant_plan_threshold:
            return True, "dominant_plan"
        
        # EV plateau (diminishing returns)
        if len(ranked_variants) >= 3:
            recent_improvement = best.predicted.ev - ranked_variants[-3].predicted.ev
            if recent_improvement < policy.ev_plateau_threshold:
                return True, "ev_plateau"
        
        # Entropy budget exhausted
        planning_cost = sum(v.predicted.cost for v in ranked_variants)
        if planning_cost > policy.planning_budget:
            return True, "budget_exhausted"
        
        # Max variants reached
        if len(ranked_variants) >= policy.max_variants:
            return True, "max_variants_reached"
        
        return False, None

```

---

### 5) **Meta-Agent (Orchestrator)**

**Role:** Coordinate the entire intent lifecycle (creation → planning → execution → measurement → promotion).

**Inputs:**

- Intent queue (pending intents)
- Agent pool (available planner/executor/curator agents)
- Ledger and KB

**Outputs:**

- Work assignments (dispatch intents to agents)
- Intent state transitions
- Human review requests

**Capabilities:**

- Create intents (root or sub-intents)
- Dispatch planning work to planner agents
- Dispatch execution work to executor agents
- Manage git flow (rebase, merge)
- Request human review
- Monitor agent performance
- Adjust trust levels

**Trust requirements:**

- **N/A** (meta-agent is a system component, not a trust-bounded agent)

**Model routing:**

- **Medium tier:** Standard orchestration logic
- **Deep tier:** Complex scheduling, conflict resolution

**Example:**
```python
class MetaAgent:
def __init__(self):
self.intent_queue = IntentQueue()
self.agent_pool = AgentPool()

    def run(self):
        while True:
            # Check for pending intents
            intent = self.intent_queue.pop_next()
            
            if intent is None:
                time.sleep(1)
                continue
            
            # Dispatch based on intent state
            if intent.state == "planning":
                self.dispatch_planning(intent)
            elif intent.state == "ready":
                self.dispatch_execution(intent)
            elif intent.state == "rebasing":
                self.handle_rebase(intent)
            elif intent.state == "awaiting_review":
                self.request_human_review(intent)
            elif intent.state == "approved":
                self.merge_to_parent(intent)
    
    def dispatch_planning(self, intent):
        # Select planner agent based on complexity
        planner = self.agent_pool.select_planner(intent)
        
        # Generate plan variants
        variants = planner.generate_plan_variants(intent, kb, ledger)
        
        # Evaluate and select
        evaluator = self.agent_pool.select_evaluator(intent)
        selected_plan = evaluator.evaluate_and_select(intent, variants, convergence_policy)
        
        if selected_plan:
            intent.state = "ready"
            intent.selected_plan = selected_plan
            self.intent_queue.push(intent)
        else:
            # Keep planning (generate more variants)
            intent.state = "planning"
            self.intent_queue.push(intent)
    
    def dispatch_execution(self, intent):
        # Rebase from parent before execution
        self.rebase_from_parent(intent)
        
        # Select executor agent
        executor = self.agent_pool.select_executor(intent)
        
        # Execute plan
        result = executor.execute_plan(intent, intent.selected_plan, sandbox)
        
        if result.status == "success":
            # Rebase from parent after execution
            self.rebase_from_parent(intent)
            
            # Check if parent intent or sub-intent
            if intent.parent_intent_id is None:
                # Parent intent → request human review
                intent.state = "awaiting_review"
            else:
                # Sub-intent → merge to parent automatically
                intent.state = "ready_to_merge"
            
            self.intent_queue.push(intent)
        else:
            # Execution failed
            intent.state = "failed"
            ledger.log("intent_state_changed",
                       intent_id=intent.intent_id,
                       from_state="executing",
                       to_state="failed",
                       reason=result.error)
    
    def request_human_review(self, intent):
        review_package = self.generate_review_package(intent)
        
        ledger.log("human_review_requested",
                   intent_id=intent.intent_id,
                   review_kind="promotion",
                   summary=review_package.summary)
        
        # Wait for human decision (external process)
        # When decision arrives, update intent state
    
    def merge_to_parent(self, intent):
        parent_branch = self.get_parent_branch(intent)
        
        result = git.merge(intent.branch, parent_branch)
        
        ledger.log("git_merge_attempted",
                   intent_id=intent.intent_id,
                   from_branch=intent.branch,
                   to_branch=parent_branch,
                   status="success" if result.success else "failed")
        
        if result.success:
            intent.state = "merged"
            
            # If merged to main, mark as promoted
            if parent_branch == "main":
                intent.state = "promoted"
                ledger.log("intent_promoted_to_main",
                           intent_id=intent.intent_id,
                           merge_sha=result.merge_sha)

```

---

### 6) **Researcher Agent** (highest trust only)

**Role:** Propose improvements to estimators, routing policies, and core patterns.

**Inputs:**

- Ledger (historical calibration data)
- KB (current estimators and policies)

**Outputs:**

- Estimator proposals (with backtest validation)
- Routing policy proposals (with ROI validation)
- Pattern proposals (with evidence)

**Capabilities:**

- Analyze calibration errors
- Identify systematic biases in estimators
- Propose improved estimator formulas
- Backtest on historical data
- Propose routing policy changes
- Validate ROI improvements

**Trust requirements:**

- **Highest:** Required (with human approval for all proposals)

**Model routing:**

- **Deep tier:** Complex analysis, hypothesis generation, backtest validation

**Example:**
```python
class ResearcherAgent:
def __init__(self, agent_id, model, trust_level):
self.agent_id = agent_id
self.model = model
self.trust_level = trust_level

        if trust_level != "highest":
            raise ValueError("Researcher agent requires highest trust level")
    
    def propose_estimator_improvement(self, metric_name, ledger, kb):
        # Get current estimator
        current = kb.get_active_estimator(metric_name)
        
        # Analyze calibration errors
        errors = self.analyze_calibration_errors(metric_name, ledger)
        
        # Identify systematic biases
        biases = self.identify_biases(errors)
        
        # Generate improved estimator
        improved = self.generate_improved_estimator(current, biases)
        
        # Backtest on historical data
        backtest_results = self.backtest(improved, ledger, window_days=30)
        
        # Check if improvement meets threshold
        if backtest_results.improvement > 0.10:
            # Create proposal
            proposal = self.create_estimator_proposal(
                metric_name=metric_name,
                new_version=f"{metric_name}_v{current.version + 1}",
                based_on=current.kb_id,
                implementation=improved,
                backtest_results=backtest_results
            )
            
            # Submit for human approval
            kb.propose_entry(proposal)
            
            ledger.log("estimator_proposed",
                       estimator_name=metric_name,
                       new_version=proposal.version,
                       calibration_improvement=backtest_results.improvement,
                       human_approval_required=True)
            
            return proposal
        else:
            # Improvement too small, don't propose
            return None

```

---

## Agent lifecycle

### 1) Agent creation

```python
def create_agent(agent_type, model, trust_level="baseline"):
agent_id = generate_agent_id(agent_type)

    agent = {
        "planner": PlannerAgent,
        "executor": ExecutorAgent,
        "curator": CuratorAgent,
        "evaluator": EvaluatorAgent,
        "researcher": ResearcherAgent
    }[agent_type](agent_id, model, trust_level)
    
    ledger.log("agent_created",
               agent_id=agent_id,
               agent_type=agent_type,
               model=model,
               trust_level=trust_level)
    
    return agent

```

### 2) Agent execution

```python
def execute_agent_task(agent, task):
ledger.log("agent_task_started",
agent_id=agent.agent_id,
task_type=task.type,
task_id=task.id)

    try:
        result = agent.execute(task)
        
        ledger.log("agent_task_completed",
                   agent_id=agent.agent_id,
                   task_id=task.id,
                   status="success",
                   result=result)
        
        return result
    
    except Exception as e:
        ledger.log("agent_task_completed",
                   agent_id=agent.agent_id,
                   task_id=task.id,
                   status="failure",
                   error=str(e))
        
        raise

```

### 3) Agent trust update

```python
def update_agent_trust(agent_id, ledger):

# Compute trust score

trust_score = compute_trust_score(agent_id, ledger)

    # Get execution count
    execution_count = ledger.count_executions(agent_id=agent_id)
    
    # Assign trust level
    new_trust_level = assign_trust_level(trust_score, execution_count)
    
    # Get current trust level
    agent = agent_pool.get_agent(agent_id)
    old_trust_level = agent.trust_level
    
    if new_trust_level != old_trust_level:
        agent.trust_level = new_trust_level
        
        ledger.log("agent_trust_changed",
                   agent_id=agent_id,
                   from_trust_level=old_trust_level,
                   to_trust_level=new_trust_level,
                   trust_score=trust_score,
                   execution_count=execution_count)

```

---

## Agent communication

### Agent-to-agent communication (via ledger)

Agents do not communicate directly. Instead:

- Agents **write to ledger** (events, results, proposals).
- Agents **read from ledger** (historical data, calibration).
- Agents **read from KB** (patterns, tactics, estimators).

This ensures:

- **Auditability:** All communication is logged.
- **Isolation:** Agents cannot interfere with each other.
- **Consistency:** Single source of truth (ledger + KB).

### Agent-to-human communication (via review packages)

Agents communicate with humans through:

- **Review packages** (intent summaries, diffs, metrics).
- **Proposals** (estimator improvements, KB entries).
- **Alerts** (critical events, trust degradation).

---

## Agent autonomy levels

### Level 0: No autonomy (human-driven)

- Human creates intents manually.
- Human selects plans manually.
- Human executes manually.

### Level 1: Execution autonomy (baseline trust)

- Agent executes assigned intents.
- Agent cannot spawn sub-intents.
- Agent cannot propose root intents.

### Level 2: Decomposition autonomy (medium trust)

- Agent can spawn sub-intents (up to depth 3).
- Agent can decompose complex intents.
- Agent cannot propose root intents.

### Level 3: Goal autonomy (high trust)

- Agent can propose root intents (subject to human approval).
- Agent can generate goals based on system needs.
- Agent cannot modify estimators.

### Level 4: Meta autonomy (highest trust)

- Agent can propose estimator improvements (subject to human approval).
- Agent can propose routing policy changes.
- Agent can propose KB patterns.
- Agent cannot modify core invariants.

### Level 5: Full autonomy (future, not in bootstrap)

- Agent can modify core invariants (subject to human approval).
- Agent can propose safety policy changes.
- Agent can propose trust model changes.

---

## Agent intent generation (autonomous goal-setting)

### When agents generate intents

Agents with **high or highest trust** can generate intents in these scenarios:

#### 1) **System needs** (proactive)

- Calibration error increasing → propose "Improve P(success) estimator"
- KB missing patterns for common intent type → propose "Extract pattern for X"
- Routing ROI declining → propose "Analyze routing policy effectiveness"

#### 2) **Failure response** (reactive)

- Rebase conflict storm → propose "Refactor module to reduce coupling"
- Repeated test failures → propose "Improve test coverage for module X"
- Sandbox escape attempt → propose "Strengthen sandbox isolation"

#### 3) **Exploration** (curiosity-driven)

- Low-probability tactic with high learning value → propose "Explore alternative approach to X"
- Novel problem with no KB patterns → propose "Research solution for X"

### Intent quality scoring

When an agent proposes an intent, the system scores its quality:

```python
def score_intent_quality(proposed_intent, agent_id, ledger, kb):
score = 0.0

    # Alignment with system needs
    if addresses_calibration_error(proposed_intent, ledger):
        score += 0.3
    if fills_kb_gap(proposed_intent, kb):
        score += 0.2
    if responds_to_failure(proposed_intent, ledger):
        score += 0.3
    
    # Novelty vs redundancy
    similar_intents = kb.find_similar_intents(proposed_intent.goal)
    if len(similar_intents) == 0:
        score += 0.2  # Novel
    else:
        score -= 0.1  # Redundant
    
    # Agent track record
    agent_trust_score = compute_trust_score(agent_id, ledger)
    score += 0.2 * agent_trust_score
    
    # Predicted EV
    predicted_ev = estimate_intent_ev(proposed_intent, kb, ledger)
    if predicted_ev > 50:
        score += 0.2
    
    return max(0.0, min(1.0, score))

```

### Intent approval gates

```python
def approve_intent_proposal(proposed_intent, agent_id, quality_score):
agent = agent_pool.get_agent(agent_id)

    # Trust level gates
    if agent.trust_level == "high":
        # High trust: auto-approve if quality > 0.6
        if quality_score > 0.6:
            return "auto_approved"
        else:
            return "human_review_required"
    
    elif agent.trust_level == "highest":
        # Highest trust: auto-approve if quality > 0.5
        if quality_score > 0.5:
            return "auto_approved"
        else:
            return "human_review_required"
    
    else:
        # Lower trust: always require human review
        return "human_review_required"

```

---

## Agent performance metrics

### Per-agent metrics (tracked in ledger)

- **Success rate:** `successful_executions / total_executions`
- **Mean calibration error:** `mean(|predicted - actual|)` for P(success), ΔS, Impact
- **Mean EV accuracy:** `mean(predicted_ev - actual_ev)`
- **Rebase conflict rate:** `rebase_conflicts / total_executions`
- **Sandbox escape attempts:** `count(sandbox_escape_attempted)`
- **Trust score:** Composite score (see `safety.md`)
- **Execution count:** Total number of intents executed
- **Planning efficiency:** `mean(planning_cost / execution_value)`
- **KB contribution rate:** `kb_entries_proposed / executions`

### Aggregate metrics (system-wide)

- **Mean agent trust score:** Across all agents
- **Trust level distribution:** Histogram of trust levels
- **Agent specialization:** Which agents excel at which intent types
- **Model routing ROI:** By agent and model tier
- **Calibration improvement over time:** System-wide learning curve

---

## Agent specialization (future evolution)

Over time, agents may specialize:

- **Planning specialists:** Excel at generating high-EV plans for specific domains
- **Execution specialists:** Excel at reliable execution with low entropy
- **Curation specialists:** Excel at extracting patterns and failure modes
- **Research specialists:** Excel at proposing estimator improvements

Specialization emerges naturally through:

- **Routing:** Meta-agent routes intents to agents with best track record for that intent type
- **Trust:** Specialized agents earn higher trust in their domain
- **KB:** Agents learn from their own successes and failures

---

## Related documents

- [`safety.md`](safety.md) — trust levels, sandboxing, entropy budgets
- [`ledger_schema.md`](ledger_schema.md) — agent events logged to ledger
- [`kb_schema.md`](kb_schema.md) — agent proposals to KB
- [`metrics.md`](metrics.md) — metrics agents use for decision-making
- [`git_flow.md`](git_flow.md) — git discipline agents must follow
- [`architecture.md`](architecture.md) — how agents fit into system architecture
