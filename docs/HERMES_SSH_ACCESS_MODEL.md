# Hermes SSH Access Model

Status: Phase 7G key-based private access model

## Approved Access Path

Preferred:

- Tailscale SSH, or standard SSH over Tailscale IP/MagicDNS.

Fallback:

- trusted LAN SSH only when Tailscale is unavailable and the exact client/server LAN IPs have been manually verified.

Not approved:

- public internet SSH exposure
- router port forwarding
- password weakening
- private keys in this repo
- broad machine trust
- sudo-driven Remote Login changes from this phase

## Approved User

Approved user:

- `michael`

Current local account observed on this Mac:

- `michaelrinebold`

Use the actual account that exists on the target Mac when testing. Do not create new users without a future explicit approval.

## Approved Clients

- `civic-main`
- `civic-dev`
- `DevMonster`
- future explicitly allowlisted machines

## Authentication

Allowed:

- `ssh-ed25519` public keys
- `ssh-rsa` public keys only for compatibility when ed25519 is not available

Not allowed:

- private keys in repo
- private keys printed into logs
- password-security weakening
- blanket shared keys for all machines

Each approved client should have its own keypair and comment.

## authorized_keys Policy

Before modification:

- inspect path and permissions without printing key contents
- back up `~/.ssh/authorized_keys`

On modification:

- append only public keys
- refuse private key files
- refuse malformed public key files
- add an adjacent comment with machine name and timestamp
- do not duplicate an existing key
- set `~/.ssh` to mode `700`
- set `~/.ssh/authorized_keys` to mode `600`

Recommended comment shape:

```text
# hermes-access <machine-name> <timestamp>
```

## Revocation

To revoke a machine:

1. Back up `~/.ssh/authorized_keys`.
2. Remove the comment and public key line for that machine.
3. Preserve the backup.
4. Verify permissions remain `700` and `600`.
5. Test that the revoked client can no longer authenticate.

## Verification Commands

From client to Mac mini:

```sh
ssh -i ~/.ssh/msr_macmini_ed25519 michael@<mac-mini-tailscale-name-or-ip> "hostname && whoami"
```

From Mac mini to client:

```sh
ssh <client-host-alias> "hostname && whoami"
```

Endpoint tunnel test from a client:

```sh
ssh -N -L 18088:127.0.0.1:8088 macmini-hermes
curl http://127.0.0.1:18088/health
```

## Troubleshooting

Remote Login disabled:

- enable macOS Remote Login manually in System Settings.
- do not use sudo in this phase.

Tailscale down:

- start Tailscale from the approved user session.
- verify MagicDNS/IP before relying on hostnames.

Key permissions wrong:

```sh
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

Hostname resolution wrong:

- prefer the detected Tailscale IPv4.
- avoid LAN fallback until stale IP conflicts are resolved.

## iPad And Remote Client Notes

iPad access uses the same SSH key model:

- install and log in to Tailscale on iPad
- use Termius, Blink Shell, or another trusted iPad SSH client
- connect to the Mac mini Tailscale MagicDNS name or Tailscale IP
- use SSH key authentication where possible
- do not weaken password settings

Remote laptops use the same model with standard OpenSSH.

Endpoint access from iPad or laptop should use SSH local port forwarding to the Mac mini localhost adapter. Direct exposure of `8088`, Tailscale Funnel, and public internet access are not approved.
