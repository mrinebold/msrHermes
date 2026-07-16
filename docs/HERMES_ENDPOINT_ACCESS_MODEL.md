# Hermes Endpoint Access Model

Status: Phase 7G private endpoint access model

## Current Rule

The Hermes model router adapter remains localhost-only.

Approved adapter bind:

```text
127.0.0.1:8088
```

Not approved:

- `0.0.0.0`
- public internet exposure
- direct LAN exposure of `8088`
- direct Tailscale exposure of `8088`
- cloud provider fallback

## Option A: SSH Tunnel To Localhost Adapter

Status: approved current recommendation.

Keep the adapter bound to `127.0.0.1` on the Mac mini. Remote machines reach the endpoint through SSH only.

Example from civic-main, civic-dev, or DevMonster:

```sh
ssh -N -L 18088:127.0.0.1:8088 macmini-hermes
curl http://127.0.0.1:18088/health
curl http://127.0.0.1:18088/v1/models
```

This keeps the adapter private to the Mac mini process namespace and exposes it only through a user-initiated SSH tunnel.

## Option B: Future Tailscale-Only Proxy

Status: future explicit approval required; not implemented.

A future phase may bind a separate proxy to the Mac mini Tailscale IP only.

Requirements before approval:

- never bind `0.0.0.0`
- bind only to the Mac mini Tailscale IPv4
- Tailscale ACL allowlist
- firewall review
- audit logging
- emergency stop behavior
- human approval

## Option C: Reverse Tunnel

Status: future explicit approval required; not default.

The Mac mini may open an explicit reverse tunnel to civic-main, civic-dev, or DevMonster for a temporary task.

This should be used only when:

- inbound SSH to the Mac mini is not available
- the remote host is allowlisted
- the tunnel command is reviewed
- the tunnel is closed after use

## Recommendation

Implement Option A now:

- use private SSH access
- keep the adapter localhost-only
- use temporary SSH tunnels for endpoint access
- do not expose `8088` directly
- do not bind any Hermes endpoint to `0.0.0.0`

SSH access does not enable Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, cloud providers, Desktop, or Hermes command execution.

## Remote And iPad Endpoint Access

Remote and iPad endpoint access uses Option A.

For iPad:

- connect the iPad to Tailscale
- SSH to the Mac mini with an approved SSH app
- use local port forwarding if the SSH client supports it
- map iPad local port `18088` to `127.0.0.1:8088` on the Mac mini

For remote laptops:

```sh
ssh -N -L 18088:127.0.0.1:8088 macmini-hermes
```

Then access:

```sh
curl http://127.0.0.1:18088/health
```

Tailscale Serve may be considered later for tailnet-only convenience, but it is not enabled in this phase.

Tailscale Funnel and any public access path are not approved.


## Phase 7I Browser Gateway

The separate browser gateway is now implemented on port 8787. It does not proxy the adapter on 8088.

- Default bind: 127.0.0.1:8787.
- Optional bind: explicit Mac mini Tailscale IP only, with token auth and HERMES_GATEWAY_ALLOW_TAILSCALE_BIND=1.
- Refused: 0.0.0.0, ::, public IPs, public URLs, and Tailscale Funnel.
- Exposed surfaces: status, inbox, outbox, audit/approvals, resident-once, and emergency stop.
- Not exposed: raw adapter, arbitrary filesystem, arbitrary command execution, Desktop, and external integrations.

The Mac mini's confirmed Tailscale address on 2026-07-15 is 100.80.79.75; treat it as an operator-confirmed address rather than a hardcoded permanent identity.
