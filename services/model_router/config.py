"""Configuration for the Helio model router."""

from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_DEVMONSTER_URL = "http://100.93.120.124:11434"
DEFAULT_DEVMONSTER_MODEL = "gemma4:26b"
DEFAULT_FAST_LOCAL_MODEL = "gemma3:4b"
DEFAULT_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True)
class ModelRouterConfig:
    devmonster_ollama_url: str
    devmonster_default_model: str
    fast_local_model: str
    openai_api_key: str
    anthropic_api_key: str
    timeout_seconds: float

    @classmethod
    def from_env(cls) -> "ModelRouterConfig":
        return cls(
            devmonster_ollama_url=os.getenv(
                "DEVMONSTER_OLLAMA_URL",
                os.getenv("GEMMA_BASE_URL", DEFAULT_DEVMONSTER_URL),
            ).rstrip("/"),
            devmonster_default_model=os.getenv(
                "DEVMONSTER_DEFAULT_MODEL",
                os.getenv("GEMMA_MODEL", DEFAULT_DEVMONSTER_MODEL),
            ),
            fast_local_model=os.getenv("FAST_LOCAL_MODEL", DEFAULT_FAST_LOCAL_MODEL),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            timeout_seconds=_float_env(
                "MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS",
                _float_env("GEMMA_TIMEOUT", DEFAULT_TIMEOUT_SECONDS),
            ),
        )


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default
