# Hermes Private Network Access

Status: Phase 7G local private-access plan and helper implementation

## Current Discovery

Mac mini local identity:

- hostname: `mac-mini.local`
- computer name: `Michael’s Mac mini`
- current user: `michaelrinebold`
- repo path: `/Users/michaelrinebold/Documents/Helio/helio-command-center`

Tailscale:

- Tailscale command is installed at `/Applications/Tailscale.app/Contents/MacOS/Tailscale`.
- Direct Tailscale status during Phase 7H showed the Mac mini on the tailnet.
- Mac mini Tailscale hostname: `michaels-mac-mini`.
- Mac mini Tailscale IPv4: `100.80.79.75`.
- Visible tailnet nodes during Phase 7H: `civic-main` at `100.92.126.17`, `devmonster-4` at `100.93.120.124`, `ipad-pro-12-9-gen-5` at `100.96.95.115`, and `iphone-15-pro-max` at `100.92.128.26`.
- `civic-dev` was not visible in the Phase 7H Tailscale status output.

LAN:

- Detected non-loopback interface IPv4 addresses during Phase 7G/7H discovery: `192.168.68.101`, `192.168.68.56`, and Tailscale `100.80.79.75`.
- The detected `192.168.68.101` conflicts with the previously known civic-dev LAN IP. Treat LAN fallback host/IP assumptions as stale until manually verified.

SSH:

- `~/.ssh` exists with mode `700`.
- `~/.ssh/authorized_keys` exists with mode `600`.
- `authorized_keys` had 3 lines during Phase 7G discovery.
- `com.openssh.sshd` appeared not running.
- No TCP listener on port `22` was detected by `lsof`.
- If macOS Remote Login is needed, enable it manually in System Settings or with an explicitly approved admin step. Do not use sudo from this phase.

Service reachability:

- DevMonster was visible on Tailscale at `100.93.120.124`.
- `curl http://100.93.120.124:11434/api/version` failed to connect during Phase 7H, so DevMonster Ollama service reachability is not currently confirmed from the Mac mini.

Repo:

- Branch: `main`.
- Public exposure changes: none.
- Adapter listener: remains localhost-only when running.

## Approved Inbound Machines

Approved clients that may be configured to reach the Mac mini over private paths:

- `civic-main`
- `civic-dev`
- `DevMonster`
- future machines added by explicit allowlist decision

Approved inbound path:

1. Tailscale SSH or standard SSH over Tailscale.
2. Trusted LAN fallback only when Tailscale is unavailable and the target IP is manually verified.

Forbidden inbound path:

- public internet exposure
- router port forwarding
- public DNS exposure
- adapter or Hermes endpoint binding to `0.0.0.0`
- direct exposure of port `8088`

## Approved Outbound Machines

Approved nodes the Mac mini may reach over private paths:

- DevMonster Tailscale: `100.93.120.124`
- DevMonster Ollama endpoint: `http://100.93.120.124:11434`
- civic-main after its private hostname/IP and key are verified
- civic-dev after its private hostname/IP and key are verified

## Operating Boundary

Private SSH access does not enable external integrations.

It does not approve:

- Google connection
- Supabase or Agent Bus connection
- Home Assistant connection
- GitHub token use
- Helio connection
- public endpoint exposure
- Hermes command execution
- Hermes Desktop launch

The current Hermes endpoint strategy remains SSH tunnel access to a localhost-only adapter.

## Remote And iPad Access

Phase 7H extends this model to remote and iPad use.

Required remote posture:

- remote/iPad access is Tailscale-only
- iPad access uses an SSH app over Tailscale
- remote laptop access uses standard SSH over Tailscale
- endpoint access uses an SSH tunnel for now
- public exposure is not approved
- Tailscale Funnel/public access is not approved
- direct adapter exposure is not approved
- adapter remains localhost-only

Detailed procedure:

- [Hermes Remote And iPad Access](HERMES_REMOTE_IPAD_ACCESS.md)


## Phase 7I Browser Gateway

The Mac mini was confirmed online in Tailscale on 2026-07-15 as michaels-mac-mini at 100.80.79.75. The private browser gateway may bind to that address only when explicitly approved through HERMES_GATEWAY_ALLOW_TAILSCALE_BIND=1 and token authentication.

The supported browser URL is http://100.80.79.75:8787. The default remains localhost-only at 127.0.0.1:8787. Tailscale Funnel, public exposure, wildcard binds, and direct adapter exposure remain forbidden.
