# Strategic Framework for Coding Agent Selection

This document establishes the technical rationale and comparative observations used to evaluate and select the optimal agentic framework for this project.

## Selection Methodology and Performance Benchmarks

The operational efficiency of Large Language Models (LLMs) is fundamentally dictated by two distinct phases: token ingestion (input) and token generation (output). A primary objective of our evaluation is to identify
tools that rigorously minimise input token volume whilst simultaneously maximising the precision and quality of the output. It is a core tenet of this framework that high-quality technical outcomes are frequently
inversely correlated with excessive token generation.

As several contemporary agents support the integration of alternative models—including local LLMs—the efficiency of the input/output cycle is a critical metric for reducing latency and operational costs. Furthermore, we
evaluate the "background noise" inherent in these tools. Many mainstream agents initiate automated request-response cycles before the user’s primary intent is even processed, introducing significant overhead that impedes
the rapid, iterative feedback loops required for agile development.

## Comparative Analysis of Architectural Efficiency

Empirical testing across several prominent agents reveals that mainstream solutions, specifically `claude-code`, `gemini-cli`, `openai-codex`, and `opencode`, tend to generate excessively bloated context windows. Even
when processing a trivial "hello" prompt, these agents transmit substantial data payloads (ranging from 27KB to 73KB per request).

Whilst server-side caching can mitigate the computational load on the model, it fails to address the physical payload size transmitted across the network. Most contemporary APIs operate statelessly; consequently, the
entire conversation history, system instructions, and tool definitions must be re-transmitted with every interaction. This architecture results in significant "over-the-wire" latency, even for the most rudimentary tasks.

In contrast, the `pi-coding-agent` demonstrates a highly streamlined footprint (approximately 4.6KB). Whilst larger agents may be suitable for monolithic planning tasks requiring exhaustive research, their architectural
overhead is difficult to justify for standard, iterative coding workflows where agility and responsiveness are paramount. Detailed logs of these interactions, filtered to isolate core LLM messaging, are available for
review in `docs/agent_selection/logs/{coding_agent}`.

## Monitoring and Quantified Methodology

To accurately quantify the data exchange, we employed `mitm` (man-in-the-middle) interception. By routing agent traffic through a transparent proxy, we inspected the raw request and response payloads transmitted to the
LLM APIs. This provided granular visibility into the structure and magnitude of the data. Note that these interception flows are not retained, as they contain sensitive session and authentication credentials.

## Technical Profiles and Performance Constraints

Our evaluation of the tested agents reveals distinct technical profiles, each with specific limitations regarding stability and efficiency.

### 1. Gemini CLI (gemini-cli)

* **Substantial Request Bloat:** A simple interaction triggers a ~40KB payload containing extensive system instructions and complex tool definitions (e.g., `codebase_investigator`).
* **Stateless Latency:** The client re-transmits the full context with every request, leading to significant network overhead despite the use of session identifiers.
* **Service Instability:** Logs indicate a susceptibility to timeouts and throttling, likely exacerbated by the sheer magnitude of the stateless context processed on every turn.
* **Performance Degradation:** Exhibits "state degradation" during prolonged sessions, frequently conflating historical information with the current state after approximately 20% of the context window is consumed.
  Evidence also suggests capability capping or routing to lower-precision (quantised) models during peak traffic periods.
* **Model Constraint:** Locked to proprietary models; lacks support for alternative or local LLMs.

### 2. OpenAI Codex (openai-codex)

* **Inherent Context Overhead:** Initial sessions involve ~27KB requests, burdened by verbose personality guidelines and complex JSON schemas for tool execution.
* **Network Inefficiency:** Operates statelessly in this CLI implementation, re-sending heavy instructions and schemas on every turn, which increases both latency and bandwidth consumption.
* *Model Drift and Safety Rerouting:** Since the "5.3 API" release in February 2026, users have reported severe degradation in technical creativity (the "frontal lobotomy" effect). This is largely attributed to safety
  protocols: as `gpt-5.3-codex` possesses advanced cybersecurity capabilities, the system frequently reroutes requests to less capable reasoning models when potential cyber-activity is detected, resulting in an
  inconsistent and degraded user experience.
* **Model Constraint:** Locked to proprietary models; lacks support for alternative or local LLMs.

### 3. Claude Code (claude-code)

* **Extreme Payload Magnitude:** Demonstrated the largest footprint, with ~73KB requests for initial interactions, including verbose skill descriptions and full state dumps.
* **Ineffective Bandwidth Optimisation:** Despite the presence of prompt-caching headers, the client continues to upload the massive 73KB payload on every request, failing to reduce network latency for the end-user.
* **Load-Based Degradation:** Users report frequent quality regressions and increased hallucinations during peak usage. Whilst developers deny intentional model switching, optimisation techniques such as reduced sampling
  precision or shallower search under high load can visibly compromise output quality.
* **Model Flexibility:** Supports integration with alternative models, including local LLM instances.

### 4. Opencode (opencode)

* **Unexpected Architectural Weight:** Contrary to its "lean" marketing, the agent transmits payloads exceeding 50KB.
* **Instructional Verbosity:** Includes exhaustive prompts regarding tone and proactiveness, making it heavier than both Gemini CLI and OpenAI Codex in standard operations.
* **Behavioural Drift:** Decision-making patterns tend to deviate from system specifications over extended interactions, a phenomenon common in complex multi-agent systems.
* **Model Agnostic:** Explicitly designed to be LLM agnostic.

### 5. Pi Coding Agent (pi-coding-agent)

* **Streamlined Architecture:** Demonstrates a significantly reduced footprint with a request size of only ~4.6KB.
* **Operational Efficiency:** Utilises a concise system prompt and surgical tool definitions, making it far more effective for iterative coding tasks where low latency is prioritised over autonomous research.
* **Degradation Mitigation:** By maintaining a lean context and avoiding complex multi-tool orchestration, Pi is significantly less susceptible to the "context rot" and performance volatility observed in bloated
  mainstream agents.
* **Model Agnostic & Extensible:** Designed to be LLM agnostic and features a marketplace where additional tooling capabilities can be integrated dynamically.

## Synthesis of Large Language Model Volatility

The evaluation confirms that mainstream coding agents are subject to three primary forms of performance degradation:

* **Model and Behavioural Drift:** Continuous model updates and system load lead to unannounced shifts in performance, often resulting in less precise code generation or a failure to adhere to complex technical
  constraints.
* **Context Rot:** As the context window approaches capacity, attention mechanisms become overextended, leading to hallucinations, ignored instructions, and the inadvertent deletion of functional code.
* **Load-Induced Volatility:** Performance is dynamic rather than static. During peak periods, models exhibit increased latency and reduced quality due to server-side optimisation strategies (e.g., quantisation or
  reduced sampling precision) or safety-based routing protocols.

## Final Selection Rationale

It is objectively clear that `pi-coding-agent` is the superior choice for high-frequency, iterative development due to its lean context and rapid feedback capabilities. Consequently, `pi` will serve as the primary tool
for the development lifecycle.

Whilst `pi` is the preferred agent the other coding agents will continue to be utilised in a secondary capacity. This will allow for ongoing comparative
benchmarking and ensure that the project benefits from the specialised research capabilities of larger models when the task complexity warrants the additional overhead.
