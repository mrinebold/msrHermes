"""Ollama-compatible DevMonster provider."""

from __future__ import annotations

import json
import logging
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProviderResult:
    ok: bool
    data: Any = None
    error: str = ""


class DevMonsterOllamaProvider:
    name = "devmonster_ollama"

    def __init__(self, base_url: str, default_model: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout_seconds = timeout_seconds

    def health_check(self) -> ProviderResult:
        result = self._request("GET", "/")
        if not result.ok:
            return result
        return ProviderResult(ok=True, data={"provider": self.name, "base_url": self.base_url})

    def list_models(self) -> ProviderResult:
        result = self._request("GET", "/api/tags")
        if result.ok:
            return result

        LOGGER.info(
            "model_router.provider_fallback",
            extra={"provider": self.name, "from_path": "/api/tags", "to_path": "/v1/models"},
        )
        return self._request("GET", "/v1/models")

    def generate(self, prompt: str, model: str | None = None) -> ProviderResult:
        body = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
        }
        result = self._request("POST", "/api/generate", body)
        if not result.ok:
            return result

        if isinstance(result.data, dict):
            text = result.data.get("response", "")
            return ProviderResult(ok=True, data={"text": text, "raw": result.data})
        return ProviderResult(ok=False, error="Unexpected Ollama response shape")

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> ProviderResult:
        url = f"{self.base_url}{path}"
        payload = None
        headers = {"Accept": "application/json"}
        if body is not None:
            payload = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url, data=payload, headers=headers, method=method)
        LOGGER.info(
            "model_router.provider_request",
            extra={"provider": self.name, "method": method, "url": url, "timeout": self.timeout_seconds},
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                if not raw:
                    return ProviderResult(ok=True, data={"status": response.status})
                try:
                    return ProviderResult(ok=True, data=json.loads(raw))
                except json.JSONDecodeError:
                    return ProviderResult(ok=True, data={"text": raw, "status": response.status})
        except urllib.error.HTTPError as exc:
            return ProviderResult(ok=False, error=f"HTTP {exc.code} from {url}")
        except urllib.error.URLError as exc:
            return ProviderResult(ok=False, error=f"Connection error for {url}: {exc.reason}")
        except (TimeoutError, socket.timeout):
            return ProviderResult(ok=False, error=f"Timed out after {self.timeout_seconds}s for {url}")
