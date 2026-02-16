# FAQ: Architectural Clarifications

This document clarifies the core design decisions for the Autonomous Agentic Coder system, explaining how the architecture addresses common concerns regarding industry standards and operational efficiency.

## 1. How does the system handle LLM context window limits?

The architecture uses a **Just-In-Time (JIT) Context Assembly** strategy. Instead of dumping the entire ledger or codebase into the prompt, we use a "State-On-Demand" model.

- **Ledger Projections:** Agents only receive ledger entries relevant to their specific task type (e.g., a Coding Agent only sees the Plan and File Discovery results).
- **Pull-based Exploration:** No codebase context is provided upfront. Agents must use tools to explore and "pull" specific code snippets into their context as needed.

## 2. Why use a simple file-based Knowledge Base instead of a Vector Database?

We use a **Precision-First Retrieval** strategy. The system relies on simple, fast tools like `grep` or `ripgrep` to find exact matches for symbols, tags, or specific terms.

- **Grep-First Approach:** This ensures 100% precision for technical queries. If an agent needs to find where a function is defined or a project rule is documented, a literal search is often more reliable than a vector
  search that might return a "similar" but irrelevant result.
- **Upgrade Path:** If performance becomes a bottleneck, we can introduce a **Hybrid Retrieval** layer. This would use semantic search to narrow down a large corpus to a smaller set of candidates, followed by exact (
  `grep`-based) search within that set to ensure technical accuracy.

## 3. Why isn't the system built on the Model Context Protocol (MCP)?

We avoid "protocol lock-in." The core architecture remains lean and agnostic. MCP is treated as a **capability of the agent**, not a foundation of the system. If an agent needs a tool available via MCP, the agent manages
that connection itself.

## 4. How do agents understand code structure without AST parsing?

Structural understanding (AST, dependency graphs) is an **evolvable trait**. We do not hardcode these tools into the base system. Agents that acquire or develop AST capabilities will naturally outperform those that
don't, succeeding under evolutionary selection pressure.

## 5. Why use a rigid "Plan-Execute-Measure" loop instead of iterative debugging?

The execution loop is a diagnostic tool for the Planner. If an agent is stuck in a long "fix-it" loop, it indicates the intent was poorly decomposed. By capturing this struggle in the ledger, we can objectively penalise
the Planner, forcing the evolution of better, more granular planning.

## 6. Does the JSONL Ledger suffer from concurrency issues?

No. We use **Git as the Transaction Manager**. Each agent operates on its own branch with its own local ledger. The "rebase at start, rebase at end" rule ensures that state is reconciled before merging into the parent
intent. This provides isolation and atomic commits without a traditional database.

## 7. Why use fixed model tiers instead of dynamic routing?

Fixed models are required for **reproducible evolution**. By treating the Model ID as a fixed variable in an agent's configuration, we can accurately measure whether improvements come from the agent's logic or the
underlying model. Useless or inefficient model-agent pairings are then pruned by selection pressure.

## 8. Isn't competitive planning too expensive?

Cost is an evolutionary pressure. To manage this, the system prioritises **smaller, faster models** for rapid feedback loops. Massive LLMs are a last resort. Agents that achieve successful outcomes using cheaper
resources earn a higher fitness score, naturally driving the system toward cost-efficiency.

## 9. Why use the term "Entropy" instead of "Risk Score"?

Entropy is a relative measure of system disorder within a specific **Project World**. A score of 10 might be "safe" in a complex legacy world but "unstable" in a simple script. The system must learn to calibrate these
thresholds for each unique environment.

## 10. Why force all communication through the Ledger?

There is no "fast path." Every interaction, including simple clarifying questions, must be recorded to ensure the **Evolutionary Record** is 100% traceable and reproducible. We prioritise the integrity of the system's "
DNA" over micro-optimisations in performance.

## 11. Why is the documentation so extensive for an MVP?

The documentation defines the **Architectural North Star**, not a delivery roadmap. Its purpose is to communicate the full design integrity, recursion, git-flow, and evolution, ensuring the core thesis is preserved
regardless of the implementation phase.

## 12. How does the system handle branch bloat from fractal recursion?

Modern Git implementations can handle hundreds of thousands of branches with minimal performance degradation. The branch-per-intent strategy provides a direct, structural mapping between the Git tree and the Ledger,
which is more valuable for traceability than the minor overhead of managing many branches.

## 13. How are financial "blowouts" managed during the bootstrap phase?

The initial evolution process for a new "World Type" will be expensive and slow. While we have not yet designed a specific **Cost Circuit Breaker** mechanism, we acknowledge this as a critical area for future
development. Once a world (like Python) is bootstrapped and stable agents have evolved, the cost per intent drops significantly. For new worlds, the initial high cost is a necessary investment in the system's education.
