# Hermes Remote And iPad Access

Status: Phase 7H remote/iPad access model; documentation and helper script only

## Remote Access Principle

Michael reaches the Mac mini over Tailscale.

Remote/iPad access is Tailscale-only unless a later explicit approval changes the access model.

Approved remote clients become trusted only after device and key approval:

- iPad
- remote laptop
- civic-main
- civic-dev
- DevMonster
- future explicitly allowlisted tailnet clients

Public internet exposure is not approved.

Not approved:

- public SSH exposure
- public HTTP exposure
- direct public Hermes adapter access
- direct public resident endpoint access
- Tailscale Funnel for Hermes control
- Cloudflare public tunnel for Hermes control
- binding the adapter to `0.0.0.0`
- exposing `8088` directly

## iPad SSH Workflow

1. Install Tailscale on the iPad.
2. Log in to the approved tailnet.
3. Confirm the Mac mini is visible in Tailscale by MagicDNS name or Tailscale IP.
4. Install an iPad SSH client such as Termius, Blink Shell, or another trusted SSH app.
5. Configure a host entry:
   - host: Mac mini Tailscale MagicDNS name or Tailscale IP
   - user: `michael`
   - auth: SSH key preferred
6. Do not weaken password settings.
7. Do not store private keys in the repo.

If the Mac mini account is `michaelrinebold` rather than `michael`, use the actual account name for SSH until a deliberate account alias/user decision is made.

## iPad Terminal Commands

After SSH login:

```sh
cd /Users/michaelrinebold/Documents/Helio/helio-command-center
scripts/hermes_local_status.sh
scripts/hermes_resident_status.sh
scripts/hermes_resident_once.sh
scripts/hermes_emergency_stop.sh "remote stop"
```

## iPad Endpoint Access Options

### Option 1: SSH Tunnel From iPad

Status: current approved endpoint access pattern.

If the iPad SSH client supports local port forwarding:

```text
local port 18088 -> 127.0.0.1:8088 on Mac mini
```

Then the iPad browser/client can reach:

```text
http://127.0.0.1:18088/health
```

The adapter must be intentionally started first. The adapter still binds only to `127.0.0.1` on the Mac mini.

### Option 2: Future Tailscale-Only Gateway

Status: future explicit approval required; not implemented.

A small gateway may be considered later. Requirements:

- bind only to the Mac mini Tailscale IP
- never bind `0.0.0.0`
- require authentication or Tailscale ACL allowlist
- expose only approved status/task endpoints
- include audit and emergency-stop behavior

### Option 3: Tailscale Serve/Funnel

Status: not enabled.

Tailscale Serve may be considered later only for tailnet-only convenience.

Tailscale Funnel/public exposure is not approved.

Do not enable Serve or Funnel in this phase.

## Remote Laptop Workflow

Remote laptops use the same Tailscale and SSH model.

Typical commands:

```sh
ssh macmini-hermes
ssh -N -L 18088:127.0.0.1:8088 macmini-hermes
```

Endpoint checks through the tunnel:

```sh
curl http://127.0.0.1:18088/health
curl http://127.0.0.1:18088/v1/models
```

## Emergency Remote Recovery

SSH in over Tailscale, then run:

```sh
cd /Users/michaelrinebold/Documents/Helio/helio-command-center
scripts/hermes_emergency_stop.sh "remote emergency stop"
scripts/hermes_local_status.sh
```

Verify:

- no `8088` listener
- no resident/Hermes/Desktop process
- freeze flag state is visible
- command execution remains disabled
- external integrations remain frozen

## Boundaries

Remote/iPad access does not approve:

- public internet exposure
- Tailscale Funnel
- Cloudflare public tunnel
- direct adapter exposure
- Desktop launch
- external integrations
- command execution
- real credentials


## Phase 7I Browser Gateway

Status: implemented; manual foreground service only.

The private browser gateway is available at 127.0.0.1:8787 by default. It requires a gateway token and exposes only status, inbox, outbox, audit/approval summaries, resident-once, and emergency-stop surfaces.

For direct iPad browser access, connect the iPad to Tailscale and start the gateway on the Mac mini with:

```sh
HERMES_GATEWAY_BIND_HOST=100.80.79.75 \\
HERMES_GATEWAY_ALLOW_TAILSCALE_BIND=1 \\
scripts/run_hermes_gateway.sh
```

Then browse to http://100.80.79.75:8787. Public exposure, Tailscale Funnel, wildcard binds, direct adapter exposure, Desktop launch, command execution, and external integrations remain disabled.

If direct binding is not desired, use an SSH local tunnel to the gateway:

```sh
ssh -N -L 18787:127.0.0.1:8787 macmini-hermes
```

Then browse to http://127.0.0.1:18787 on the device running the tunnel.
