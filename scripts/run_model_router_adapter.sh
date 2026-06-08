#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  shift
fi

if [[ $# -ne 0 ]]; then
  echo "usage: scripts/run_model_router_adapter.sh [--dry-run]" >&2
  exit 2
fi

export MODEL_ROUTER_ADAPTER_HOST="${MODEL_ROUTER_ADAPTER_HOST:-127.0.0.1}"
export MODEL_ROUTER_ADAPTER_PORT="${MODEL_ROUTER_ADAPTER_PORT:-8088}"
export DEVMONSTER_OLLAMA_URL="${DEVMONSTER_OLLAMA_URL:-http://100.93.120.124:11434}"
export DEVMONSTER_DEFAULT_MODEL="${DEVMONSTER_DEFAULT_MODEL:-gemma4:26b}"
export MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS="${MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS:-120}"
export MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE="${MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE:-true}"
export MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE="${MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE:-instruction_context}"
export MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS="${MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS:-1500}"
export MODEL_ROUTER_ADAPTER_LOG_REQUESTS="${MODEL_ROUTER_ADAPTER_LOG_REQUESTS:-true}"
export MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES="${MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES:-true}"
export MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE="${MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE:-true}"

if [[ "${MODEL_ROUTER_ADAPTER_HOST}" != "127.0.0.1" ]]; then
  echo "Refusing to bind model router adapter to non-localhost host: ${MODEL_ROUTER_ADAPTER_HOST}" >&2
  exit 2
fi

if [[ "${MODEL_ROUTER_ADAPTER_PORT}" != "8088" ]]; then
  echo "Refusing to run model router adapter on non-pilot port: ${MODEL_ROUTER_ADAPTER_PORT}" >&2
  exit 2
fi

cat <<EOF
model_router_adapter.runner_config
  repo_root=${REPO_ROOT}
  host=${MODEL_ROUTER_ADAPTER_HOST}
  port=${MODEL_ROUTER_ADAPTER_PORT}
  devmonster_ollama_url=${DEVMONSTER_OLLAMA_URL}
  devmonster_default_model=${DEVMONSTER_DEFAULT_MODEL}
  provider_timeout_seconds=${MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS}
  local_compat_mode=${MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE}
  gemma_prompt_mode=${MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE}
  local_summary_max_context_chars=${MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS}
  log_requests=${MODEL_ROUTER_ADAPTER_LOG_REQUESTS}
  log_response_shapes=${MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES}
  log_message_structure=${MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE}
  prompt_text_logging=disabled
  file_content_logging=disabled
  secrets=redacted
  foreground_only=true
EOF

if [[ "${DRY_RUN}" == "true" ]]; then
  echo "model_router_adapter.dry_run_complete"
  exit 0
fi

cd "${REPO_ROOT}"

python3 -c 'from services.model_router_adapter.server import main
try:
    main()
except KeyboardInterrupt:
    print("model_router_adapter.stopped")
'
