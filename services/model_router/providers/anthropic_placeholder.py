"""Placeholder for future Anthropic routing."""

from __future__ import annotations

from .devmonster_ollama import ProviderResult


class AnthropicPlaceholderProvider:
    name = "anthropic_placeholder"

    def __init__(self, api_key: str, timeout_seconds: float) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def health_check(self) -> ProviderResult:
        return ProviderResult(ok=False, error="Anthropic provider is not configured yet")

    def list_models(self) -> ProviderResult:
        return ProviderResult(ok=False, error="Anthropic provider is not configured yet")

    def generate(self, prompt: str, model: str | None = None) -> ProviderResult:
        return ProviderResult(ok=False, error="Anthropic provider is reserved for future approved cloud routing")
