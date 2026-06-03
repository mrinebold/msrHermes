"""Mock-only Hermes Helio agent bus adapter client.

This scaffold intentionally performs no network or database calls.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Mapping

from .config import AgentBusConfig, load_config
from .permissions import can_dry_run, can_read, can_write
from .schemas import (
    AgentBusError,
    InboundAgentMessage,
    OrgMessagingConfig,
    OutboundBotMessageDraft,
    OutboundDryRunResult,
)


class AgentBusClient:
    def __init__(
        self,
        config: AgentBusConfig | None = None,
        org_configs: Iterable[Mapping[str, Any]] | None = None,
        messages: Iterable[Mapping[str, Any]] | None = None,
    ) -> None:
        self.config = config or load_config()
        self._org_configs = tuple(OrgMessagingConfig.from_mapping(row) for row in (org_configs or ()))
        self._messages = tuple(InboundAgentMessage.from_mapping(row) for row in (messages or ()))

    def list_org_messaging_configs(self) -> tuple[OrgMessagingConfig, ...]:
        self._require(can_read(self.config))
        configs = [row for row in self._org_configs if row.org_id == self.config.default_org]
        if not configs:
            raise AgentBusError("org_messaging_config unavailable for default org")
        return tuple(configs)

    def read_recent_messages(
        self,
        limit: int = 25,
        statuses: Iterable[str] | None = None,
    ) -> tuple[InboundAgentMessage, ...]:
        self._require(can_read(self.config))
        allowed_statuses = set(statuses or ())
        rows = [
            row
            for row in self._messages
            if row.org_id == self.config.default_org
            and row.to_agent == self.config.agent_id
            and (not allowed_statuses or row.status in allowed_statuses)
        ]
        rows.sort(key=lambda row: row.created_at, reverse=True)
        return tuple(rows[: max(0, limit)])

    def build_outbound_dry_run(
        self,
        bot_name: str,
        chat_id_ref: str,
        message_text: str,
        hermes_request_id: str,
        parse_mode: str | None = None,
        reply_to_message_id: str | None = None,
        requested_by: str | None = None,
    ) -> OutboundDryRunResult:
        self._require(can_dry_run(self.config))
        self._require(can_write(self.config), allow_denied_write=True)
        normalized_bot = bot_name.strip().lower()
        if not normalized_bot:
            raise AgentBusError("unsupported message target: bot_name is required")
        if not chat_id_ref.strip():
            raise AgentBusError("chat_id_ref is required for dry run")
        if not message_text.strip():
            raise AgentBusError("message_text is required for dry run")
        self._require_known_bot(normalized_bot)

        draft = OutboundBotMessageDraft(
            org_id=self.config.default_org,
            workspace=self.config.default_workspace,
            bot_name=normalized_bot,
            chat_id_ref=chat_id_ref,
            message_text=message_text,
            parse_mode=parse_mode,
            reply_to_message_id=reply_to_message_id,
            requested_by=requested_by or self.config.agent_id,
            hermes_request_id=hermes_request_id,
        )
        return OutboundDryRunResult(
            payload=draft.to_payload(),
            would_send=False,
            warnings=("write denied by scaffold; payload was not sent",),
        )

    def _require_known_bot(self, bot_name: str) -> None:
        configs = self.list_org_messaging_configs()
        bot_names: set[str] = set()
        for row in configs:
            if row.config_type == "bot_roster":
                bot_names.update(str(bot).lower() for bot in row.config_data.get("bots", []))
        if bot_names and bot_name not in bot_names:
            raise AgentBusError(f"unsupported message target: {bot_name}")

    @staticmethod
    def _require(decision, allow_denied_write: bool = False) -> None:
        if decision.allowed:
            return
        if allow_denied_write and decision.reason == "write denied by default in scaffold":
            return
        raise AgentBusError(decision.reason)


def list_org_messaging_configs(
    config: AgentBusConfig | None = None,
    org_configs: Iterable[Mapping[str, Any]] | None = None,
) -> tuple[OrgMessagingConfig, ...]:
    return AgentBusClient(config=config, org_configs=org_configs).list_org_messaging_configs()


def read_recent_messages(
    config: AgentBusConfig | None = None,
    org_configs: Iterable[Mapping[str, Any]] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    limit: int = 25,
) -> tuple[InboundAgentMessage, ...]:
    return AgentBusClient(config=config, org_configs=org_configs, messages=messages).read_recent_messages(limit=limit)


def build_outbound_dry_run(
    config: AgentBusConfig | None = None,
    org_configs: Iterable[Mapping[str, Any]] | None = None,
    **kwargs,
) -> OutboundDryRunResult:
    return AgentBusClient(config=config, org_configs=org_configs).build_outbound_dry_run(**kwargs)

