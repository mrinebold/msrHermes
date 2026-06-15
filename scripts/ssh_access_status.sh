#!/usr/bin/env bash
set -euo pipefail

TAILSCALE_BIN="${TAILSCALE_BIN:-/Applications/Tailscale.app/Contents/MacOS/Tailscale}"
SSH_DIR="${HERMES_SSH_HOME:-$HOME/.ssh}"
AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"

print_kv() {
  printf '%s=%s\n' "$1" "$2"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

hostname_value="$(hostname 2>/dev/null || printf 'unknown')"
print_kv "hostname" "$hostname_value"

if command_exists scutil; then
  print_kv "computer_name" "$(scutil --get ComputerName 2>/dev/null || printf 'unknown')"
else
  print_kv "computer_name" "unknown"
fi

if [[ -x "$TAILSCALE_BIN" ]]; then
  if tailscale_status="$("$TAILSCALE_BIN" status 2>&1)"; then
    if printf '%s\n' "$tailscale_status" | grep -qi 'failed to load preferences'; then
      print_kv "tailscale_status" "unavailable"
    else
      print_kv "tailscale_status" "running"
    fi
    printf '%s\n' "$tailscale_status" | awk 'NR==1 {print "tailscale_status_first_line="$0}'
  else
    print_kv "tailscale_status" "stopped_or_unavailable"
    printf '%s\n' "$tailscale_status" | awk 'NR==1 {print "tailscale_status_first_line="$0}'
  fi

  if tailscale_ip="$("$TAILSCALE_BIN" ip -4 2>/dev/null)"; then
    if [[ "$tailscale_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      print_kv "tailscale_ipv4" "$tailscale_ip"
    else
      print_kv "tailscale_ipv4" "unavailable"
    fi
  else
    print_kv "tailscale_ipv4" "unavailable"
  fi
else
  print_kv "tailscale_status" "not_installed"
  print_kv "tailscale_ipv4" "unavailable"
fi

if command_exists ifconfig; then
  lan_ips="$(ifconfig 2>/dev/null | awk '/inet / && $2 !~ /^127\./ {print $2}' | paste -sd, -)"
  print_kv "lan_ipv4" "${lan_ips:-unavailable}"
else
  print_kv "lan_ipv4" "unavailable"
fi

if command_exists launchctl; then
  ssh_launch_state="$(launchctl print system/com.openssh.sshd 2>/dev/null | awk -F'= ' '/state =/ {print $2; exit}')"
  print_kv "ssh_launchd_state" "${ssh_launch_state:-unknown}"
else
  print_kv "ssh_launchd_state" "unknown"
fi

ssh_listener="no"
ssh_public_exposure="no"
if command_exists lsof; then
  lsof_output="$(lsof -nP -iTCP:22 -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$lsof_output" ]]; then
    ssh_listener="yes"
    if printf '%s\n' "$lsof_output" | grep -Eq '(\*:22|0\.0\.0\.0:22|\[::\]:22)'; then
      ssh_public_exposure="possible_wildcard_listener"
    fi
  fi
fi
print_kv "ssh_listener_22" "$ssh_listener"

adapter_listener_public="no"
if command_exists lsof; then
  adapter_lsof="$(lsof -nP -iTCP:8088 -sTCP:LISTEN 2>/dev/null || true)"
  if printf '%s\n' "$adapter_lsof" | grep -Eq '(\*:8088|0\.0\.0\.0:8088|\[::\]:8088)'; then
    adapter_listener_public="yes"
  fi
fi
print_kv "adapter_8088_public_listener" "$adapter_listener_public"

if [[ "$ssh_public_exposure" == "no" && "$adapter_listener_public" == "no" ]]; then
  print_kv "public_exposure_detected" "no"
else
  print_kv "public_exposure_detected" "possible"
fi

if [[ -d "$SSH_DIR" ]]; then
  ssh_mode="$(stat -f '%Sp' "$SSH_DIR" 2>/dev/null || stat -c '%A' "$SSH_DIR" 2>/dev/null || printf 'unknown')"
  print_kv "ssh_dir_exists" "yes"
  print_kv "ssh_dir_mode" "$ssh_mode"
else
  print_kv "ssh_dir_exists" "no"
  print_kv "ssh_dir_mode" "missing"
fi

if [[ -f "$AUTHORIZED_KEYS" ]]; then
  key_mode="$(stat -f '%Sp' "$AUTHORIZED_KEYS" 2>/dev/null || stat -c '%A' "$AUTHORIZED_KEYS" 2>/dev/null || printf 'unknown')"
  key_lines="$(wc -l < "$AUTHORIZED_KEYS" | tr -d ' ')"
  print_kv "authorized_keys_exists" "yes"
  print_kv "authorized_keys_mode" "$key_mode"
  print_kv "authorized_keys_line_count" "$key_lines"
else
  print_kv "authorized_keys_exists" "no"
  print_kv "authorized_keys_mode" "missing"
  print_kv "authorized_keys_line_count" "0"
fi
