# Architecture

## Goal

Helio Command Center will coordinate local and cloud-connected research operations while keeping authority permission-gated and auditable.

## Proposed Components

- Supervisor UI/API: local-first command surface for task review, approvals, status, and logs.
- Policy gate: centralized approval rules for installing software, using credentials, reaching external APIs, and changing system state.
- Worker queue: task dispatch layer for local workers and future remote workers.
- Private model worker: DevMonster-hosted Gemma4 endpoint on the Tailscale mesh, with local runtimes as optional fallbacks.
- Google Workspace connector: permission-scoped integration for mail, calendar, drive, docs, sheets, and tasks.
- Home Assistant connector: Tailscale or LAN-only integration for home telemetry and approved automations.
- Audit log: append-only local event stream for commands, approvals, rejections, and worker outputs.
- Secrets store: local `.env` during development, moving to a managed secret store if needed.

## Model Routing Strategy

Helio should prefer private inference before cloud APIs whenever feasible.

Routing order:

1. DevMonster Gemma4 endpoint on the private Tailscale mesh.
2. Localhost-only model runtimes on the Mac mini, if configured.
3. Cloud AI APIs only when the task requires capabilities unavailable locally or privately, and only through an explicit policy gate.

The DevMonster endpoint should be treated as an OpenAI-compatible API where possible so workers can share client code, request schema, timeout handling, and future fallback behavior. The supervisor should keep inference endpoints private, avoid public ingress, and record model routing decisions in the audit log when tasks cross from local supervision to a worker node.

Initial configuration placeholders:

- `GEMMA_BASE_URL`
- `GEMMA_API_KEY`
- `GEMMA_MODEL`
- `GEMMA_TIMEOUT`

## Default Network Posture

- Bind local services to `127.0.0.1` by default.
- Permit remote access only through Tailscale when explicitly approved.
- Do not expose inbound services to the public internet.

## Bootstrap Boundary

This initial scaffold performs inspection only. Installation and service configuration are deferred until approval.
