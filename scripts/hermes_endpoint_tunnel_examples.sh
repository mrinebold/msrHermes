#!/usr/bin/env bash
set -euo pipefail

LOCAL_PORT="${HERMES_TUNNEL_LOCAL_PORT:-18088}"
REMOTE_PORT="${HERMES_TUNNEL_REMOTE_PORT:-8088}"
HOST_ALIAS="${HERMES_TUNNEL_HOST:-macmini-hermes}"

print_examples() {
  cat <<EOF
Hermes endpoint access remains SSH-tunnel-only.

Start a temporary tunnel from an approved remote machine:

  ssh -N -L ${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT} ${HOST_ALIAS}

Health check through the tunnel:

  curl http://127.0.0.1:${LOCAL_PORT}/health

Models check through the tunnel:

  curl http://127.0.0.1:${LOCAL_PORT}/v1/models

Direct adapter exposure is not approved:

  no 0.0.0.0 bind
  no public internet exposure
  no direct 8088 exposure
EOF
}

if [[ "${1:-}" == "--run" ]]; then
  print_examples
  printf '\n'
  printf 'To actually start the tunnel, set HERMES_TUNNEL_CONFIRM=RUN and rerun with --run.\n'
  if [[ "${HERMES_TUNNEL_CONFIRM:-}" != "RUN" ]]; then
    exit 2
  fi
  exec ssh -N -L "${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT}" "$HOST_ALIAS"
fi

print_examples
