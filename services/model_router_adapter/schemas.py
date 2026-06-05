"""OpenAI-compatible request and response helpers for the adapter."""

from __future__ import annotations

import time
import re
from typing import Any


ROLE_ORDER = {"system", "developer", "user", "assistant", "tool"}
TOOL_VOCAB_PATTERN = re.compile(r"\b(tool|function|schema|call)\b", re.IGNORECASE)
XML_OR_TOOL_TAG_PATTERN = re.compile(r"</?[\w:-]+(?:\s+[^>]*)?>")
JSON_LIKE_BLOCK_PATTERN = re.compile(r"\{[^{}]*(?:\"[^\"]+\"\s*:)[^{}]*\}", re.DOTALL)
FENCED_BLOCK_PATTERN = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
MARKER_PATTERN = re.compile(
    r"(?im)^(source file|file|document/context|document|context|content)\s*:\s*.*$"
)
MARKDOWN_START_PATTERN = re.compile(r"(?m)^(#\s+|---\s*$)")


def prompt_from_messages(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for message in messages:
        role = str(message.get("role", "user"))
        content = message_content_text(message.get("content", ""))
        parts.append(f"{role}: {content}")
    return "\n".join(parts).strip()


def local_compat_prompt_from_messages(
    messages: list[Any],
    mode: str = "flattened",
    max_context_chars: int | None = None,
) -> str:
    return gemma_prompt_from_messages(messages, mode, max_context_chars=max_context_chars)


def gemma_prompt_from_messages(
    messages: list[Any],
    mode: str = "flattened",
    max_context_chars: int | None = None,
) -> str:
    if mode == "local_summary":
        return local_summary_prompt_from_messages(messages, max_context_chars=max_context_chars)
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


def local_summary_prompt_from_messages(messages: list[Any], max_context_chars: int | None = None) -> str:
    extraction = local_summary_extraction(messages, max_context_chars=max_context_chars)
    if not extraction["success"]:
        return ""
    return (
        "You are summarizing a local sandbox document.\n"
        "Follow the user instruction exactly.\n\n"
        "User instruction:\n"
        f"{extraction['instruction']}\n\n"
        "Document/context:\n"
        f"{extraction['context']}\n\n"
        "Return only the requested answer."
    )


def local_summary_extraction(messages: list[Any], max_context_chars: int | None = None) -> dict[str, Any]:
    sections = _message_sections(messages)
    latest_user = _final_user_section(sections)
    instruction = latest_user["content"].strip() if latest_user else ""
    user_context = _extract_context_from_text(instruction)
    if user_context:
        instruction = _instruction_before_context(instruction, user_context)
    context = user_context or _largest_file_like_context(sections)
    instruction = _clean_summary_text(instruction)
    context = _clean_context_text(context)
    context_original_chars = len(context)
    context = _truncate_context(context, max_context_chars)
    return {
        "success": bool(instruction and context),
        "instruction": instruction,
        "context": context,
        "instruction_chars": len(instruction),
        "context_chars": len(context),
        "context_original_chars": context_original_chars,
        "context_sent_chars": len(context),
        "context_truncated": bool(context_original_chars and len(context) < context_original_chars),
        "dropped_system_chars": sum(len(section["content"]) for section in sections if section["role"] in {"system", "developer"}),
    }


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


def _extract_context_from_text(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    fenced = FENCED_BLOCK_PATTERN.findall(stripped)
    if fenced:
        return max((block.strip() for block in fenced), key=len, default="")
    marker = MARKER_PATTERN.search(stripped)
    if marker:
        return stripped[marker.end() :].strip()
    markdown_start = MARKDOWN_START_PATTERN.search(stripped)
    if markdown_start:
        return stripped[markdown_start.start() :].strip()
    if _looks_like_context_text(stripped):
        return stripped
    return ""


def _instruction_before_context(text: str, context: str) -> str:
    context_start = text.find(context)
    if context_start <= 0:
        return text
    return text[:context_start].strip()


def _largest_file_like_context(sections: list[dict[str, str]]) -> str:
    candidates = [
        _extract_context_from_text(section["content"])
        for section in sections
        if section["role"] in {"user", "system", "developer"}
    ]
    return max((candidate for candidate in candidates if candidate), key=len, default="")


def _looks_like_context_text(text: str) -> bool:
    return text.startswith("# ") or "\n# " in text or text.count("\n") >= 3 or "---\n" in text


def _clean_summary_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if _looks_like_tool_scaffold(line):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _clean_context_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if _looks_like_tool_scaffold(line):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _truncate_context(text: str, max_chars: int | None) -> str:
    if max_chars is None or max_chars <= 0 or len(text) <= max_chars:
        return text
    marker = "\n\n[...local summary context truncated...]\n\n"
    if max_chars <= len(marker) + 20:
        return text[:max_chars].rstrip()
    remaining = max_chars - len(marker)
    head_chars = remaining // 2
    tail_chars = remaining - head_chars
    return f"{text[:head_chars].rstrip()}{marker}{text[-tail_chars:].lstrip()}"


def _looks_like_tool_scaffold(line: str) -> bool:
    lowered = line.strip().lower()
    if not lowered:
        return False
    return (
        lowered.startswith("```")
        or lowered.startswith("[system]")
        or lowered.startswith("[developer]")
        or lowered.startswith("[tool]")
        or MARKER_PATTERN.match(line) is not None
        or "tool_choice" in lowered
        or "tool schema" in lowered
        or "function schema" in lowered
        or "function call" in lowered
    )


def prompt_construction_metadata(
    messages: list[Any],
    prompt: str,
    max_context_chars: int | None = None,
) -> dict[str, Any]:
    sections = _message_sections(messages)
    role_sections = [section["role"] for section in sections]
    user_chars = sum(len(section["content"]) for section in sections if section["role"] == "user")
    system_chars = sum(len(section["content"]) for section in sections if section["role"] == "system")
    final_user = _final_user_section(sections)
    final_user_start_index = -1
    if final_user:
        final_user_start_index = prompt.find(final_user["content"])
    keyword_counts = _keyword_counts(prompt)
    metadata = {
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
    extraction = local_summary_extraction(messages, max_context_chars=max_context_chars)
    metadata.update(
        {
            "instruction_chars": extraction["instruction_chars"] if extraction["success"] else 0,
            "context_chars": extraction["context_chars"] if extraction["success"] else 0,
            "context_original_chars": extraction["context_original_chars"] if extraction["success"] else 0,
            "context_sent_chars": extraction["context_sent_chars"] if extraction["success"] else 0,
            "context_truncated": extraction["context_truncated"] if extraction["success"] else False,
            "dropped_system_chars": extraction["dropped_system_chars"] if extraction["success"] else 0,
            "local_summary_extraction_success": extraction["success"],
        }
    )
    return metadata


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
