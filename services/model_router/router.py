"""Local-first model routing rules for Helio Command Center."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from .config import ModelRouterConfig
from .providers.anthropic_placeholder import AnthropicPlaceholderProvider
from .providers.devmonster_ollama import DevMonsterOllamaProvider, ProviderResult
from .providers.openai_placeholder import OpenAIPlaceholderProvider

LOGGER = logging.getLogger(__name__)

DEVMONSTER_TASKS = {
    "private_brainstorming",
    "summary",
    "summaries",
    "summarization",
    "brainstorming",
    "prd_drafting",
    "internal_planning",
    "internal_reasoning",
    "low_risk_agent_reasoning",
}
FAST_LOCAL_TASKS = {"classify", "route", "quick_summary", "command_parse"}
HUMAN_APPROVAL_TASKS = {
    "autonomous_execution_decisions",
    "sending_emails",
    "editing_production_code_without_review",
    "google_workspace_actions",
    "home_assistant_control",
}
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
    task_type: str
    timestamp: str
    elapsed_seconds: float
    human_approval_required: bool


@dataclass(frozen=True)
class RouteDecision:
    task_type: str
    provider: str
    model: str
    timestamp: str
    human_approval_required: bool


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
        decision = self.route(request.task_type, request.model)
        provider = self._provider_by_name(decision.provider)
        started = time.perf_counter()
        result = provider.generate(request.prompt, decision.model)
        elapsed = round(time.perf_counter() - started, 3)
        if not result.ok:
            LOGGER.warning(
                "model_router.generate_failed",
                extra={
                    "provider": provider.name,
                    "task_type": request.task_type,
                    "model": decision.model,
                    "elapsed_seconds": elapsed,
                    "human_approval_required": decision.human_approval_required,
                    "error": result.error,
                },
            )
            raise RuntimeError(result.error)

        text = ""
        if isinstance(result.data, dict):
            text = str(result.data.get("text", ""))
        LOGGER.info(
            "model_router.generate_succeeded",
            extra={
                "provider": provider.name,
                "task_type": request.task_type,
                "model": decision.model,
                "timestamp": decision.timestamp,
                "elapsed_seconds": elapsed,
                "human_approval_required": decision.human_approval_required,
            },
        )
        return RouteResponse(
            provider=provider.name,
            model=decision.model,
            text=text,
            task_type=decision.task_type,
            timestamp=decision.timestamp,
            elapsed_seconds=elapsed,
            human_approval_required=decision.human_approval_required,
        )

    def route(self, task_type: str, model: str | None = None) -> RouteDecision:
        normalized = _normalize_task_type(task_type)
        provider = self._select_provider(normalized)
        selected_model = model or self._default_model_for_task(normalized)
        approval_required = normalized in HUMAN_APPROVAL_TASKS or provider.name != self.devmonster.name
        decision = RouteDecision(
            task_type=normalized,
            provider=provider.name,
            model=selected_model,
            timestamp=datetime.now(timezone.utc).isoformat(),
            human_approval_required=approval_required,
        )
        LOGGER.info(
            "model_router.route_decision",
            extra={
                "task_type": decision.task_type,
                "provider": decision.provider,
                "model": decision.model,
                "timestamp": decision.timestamp,
                "human_approval_required": decision.human_approval_required,
            },
        )
        return decision

    def _default_model_for_task(self, task_type: str) -> str:
        if task_type in FAST_LOCAL_TASKS and self.config.fast_local_model:
            return self.config.fast_local_model
        return self.config.devmonster_default_model

    def _select_provider(self, task_type: str) -> ModelProvider:
        if task_type in FAST_LOCAL_TASKS:
            return self.devmonster
        if task_type in DEVMONSTER_TASKS:
            return self.devmonster
        if task_type in HUMAN_APPROVAL_TASKS:
            return self.devmonster
        if task_type in OPENAI_RESERVED_TASKS:
            LOGGER.info(
                "model_router.cloud_reserved",
                extra={"task_type": task_type, "provider": self.openai.name},
            )
            return self.openai
        if task_type in ANTHROPIC_RESERVED_TASKS:
            LOGGER.info(
                "model_router.cloud_reserved",
                extra={"task_type": task_type, "provider": self.anthropic.name},
            )
            return self.anthropic
        return self.devmonster

    def _provider_by_name(self, name: str) -> ModelProvider:
        if name == self.devmonster.name:
            return self.devmonster
        if name == self.openai.name:
            return self.openai
        if name == self.anthropic.name:
            return self.anthropic
        raise ValueError(f"Unknown provider: {name}")


def _normalize_task_type(task_type: str) -> str:
    return task_type.strip().lower().replace("-", "_").replace(" ", "_")
