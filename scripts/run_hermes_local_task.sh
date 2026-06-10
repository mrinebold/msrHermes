#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

INBOX_DIR="${REPO_ROOT}/sandbox/hermes_inbox"
OUTBOX_DIR="${REPO_ROOT}/sandbox/hermes_outbox"
HERMES_BIN="${HERMES_BIN:-${HOME}/.local/bin/hermes}"
ADAPTER_HEALTH_URL="http://127.0.0.1:8088/health"

usage() {
  cat <<'EOF'
usage: scripts/run_hermes_local_task.sh sandbox/hermes_inbox/<task>.task.md

Runs one local-only Hermes task file through the persistent localhost adapter
config. The adapter must already be running and healthy.
EOF
}

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 2
fi

TASK_INPUT="$1"

if [[ ! -f "${TASK_INPUT}" ]]; then
  echo "Task file not found: ${TASK_INPUT}" >&2
  exit 2
fi

TASK_DIR="$(cd "$(dirname "${TASK_INPUT}")" && pwd -P)"
TASK_BASENAME="$(basename "${TASK_INPUT}")"
TASK_PATH="${TASK_DIR}/${TASK_BASENAME}"
INBOX_ABS="$(cd "${INBOX_DIR}" && pwd -P)"
OUTBOX_ABS="$(mkdir -p "${OUTBOX_DIR}" && cd "${OUTBOX_DIR}" && pwd -P)"

case "${TASK_PATH}" in
  "${INBOX_ABS}/"*) ;;
  *)
    echo "Refusing task path outside sandbox/hermes_inbox: ${TASK_INPUT}" >&2
    exit 2
    ;;
esac

if [[ "${TASK_BASENAME}" == *.task.md ]]; then
  TASK_NAME="${TASK_BASENAME%.task.md}"
else
  TASK_NAME="${TASK_BASENAME%.*}"
fi

OUTPUT_PATH="${OUTBOX_ABS}/${TASK_NAME}.out.md"
STDERR_PATH="${OUTBOX_ABS}/${TASK_NAME}.stderr"
METRICS_PATH="${OUTBOX_ABS}/${TASK_NAME}.metrics"
TMP_OUTPUT="${OUTPUT_PATH}.tmp"

if ! curl -fsS --max-time 10 "${ADAPTER_HEALTH_URL}" >/dev/null; then
  echo "Adapter health check failed: ${ADAPTER_HEALTH_URL}" >&2
  exit 3
fi

if [[ ! -x "${HERMES_BIN}" ]]; then
  echo "Hermes binary is not executable: ${HERMES_BIN}" >&2
  exit 2
fi

PROMPT_TEXT="$(cat "${TASK_PATH}")"

umask 077
SECONDS=0
set +e
env -i \
  "HOME=${HOME}" \
  "USER=${USER:-}" \
  "TMPDIR=${TMPDIR:-/private/tmp}" \
  "PATH=/usr/bin:/bin:/usr/sbin:/sbin:${HOME}/.local/bin" \
  "${HERMES_BIN}" --ignore-rules -z "${PROMPT_TEXT}" > "${TMP_OUTPUT}" 2> "${STDERR_PATH}"
CODE=$?
set -e

mv "${TMP_OUTPUT}" "${OUTPUT_PATH}"
STDOUT_BYTES="$(wc -c < "${OUTPUT_PATH}")"
STDERR_BYTES="$(wc -c < "${STDERR_PATH}")"
cat > "${METRICS_PATH}" <<EOF
exit_code=${CODE}
elapsed_seconds=${SECONDS}
stdout_bytes=${STDOUT_BYTES}
stderr_bytes=${STDERR_BYTES}
output_path=${OUTPUT_PATH}
EOF

echo "hermes_local_task.output=${OUTPUT_PATH}"
echo "hermes_local_task.metrics=${METRICS_PATH}"
echo "hermes_local_task.exit_code=${CODE}"
exit "${CODE}"
