# Architecture

## Goal

Helio Command Center will coordinate local and cloud-connected research operations while keeping authority permission-gated and auditable.

## Proposed Components

- Supervisor UI/API: local-first command surface for task review, approvals, status, and logs.
- Policy gate: centralized approval rules for installing software, using credentials, reaching external APIs, and changing system state.
- Worker queue: task dispatch layer for local workers and future remote workers.
- Local model worker: Ollama/Gemma-based worker for private local reasoning where appropriate.
- Google Workspace connector: permission-scoped integration for mail, calendar, drive, docs, sheets, and tasks.
- Home Assistant connector: Tailscale or LAN-only integration for home telemetry and approved automations.
- Audit log: append-only local event stream for commands, approvals, rejections, and worker outputs.
- Secrets store: local `.env` during development, moving to a managed secret store if needed.

## Default Network Posture

- Bind local services to `127.0.0.1` by default.
- Permit remote access only through Tailscale when explicitly approved.
- Do not expose inbound services to the public internet.

## Bootstrap Boundary

This initial scaffold performs inspection only. Installation and service configuration are deferred until approval.
