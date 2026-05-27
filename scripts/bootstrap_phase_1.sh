#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$ROOT_DIR/logs/bootstrap.log"

mkdir -p "$ROOT_DIR/logs"
printf '[%s] BLOCKED: bootstrap phase 1 requires explicit approval before installation or mutation.\n' "$(date +"%Y-%m-%d %H:%M:%S %Z")" | tee -a "$LOG_FILE"

cat <<'MSG'
bootstrap_phase_1.sh is intentionally disabled.

Approve the phase plan before running installation or system mutation steps.
MSG

exit 2
