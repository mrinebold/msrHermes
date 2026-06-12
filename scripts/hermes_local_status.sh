#!/usr/bin/env bash
set -u

REPO_PATH="/Users/michaelrinebold/Documents/Helio/helio-command-center"
LABEL="com.msr.hermes.model-router-adapter"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"
TARGET="$DOMAIN/$LABEL"
CONFIG="$HOME/.hermes/config.yaml"
HERMES_BIN="${HERMES_BIN:-$HOME/.local/bin/hermes}"
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

has_command() {
  command -v "$1" >/dev/null 2>&1
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
