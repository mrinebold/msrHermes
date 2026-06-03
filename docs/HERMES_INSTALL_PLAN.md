# Hermes Install Plan

Planning date: 2026-06-03.

Phase 5B is installation planning only. Do not install Hermes, enable autonomous execution, connect Google Workspace, or connect Home Assistant in this phase.

## Intended Hermes Client

Use the official Nous Research Hermes Agent project:

- Repository: https://github.com/NousResearch/hermes-agent
- Documentation: https://hermes-agent.nousresearch.com/docs/
- Install script: `https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh`
- CLI/package identity: Hermes Agent / `hermes-agent`, exposing the `hermes` command
- Latest release observed on 2026-06-03: `v2026.5.29.2`, branded as Hermes Agent `v0.15.2`

Recommended install target for this Mac mini:

- Use the official per-user git installer only after approval.
- Prefer a reproducible release pin or recorded commit hash for the first production install.
- Do not use root-mode install.
- Do not install third-party desktop repackages for the Phase 5B plan.

Official references:

- https://hermes-agent.nousresearch.com/docs/getting-started/installation/
- https://hermes-agent.nousresearch.com/docs/user-guide/configuration/
- https://hermes-agent.nousresearch.com/docs/user-guide/messaging/
- https://hermes-agent.nousresearch.com/docs/integrations/providers/
- https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp/

## macOS Apple Silicon Installation Options

### Option A: Official Per-User Git Installer

Official command, not to run in Phase 5B:

```sh
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

Expected behavior from official docs:

- Works on macOS, Linux, WSL2, and Termux.
- Requires Git to be available.
- Installs missing runtime dependencies automatically.
- Clones Hermes under the per-user Hermes home.
- Creates a Python virtual environment.
- Creates the `hermes` command under `~/.local/bin/hermes`.
- Starts the model/provider setup flow.

Pros:

- Official supported path.
- No `sudo` expected for the per-user install.
- Captures the upstream expected layout.

Risks:

- Tracks `main` by default, so first install should record the resulting commit.
- May adjust shell path or shell startup files.
- May prompt for model/provider setup before Helio gates are ready.

Recommendation: use this path only after approving shell path behavior and a rollback plan.

### Option B: Manual Pinned Source Install

Planning-only outline:

1. Clone `https://github.com/NousResearch/hermes-agent`.
2. Check out approved tag or commit, initially `v2026.5.29.2` unless a newer release is approved.
3. Use `uv` to create the Python environment.
4. Install Hermes from source with the desired extras.
5. Create the `hermes` command only after path approval.

Pros:

- More reproducible.
- Easier to audit before first run.
- Can pin a known tag.

Risks:

- More manual than the official installer.
- Must ensure extras match standard install behavior.

Recommendation: use this path if we want strict release pinning before the first resident-operator install.

### Option C: pip Install

Official docs list pip install layout as a supported layout, but this is not the preferred first Mac mini plan.

Pros:

- Simple Python package lifecycle.

Risks:

- Less transparent than a source checkout for local governance review.
- Still needs model/provider and tool configuration.

Recommendation: not preferred for Phase 5B.

### Option D: Nix

Hermes has a Nix setup path. This is not recommended for the current Mac mini unless Nix is already part of the machine's approved foundation.

Recommendation: defer.

## Runtime Requirements

### Python

- Hermes requires Python 3.11 or newer.
- The official installer provisions Python 3.11 through `uv` when needed.
- The Hermes virtual environment should remain inside the Hermes install tree, not inside this repository.

### Node

- The official installer provisions Node.js 22.
- Node is used by Hermes features such as browser automation and messaging bridge support.
- Do not separately install Node in Phase 5B.

### Package Manager

- `uv` is the expected Python package manager in the official installer.
- `npx`/Node tooling may be used by MCP servers after install.
- Do not install extra package managers in Phase 5B.

### Supporting Tools

The official installer handles:

- `ripgrep`
- `ffmpeg`
- Git validation or use of available Git

Do not install supporting tools manually during Phase 5B.

### Env Files

Hermes stores secrets in `~/.hermes/.env` by default.

Helio should keep a committed planning sample in:

- `config/hermes.example.env`

The real runtime env file must remain untracked:

- `~/.hermes/.env`
- or a future profile-specific `.env` if a separate Hermes profile is used

No real tokens, API keys, OAuth secrets, Home Assistant tokens, GitHub tokens, or Supabase credentials should be committed.

### Local Storage

Official Hermes configuration storage:

```text
~/.hermes/
  config.yaml
  .env
  auth.json
  SOUL.md
  memories/
  skills/
  cron/
  sessions/
  logs/
```

Recommended Helio/Hermes layout:

```text
~/.hermes/
  hermes-agent/        # official git installer code checkout
  config.yaml          # model, terminal, tools, MCP, non-secret settings
  .env                 # secrets, disabled/blank until approved
  SOUL.md              # resident operator identity
  memories/
  skills/
  cron/
  sessions/
  logs/
```

Optional future profile layout:

```text
~/.hermes/profiles/msr-operator/
```

Recommendation: start with the default `~/.hermes` profile unless a separate profile is required for isolation. Profiles isolate Hermes state, but they do not sandbox filesystem access.

### Service And Launch Agent Behavior

Hermes can run a messaging gateway as a managed macOS launchd agent.

Official behavior:

- `hermes gateway install` creates a user LaunchAgent.
- The default plist path is `~/Library/LaunchAgents/ai.hermes.gateway.plist`.
- The plist captures `PATH`, `VIRTUAL_ENV`, and `HERMES_HOME`.
- Logs are available under `~/.hermes/logs/gateway.log`.
- Multiple profiles create separate LaunchAgent labels.

Phase 5B rule:

- Do not run `hermes gateway install`.
- Do not create a LaunchAgent.
- Do not enable background resident service behavior.
- First install validation should run in foreground only after install approval.

## Connection Plan

### Local Model Router

Current state:

- Helio has a Python model router in `services/model_router`.
- It reads `DEVMONSTER_OLLAMA_URL`, `DEVMONSTER_DEFAULT_MODEL`, `FAST_LOCAL_MODEL`, and related fallback env vars.
- It is not yet exposed as a Hermes-consumable HTTP or MCP endpoint.

Required before governed Hermes use:

- Add a local Helio model-router adapter.
- Preferred adapter: localhost OpenAI-compatible endpoint, for example `http://127.0.0.1:8787/v1`.
- Alternative adapter: Helio MCP server with a `helio_model_route` tool.
- The adapter must log task type, model, provider, elapsed time, and approval requirement.

Phase 5B plan:

- Document the adapter requirement.
- Do not implement or run it yet unless separately approved.

### DevMonster Gemma4

Current DevMonster target:

- Ollama-compatible URL: `http://100.93.120.124:11434`
- Model: `gemma4:26b`
- Network: Tailscale private address

Preferred route:

- Hermes calls Helio model router.
- Helio model router calls DevMonster.

Fallback only after approval:

- Hermes custom model provider points to DevMonster's OpenAI-compatible Ollama endpoint, likely `http://100.93.120.124:11434/v1`.
- This fallback should be used only for low-risk local operator chat until the Helio model-router adapter exists.
- Direct DevMonster routing must not be used for autonomous execution, Google Workspace actions, Home Assistant control, or production code edits.

### Helio Agent Dispatcher

Current state:

- The 40-agent dispatcher does not yet exist as a local service.

Required future interface:

- Local MCP server or localhost HTTP API exposed by Helio.
- Hermes-visible tools should start read-only and dry-run:
  - `helio_policy_check`
  - `helio_request_approval`
  - `helio_audit_event`
  - `helio_agent_list`
  - `helio_task_draft`

Execution tools such as `helio_task_submit` require a later approval gate.

### Future Google Workspace Tools

Hermes has its own Google Workspace skill, but Helio should not give Hermes direct Google authority during install.

Phase 5B posture:

- Do not run Google OAuth.
- Do not place Google credentials in `~/.hermes/.env`.
- Do not configure Hermes Google Workspace skill.
- Future Google usage must route through Helio's permission and audit framework.

Future route:

- Hermes drafts a Google action.
- Helio evaluates scope, permission tier, and approval requirement.
- Helio executes read/draft/write only according to the staged Google Workspace plan.

### Future Home Assistant Tools

Hermes has native Home Assistant support through `HASS_TOKEN` and `HASS_URL`, and the toolset auto-enables when `HASS_TOKEN` is set.

Phase 5B posture:

- Do not set `HASS_TOKEN`.
- Do not set a live `HASS_URL`.
- Do not create a Home Assistant long-lived token.
- Do not enable the Home Assistant toolset.

Future route:

- Hermes proposes a Home Assistant read or action.
- Helio safety layer checks entity/domain allowlists and risk tier.
- Human approval is required for every service call.
- Helio logs the service call and result.

## Proposed Install Directory And Config Layout

Recommended code and runtime layout:

```text
~/.hermes/hermes-agent/              # Hermes code checkout
~/.local/bin/hermes                  # CLI symlink
~/.hermes/config.yaml                # Hermes non-secret config
~/.hermes/.env                       # Hermes secrets, initially blank/minimal
~/.hermes/logs/                      # Hermes logs
~/Library/LaunchAgents/              # No Hermes plist until service approval
```

Recommended project-side planning files:

```text
config/hermes.example.env            # committed sample only
docs/HERMES_INSTALL_PLAN.md          # this plan
docs/HERMES_SECURITY_MODEL.md        # install and runtime safety boundaries
```

Initial `config.yaml` posture after approval:

- model provider points to a Helio model-router adapter if available
- terminal backend remains local but shell/file tools are disabled or approval-gated
- MCP servers expose only Helio read/draft tools
- Google Workspace not configured
- Home Assistant not configured
- gateway not installed as a LaunchAgent

## Phase 5B Approval Gates

Before Hermes may run shell commands:

- approve terminal backend
- define allowed command categories
- configure command approval prompts
- log command, cwd, user approval ID, and result

Before Hermes may edit files:

- define approved project roots
- restrict deletions
- require approval for production code edits
- require diff review before commit

Before Hermes may call Google:

- approve OAuth account and scopes
- start with read-only validation
- log every read
- require approval for sends, edits, shares, deletes, and calendar mutations

Before Hermes may dispatch Helio agents:

- implement Helio agent registry
- define agent capability tiers
- require policy check and audit event
- require human approval for high-risk or external-side-effect tasks

Before Hermes may control Home Assistant:

- implement Home Assistant safety layer
- define entity/domain allowlists
- require approval for all service calls
- keep locks, alarms, garage doors, HVAC, power, appliances, and security systems high risk
- log every call

## Phase 5B Proposed Checklist

1. Review this plan.
2. Confirm install method: official per-user installer or manual pinned source install.
3. Confirm target release or commit.
4. Confirm no root-mode install.
5. Confirm whether `~/.local/bin` path changes are approved.
6. Confirm initial Hermes model provider path.
7. Confirm no LaunchAgent service install.
8. Confirm no Google, Home Assistant, GitHub write, Supabase, or agent-dispatch credentials.
9. Confirm rollback plan.
10. Approve Phase 5C before any install command runs.

## Rollback Plan For Future Install

If a future approved install must be removed:

1. Stop any foreground Hermes process.
2. If a future gateway was installed, remove its launchd agent first.
3. Run the official uninstall command if available.
4. Remove `~/.local/bin/hermes` if it remains.
5. Archive or remove `~/.hermes/` according to the chosen data-retention policy.
6. Remove any shell path modifications if they were added.

Do not perform rollback steps in Phase 5B because Hermes is not installed.

## Phase 5C Install Command Proposal

Status: proposal only. Do not run these commands without explicit approval.

### Source Confirmation

The intended Hermes source remains the official Nous Research Hermes Agent project:

- Repository: `https://github.com/NousResearch/hermes-agent`
- CLI/package identity: `hermes-agent`, exposing the `hermes` command
- Official installer: `https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh`
- First proposed release target: `v2026.5.29.2`

The current installer supports `--skip-setup`, `--branch`, `--commit`, `--dir`, and `--hermes-home`. The proposed command uses `--skip-setup` so Phase 5C installs files only and does not run the interactive setup wizard.

### Environment Inspection

Read-only inspection on 2026-06-03 found:

| Check | Result | Phase 5C meaning |
| --- | --- | --- |
| OS | macOS 26.5, arm64 | Apple Silicon supported by official macOS installer path |
| Git | `/usr/bin/git`, version `2.50.1` | prerequisite present |
| Homebrew | `/opt/homebrew/bin/brew`, version `5.1.14` | present, but not needed for the proposed install |
| Generic Python | `/usr/bin/python3`, version `3.9.6` | below Hermes requirement |
| Python 3.11 | `/opt/homebrew/bin/python3.11`, version `3.11.14` | suitable Python already present |
| Generic Node | `/opt/homebrew/bin/node`, version `25.6.1` | newer generic Node present |
| Node 22 | `/opt/homebrew/opt/node@22/bin/node`, version `22.21.1` | suitable Node 22 present |
| npm/npx | `/opt/homebrew/bin/npm` and `/opt/homebrew/bin/npx`, version `11.9.0` | present |
| ripgrep | `/opt/homebrew/bin/rg`, version `15.1.0` | present |
| uv | not found in PATH or `~/.hermes/bin/uv` | installer should provision managed uv |
| ffmpeg | not found in PATH | installer should provision if needed |
| Hermes CLI | not found | Hermes is not currently installed |
| Hermes home | no `~/.hermes` entry observed | no existing default Hermes home found |
| Hermes symlink | no `~/.local/bin/hermes` entry observed | no existing CLI symlink found |
| launchd plist | no `~/Library/LaunchAgents/ai.hermes.gateway.plist` entry observed | no Hermes gateway service found |
| PATH | includes `~/.local/bin` | no shell profile change should be needed for the CLI symlink |

### Recommended Install Method

Recommended Phase 5C method: official per-user installer, pinned to the observed release tag, with setup and browser bootstrap skipped.

Rationale:

- Uses the official installer and official repo.
- Avoids root-mode install.
- Avoids `hermes setup`.
- Avoids background service setup.
- Avoids Google, Home Assistant, GitHub, Supabase, or agent-dispatch credentials.
- Records the installed release/commit immediately after install.

### Exact Install Commands

Do not run until approved:

```sh
cd /Users/michaelrinebold/Documents/Helio/helio-command-center
mkdir -p /private/tmp/hermes-install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh \
  -o /private/tmp/hermes-install/install.sh
bash /private/tmp/hermes-install/install.sh \
  --skip-setup \
  --skip-browser \
  --branch v2026.5.29.2 \
  --hermes-home "$HOME/.hermes" \
  --dir "$HOME/.hermes/hermes-agent"
"$HOME/.local/bin/hermes" --version
git -C "$HOME/.hermes/hermes-agent" rev-parse --short HEAD
```

Notes:

- `--skip-setup` prevents the interactive setup wizard from running.
- `--skip-browser` avoids browser/Playwright bootstrap for the first install.
- `--branch v2026.5.29.2` pins the checkout to the observed release tag.
- `--hermes-home "$HOME/.hermes"` uses the official default data directory explicitly.
- `--dir "$HOME/.hermes/hermes-agent"` uses the official default code directory explicitly.

Alternative if release pinning fails because the installer expects a branch name:

```sh
cd /Users/michaelrinebold/Documents/Helio/helio-command-center
mkdir -p /private/tmp/hermes-install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh \
  -o /private/tmp/hermes-install/install.sh
bash /private/tmp/hermes-install/install.sh \
  --skip-setup \
  --skip-browser \
  --branch main \
  --hermes-home "$HOME/.hermes" \
  --dir "$HOME/.hermes/hermes-agent"
git -C "$HOME/.hermes/hermes-agent" checkout v2026.5.29.2
"$HOME/.local/bin/hermes" --version
git -C "$HOME/.hermes/hermes-agent" rev-parse --short HEAD
```

Do not run:

```sh
hermes setup
hermes model
hermes gateway install
hermes gateway start
```

### Exact Config File Commands

These commands are proposed for after the installer completes and before the first Hermes launch. Do not run until approved:

```sh
mkdir -p "$HOME/.hermes"
install -m 600 /Users/michaelrinebold/Documents/Helio/helio-command-center/config/hermes.example.env \
  "$HOME/.hermes/.env"
cat > "$HOME/.hermes/config.yaml" <<'YAML'
terminal:
  backend: local
  cwd: /Users/michaelrinebold/Documents/Helio/helio-command-center
  timeout: 60

mcp_servers: {}
YAML
chmod 600 "$HOME/.hermes/config.yaml"
```

This creates:

- `~/.hermes/.env` from the committed blank sample
- `~/.hermes/config.yaml` with no Google, Home Assistant, GitHub, Supabase, or Helio dispatcher credentials

Model configuration should wait until one of these is approved:

1. Helio exposes a localhost model-router adapter, preferred.
2. Direct DevMonster custom provider is approved as a temporary low-risk fallback.

Proposed future model-router config shape after the Helio adapter exists:

```yaml
model:
  provider: custom
  default: gemma4:26b
  base_url: http://127.0.0.1:8787/v1
```

Proposed future DevMonster fallback config only if separately approved:

```yaml
model:
  provider: custom
  default: gemma4:26b
  base_url: http://100.93.120.124:11434/v1
```

### Rollback Commands

Do not run unless rollback is approved or explicitly requested:

```sh
"$HOME/.local/bin/hermes" gateway stop 2>/dev/null || true
launchctl remove ai.hermes.gateway 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/ai.hermes.gateway.plist"
rm -f "$HOME/.local/bin/hermes"
rm -rf "$HOME/.hermes/hermes-agent"
```

Optional data archive before removing Hermes state:

```sh
tar -czf "$HOME/Desktop/hermes-home-backup-$(date +%Y%m%d-%H%M%S).tgz" \
  -C "$HOME" .hermes
```

Optional full state removal after archive approval:

```sh
rm -rf "$HOME/.hermes"
```

### Sudo, launchd, background services, and shell profile changes

Expected Phase 5C install characteristics:

- `sudo`: not needed for the proposed per-user install.
- launchd: not needed; do not run `hermes gateway install`.
- background services: not enabled; do not run `hermes gateway start`.
- shell profile changes: should not be needed because `~/.local/bin` is already on PATH.
- persistent service file: no `~/Library/LaunchAgents/ai.hermes.gateway.plist` should be created.
- setup wizard: skipped with `--skip-setup`.
- browser bootstrap: skipped with `--skip-browser`.

## Stop Conditions

Stop Phase 5C command proposal after documenting exact commands and asking for approval.

Do not:

- install Hermes
- run the Hermes installer
- run `hermes setup`
- run `hermes model`
- run `hermes gateway install`
- enable autonomous execution
- connect Google Workspace
- create Home Assistant tokens
- create GitHub/Supabase credentials
- dispatch agents
