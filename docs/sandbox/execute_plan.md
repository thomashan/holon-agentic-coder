# Running Execution via Docker

This guide explains how to run the Sandbox Executor role using the Docker sandbox environment.

The Executor checks out a plan branch, runs the AI coding agent to implement changes, executes validation test suites,
records execution results in the ledger `holon-knowledge/ledger/executions.jsonl`, and pushes the execution branch.

---

## Recommended Execution Method (`./holon` CLI)

> [!IMPORTANT] **Use `./holon` instead of raw `docker run` commands.** Always run sandbox executions via the
> [`./holon`](../../holon) host CLI script from the repository root:

```bash
./holon execute "I-1782654790-bootstrap-holon-cli-intent/P-1784988130-antigravity-agent-gemini-3.5-flash/_" --agent antigravity-agent --model gemini-3.5-flash
```

The `./holon` wrapper script automatically manages:

- GitHub token and API key discovery (`GITHUB_TOKEN`, `HOLON_AGENT_KEY`, etc.)
- Cross-platform SSH agent socket forwarding
- Read-only agent session mounts (`~/.gemini/antigravity-cli`, `~/.config/claude`, etc.)
- Routing role environment variables (`HOLON_ROLE=executor`)

---

## Command Breakdown

- **`plan_branch`** (positional, required): The target plan branch to execute.
- **`--agent`** (optional, default: `antigravity-agent`): Agent runner to execute.
- **`--model`** (optional, default: `gemini-3.5-flash`): Target LLM model name.
