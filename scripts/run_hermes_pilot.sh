#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

HERMES_HOME="${HERMES_HOME:-/private/tmp/hermes-pilot-home}"
HERMES_BIN="${HERMES_BIN:-${HOME}/.local/bin/hermes}"
HERMES_PILOT_MODEL="${HERMES_PILOT_MODEL:-gemma4:26b}"
HERMES_PILOT_BASE_URL="${HERMES_PILOT_BASE_URL:-http://127.0.0.1:8088/v1}"
HERMES_PILOT_API_KEY="${HERMES_PILOT_API_KEY:-dummy-local-adapter-key}"
HERMES_PILOT_OUTPUT="${HERMES_PILOT_OUTPUT:-${REPO_ROOT}/sandbox/output/hermes_pilot_output.md}"

PROMPT_TEXT=""
PROMPT_FILE=""
OUTPUT_MODE="file"
DRY_RUN=false
ALLOW_OUTSIDE_OUTPUT=false

usage() {
  cat <<'EOF'
usage: scripts/run_hermes_pilot.sh (--prompt TEXT | --prompt-file FILE) [--stdout | --output FILE] [--allow-outside-output] [--dry-run]

Runs one foreground Hermes pilot prompt through an isolated HERMES_HOME and the
localhost model router adapter. Does not start the adapter.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt)
      PROMPT_TEXT="${2:-}"
      shift 2
      ;;
    --prompt-file)
      PROMPT_FILE="${2:-}"
      shift 2
      ;;
    --output)
      HERMES_PILOT_OUTPUT="${2:-}"
      OUTPUT_MODE="file"
      shift 2
      ;;
    --stdout)
      OUTPUT_MODE="stdout"
      shift
      ;;
    --allow-outside-output)
      ALLOW_OUTSIDE_OUTPUT=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -n "${PROMPT_TEXT}" && -n "${PROMPT_FILE}" ]]; then
  echo "Use either --prompt or --prompt-file, not both." >&2
  exit 2
fi

if [[ -z "${PROMPT_TEXT}" && -z "${PROMPT_FILE}" ]]; then
  echo "Pilot mode requires an explicit --prompt or --prompt-file." >&2
  exit 2
fi

if [[ -n "${PROMPT_FILE}" ]]; then
  if [[ ! -f "${PROMPT_FILE}" ]]; then
    echo "Prompt file not found: ${PROMPT_FILE}" >&2
    exit 2
  fi
  PROMPT_TEXT="$(cat "${PROMPT_FILE}")"
fi

if [[ "${HERMES_PILOT_BASE_URL}" != "http://127.0.0.1:8088/v1" ]]; then
  echo "Refusing non-pilot Hermes base URL: ${HERMES_PILOT_BASE_URL}" >&2
  exit 2
fi

if [[ "${HERMES_PILOT_MODEL}" != "gemma4:26b" ]]; then
  echo "Refusing non-pilot Hermes model: ${HERMES_PILOT_MODEL}" >&2
  exit 2
fi

if [[ "${OUTPUT_MODE}" == "file" ]]; then
  OUTPUT_DIR="$(cd "$(dirname "${HERMES_PILOT_OUTPUT}")" && pwd)"
  SANDBOX_OUTPUT_DIR="$(cd "${REPO_ROOT}/sandbox/output" && pwd)"
  if [[ "${ALLOW_OUTSIDE_OUTPUT}" != "true" && "${OUTPUT_DIR}" != "${SANDBOX_OUTPUT_DIR}" ]]; then
    echo "Refusing output outside sandbox/output without --allow-outside-output: ${HERMES_PILOT_OUTPUT}" >&2
    exit 2
  fi
fi

umask 077
mkdir -p "${HERMES_HOME}"
mkdir -p "${REPO_ROOT}/sandbox/output"

cat > "${HERMES_HOME}/config.yaml" <<EOF
model:
  provider: custom
  default: ${HERMES_PILOT_MODEL}
  base_url: ${HERMES_PILOT_BASE_URL}
  api_key: ${HERMES_PILOT_API_KEY}
platform_toolsets:
  cli: []
EOF

cat <<EOF
hermes_pilot.runner_config
  repo_root=${REPO_ROOT}
  hermes_home=${HERMES_HOME}
  hermes_bin=${HERMES_BIN}
  model=${HERMES_PILOT_MODEL}
  base_url=${HERMES_PILOT_BASE_URL}
  api_key=redacted_dummy_local
  platform_toolsets_cli=disabled
  output_mode=${OUTPUT_MODE}
  output_path=$([[ "${OUTPUT_MODE}" == "file" ]] && echo "${HERMES_PILOT_OUTPUT}" || echo "stdout")
  foreground_only=true
  resident_mode=false
  background_services=false
  sensitive_env=unset_in_child_process
EOF

if [[ "${DRY_RUN}" == "true" ]]; then
  echo "hermes_pilot.dry_run_complete"
  exit 0
fi

if [[ ! -x "${HERMES_BIN}" ]]; then
  echo "Hermes binary is not executable: ${HERMES_BIN}" >&2
  exit 2
fi

SANITIZED_ENV=(
  env -i
  "HOME=${HOME}"
  "USER=${USER:-}"
  "TMPDIR=${TMPDIR:-/private/tmp}"
  "PATH=/usr/bin:/bin:/usr/sbin:/sbin:${HOME}/.local/bin"
  "HERMES_HOME=${HERMES_HOME}"
  "OPENAI_API_KEY=${HERMES_PILOT_API_KEY}"
)

if [[ "${OUTPUT_MODE}" == "stdout" ]]; then
  "${SANITIZED_ENV[@]}" "${HERMES_BIN}" --ignore-rules -z "${PROMPT_TEXT}"
else
  OUTPUT_TMP="${HERMES_PILOT_OUTPUT}.tmp"
  "${SANITIZED_ENV[@]}" "${HERMES_BIN}" --ignore-rules -z "${PROMPT_TEXT}" > "${OUTPUT_TMP}"
  mv "${OUTPUT_TMP}" "${HERMES_PILOT_OUTPUT}"
  echo "hermes_pilot.output_written=${HERMES_PILOT_OUTPUT}"
fi
