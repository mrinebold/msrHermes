#!/usr/bin/env bash
set -u

REPO_PATH="${HERMES_REPO_ROOT:-/Users/michaelrinebold/Documents/Helio/helio-command-center}"
LABEL="com.msr.hermes.resident-once"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
RUNTIME_PATH="$HOME/Library/Application Support/Helio/hermes-resident-once/current"
WRAPPER="$HOME/.local/bin/msr-hermes-resident-once"
DOMAIN="gui/$(id -u)"
TARGET="$DOMAIN/$LABEL"
RESIDENT_ONCE="$REPO_PATH/scripts/hermes_resident_once.sh"
LOCAL_STATUS="$REPO_PATH/scripts/hermes_local_status.sh"
DESKTOP_APP="/Applications/Hermes.app"

print_kv() {
  printf '%s=%s\n' "$1" "$2"
}

has_command() {
  command -v "$1" >/dev/null 2>&1
}

print_kv "repo_path" "$REPO_PATH"
if [[ -x "$RESIDENT_ONCE" ]]; then
  print_kv "resident_once_script_exists" "yes"
else
  print_kv "resident_once_script_exists" "no"
fi
print_kv "resident_once_runtime_path" "$RUNTIME_PATH"
if [[ -x "$RUNTIME_PATH/scripts/hermes_resident_once.sh" ]]; then
  print_kv "resident_once_runtime_installed" "yes"
else
  print_kv "resident_once_runtime_installed" "no"
fi
if [[ -x "$WRAPPER" ]]; then
  print_kv "resident_once_wrapper_installed" "yes"
else
  print_kv "resident_once_wrapper_installed" "no"
fi

if [[ -f "$PLIST" ]]; then
  print_kv "resident_once_launchagent_installed" "yes"
else
  print_kv "resident_once_launchagent_installed" "no"
fi

if has_command launchctl; then
  if launchctl print "$TARGET" >/dev/null 2>&1; then
    print_kv "resident_once_launchagent_loaded" "yes"
  else
    print_kv "resident_once_launchagent_loaded" "no"
  fi
else
  print_kv "resident_once_launchagent_loaded" "unknown"
fi

if has_command pgrep && pgrep -f 'hermes_resident_once|msr-hermes-resident-once|com.msr.hermes.resident-once' >/dev/null 2>&1; then
  print_kv "resident_once_process_present" "yes"
else
  print_kv "resident_once_process_present" "no"
fi

if [[ -d "$DESKTOP_APP" ]]; then
  print_kv "desktop_app_present" "yes"
else
  print_kv "desktop_app_present" "no"
fi

if has_command pgrep && pgrep -f 'Hermes-Setup|/Applications/Hermes.app' >/dev/null 2>&1; then
  print_kv "desktop_process_present" "yes"
else
  print_kv "desktop_process_present" "no"
fi

if [[ -x "$LOCAL_STATUS" ]]; then
  "$LOCAL_STATUS" | grep -E '^(freeze_flag_exists|adapter_launchagent_loaded|adapter_listener_8088|latest_audit_|latest_approval_|command_execution_enabled|resident_mode_enabled|external_integrations_enabled|desktop_installed|desktop_verified|desktop_running|emergency_stop_script_exists)=' || true
fi

print_kv "command_execution_enabled" "no"
print_kv "external_integrations_enabled" "no"
