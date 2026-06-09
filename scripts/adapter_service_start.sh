#!/usr/bin/env bash
set -euo pipefail

LABEL="com.msr.hermes.model-router-adapter"
PLIST="${HOME}/Library/LaunchAgents/${LABEL}.plist"
TARGET="gui/$(id -u)/${LABEL}"
DOMAIN="gui/$(id -u)"
PORT="8088"
HOST="127.0.0.1"

fail() {
  echo "adapter_service_start.error: $*" >&2
  exit 1
}

listener_output() {
  lsof -nP -iTCP:${PORT} -sTCP:LISTEN 2>/dev/null || true
}

assert_no_listener() {
  local listeners
  listeners="$(listener_output)"
  if [[ -n "${listeners}" ]]; then
    echo "${listeners}" >&2
    fail "port ${PORT} already has a listener"
  fi
}

assert_localhost_listener() {
  local listeners
  listeners="$(listener_output)"
  if [[ -z "${listeners}" ]]; then
    fail "service did not create a listener on ${HOST}:${PORT}"
  fi
  echo "${listeners}"
  if ! grep -q "${HOST}:${PORT} (LISTEN)" <<<"${listeners}"; then
    fail "listener is not bound to ${HOST}:${PORT}"
  fi
  if grep -Eq "(0\\.0\\.0\\.0|\\*:|100\\.|192\\.168\\.|10\\.|172\\.(1[6-9]|2[0-9]|3[0-1])\\.)" <<<"${listeners}"; then
    fail "unexpected non-localhost listener detected"
  fi
}

assert_plist_policy() {
  [[ -f "${PLIST}" ]] || fail "missing plist: ${PLIST}"
  plutil -lint "${PLIST}" >/dev/null
  /usr/bin/python3 - "${PLIST}" <<'PY'
import plistlib
import sys
from pathlib import Path

plist = Path(sys.argv[1])
with plist.open("rb") as handle:
    data = plistlib.load(handle)

expected_args = ["/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter"]
expected_workdir = "/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current"
env = data.get("EnvironmentVariables", {})
checks = {
    "RunAtLoad_false": data.get("RunAtLoad") is False,
    "KeepAlive_false": data.get("KeepAlive") is False,
    "ProgramArguments_wrapper": data.get("ProgramArguments") == expected_args,
    "WorkingDirectory_runtime": data.get("WorkingDirectory") == expected_workdir,
    "Host_localhost": env.get("MODEL_ROUTER_ADAPTER_HOST") == "127.0.0.1",
    "Port_8088": env.get("MODEL_ROUTER_ADAPTER_PORT") == "8088",
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("plist policy failed: " + ", ".join(failed))
PY
}

echo "adapter_service_start.preflight"
assert_plist_policy
assert_no_listener

if ! launchctl print "${TARGET}" >/dev/null 2>&1; then
  launchctl bootstrap "${DOMAIN}" "${PLIST}"
fi

launchctl kickstart "${TARGET}"
sleep 2

echo "adapter_service_start.status"
launchctl print "${TARGET}" | sed -n '1,80p'

echo "adapter_service_start.health"
curl --max-time 10 -fsS "http://${HOST}:${PORT}/health"
echo

echo "adapter_service_start.models"
curl --max-time 20 -fsS "http://${HOST}:${PORT}/v1/models"
echo

echo "adapter_service_start.listener"
assert_localhost_listener

echo "adapter_service_start.ok"
