"""Localhost OpenAI-compatible HTTP adapter for services.model_router."""

from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from services.model_router.router import ModelRouter, RouteRequest

from .config import AdapterConfig
from .schemas import (
    chat_completion_response,
    error_response,
    models_response,
    normalize_models,
    prompt_from_messages,
)

LOGGER = logging.getLogger(__name__)
MAX_BODY_BYTES = 1_000_000


def create_server(config: AdapterConfig | None = None, router: ModelRouter | None = None) -> ThreadingHTTPServer:
    adapter_config = config or AdapterConfig.from_env()
    handler = make_handler(router or ModelRouter(), adapter_config)
    return ThreadingHTTPServer((adapter_config.host, adapter_config.port), handler)


def make_handler(router: Any, config: AdapterConfig) -> type[BaseHTTPRequestHandler]:
    class ModelRouterAdapterHandler(BaseHTTPRequestHandler):
        server_version = "MSRModelRouterAdapter/0.1"

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            if self.path == "/health":
                self._write_json(
                    200,
                    {
                        "status": "ok",
                        "service": "model_router_adapter",
                        "host": config.host,
                        "port": config.port,
                    },
                )
                return

            if self.path == "/v1/models":
                result = router.list_models()
                if not getattr(result, "ok", False):
                    self._write_json(502, error_response(getattr(result, "error", "model listing failed")))
                    return
                self._write_json(200, models_response(normalize_models(getattr(result, "data", {}))))
                return

            self._write_json(404, error_response("Unknown endpoint", "not_found"))

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            if self.path != "/v1/chat/completions":
                self._write_json(404, error_response("Unknown endpoint", "not_found"))
                return

            try:
                payload = self._read_json()
                messages = payload.get("messages")
                if not isinstance(messages, list):
                    self._write_json(400, error_response("messages must be a list", "bad_request"))
                    return

                model = str(payload.get("model") or "")
                task_type = str(payload.get("task_type") or config.default_task_type)
                prompt = prompt_from_messages(messages)
                route_response = router.generate(RouteRequest(task_type=task_type, prompt=prompt, model=model or None))
                self._write_json(200, chat_completion_response(route_response, model))
            except ValueError as exc:
                self._write_json(400, error_response(str(exc), "bad_request"))
            except RuntimeError as exc:
                self._write_json(502, error_response(str(exc), "router_error"))

        def log_message(self, format: str, *args: Any) -> None:
            LOGGER.info("model_router_adapter.http", extra={"client": self.client_address[0], "message": format % args})

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0:
                raise ValueError("request body required")
            if length > MAX_BODY_BYTES:
                raise ValueError("request body too large")
            raw = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError("invalid JSON") from exc
            if not isinstance(data, dict):
                raise ValueError("request body must be a JSON object")
            return data

        def _write_json(self, status: int, payload: dict[str, Any]) -> None:
            encoded = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    return ModelRouterAdapterHandler


def main() -> None:
    config = AdapterConfig.from_env()
    if config.host != "127.0.0.1":
        raise SystemExit("MODEL_ROUTER_ADAPTER_HOST must be 127.0.0.1 for Phase 5G")
    server = create_server(config=config)
    LOGGER.warning("model_router_adapter.starting", extra={"host": config.host, "port": config.port})
    server.serve_forever()


if __name__ == "__main__":
    main()

