#!/bin/bash
# Stop only a manually started Hermes gateway owned by this repository.
# It never uses sudo and refuses to signal an unrelated listener.

set -euo pipefail

port="${HERMES_GATEWAY_PORT:-8787}"
if ! command -v lsof >/dev/null 2>&1; then
  echo "lsof is required to stop the gateway safely; use Ctrl-C in its terminal." >&2
  exit 2
fi

listener="$(lsof -nP -iTCP:"${port}" -sTCP:LISTEN -t 2>/dev/null | head -n 1 || true)"
if [[ -z "${listener}" ]]; then
  echo "No Hermes gateway listener found on ${port}."
  exit 0
fi

command_line="$(ps -p "${listener}" -o command= 2>/dev/null || true)"
if [[ "${command_line}" != *"services.hermes_gateway.server"* ]]; then
  echo "Refusing to stop unrelated listener PID ${listener}." >&2
  exit 2
fi

kill -INT "${listener}"
echo "Sent Ctrl-C signal to Hermes gateway PID ${listener}."
