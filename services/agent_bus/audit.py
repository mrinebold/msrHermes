"""Audit helpers for mocked agent bus adapter actions."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from .schemas import AdapterAuditEvent

SECRET_MARKERS = ("key", "token", "secret", "password", "credential")


def redact_mapping(raw: Mapping[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in raw.items():
        lowered = key.lower()
        if any(marker in lowered for marker in SECRET_MARKERS):
            redacted[key] = "[REDACTED]"
        elif isinstance(value, Mapping):
            redacted[key] = redact_mapping(value)
        else:
            redacted[key] = value
    return redacted


def build_audit_event(
    action: str,
    mode: str,
    status: str,
    org_id: str,
    workspace: str,
    details: Mapping[str, Any] | None = None,
) -> AdapterAuditEvent:
    return AdapterAuditEvent(
        action=action,
        mode=mode,
        status=status,
        org_id=org_id,
        workspace=workspace,
        details=redact_mapping(details or {}),
    )


def audit_event_to_dict(event: AdapterAuditEvent) -> dict[str, Any]:
    return asdict(event)

