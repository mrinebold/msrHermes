"""Configuration for the localhost model router adapter."""

from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8088
DEFAULT_TASK_TYPE = "summary"


@dataclass(frozen=True)
class AdapterConfig:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    default_task_type: str = DEFAULT_TASK_TYPE

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "AdapterConfig":
        values = env if env is not None else os.environ
        return cls(
            host=values.get("MODEL_ROUTER_ADAPTER_HOST", DEFAULT_HOST),
            port=_int_env(values, "MODEL_ROUTER_ADAPTER_PORT", DEFAULT_PORT),
            default_task_type=values.get("MODEL_ROUTER_ADAPTER_TASK_TYPE", DEFAULT_TASK_TYPE),
        )


def _int_env(env: dict[str, str], name: str, default: int) -> int:
    raw = env.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default

