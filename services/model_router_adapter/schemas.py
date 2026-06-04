"""OpenAI-compatible request and response helpers for the adapter."""

from __future__ import annotations

import time
from typing import Any


def prompt_from_messages(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for message in messages:
        role = str(message.get("role", "user"))
        content = message.get("content", "")
        if isinstance(content, list):
            content = " ".join(str(item.get("text", item)) for item in content)
        parts.append(f"{role}: {content}")
    return "\n".join(parts).strip()


def normalize_models(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []

    if isinstance(data.get("data"), list):
        return [
            {
                "id": str(item.get("id") or item.get("name")),
                "object": "model",
                "owned_by": "msr-model-router",
            }
            for item in data["data"]
            if isinstance(item, dict) and (item.get("id") or item.get("name"))
        ]

    models = data.get("models")
    if isinstance(models, list):
        return [
            {
                "id": str(item.get("name") or item.get("model") or item.get("id")),
                "object": "model",
                "owned_by": "msr-model-router",
            }
            for item in models
            if isinstance(item, dict) and (item.get("name") or item.get("model") or item.get("id"))
        ]

    return []


def models_response(models: list[dict[str, Any]]) -> dict[str, Any]:
    return {"object": "list", "data": models}


def chat_completion_response(route_response: Any, request_model: str) -> dict[str, Any]:
    created = int(time.time())
    model = getattr(route_response, "model", request_model)
    text = getattr(route_response, "text", "")
    return {
        "id": f"chatcmpl-msr-{created}",
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
        "msr_route": {
            "provider": getattr(route_response, "provider", ""),
            "task_type": getattr(route_response, "task_type", ""),
            "elapsed_seconds": getattr(route_response, "elapsed_seconds", 0),
            "human_approval_required": getattr(route_response, "human_approval_required", False),
        },
    }


def chat_completion_stream_chunks(route_response: Any, request_model: str) -> list[dict[str, Any]]:
    created = int(time.time())
    model = getattr(route_response, "model", request_model)
    text = getattr(route_response, "text", "")
    chunk_id = f"chatcmpl-msr-{created}"
    return [
        {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": text},
                    "finish_reason": None,
                }
            ],
        },
        {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }
            ],
        },
    ]


def error_response(message: str, code: str = "adapter_error") -> dict[str, Any]:
    return {"error": {"message": message, "type": code}}
