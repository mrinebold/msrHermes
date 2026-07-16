# Hermes Browser Gateway — Phase 7I

## Purpose

Phase 7I adds a small private browser gateway on the Mac mini so Michael can
use Hermes from an iPad, remote laptop browser, `civic-main`, `DevMonster`, or
another approved private-network device.

This is a browser UI/API gateway, not Hermes Desktop and not a public service.
It exposes only governed status, inbox, outbox, audit/approval summaries,
resident-once, and emergency-stop surfaces.

## Security posture

- Default bind: `127.0.0.1:8787`.
- Wildcard (`0.0.0.0`, `::`, `*`), hostname, LAN, and public-IP binds are refused.
- A Tailscale bind requires an explicit literal `100.64.0.0/10` address and
  `HERMES_GATEWAY_ALLOW_TAILSCALE_BIND=1`.
- A token is required from `HERMES_GATEWAY_TOKEN` or
  `~/Library/Application Support/Helio/hermes-gateway/token`.
- Tailscale binding additionally requires a token at least 16 characters long.
- Tailscale Funnel and public URLs are not approved or implemented.
- The raw adapter (`127.0.0.1:8088`) is never proxied.
- Command execution, Desktop launch, and external integrations remain disabled/frozen.
- Only the four approved local scripts may be invoked.
- Tokens, audit data, inbox tasks, and outbox results are runtime state and are
  excluded from Git.

## Start locally

Create the token manually on the Mac mini; do not commit it:

```sh
mkdir -p "$HOME/Library/Application Support/Helio/hermes-gateway"
chmod 700 "$HOME/Library/Application Support/Helio/hermes-gateway"
umask 077
read -r -s -p 'Hermes gateway token: ' HERMES_TOKEN
printf '\n'
printf '%s\n' "$HERMES_TOKEN" > "$HOME/Library/Application Support/Helio/hermes-gateway/token"
unset HERMES_TOKEN
```

From the repository, run manually in a terminal:

```sh
scripts/run_hermes_gateway.sh
```

The process is foreground-only. Press Ctrl-C to stop it. No LaunchAgent is
created, and there is no `RunAtLoad` or `KeepAlive` behavior.

## iPad and private-network access

The iPad must be on Tailscale. To browse directly, the gateway must be started
with the Mac mini's approved Tailscale IP:

```sh
HERMES_GATEWAY_BIND_HOST=<mac-mini-tailscale-ip> \
HERMES_GATEWAY_ALLOW_TAILSCALE_BIND=1 \
scripts/run_hermes_gateway.sh
```

Then browse to `http://<mac-mini-tailscale-ip>:8787`.

If the gateway remains localhost-only, use a local SSH tunnel from the iPad's
SSH client or from a trusted laptop:

```sh
ssh -N -L 18787:127.0.0.1:8787 macmini-hermes
```

Browse to `http://127.0.0.1:18787` on the device running that tunnel.

Public internet exposure, port forwarding, reverse proxies, and Tailscale
Funnel are not approved.

## Routes

HTML routes: `/`, `/login`, `/status`, `/inbox`, `/outbox`,
`/outbox/{name}`, `/audit`, `/approvals`.

JSON routes: `/api/status`, `/api/inbox`, `/api/outbox`,
`/api/outbox/{name}`, `/api/audit`, `/api/approvals`,
`/api/resident/run-once`, and `/api/emergency-stop`.

Mutating requests write bounded audit events. File access is limited to the
Hermes inbox/outbox zones, rejects traversal and symlinks, and applies size
limits. Status and audit responses redact likely credential values.

## Approved script boundary

The gateway may invoke only:

- `scripts/hermes_local_status.sh`
- `scripts/hermes_resident_status.sh`
- `scripts/hermes_resident_once.sh`
- `scripts/hermes_emergency_stop.sh`

Missing scripts produce an unavailable/fail-closed response. The gateway does
not synthesize them, start the adapter, launch Desktop, or run arbitrary shell.
