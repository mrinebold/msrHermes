"""Local-first model routing rules for Helio Command Center."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from .config import ModelRouterConfig
from .providers.anthropic_placeholder import AnthropicPlaceholderProvider
from .providers.devmonster_ollama import DevMonsterOllamaProvider, ProviderResult
from .providers.openai_placeholder import OpenAIPlaceholderProvider

LOGGER = logging.getLogger(__name__)

DEVMONSTER_TASKS = {"summary", "summaries", "brainstorming", "prd_drafting", "internal_reasoning"}
OPENAI_RESERVED_TASKS = {"advanced_coding", "fallback_handling"}
ANTHROPIC_RESERVED_TASKS = {"large_context_analysis"}


class ModelProvider(Protocol):
    name: str

    def health_check(self) -> ProviderResult: ...

    def list_models(self) -> ProviderResult: ...

    def generate(self, prompt: str, model: str | None = None) -> ProviderResult: ...


@dataclass(frozen=True)
class RouteRequest:
    task_type: str
    prompt: str
    model: str | None = None


@dataclass(frozen=True)
class RouteResponse:
    provider: str
    model: str
    text: str


class ModelRouter:
    def __init__(
        self,
        config: ModelRouterConfig | None = None,
        devmonster_provider: ModelProvider | None = None,
        openai_provider: ModelProvider | None = None,
        anthropic_provider: ModelProvider | None = None,
    ) -> None:
        self.config = config or ModelRouterConfig.from_env()
        self.devmonster = devmonster_provider or DevMonsterOllamaProvider(
            self.config.devmonster_ollama_url,
            self.config.devmonster_default_model,
            self.config.timeout_seconds,
        )
        self.openai = openai_provider or OpenAIPlaceholderProvider(
            self.config.openai_api_key,
            self.config.timeout_seconds,
        )
        self.anthropic = anthropic_provider or AnthropicPlaceholderProvider(
            self.config.anthropic_api_key,
            self.config.timeout_seconds,
        )

    def health_check(self) -> dict[str, ProviderResult]:
        return {
            "devmonster": self.devmonster.health_check(),
            "openai": self.openai.health_check(),
            "anthropic": self.anthropic.health_check(),
        }

    def list_models(self) -> ProviderResult:
        return self.devmonster.list_models()

    def generate(self, request: RouteRequest) -> RouteResponse:
        provider = self._select_provider(request.task_type)
        model = request.model or self.config.devmonster_default_model
        result = provider.generate(request.prompt, model)
        if not result.ok:
            LOGGER.warning(
                "model_router.generate_failed",
                extra={"provider": provider.name, "task_type": request.task_type, "error": result.error},
            )
            raise RuntimeError(result.error)

        text = ""
        if isinstance(result.data, dict):
            text = str(result.data.get("text", ""))
        LOGGER.info(
            "model_router.generate_succeeded",
            extra={"provider": provider.name, "task_type": request.task_type, "model": model},
        )
        return RouteResponse(provider=provider.name, model=model, text=text)

    def _select_provider(self, task_type: str) -> ModelProvider:
        normalized = task_type.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in DEVMONSTER_TASKS:
            return self.devmonster
        if normalized in OPENAI_RESERVED_TASKS:
            LOGGER.info(
                "model_router.cloud_reserved",
                extra={"task_type": normalized, "provider": self.openai.name},
            )
            return self.openai
        if normalized in ANTHROPIC_RESERVED_TASKS:
            LOGGER.info(
                "model_router.cloud_reserved",
                extra={"task_type": normalized, "provider": self.anthropic.name},
            )
            return self.anthropic
        return self.devmonster
