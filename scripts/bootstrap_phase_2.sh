#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$ROOT_DIR/logs/bootstrap.log"

mkdir -p "$ROOT_DIR/logs"
printf '[%s] BLOCKED: bootstrap phase 2 requires explicit approval before installation or mutation.\n' "$(date +"%Y-%m-%d %H:%M:%S %Z")" | tee -a "$LOG_FILE"

cat <<'MSG'
bootstrap_phase_2.sh is intentionally disabled.

Approve phase 1 results and the phase 2 plan before enabling integration setup.
MSG

exit 2
