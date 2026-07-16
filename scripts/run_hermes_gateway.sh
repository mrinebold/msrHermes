#!/bin/bash
# Run the private Hermes browser gateway manually.
# Default: 127.0.0.1:8787. Ctrl-C stops it. No LaunchAgent is installed.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

if [[ "${HERMES_GATEWAY_BIND_HOST:-127.0.0.1}" == "0.0.0.0" || "${HERMES_GATEWAY_BIND_HOST:-127.0.0.1}" == "::" ]]; then
  echo "Refusing wildcard gateway bind." >&2
  exit 2
fi

if [[ "${HERMES_GATEWAY_TEST_MODE:-0}" == "1" ]]; then
  if [[ "${HERMES_GATEWAY_BIND_HOST:-127.0.0.1}" != "127.0.0.1" ]]; then
    echo "Test mode is localhost-only." >&2
    exit 2
  fi
  if [[ -z "${HERMES_GATEWAY_TOKEN:-}" ]]; then
    HERMES_GATEWAY_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
    export HERMES_GATEWAY_TOKEN
    echo "Hermes gateway temporary test token created (value withheld)."
  fi
fi

exec python3 -m services.hermes_gateway.server
