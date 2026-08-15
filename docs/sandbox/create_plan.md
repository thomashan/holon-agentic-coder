# Running Plan Generation via Docker

This guide explains how to run the Plan Generation role using the Docker sandbox environment.

The Planner initializes a new plan branch off of the active intent branch, compiles a prompt using system templates and
intent metadata, runs the AI agent (e.g.,`pi`) to write a structured markdown plan, extracts predicted metrics, logs
them to the plans ledger `holon-knowledge/ledger/plans.jsonl`, and pushes the new plan branch to the remote repository.

---

## Prerequisites

Before running the command, ensure you have:

1. Built the Docker images using the build script:
   ```bash
   ./apps/sandbox-executor/build_all_images.sh
   ```
2. Set up SSH keys on your host machine configured for GitHub access.
3. Configured SSH keys and ensured your local SSH agent is running and has your keys loaded (i.e., `ssh-add -l` displays
   your key), as SSH Agent Forwarding inside the container relies on host authentication.
4. Created an intent branch (e.g., `I-1771890389-refactor-metrics/_`) and registered it in the intent ledger.

---

## Recommended Execution Method (`./holon` CLI)

> [!IMPORTANT] **Use `./holon` instead of raw `docker run` commands.** The host wrapper script [`./holon`](../../holon)
> automatically manages image mapping, credential passing, and SSH agent socket mounts.

Run from the repository root:

```bash
./holon plan "I-1782654790-bootstrap-holon-cli-intent/_" --agent pi-agent --model gemini-3.5-flash
```

---

## Low-Level Execution (Manual `docker run`)

If you need to invoke Docker manually, run the following command to start the planner container, replacing arguments as
needed:

### For macOS (Docker Desktop)

```bash
docker run --rm \
  -e HOLON_ROLE=planner \
  -v /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock \
  -e SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock \
  holon/agent-pi \
  "I-1782654790-bootstrap-holon-cli-intent/_" \
  "pi-agent" \
  "gemini-3.5-flash"
```

### For Linux

> [!IMPORTANT] Ensure your `SSH_AUTH_SOCK` environment variable is set and non-empty (e.g., `echo $SSH_AUTH_SOCK` shows
> a path) before running this command. If it is empty, the bind mount `-v "$SSH_AUTH_SOCK:/run/ssh-agent"` will resolve
> to a syntax error.

```bash
docker run --rm \
  -e HOLON_ROLE=planner \
  -v "$SSH_AUTH_SOCK:/run/ssh-agent" \
  -e SSH_AUTH_SOCK=/run/ssh-agent \
  holon/agent-pi \
  "I-1782654790-bootstrap-holon-cli-intent/_" \
  "pi-agent" \
  "gemini-3.5-flash"
```

### Argument Breakdown:

- **`-e HOLON_ROLE=planner`**: Routes the entrypoint call to the Python planner module (`planner.py`) inside the
  container.
- **`-v /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock` / `-v "$SSH_AUTH_SOCK:/run/ssh-agent"`**:
  Mounts the host's SSH agent socket into the container to enable SSH Agent Forwarding. This allows the container to
  authenticate using your host's SSH credentials securely without exposing private key files directly to the container.
  (The container automatically configures `StrictHostKeyChecking=no` internally).
- **`holon/agent-pi`**: The name of the built Docker image for the chosen agent (e.g., `holon/agent-pi`,
  `holon/agent-claude`).
- **Container Arguments:**
  1. **`intent_branch`** (e.g., `"I-1771890389-refactor-metrics/_"`): The target intent branch to branch off from.
  2. **`agent_name`** (e.g., `"pi-agent"`): The name of the planning agent.
  3. **`model_name`** (e.g., `"gemini-3.5-flash"`): The model used for planning.

---

## 2. Execution Details & Fail-Fast Behavior

During execution, the container performs the following operations:

1. Clones the repository fresh into `/home/holon/repo` targeting the provided `intent_branch`.
2. Creates an ephemeral plan branch: `I-{timestamp}-{slug}/P-{plan_timestamp}-{agent_name}-{model_name}/_`.
3. Compiles a detailed prompt using the template in `holon-config/prompts/planner.template.md` combined with the intent
   data from the ledger.
4. Invokes the AI planning agent (and fails fast, exiting with a non-zero exit code if the agent invocation fails or
   returns empty).
5. Parses metrics (`p_success`, `entropy`, `impact`, `cost`, `learning_value`, `ev`) directly from the markdown plan
   file.
6. Appends a structured plan entry to `holon-knowledge/ledger/plans.jsonl`.
7. Commits the changes and pushes the plan branch to origin.

---

## 3. Verification

Once execution completes, you should verify:

1. A new remote plan branch exists:
   ```bash
   git fetch origin && git branch -r
   # e.g., origin/I-1771890389-refactor-metrics/P-1772691068-pi-agent-gemini-3.5-flash/_
   ```
   > [!NOTE] The agent name in the branch and plan identifiers reflects the `agent_name` argument passed to the
   > container (e.g., `pi-agent`, `claude-agent`, `antigravity-agent`).
2. The generated plan markdown file is present under `plans/`:
   ```markdown
   # plans/P-{timestamp}-{agent}-{model}.md
   ```
3. A plan entry is appended to `holon-knowledge/ledger/plans.jsonl` with parsed metrics and expected value (EV)
   calculations:
   ```json
   {
     "plan_id": "P-1772691068-pi-agent-gemini-3.5-flash",
     "intent_branch": "I-1771890389-refactor-metrics/_",
     "agent": "pi-agent",
     "model": "gemini-3.5-flash",
     "p_success": 0.7,
     "entropy": 2.5,
     "impact": 1.0,
     "cost": 0.5,
     "learning_value": 0.0,
     "ev": 0.45,
     "created_at": "2026-06-27T13:14:15.000Z",
     "plan_file": "plans/P-1772691068-pi-agent-gemini-3.5-flash.md",
     "status": "proposed"
   }
   ```
