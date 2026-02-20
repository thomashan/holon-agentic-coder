With your SSH keys mounted, the container now has the "identity" needed to clone and push directly to GitHub. The
process is now a fully automated loop where the container handles the Git heavy lifting.

### 1. The Overall Process

1. **Inception:** You run `./holon create-intent`. The container clones the `main` branch, creates a new branch (e.g.,
   `I-0-bootstrap`), appends the intent to the ledger, commits with a descriptive message, and **pushes
   ** to GitHub.
2. **Planning:** You run `./holon plan`. The container fetches the intent branch, spawns a planner agent to create
   `plan.md`, commits it to a new `P-` branch, and **pushes** to GitHub.
3. **Execution:** You run `./holon execute`. The container fetches the plan branch, spawns a coder agent to write the
   code, commits it to an `E-` branch, and **pushes** to GitHub.
4. **Synchronisation:** On your host machine, you simply run `git fetch` to see all the "thinking" and "coding" the
   agents have done.

---

### 2. Example Commands

#### Step 0: Build the Orchestrator

Ensure your Docker image is up to date with the latest entrypoint scripts.

```bash
docker build --target holon-orchestrator -t holon/orchestrator .
```

#### Step 1: Create the Root Intent

This command mounts your local JSON and your SSH keys. The agent will push the new branch to origin.

```bash
./holon create-intent $(pwd)/app/scripts/intent_bootstrap_cli.json
```

* **Result:** A new branch `I-0-bootstrap-cli` appears on GitHub.

#### Step 2: Generate Competing Plans

The agent will branch off the intent branch and push the plans.//`

```bash
./holon plan I-0-bootstrap-cli/_ pi claude-3.5-sonnet
./holon plan I-0-bootstrap-cli/_ opencode gemini-2.0-flash
```

* **Result:** Branches like `I-0-bootstrap-cli/P-17082500-architect-agent-claude-3.5-sonnet` are pushed.

#### Step 3: Execute an Action

Pick a plan branch and tell an agent to code a specific action.

```bash
./holon execute I-0-bootstrap-cli/P-17082500-architect-agent-claude-3.5-sonnet coder-agent claude-3.5-sonnet init-project
```

* **Result:** An execution branch `I-0-bootstrap-cli/P-.../E-...-init-project` is pushed with the new code.

#### Step 4: Sync and Review on Host

Since the agents pushed everything to GitHub, you can review the work locally on your Mac.

```bash
git fetch origin
git checkout I-0-bootstrap-cli/P-17082500-architect-agent-claude-3.5-sonnet/E-1708250050-coder-agent-claude-3.5-sonnet-init-project
# Review the code in your IDE
```

---

### 3. Critical Script Reminders

For this to work, ensure your **`intent_creator.sh`** (and others) use the SSH URL:

```bash
# Inside the container scripts
git clone git@github.com:Holon-Agentic-Coder/holon-agentic-coder-ref.git
```

And ensure you handle the **Known Hosts** to avoid the "Host authenticity" prompt:

```bash
# Add this to the top of your entrypoint scripts or Dockerfile
mkdir -p ~/.ssh
ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null
```

This setup creates a "Cloud-Native" development loop where your local machine is just a thin client for the agentic
swarm working in Docker.

--------

```bash
docker run --rm -it \
      -v /Users/thomashan/git/holon-agentic-coder-ref/app/scripts/intent_bootstrap_cli.json:/tmp/intent.json \
      -v "$HOME/.ssh":/home/holon/.ssh:ro \
      --entrypoint=/bin/bash holon/orchestrator

export INTENT_BRANCH=I-0-bootstrap-cli/_
export AGENT_NAME=pi
export MODEL_NAME=qwen3-coder-30b
```
