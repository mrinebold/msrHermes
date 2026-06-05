"""OpenAI-compatible request and response helpers for the adapter."""

from __future__ import annotations

import time
import re
from typing import Any


ROLE_ORDER = {"system", "developer", "user", "assistant", "tool"}
TOOL_VOCAB_PATTERN = re.compile(r"\b(tool|function|schema|call)\b", re.IGNORECASE)
XML_OR_TOOL_TAG_PATTERN = re.compile(r"</?[\w:-]+(?:\s+[^>]*)?>")
JSON_LIKE_BLOCK_PATTERN = re.compile(r"\{[^{}]*(?:\"[^\"]+\"\s*:)[^{}]*\}", re.DOTALL)


def prompt_from_messages(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for message in messages:
        role = str(message.get("role", "user"))
        content = message_content_text(message.get("content", ""))
        parts.append(f"{role}: {content}")
    return "\n".join(parts).strip()


def local_compat_prompt_from_messages(messages: list[Any], mode: str = "flattened") -> str:
    return gemma_prompt_from_messages(messages, mode)


def gemma_prompt_from_messages(messages: list[Any], mode: str = "flattened") -> str:
    sections = _message_sections(messages)
    if mode == "user_only":
        return _join_sections(section for section in sections if section["role"] == "user")
    if mode == "final_user":
        final_user = _final_user_section(sections)
        return _join_sections([final_user] if final_user else [])
    if mode == "instruction_context":
        final_user = _final_user_section(sections)
        context = [section for section in sections if section is not final_user]
        ordered = ([final_user] if final_user else []) + context
        return _join_sections(ordered)
    if mode == "no_tool_vocab":
        return TOOL_VOCAB_PATTERN.sub("", _join_sections(sections)).strip()
    return _join_sections(sections)


def _message_sections(messages: list[Any]) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role", "user")).strip().lower() or "user"
        if role not in ROLE_ORDER:
            role = "user"
        content = message_content_text(message.get("content", "")).strip()
        if not content:
            continue
        sections.append({"role": role, "content": content})
    return sections


def _join_sections(sections: Any) -> str:
    return "\n\n".join(f"[{section['role']}]\n{section['content']}" for section in sections).strip()


def _final_user_section(sections: list[dict[str, str]]) -> dict[str, str] | None:
    for section in reversed(sections):
        if section["role"] == "user":
            return section
    return None


def prompt_construction_metadata(messages: list[Any], prompt: str) -> dict[str, Any]:
    sections = _message_sections(messages)
    role_sections = [section["role"] for section in sections]
    user_chars = sum(len(section["content"]) for section in sections if section["role"] == "user")
    system_chars = sum(len(section["content"]) for section in sections if section["role"] == "system")
    final_user = _final_user_section(sections)
    final_user_start_index = -1
    if final_user:
        final_user_start_index = prompt.find(final_user["content"])
    keyword_counts = _keyword_counts(prompt)
    return {
        "prompt_total_chars": len(prompt),
        "prompt_role_sections": sorted(set(role_sections)),
        "prompt_section_order": role_sections,
        "prompt_prefix_chars_logged": 0,
        "prompt_suffix_chars_logged": 0,
        "markdown_fence_count": prompt.count("```"),
        "xml_or_tool_like_tag_count": len(XML_OR_TOOL_TAG_PATTERN.findall(prompt)),
        "json_like_block_count": len(JSON_LIKE_BLOCK_PATTERN.findall(prompt)),
        "tool_keyword_count": keyword_counts["tool"],
        "function_keyword_count": keyword_counts["function"],
        "schema_keyword_count": keyword_counts["schema"],
        "call_keyword_count": keyword_counts["call"],
        "contains_tool_keyword": keyword_counts["tool"] > 0,
        "contains_function_keyword": keyword_counts["function"] > 0,
        "contains_schema_keyword": keyword_counts["schema"] > 0,
        "contains_call_keyword": keyword_counts["call"] > 0,
        "final_user_content_start_index": final_user_start_index,
        "user_content_chars": user_chars,
        "system_content_chars": system_chars,
        "user_content_dominates_system": user_chars > system_chars,
    }


def _keyword_counts(prompt: str) -> dict[str, int]:
    counts = {"tool": 0, "function": 0, "schema": 0, "call": 0}
    for match in TOOL_VOCAB_PATTERN.finditer(prompt):
        counts[match.group(1).lower()] += 1
    return counts


def has_nonempty_user_content(messages: list[Any]) -> bool:
    for message in messages:
        if not isinstance(message, dict):
            continue
        if str(message.get("role", "user")).strip().lower() != "user":
            continue
        if message_content_text(message.get("content", "")).strip():
            return True
    return False


def message_content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if "text" in item:
                    parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))
        return " ".join(parts)
    if content is None:
        return ""
    return str(content)


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
