"""Localhost OpenAI-compatible HTTP adapter for services.model_router."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from services.model_router.router import ModelRouter, RouteRequest

from .config import AdapterConfig
from .schemas import (
    chat_completion_response,
    chat_completion_stream_chunks,
    error_response,
    has_nonempty_user_content,
    local_summary_extraction,
    local_compat_prompt_from_messages,
    message_content_text,
    models_response,
    normalize_models,
    prompt_construction_metadata,
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
            started = time.perf_counter()
            selected_model = ""
            status = 500
            if self.path == "/health":
                status = 200
                self._write_json(
                    200,
                    {
                        "status": "ok",
                        "service": "model_router_adapter",
                        "host": config.host,
                        "port": config.port,
                    },
                )
                self._log_request(started, status, selected_model)
                return

            if self.path == "/v1/models":
                result = router.list_models()
                if not getattr(result, "ok", False):
                    status = 502
                    self._write_json(status, error_response(getattr(result, "error", "model listing failed")))
                    self._log_request(started, status, selected_model)
                    return
                status = 200
                self._write_json(status, models_response(normalize_models(getattr(result, "data", {}))))
                self._log_request(started, status, selected_model)
                return

            status = 404
            self._write_json(status, error_response("Unknown endpoint", "not_found"))
            self._log_request(started, status, selected_model)

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            started = time.perf_counter()
            selected_model = ""
            status = 500
            if self.path != "/v1/chat/completions":
                status = 404
                self._write_json(status, error_response("Unknown endpoint", "not_found"))
                self._log_request(started, status, selected_model)
                return

            try:
                payload = self._read_json()
                streaming_requested = bool(payload.get("stream"))
                messages = payload.get("messages")
                if not isinstance(messages, list):
                    status = 400
                    self._write_json(status, error_response("messages must be a list", "bad_request"))
                    self._log_request(started, status, selected_model)
                    return

                model = str(payload.get("model") or "")
                selected_model = model
                task_type = str(payload.get("task_type") or config.default_task_type)
                use_local_compat = _uses_local_compat(config, model)
                if use_local_compat and not has_nonempty_user_content(messages):
                    status = 400
                    prompt = local_compat_prompt_from_messages(
                        messages,
                        config.gemma_prompt_mode,
                        config.local_summary_max_context_chars,
                    )
                    self._log_message_structure(payload, messages, streaming_requested, use_local_compat, prompt)
                    self._write_json(status, error_response("local compatibility mode requires non-empty user content", "bad_request"))
                    self._log_request(started, status, selected_model)
                    return
                if use_local_compat and config.gemma_prompt_mode == "local_summary":
                    extraction = local_summary_extraction(messages, config.local_summary_max_context_chars)
                    if not extraction["success"]:
                        status = 400
                        self._log_message_structure(payload, messages, streaming_requested, use_local_compat, "")
                        self._write_json(status, error_response("local summary mode requires user instruction and file-like context", "bad_request"))
                        self._log_request(started, status, selected_model)
                        return

                prompt = (
                    local_compat_prompt_from_messages(
                        messages,
                        config.gemma_prompt_mode,
                        config.local_summary_max_context_chars,
                    )
                    if use_local_compat
                    else prompt_from_messages(messages)
                )
                self._log_message_structure(payload, messages, streaming_requested, use_local_compat, prompt)
                route_response = router.generate(RouteRequest(task_type=task_type, prompt=prompt, model=model or None))
                selected_model = str(getattr(route_response, "model", model) or model)
                status = 200
                response_payload = chat_completion_response(route_response, model)
                self._log_response_shape(response_payload, streaming_requested)
                if streaming_requested:
                    self._write_sse(status, chat_completion_stream_chunks(route_response, model))
                else:
                    self._write_json(status, response_payload)
            except ValueError as exc:
                status = 400
                self._write_json(status, error_response(str(exc), "bad_request"))
            except RuntimeError as exc:
                status = 502
                self._write_json(status, error_response(str(exc), "router_error"))
            finally:
                self._log_request(started, status, selected_model)

        def log_message(self, format: str, *args: Any) -> None:
            LOGGER.info("model_router_adapter.http", extra={"client": self.client_address[0], "http_message": format % args})

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

        def _write_sse(self, status: int, chunks: list[dict[str, Any]]) -> None:
            encoded_chunks = [f"data: {json.dumps(chunk)}\n\n".encode("utf-8") for chunk in chunks]
            encoded_chunks.append(b"data: [DONE]\n\n")
            encoded = b"".join(encoded_chunks)
            self.send_response(status)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _log_request(self, started: float, status: int, selected_model: str) -> None:
            if not config.log_requests:
                return
            metadata = {
                "event": "model_router_adapter.request",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": self.command,
                "path": self.path,
                "status": status,
                "selected_model": selected_model,
                "elapsed_seconds": round(time.perf_counter() - started, 3),
            }
            LOGGER.info(
                json.dumps(metadata, sort_keys=True),
                extra=metadata,
            )

        def _log_response_shape(self, payload: dict[str, Any], streaming_requested: bool) -> None:
            if not config.log_response_shapes:
                return
            choices = payload.get("choices")
            first_choice = choices[0] if isinstance(choices, list) and choices else {}
            message = first_choice.get("message") if isinstance(first_choice, dict) else {}
            content = message.get("content") if isinstance(message, dict) else None
            metadata = {
                "event": "model_router_adapter.response_shape",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": self.path,
                "top_level_keys": sorted(str(key) for key in payload.keys()),
                "choices_count": len(choices) if isinstance(choices, list) else 0,
                "content_length": len(content) if isinstance(content, str) else 0,
                "finish_reason": first_choice.get("finish_reason") if isinstance(first_choice, dict) else None,
                "streaming_requested": streaming_requested,
            }
            LOGGER.info(json.dumps(metadata, sort_keys=True), extra=metadata)

        def _log_message_structure(
            self,
            payload: dict[str, Any],
            messages: list[Any],
            streaming_requested: bool,
            compat_mode_enabled: bool,
            flattened_prompt: str,
        ) -> None:
            if not config.log_message_structure:
                return

            roles: list[str] = []
            char_counts: list[int] = []
            final_user_length: int | None = None
            contains_file_content = False
            for message in messages:
                if not isinstance(message, dict):
                    role = "unknown"
                    text = ""
                else:
                    role = str(message.get("role", "user"))
                    text = message_content_text(message.get("content", ""))
                roles.append(role)
                char_counts.append(len(text))
                if role == "user":
                    final_user_length = len(text.strip())
                if _looks_like_file_content(text):
                    contains_file_content = True

            metadata = {
                "event": "model_router_adapter.message_structure",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": self.path,
                "message_count": len(messages),
                "roles_present": sorted(set(roles)),
                "message_char_counts": char_counts,
                "final_user_message_empty": final_user_length in (None, 0),
                "any_message_contains_file_content": contains_file_content,
                "tools_present": bool(payload.get("tools")),
                "tool_choice_present": "tool_choice" in payload,
                "max_tokens_present": "max_tokens" in payload or "max_completion_tokens" in payload,
                "temperature_present": "temperature" in payload,
                "stream_present": "stream" in payload,
                "streaming_requested": streaming_requested,
                "compat_mode_enabled": compat_mode_enabled,
                "flattened_message_count": _flattened_message_count(messages) if compat_mode_enabled else 0,
                "flattened_prompt_chars": len(flattened_prompt) if compat_mode_enabled else 0,
                "tool_schemas_present": bool(payload.get("tools")),
                "tool_schemas_forwarded": False,
                "dropped_tool_schema_count": len(payload.get("tools")) if isinstance(payload.get("tools"), list) else 0,
                "gemma_prompt_mode": config.gemma_prompt_mode if compat_mode_enabled else "",
                "timeout_seconds": config.provider_timeout_seconds if compat_mode_enabled else 0,
            }
            if compat_mode_enabled:
                metadata.update(
                    prompt_construction_metadata(
                        messages,
                        flattened_prompt,
                        config.local_summary_max_context_chars,
                    )
                )
            LOGGER.info(json.dumps(metadata, sort_keys=True), extra=metadata)

    return ModelRouterAdapterHandler


def _looks_like_file_content(text: str) -> bool:
    if not text:
        return False
    stripped = text.lstrip()
    return (
        stripped.startswith("# ")
        or "\n# " in text
        or "```" in text
        or text.count("\n") >= 3
        or "---\n" in text
    )


def _uses_local_compat(config: AdapterConfig, model: str) -> bool:
    if not config.local_compat_mode:
        return False
    normalized = model.strip().lower()
    return not normalized or "gemma" in normalized


def _flattened_message_count(messages: list[Any]) -> int:
    count = 0
    for message in messages:
        if not isinstance(message, dict):
            continue
        if message_content_text(message.get("content", "")).strip():
            count += 1
    return count


def main() -> None:
    config = AdapterConfig.from_env()
    if config.log_requests or config.log_response_shapes or config.log_message_structure:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    if config.host != "127.0.0.1":
        raise SystemExit("MODEL_ROUTER_ADAPTER_HOST must be 127.0.0.1 for Phase 5G")
    server = create_server(config=config)
    LOGGER.warning("model_router_adapter.starting", extra={"host": config.host, "port": config.port})
    server.serve_forever()


if __name__ == "__main__":
    main()
