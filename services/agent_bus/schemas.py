"""Schemas for mocked Hermes Helio agent bus reads and dry runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


class AgentBusError(RuntimeError):
    """Raised when the scaffold refuses an unsafe or unsupported operation."""


@dataclass(frozen=True)
class OrgMessagingConfig:
    org_id: str
    config_type: str
    config_data: dict[str, Any]
    updated_at: str | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "OrgMessagingConfig":
        return cls(
            org_id=str(raw.get("org_id", "")),
            config_type=str(raw.get("config_type", "")),
            config_data=dict(raw.get("config_data") or {}),
            updated_at=raw.get("updated_at"),
        )


@dataclass(frozen=True)
class InboundAgentMessage:
    id: str
    from_agent: str
    to_agent: str
    message_type: str
    payload: dict[str, Any]
    risk_level: str
    status: str
    priority: int
    org_id: str
    created_at: str
    parent_message_id: str | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "InboundAgentMessage":
        return cls(
            id=str(raw.get("id", "")),
            from_agent=str(raw.get("from_agent", "")),
            to_agent=str(raw.get("to_agent", "")),
            message_type=str(raw.get("message_type", "")),
            payload=dict(raw.get("payload") or {}),
            risk_level=str(raw.get("risk_level", "read")),
            status=str(raw.get("status", "")),
            priority=int(raw.get("priority", 5)),
            org_id=str(raw.get("org_id", "")),
            created_at=str(raw.get("created_at", "")),
            parent_message_id=raw.get("parent_message_id"),
        )


@dataclass(frozen=True)
class OutboundBotMessageDraft:
    org_id: str
    workspace: str
    bot_name: str
    chat_id_ref: str
    message_text: str
    requested_by: str
    hermes_request_id: str
    parse_mode: str | None = None
    reply_to_message_id: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "org_id": self.org_id,
            "workspace": self.workspace,
            "bot_name": self.bot_name,
            "chat_id_ref": self.chat_id_ref,
            "message_text": self.message_text,
            "parse_mode": self.parse_mode,
            "reply_to_message_id": self.reply_to_message_id,
            "requested_by": self.requested_by,
            "hermes_request_id": self.hermes_request_id,
        }


@dataclass(frozen=True)
class OutboundDryRunResult:
    payload: dict[str, Any]
    would_send: bool = False
    status: str = "dry_run"
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class AdapterAuditEvent:
    action: str
    mode: str
    status: str
    org_id: str
    workspace: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

