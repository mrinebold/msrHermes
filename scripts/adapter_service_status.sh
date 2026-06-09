#!/usr/bin/env bash
set -euo pipefail

LABEL="com.msr.hermes.model-router-adapter"
PLIST="${HOME}/Library/LaunchAgents/${LABEL}.plist"
TARGET="gui/$(id -u)/${LABEL}"
PORT="8088"
HOST="127.0.0.1"
STDOUT_LOG="${HOME}/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stdout.log"
STDERR_LOG="${HOME}/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stderr.log"

fail() {
  echo "adapter_service_status.error: $*" >&2
  exit 1
}

listener_output() {
  lsof -nP -iTCP:${PORT} -sTCP:LISTEN 2>/dev/null || true
}

echo "adapter_service_status.plist=${PLIST}"
if [[ -f "${PLIST}" ]]; then
  echo "adapter_service_status.plist_present=true"
else
  echo "adapter_service_status.plist_present=false"
fi

if launchctl print "${TARGET}" >/dev/null 2>&1; then
  echo "adapter_service_status.loaded=true"
  launchctl print "${TARGET}" | sed -n '1,80p'
else
  echo "adapter_service_status.loaded=false"
fi

listeners="$(listener_output)"
if [[ -n "${listeners}" ]]; then
  echo "adapter_service_status.listener=true"
  echo "${listeners}"
  if ! grep -q "${HOST}:${PORT} (LISTEN)" <<<"${listeners}"; then
    fail "listener is not bound to ${HOST}:${PORT}"
  fi
  if grep -Eq "(0\\.0\\.0\\.0|\\*:|100\\.|192\\.168\\.|10\\.|172\\.(1[6-9]|2[0-9]|3[0-1])\\.)" <<<"${listeners}"; then
    fail "unexpected non-localhost listener detected"
  fi
  echo "adapter_service_status.health"
  if curl --retry 2 --retry-delay 1 --max-time 10 -fsS "http://${HOST}:${PORT}/health"; then
    echo
  else
    echo "adapter_service_status.health=false"
  fi
else
  echo "adapter_service_status.listener=false"
fi

echo "adapter_service_status.stdout_log=${STDOUT_LOG}"
echo "adapter_service_status.stderr_log=${STDERR_LOG}"
