#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
Hermes remote and iPad access is Tailscale SSH only.

iPad setup:
  1. Install Tailscale on iPad and join the approved tailnet.
  2. Confirm the Mac mini appears by MagicDNS name or Tailscale IP.
  3. Use an SSH app such as Termius, Blink Shell, or another trusted SSH client.
  4. Configure:
       Host: Mac mini Tailscale MagicDNS name or Tailscale IP
       User: michael
       Auth: SSH key preferred
  5. Do not weaken password settings.

Remote laptop setup:
  ssh macmini-hermes

Mac mini working directory:
  cd /Users/michaelrinebold/Documents/Helio/helio-command-center

Status commands:
  scripts/hermes_local_status.sh
  scripts/hermes_resident_status.sh

Resident-once manual run:
  scripts/hermes_resident_once.sh

Emergency stop:
  scripts/hermes_emergency_stop.sh "remote stop"

Endpoint access through SSH tunnel:
  ssh -N -L 18088:127.0.0.1:8088 macmini-hermes
  curl http://127.0.0.1:18088/health
  curl http://127.0.0.1:18088/v1/models

Boundaries:
  no public internet exposure
  no Tailscale Funnel
  no Cloudflare public tunnel
  no 0.0.0.0 adapter bind
  no direct 8088 exposure
  no Desktop launch
  no external integrations
  no command execution
EOF
