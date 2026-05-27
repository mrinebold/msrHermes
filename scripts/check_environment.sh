#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$ROOT_DIR/logs/bootstrap.log"
REPORT_FILE="$ROOT_DIR/docs/ENVIRONMENT_REPORT.md"

mkdir -p "$ROOT_DIR/logs"

timestamp() {
  date +"%Y-%m-%d %H:%M:%S %Z"
}

log() {
  printf '[%s] %s\n' "$(timestamp)" "$*" | tee -a "$LOG_FILE" >/dev/null
}

run_check() {
  local label="$1"
  shift
  log "CHECK: $label"
  printf '### %s\n\n' "$label" >> "$REPORT_FILE"
  {
    printf '```text\n'
    "$@" 2>&1
    local status=$?
    printf '\nexit_status=%s\n' "$status"
    printf '```\n\n'
  } >> "$REPORT_FILE"
}

check_command() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
  else
    printf '%s not found\n' "$name"
    return 127
  fi
}

{
  printf '# Environment Report\n\n'
  printf 'Generated: %s\n\n' "$(timestamp)"
  printf 'Mode: read-only inspection. No installs, sudo, shell profile edits, deletions, or public service exposure.\n\n'
} > "$REPORT_FILE"

log "START: environment inspection"

run_check "macOS version" sw_vers
run_check "chip architecture" uname -a
run_check "Homebrew status" bash -lc 'if command -v brew >/dev/null 2>&1; then brew --version; else echo "Homebrew not found"; fi'
run_check "Git status" bash -lc 'git --version; git -C "'"$ROOT_DIR"'" status --short --branch 2>&1 || true'
run_check "Python version" bash -lc 'if command -v python3 >/dev/null 2>&1; then python3 --version; elif command -v python >/dev/null 2>&1; then python --version; else echo "Python not found"; fi'
run_check "Node version" bash -lc 'if command -v node >/dev/null 2>&1; then node --version; else echo "Node not found"; fi'
run_check "Codex CLI status" bash -lc 'if command -v codex >/dev/null 2>&1; then codex --version; else echo "Codex CLI not found"; fi'
run_check "Docker or OrbStack status" bash -lc 'if command -v docker >/dev/null 2>&1; then docker --version; docker context ls 2>&1 || true; else echo "Docker CLI not found"; fi; if command -v orb >/dev/null 2>&1; then orb version; else echo "OrbStack CLI not found"; fi'
run_check "Tailscale status" bash -lc 'if command -v tailscale >/dev/null 2>&1; then tailscale version; tailscale status 2>&1 || true; else echo "Tailscale not found"; fi'
run_check "SSH Remote Login status" bash -lc 'systemsetup -getremotelogin 2>&1; launchctl print system/com.openssh.sshd 2>&1 | sed -n "1,80p"; true'
run_check "disk space" df -h /
run_check "memory" bash -lc 'sysctl -n hw.memsize 2>/dev/null || system_profiler SPHardwareDataType 2>/dev/null | awk -F: "/Memory/ {print \$0}"; vm_stat'
run_check "Ollama status" bash -lc 'if command -v ollama >/dev/null 2>&1; then ollama --version; ollama list 2>&1 || true; else echo "Ollama not found"; fi'
run_check "Google Cloud CLI status" bash -lc 'if command -v gcloud >/dev/null 2>&1; then gcloud --version; else echo "Google Cloud CLI not found"; fi'
run_check "existing ~/Projects contents" bash -lc 'ls -la "$HOME/Projects" 2>&1 || true'

log "END: environment inspection"
printf 'Environment report written to %s\n' "$REPORT_FILE"
