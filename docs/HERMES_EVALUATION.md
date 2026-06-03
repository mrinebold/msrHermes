# Hermes Evaluation

Planning date: 2026-06-03.

Phase 5A is planning only. Hermes has not been installed, configured, authenticated, or connected to any local service.

## Objective

Evaluate Nous Research Hermes Agent as the resident supervisory agent for the Helio Command Center Mac mini.

Updated operating intent:

- Hermes should own this machine as the primary local operator.
- Helio should remain the governed access layer for the broader agent network.
- Hermes should use Helio's governance rules to reach the rest of the agent fleet instead of bypassing them.

## Current Hermes Baseline

Sources reviewed:

- Official installation guide: https://hermes-agent.nousresearch.com/docs/getting-started/installation/
- Official repository: https://github.com/NousResearch/hermes-agent
- Latest release page: https://github.com/NousResearch/hermes-agent/releases/latest
- MCP feature docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp/
- AI provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers/
- Google Workspace skill docs: https://hermes-agent.nousresearch.com/docs/user-guide/skills/google-workspace
- Home Assistant docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/homeassistant
- Tools reference: https://hermes-agent.nousresearch.com/docs/reference/tools-reference/

As of 2026-06-03, the latest GitHub release observed was `v2026.5.29.2`, branded as Hermes Agent `v0.15.2`, released 2026-05-29.

## Installation Requirements

Supported installation paths:

- Linux, macOS, WSL2, and Termux: one-line shell installer from the official repository.
- Windows native: PowerShell installer, currently described as early beta.
- Developer setup: clone the repository, run `setup-hermes.sh`, or create a Python 3.11 virtual environment with `uv` and install editable extras.

The standard installer is designed to provision:

- `uv`
- Python 3.11
- Node.js 22
- `ripgrep`
- `ffmpeg`
- Git, or portable Git on native Windows when needed
- Hermes source checkout
- Python virtual environment
- Global `hermes` command
- Initial LLM provider configuration flow

Default per-user layout:

- Code: `~/.hermes/hermes-agent/`
- CLI symlink: `~/.local/bin/hermes`
- Data and config: `~/.hermes/`

Root-mode layout exists for shared-machine installs, but Helio should avoid it for now because current Helio operating rules avoid `sudo` and public service exposure without explicit approval.

Important Phase 5A decision: do not run the installer yet. A future install phase should first approve install path, account, network binding, credentials, and which Hermes tools are enabled.

## Capability Summary

Hermes is strongest as a persistent personal or server-resident agent. Its relevant capabilities include:

- Multi-provider model configuration, including cloud providers and custom OpenAI-compatible endpoints.
- Custom endpoint support suitable for Ollama and other self-hosted model servers.
- Built-in tools for files, terminal, browser, web, memory, scheduled jobs, delegation, code execution, and messaging.
- MCP client support for stdio and HTTP MCP servers with per-server tool filtering.
- Ability to run as an MCP server exposing messaging bridge tools.
- Skill system with bundled and optional skills, including GitHub workflows and Google Workspace.
- Home Assistant support through both gateway events and LLM-callable device tools.
- Messaging gateway orientation for Telegram, Discord, Slack, WhatsApp, and related surfaces.
- Memory and skill self-improvement loops that can make it more useful over time.

## Evaluation Against Helio Components

| Helio area | Hermes fit | Overlap | Gaps and risks | Recommended posture |
| --- | --- | --- | --- | --- |
| Model Router | Medium to high | Hermes can select providers and use custom endpoints, including Ollama-style OpenAI-compatible URLs. | Helio already has explicit private-first routing, audit fields, and fail-closed cloud placeholders. Hermes model switching may bypass Helio's local/cloud policy if unconstrained. | Let Hermes call Helio's model router for governed tasks. Allow direct Hermes model use only for local operator chat and low-risk planning. |
| DevMonster Gemma4 | High | Hermes custom endpoint support can point at DevMonster's Ollama/OpenAI-compatible service. | Gemma4 latency is high for control-plane routing; Hermes may need a faster model for command parsing. DevMonster is not yet approved for autonomous execution decisions. | Configure Hermes to use DevMonster through Helio policy or a Helio-provided custom endpoint once approved. Keep direct DevMonster credentials out of unrestricted Hermes sessions. |
| Google Workspace | High | Hermes has a bundled Google Workspace skill covering Gmail, Calendar, Drive, Contacts, Sheets, and Docs with OAuth/token refresh. | Hermes can send, reply, create events, update sheets, and modify resources; this exceeds Helio's current read-only/draft-first rollout. | Use Hermes for draft/proposal workflows only until Helio's Google approval gates exist. Prefer Helio-held OAuth policy and audit logs over standalone Hermes authority. |
| GitHub | High | Hermes supports GitHub workflows through skills and MCP servers with tool whitelisting. | GitHub writes, PR merges, issue changes, and CI-triggering actions require policy gates. Token scope can become too broad. | Expose a GitHub MCP server or Helio GitHub gateway with minimal read/draft tools first; add write tools after approval IDs and audit logging. |
| Home Assistant | High but high-risk | Hermes has native Home Assistant integration using `HASS_TOKEN` and `HASS_URL`, with device query/control tools and event gateway support. | Physical-world actions are high-risk. A single long-lived token may expose broad Home Assistant authority. | Do not give Hermes direct broad Home Assistant control in Phase 5. Route Home Assistant actions through Helio allowlists and approval gates. Read-only telemetry can be considered first. |
| Future Supabase task bus | Medium | Hermes can connect to databases/internal APIs through MCP, HTTP tools, code execution, or custom skills. | No Helio task bus exists yet; direct DB writes could bypass queue semantics, lease handling, idempotency, and audit trails. | Build Supabase task bus as Helio's governed queue. Hermes submits tasks to Helio, not directly to all agents. |
| 40-agent fleet | Medium to high | Hermes can delegate, spawn subagents, use MCP, and communicate over gateways. | Raw delegation could ignore per-agent permissions, rate limits, ownership boundaries, and audit requirements. | Hermes should access the fleet through Helio's agent registry and governance rules. Helio mediates identity, capability grants, task leases, and audit. |

## Overlap

Hermes overlaps with planned Helio work in several places:

- Supervisor UI/API intent: Hermes already provides persistent agent behavior, sessions, messaging, jobs, and command surfaces.
- Worker queue intent: Hermes has delegation, cron, and task execution patterns.
- Model routing: Hermes can configure model providers and custom endpoints.
- Google Workspace: Hermes has an existing bundled workflow.
- Home Assistant: Hermes has existing native support.
- GitHub: Hermes has skills and MCP-based access patterns.
- Memory and skills: Hermes has a more mature learning loop than current Helio scaffolding.

This overlap is useful, but only if Helio narrows to governance instead of duplicating every Hermes operator feature.

## Gaps

Hermes does not automatically provide the Helio-specific guarantees already defined in this repository:

- Private-first model routing as an enforced policy boundary.
- Fail-closed cloud provider behavior.
- Explicit approval IDs for sensitive actions.
- Append-only Helio audit event schema.
- Tailscale-only network posture as a project rule.
- Home Assistant high-risk entity/domain allowlists.
- Google Workspace read-only, draft-only, then approved execution progression.
- Fleet governance for 40 agents.
- Future task bus semantics such as leases, retries, idempotency, priority, dead-lettering, and per-agent capability grants.

## Replacement Opportunities

Hermes can likely replace or defer these Helio implementation areas:

- A custom always-on chat shell for this Mac mini.
- A custom memory system in early phases.
- A custom skill/plugin discovery system.
- Some custom Google Workspace workflow code, if Helio wraps Hermes execution behind approval gates.
- Some custom Home Assistant query code, if Helio limits Hermes to read-only telemetry or approved service calls.
- Some custom GitHub workflow helpers, if exposed through a filtered MCP server or skill path.

Hermes should not replace these Helio areas:

- Governance policy.
- Approval gates.
- Audit log ownership.
- Secret scoping.
- Physical-world action policy.
- Agent fleet registry and capability grants.
- Supabase task bus contract.

## Recommended Decision

Hermes should own this machine, but should not become all of Helio.

Recommended role split:

- Hermes: resident machine owner, local operator, conversation surface, memory, skills, scheduling, and hands-on task execution on this Mac mini.
- Helio: governance plane, agent fleet access broker, model-routing policy, approval gate, audit log, and future Supabase task bus.

Against the original options:

- `become Helio`: partially. Hermes should become the local operator face of Helio on this Mac mini.
- `operate under Helio`: not quite. The desired direction is for Hermes to own the machine rather than remain only a subordinate worker.
- `operate beside Helio`: acceptable only during evaluation.

Final recommendation: Hermes should become Helio's local machine owner while Helio remains the governance substrate for external systems and the 40-agent fleet.

## Phase 5A Conclusion

Hermes is a strong fit for the resident supervisory layer if authority is deliberately split:

1. Hermes gets local presence.
2. Helio retains governance.
3. All high-risk external access goes through Helio policy.
4. The 40-agent network is exposed to Hermes through a Helio agent gateway, not direct ad hoc tool access.

No Hermes installation should happen until Phase 5B approves install path, model routing, credentials, tool exposure, and audit integration.
