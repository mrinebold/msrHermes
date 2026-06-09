#!/usr/bin/env bash
set -euo pipefail

LABEL="com.msr.hermes.model-router-adapter"
PLIST="${HOME}/Library/LaunchAgents/${LABEL}.plist"
TARGET="gui/$(id -u)/${LABEL}"
DOMAIN="gui/$(id -u)"
PORT="8088"

fail() {
  echo "adapter_service_stop.error: $*" >&2
  exit 1
}

listener_output() {
  lsof -nP -iTCP:${PORT} -sTCP:LISTEN 2>/dev/null || true
}

if launchctl print "${TARGET}" >/dev/null 2>&1; then
  launchctl bootout "${DOMAIN}" "${PLIST}"
else
  echo "adapter_service_stop.info: service not loaded"
fi

sleep 1

listeners="$(listener_output)"
if [[ -n "${listeners}" ]]; then
  echo "${listeners}" >&2
  fail "port ${PORT} still has a listener after stop"
fi

echo "adapter_service_stop.ok: no ${PORT} listener remains"
