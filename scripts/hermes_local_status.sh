#!/usr/bin/env bash
set -u

REPO_PATH="${HERMES_REPO_ROOT:-/Users/michaelrinebold/Documents/Helio/helio-command-center}"
LABEL="com.msr.hermes.model-router-adapter"
RESIDENT_ONCE_LABEL="com.msr.hermes.resident-once"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
RESIDENT_ONCE_PLIST="$HOME/Library/LaunchAgents/$RESIDENT_ONCE_LABEL.plist"
RESIDENT_ONCE_RUNTIME="$HOME/Library/Application Support/Helio/hermes-resident-once/current"
RESIDENT_ONCE_WRAPPER="$HOME/.local/bin/msr-hermes-resident-once"
DOMAIN="gui/$(id -u)"
TARGET="$DOMAIN/$LABEL"
RESIDENT_ONCE_TARGET="$DOMAIN/$RESIDENT_ONCE_LABEL"
CONFIG="$HOME/.hermes/config.yaml"
HERMES_BIN="${HERMES_BIN:-$HOME/.local/bin/hermes}"
DESKTOP_APP="/Applications/Hermes.app"
AUDIT_DIR="$REPO_PATH/logs/hermes_audit"
APPROVAL_DIR="$REPO_PATH/logs/hermes_approvals"
FREEZE_FLAG="$REPO_PATH/sandbox/hermes_control/FROZEN"
FREEZE_REASON="$REPO_PATH/sandbox/hermes_control/FROZEN.reason"
EMERGENCY_STOP_SCRIPT="$REPO_PATH/scripts/hermes_emergency_stop.sh"
POLICY_CHECK_SCRIPT="$REPO_PATH/scripts/hermes_policy_check.py"
DRY_RUN_RESIDENT_SCRIPT="$REPO_PATH/scripts/hermes_resident_dry_run.sh"
RESIDENT_ONCE_SCRIPT="$REPO_PATH/scripts/hermes_resident_once.sh"
RESIDENT_STATUS_SCRIPT="$REPO_PATH/scripts/hermes_resident_status.sh"
FORBIDDEN_ENV_VARS=(
  OPENAI_API_KEY
  ANTHROPIC_API_KEY
  OPENROUTER_API_KEY
  SUPABASE_URL
  SUPABASE_ANON_KEY
  SUPABASE_SERVICE_ROLE_KEY
  GOOGLE_CLIENT_SECRET_FILE
  GOOGLE_TOKEN_FILE
  GITHUB_PERSONAL_ACCESS_TOKEN
  HASS_URL
  HASS_TOKEN
  HELIO_GATEWAY_URL
  HELIO_DISPATCHER_MCP_URL
)

print_kv() {
  printf '%s=%s\n' "$1" "$2"
}

safe_line() {
  printf '%s' "$1" | sed -E 's/(sk-[A-Za-z0-9_-]{4,}|g[h]p_[A-Za-z0-9_]{4,}|github[_]pat_[A-Za-z0-9_]{4,}|Bearer[[:space:]]+[A-Za-z0-9._-]{4,})/[REDACTED]/g'
}

has_command() {
  command -v "$1" >/dev/null 2>&1
}

print_latest_jsonl_summary() {
  local kind="$1"
  local dir="$2"
  if [[ ! -d "$dir" ]]; then
    print_kv "${kind}_log_dir_exists" "no"
    print_kv "${kind}_log_file_count" "0"
    print_kv "latest_${kind}_timestamp" "not_initialized"
    print_kv "latest_${kind}_status" "not_initialized"
    if [[ "$kind" == "audit" ]]; then
      print_kv "latest_audit_action" "not_initialized"
      print_kv "latest_audit_risk_level" "not_initialized"
    else
      print_kv "latest_approval_action" "not_initialized"
      print_kv "latest_approval_expiration" "not_initialized"
      print_kv "valid_approval_count" "0"
    fi
    return 0
  fi

  print_kv "${kind}_log_dir_exists" "yes"
  if has_command python3; then
    python3 - "$kind" "$dir" <<'PY'
import json
import sys
from pathlib import Path

kind = sys.argv[1]
directory = Path(sys.argv[2])
files = sorted(directory.glob("*.jsonl"))
print(f"{kind}_log_file_count={len(files)}")
if not files:
    print(f"latest_{kind}_timestamp=no_events")
    print(f"latest_{kind}_status=no_events")
    if kind == "audit":
        print("latest_audit_action=no_events")
        print("latest_audit_risk_level=no_events")
    else:
        print("latest_approval_action=no_events")
        print("latest_approval_expiration=no_events")
        print("valid_approval_count=0")
    raise SystemExit(0)

latest = None
valid_approvals = 0
for path in files:
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    record = json.loads(stripped)
                    latest = record
                    if kind == "approval" and record.get("status") == "granted":
                        try:
                            expiration = record.get("expiration")
                            if expiration:
                                from datetime import datetime, timezone

                                parsed = datetime.fromisoformat(str(expiration).replace("Z", "+00:00"))
                                if parsed.tzinfo is None:
                                    parsed = parsed.replace(tzinfo=timezone.utc)
                                if datetime.now(timezone.utc) < parsed.astimezone(timezone.utc):
                                    valid_approvals += 1
                        except (TypeError, ValueError):
                            pass
    except (OSError, json.JSONDecodeError):
        continue

if not isinstance(latest, dict):
    print(f"latest_{kind}_timestamp=unreadable")
    print(f"latest_{kind}_status=unreadable")
    if kind == "audit":
        print("latest_audit_action=unreadable")
        print("latest_audit_risk_level=unreadable")
    else:
        print("latest_approval_action=unreadable")
        print("latest_approval_expiration=unreadable")
        print("valid_approval_count=0")
    raise SystemExit(0)

if kind == "audit":
    print(f"latest_audit_timestamp={latest.get('timestamp', 'unknown')}")
    print(f"latest_audit_action={latest.get('action_type', 'unknown')}")
    print(f"latest_audit_status={latest.get('status', 'unknown')}")
    print(f"latest_audit_risk_level={latest.get('risk_level', 'unknown')}")
else:
    timestamp = latest.get("timestamp_granted") or latest.get("timestamp_requested") or "unknown"
    print(f"latest_approval_timestamp={timestamp}")
    print(f"latest_approval_status={latest.get('status', 'unknown')}")
    print(f"latest_approval_action={latest.get('action_type', 'unknown')}")
    print(f"latest_approval_expiration={latest.get('expiration', 'unknown')}")
    print(f"valid_approval_count={valid_approvals}")
PY
  else
    print_kv "${kind}_log_file_count" "python3_unavailable"
    print_kv "latest_${kind}_timestamp" "python3_unavailable"
    print_kv "latest_${kind}_status" "python3_unavailable"
    if [[ "$kind" == "audit" ]]; then
      print_kv "latest_audit_action" "python3_unavailable"
      print_kv "latest_audit_risk_level" "python3_unavailable"
    else
      print_kv "latest_approval_action" "python3_unavailable"
      print_kv "latest_approval_expiration" "python3_unavailable"
      print_kv "valid_approval_count" "python3_unavailable"
    fi
  fi
}

print_kv "repo_path" "$REPO_PATH"

if [[ -d "$REPO_PATH/.git" ]] && has_command git; then
  branch="$(git -C "$REPO_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  dirty="$(git -C "$REPO_PATH" status --short 2>/dev/null || true)"
  print_kv "git_branch" "${branch:-unknown}"
  if [[ -n "$dirty" ]]; then
    print_kv "git_clean" "false"
  else
    print_kv "git_clean" "true"
  fi
else
  print_kv "git_branch" "unknown"
  print_kv "git_clean" "unknown"
fi

print_kv "adapter_launchagent_plist" "$PLIST"
if [[ -f "$PLIST" ]]; then
  print_kv "adapter_launchagent_plist_present" "true"
else
  print_kv "adapter_launchagent_plist_present" "false"
fi

print_kv "resident_once_launchagent_plist" "$RESIDENT_ONCE_PLIST"
if [[ -f "$RESIDENT_ONCE_PLIST" ]]; then
  print_kv "resident_once_launchagent_installed" "yes"
else
  print_kv "resident_once_launchagent_installed" "no"
fi
print_kv "resident_once_runtime_path" "$RESIDENT_ONCE_RUNTIME"
if [[ -x "$RESIDENT_ONCE_RUNTIME/scripts/hermes_resident_once.sh" ]]; then
  print_kv "resident_once_runtime_installed" "yes"
else
  print_kv "resident_once_runtime_installed" "no"
fi
if [[ -x "$RESIDENT_ONCE_WRAPPER" ]]; then
  print_kv "resident_once_wrapper_installed" "yes"
else
  print_kv "resident_once_wrapper_installed" "no"
fi

if has_command launchctl; then
  if launchctl print "$RESIDENT_ONCE_TARGET" >/dev/null 2>&1; then
    print_kv "resident_once_launchagent_loaded" "yes"
  else
    print_kv "resident_once_launchagent_loaded" "no"
  fi
else
  print_kv "resident_once_launchagent_loaded" "unknown"
fi

if has_command launchctl; then
  if launchctl print "$TARGET" >/dev/null 2>&1; then
    print_kv "adapter_launchagent_loaded" "true"
  else
    print_kv "adapter_launchagent_loaded" "false"
  fi
else
  print_kv "adapter_launchagent_loaded" "unknown"
fi

listener_lines=""
if has_command lsof; then
  listener_lines="$(lsof -nP -iTCP:8088 -sTCP:LISTEN 2>/dev/null || true)"
fi

if [[ -n "$listener_lines" ]]; then
  print_kv "adapter_listener_8088" "true"
  if printf '%s\n' "$listener_lines" | awk 'NR > 1 {print $0}' | grep -Eq '127\.0\.0\.1:8088|\[::1\]:8088|localhost:8088'; then
    print_kv "adapter_listener_localhost" "true"
  else
    print_kv "adapter_listener_localhost" "false"
    print_kv "warning_adapter_non_localhost_listener" "true"
  fi
  if printf '%s\n' "$listener_lines" | awk 'NR > 1 {print $0}' | grep -Eq '\*:8088|0\.0\.0\.0:8088'; then
    print_kv "warning_adapter_wildcard_listener" "true"
  fi
else
  print_kv "adapter_listener_8088" "false"
  print_kv "adapter_listener_localhost" "false"
fi

if [[ -n "$listener_lines" ]] && has_command curl; then
  if curl --max-time 5 -fsS http://127.0.0.1:8088/health >/dev/null 2>&1; then
    print_kv "adapter_health" "ok"
  else
    print_kv "adapter_health" "failed"
  fi
  if curl --max-time 8 -fsS http://127.0.0.1:8088/v1/models >/dev/null 2>&1; then
    print_kv "adapter_models" "ok"
  else
    print_kv "adapter_models" "failed"
  fi
else
  print_kv "adapter_health" "not_checked_no_listener"
  print_kv "adapter_models" "not_checked_no_listener"
fi

if [[ -x "$HERMES_BIN" ]]; then
  print_kv "hermes_cli_path" "$HERMES_BIN"
  hermes_version="$("$HERMES_BIN" --version 2>/dev/null | head -n 1 || true)"
  print_kv "hermes_cli_version" "${hermes_version:-unknown}"
elif has_command hermes; then
  hermes_path="$(command -v hermes)"
  print_kv "hermes_cli_path" "$hermes_path"
  hermes_version="$(hermes --version 2>/dev/null | head -n 1 || true)"
  print_kv "hermes_cli_version" "${hermes_version:-unknown}"
else
  print_kv "hermes_cli_path" "not_found"
  print_kv "hermes_cli_version" "not_found"
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
if [[ "$desktop_present" == "true" ]]; then
  print_kv "warning_desktop_running" "true"
fi
if [[ "$resident_present" == "true" ]]; then
  print_kv "warning_hermes_resident_like_process" "true"
fi

if has_command pgrep && pgrep -f 'hermes_resident_once|msr-hermes-resident-once|com.msr.hermes.resident-once' >/dev/null 2>&1; then
  print_kv "resident_once_process_present" "yes"
else
  print_kv "resident_once_process_present" "no"
fi

if [[ -d "$DESKTOP_APP" ]]; then
  print_kv "desktop_installed" "yes"
  desktop_codesign="unknown"
  desktop_spctl="unknown"
  if has_command codesign; then
    if codesign --verify --deep --strict "$DESKTOP_APP" >/dev/null 2>&1; then
      desktop_codesign="passed"
    else
      desktop_codesign="failed"
    fi
  fi
  if has_command spctl; then
    if spctl --assess --type execute "$DESKTOP_APP" >/dev/null 2>&1; then
      desktop_spctl="accepted"
    else
      desktop_spctl="failed"
    fi
  fi
  print_kv "desktop_codesign_strict" "$desktop_codesign"
  print_kv "desktop_spctl_assessment" "$desktop_spctl"
  if [[ "$desktop_codesign" == "passed" && "$desktop_spctl" == "accepted" ]]; then
    print_kv "desktop_verified" "yes"
  elif [[ "$desktop_codesign" == "failed" || "$desktop_spctl" == "failed" ]]; then
    print_kv "desktop_verified" "no"
  else
    print_kv "desktop_verified" "unknown"
  fi
else
  print_kv "desktop_installed" "no"
  print_kv "desktop_codesign_strict" "not_installed"
  print_kv "desktop_spctl_assessment" "not_installed"
  print_kv "desktop_verified" "unknown"
fi
print_kv "desktop_running" "$desktop_present"

if [[ -f "$CONFIG" ]]; then
  print_kv "hermes_config_present" "true"
  if grep -Eq 'base_url:[[:space:]]*http://127\.0\.0\.1:8088/v1' "$CONFIG"; then
    print_kv "hermes_config_base_url_localhost" "true"
  else
    print_kv "hermes_config_base_url_localhost" "false"
  fi
  if grep -Eq 'provider:[[:space:]]*custom' "$CONFIG"; then
    print_kv "hermes_config_provider_custom" "true"
  else
    print_kv "hermes_config_provider_custom" "false"
  fi
  if grep -Eq 'default:[[:space:]]*gemma4:26b' "$CONFIG"; then
    print_kv "hermes_config_model_gemma4" "true"
  else
    print_kv "hermes_config_model_gemma4" "false"
  fi
else
  print_kv "hermes_config_present" "false"
  print_kv "hermes_config_base_url_localhost" "false"
  print_kv "hermes_config_provider_custom" "false"
  print_kv "hermes_config_model_gemma4" "false"
fi

set_forbidden_names=()
for env_name in "${FORBIDDEN_ENV_VARS[@]}"; do
  if [[ -n "${!env_name+x}" ]]; then
    set_forbidden_names+=("$env_name")
  fi
done

if [[ "${#set_forbidden_names[@]}" -gt 0 ]]; then
  print_kv "forbidden_env_vars_set" "$(IFS=,; printf '%s' "${set_forbidden_names[*]}")"
else
  print_kv "forbidden_env_vars_set" "none"
fi

if has_command python3; then
  if PYTHONPATH="$REPO_PATH${PYTHONPATH:+:$PYTHONPATH}" python3 - <<'PY' >/dev/null 2>&1
import services.hermes_safety.audit_log
import services.hermes_safety.approval_records
import services.hermes_safety.file_zones
import services.hermes_safety.command_policy
PY
  then
    print_kv "safety_modules_importable" "yes"
  else
    print_kv "safety_modules_importable" "no"
  fi
else
  print_kv "safety_modules_importable" "unknown"
fi

print_latest_jsonl_summary "audit" "$AUDIT_DIR"
print_latest_jsonl_summary "approval" "$APPROVAL_DIR"

print_kv "freeze_flag_path" "$FREEZE_FLAG"
if [[ -f "$FREEZE_FLAG" ]]; then
  print_kv "freeze_flag_exists" "yes"
else
  print_kv "freeze_flag_exists" "no"
fi
if [[ -f "$FREEZE_REASON" ]]; then
  print_kv "freeze_reason_exists" "yes"
  first_reason_line="$(head -n 1 "$FREEZE_REASON" 2>/dev/null || true)"
  print_kv "freeze_reason_first_line" "$(safe_line "${first_reason_line:-empty}")"
else
  print_kv "freeze_reason_exists" "no"
  print_kv "freeze_reason_first_line" "not_initialized"
fi
if [[ -x "$EMERGENCY_STOP_SCRIPT" ]]; then
  print_kv "emergency_stop_script_exists" "yes"
else
  print_kv "emergency_stop_script_exists" "no"
fi
if [[ -f "$POLICY_CHECK_SCRIPT" ]]; then
  print_kv "policy_check_script_exists" "yes"
else
  print_kv "policy_check_script_exists" "no"
fi
if [[ -x "$DRY_RUN_RESIDENT_SCRIPT" ]]; then
  print_kv "dry_run_resident_loop_exists" "yes"
else
  print_kv "dry_run_resident_loop_exists" "no"
fi
if [[ -x "$RESIDENT_ONCE_SCRIPT" ]]; then
  print_kv "resident_once_script_exists" "yes"
else
  print_kv "resident_once_script_exists" "no"
fi
if [[ -x "$RESIDENT_STATUS_SCRIPT" ]]; then
  print_kv "resident_status_script_exists" "yes"
else
  print_kv "resident_status_script_exists" "no"
fi

print_kv "command_execution_enabled" "no"
print_kv "resident_mode_enabled" "no"
print_kv "external_integrations_enabled" "no"
