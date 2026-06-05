"""Configuration for the localhost model router adapter."""

from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8088
DEFAULT_TASK_TYPE = "summary"
DEFAULT_GEMMA_PROMPT_MODE = "flattened"
DEFAULT_LOCAL_SUMMARY_MAX_CONTEXT_CHARS = 3000
DEFAULT_PROVIDER_TIMEOUT_SECONDS = 30.0
GEMMA_PROMPT_MODES = {
    "flattened",
    "user_only",
    "final_user",
    "instruction_context",
    "local_summary",
    "no_tool_vocab",
}


@dataclass(frozen=True)
class AdapterConfig:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    default_task_type: str = DEFAULT_TASK_TYPE
    log_requests: bool = False
    log_response_shapes: bool = False
    log_message_structure: bool = False
    local_compat_mode: bool = False
    gemma_prompt_mode: str = DEFAULT_GEMMA_PROMPT_MODE
    local_summary_max_context_chars: int = DEFAULT_LOCAL_SUMMARY_MAX_CONTEXT_CHARS
    provider_timeout_seconds: float = DEFAULT_PROVIDER_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "AdapterConfig":
        values = env if env is not None else os.environ
        return cls(
            host=values.get("MODEL_ROUTER_ADAPTER_HOST", DEFAULT_HOST),
            port=_int_env(values, "MODEL_ROUTER_ADAPTER_PORT", DEFAULT_PORT),
            default_task_type=values.get("MODEL_ROUTER_ADAPTER_TASK_TYPE", DEFAULT_TASK_TYPE),
            log_requests=_bool_env(values, "MODEL_ROUTER_ADAPTER_LOG_REQUESTS", False),
            log_response_shapes=_bool_env(values, "MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES", False),
            log_message_structure=_bool_env(values, "MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE", False),
            local_compat_mode=_bool_env(values, "MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE", False),
            gemma_prompt_mode=_prompt_mode_env(values),
            local_summary_max_context_chars=_int_env(
                values,
                "MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS",
                DEFAULT_LOCAL_SUMMARY_MAX_CONTEXT_CHARS,
            ),
            provider_timeout_seconds=_float_env(
                values,
                "MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS",
                _float_env(values, "GEMMA_TIMEOUT", DEFAULT_PROVIDER_TIMEOUT_SECONDS),
            ),
        )


def _int_env(env: dict[str, str], name: str, default: int) -> int:
    raw = env.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _bool_env(env: dict[str, str], name: str, default: bool) -> bool:
    raw = env.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _float_env(env: dict[str, str], name: str, default: float) -> float:
    raw = env.get(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _prompt_mode_env(env: dict[str, str]) -> str:
    raw = env.get("MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE", DEFAULT_GEMMA_PROMPT_MODE)
    normalized = raw.strip().lower()
    if normalized in GEMMA_PROMPT_MODES:
        return normalized
    return DEFAULT_GEMMA_PROMPT_MODE
