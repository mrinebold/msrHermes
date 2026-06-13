#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="${HERMES_REPO_ROOT:-$CODE_ROOT}"
CONTROL_DIR="${REPO_ROOT}/sandbox/hermes_control"
FREEZE_FLAG="${CONTROL_DIR}/FROZEN"
FREEZE_REASON="${CONTROL_DIR}/FROZEN.reason"
ADAPTER_STOP="${REPO_ROOT}/scripts/adapter_service_stop.sh"
LABEL="com.msr.hermes.model-router-adapter"
DOMAIN="gui/$(id -u)"
TARGET="$DOMAIN/$LABEL"

print_kv() {
  printf '%s=%s\n' "$1" "$2"
}

has_command() {
  command -v "$1" >/dev/null 2>&1
}

timestamp_utc() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

write_freeze_flag() {
  mkdir -p "$CONTROL_DIR"
  if [[ ! -f "$FREEZE_FLAG" ]]; then
    printf 'frozen\n' > "$FREEZE_FLAG"
  fi
  {
    printf 'timestamp=%s\n' "$(timestamp_utc)"
    printf 'reason=%s\n' "${HERMES_EMERGENCY_REASON:-manual_emergency_stop}"
    printf 'script=hermes_emergency_stop.sh\n'
  } > "$FREEZE_REASON"
}

adapter_listener_present() {
  if ! has_command lsof; then
    return 1
  fi
  lsof -nP -iTCP:8088 -sTCP:LISTEN >/dev/null 2>&1
}

adapter_launchagent_loaded() {
  if ! has_command launchctl; then
    return 1
  fi
  launchctl print "$TARGET" >/dev/null 2>&1
}

write_audit_event_if_available() {
  if ! has_command python3; then
    print_kv "audit_event" "skipped_python3_unavailable"
    return 0
  fi

  PYTHONPATH="$CODE_ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 - "$REPO_ROOT" <<'PY'
import sys
from pathlib import Path

try:
    from services.hermes_safety.audit_log import build_audit_event, write_audit_event
except Exception:
    print("audit_event=skipped_import_unavailable")
    raise SystemExit(0)

repo_root = Path(sys.argv[1])
event = build_audit_event(
    phase="6R",
    actor="codex",
    authority_tier="tier_0_observe",
    action_type="emergency_stop",
    target_type="service",
    target_identifier="local_hermes_safety",
    status="succeeded",
    risk_level="medium",
    rollback_available=False,
    human_summary="Emergency stop script created or refreshed the local freeze flag.",
    machine_summary="hermes_emergency_stop_freeze",
    metadata={"freeze_flag": "sandbox/hermes_control/FROZEN"},
)
write_audit_event(event, log_dir=repo_root / "logs" / "hermes_audit")
print("audit_event=written")
PY
}

print_kv "emergency_stop" "start"
print_kv "repo_root" "$REPO_ROOT"

write_freeze_flag
print_kv "freeze_flag" "$FREEZE_FLAG"
print_kv "freeze_flag_exists" "yes"

adapter_listener="false"
if adapter_listener_present; then
  adapter_listener="true"
fi
print_kv "adapter_listener_8088" "$adapter_listener"

adapter_loaded="false"
if adapter_launchagent_loaded; then
  adapter_loaded="true"
fi
print_kv "adapter_launchagent_loaded" "$adapter_loaded"

if [[ "$adapter_listener" == "true" || "$adapter_loaded" == "true" ]]; then
  if [[ -x "$ADAPTER_STOP" ]]; then
    print_kv "adapter_stop_attempted" "yes"
    "$ADAPTER_STOP"
  else
    print_kv "adapter_stop_attempted" "no_stop_script_unavailable"
  fi
else
  print_kv "adapter_stop_attempted" "no_not_running"
fi

desktop_present="false"
hermes_present="false"
resident_present="false"
if has_command pgrep; then
  if pgrep -f 'Hermes-Setup|/Applications/Hermes.app' >/dev/null 2>&1; then
    desktop_present="true"
  fi
  if pgrep -f '/Users/michaelrinebold/.local/bin/hermes|hermes-agent|run_hermes_pilot|run_hermes_local_task' >/dev/null 2>&1; then
    hermes_present="true"
  fi
  if pgrep -f 'hermes.*resident|hermes.*daemon|hermes.*gateway' >/dev/null 2>&1; then
    resident_present="true"
  fi
fi
print_kv "hermes_desktop_process_present" "$desktop_present"
print_kv "hermes_process_present" "$hermes_present"
print_kv "hermes_resident_like_process_present" "$resident_present"

if [[ "$resident_present" == "true" ]]; then
  print_kv "warning_resident_like_process_detected" "true"
  print_kv "resident_process_stopped" "no_not_approved"
fi

write_audit_event_if_available

print_kv "external_integrations_touched" "no"
print_kv "credentials_printed" "no"
print_kv "emergency_stop" "complete"
