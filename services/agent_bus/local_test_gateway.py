"""In-process Helio contract gateway used only by Phase 1 tests.

This is not an HTTP listener and cannot reach Supabase or an external service.
It exercises the Hermes-to-Helio request boundary with representative,
in-memory records, leaving Helio as the future sole router and dispatcher.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Mapping

from .schemas import AgentBusError, InboundAgentMessage, OrgMessagingConfig


class LocalHelioTestGateway:
    """Small, non-network stand-in for Helio's governed read/dry-run API."""

    def __init__(
        self,
        org_configs: Iterable[Mapping[str, Any]] = (),
        messages: Iterable[Mapping[str, Any]] = (),
    ) -> None:
        self._org_configs = tuple(OrgMessagingConfig.from_mapping(row) for row in org_configs)
        self._messages = tuple(InboundAgentMessage.from_mapping(row) for row in messages)
        self.requests: list[dict[str, Any]] = []

    def list_messaging_configs(self, org_id: str) -> tuple[OrgMessagingConfig, ...]:
        self.requests.append(
            {
                "method": "GET",
                "path": f"/agent-bus/orgs/{org_id}/messaging-config",
                "org_id": org_id,
            }
        )
        rows = tuple(row for row in self._org_configs if row.org_id == org_id)
        if not rows:
            raise AgentBusError("org_messaging_config unavailable for default org")
        return rows

    def read_inbound_messages(
        self,
        org_id: str,
        agent_id: str,
        limit: int,
        statuses: Iterable[str] | None = None,
    ) -> tuple[InboundAgentMessage, ...]:
        selected_statuses = tuple(sorted(set(statuses or ())))
        self.requests.append(
            {
                "method": "GET",
                "path": f"/agent-bus/messages/inbound/{agent_id}",
                "org_id": org_id,
                "limit": max(0, limit),
                "statuses": selected_statuses,
            }
        )
        allowed = set(selected_statuses)
        rows = [
            row
            for row in self._messages
            if row.org_id == org_id
            and row.to_agent == agent_id
            and (not allowed or row.status in allowed)
        ]
        rows.sort(key=lambda row: row.created_at, reverse=True)
        return tuple(rows[: max(0, limit)])

    def propose_task_dry_run(
        self,
        org_id: str,
        workspace: str,
        hermes_request_id: str,
        summary: str,
    ) -> dict[str, Any]:
        """Return the future Helio proposal shape without storing or dispatching work."""
        if not hermes_request_id.strip() or not summary.strip():
            raise AgentBusError("dry-run task proposal requires request id and summary")
        self.requests.append(
            {
                "method": "POST",
                "path": "/agent-bus/tasks/propose",
                "org_id": org_id,
                "workspace": workspace,
            }
        )
        return {
            "status": "dry_run",
            "would_dispatch": False,
            "route": "helio_only",
            "hermes_request_id": hermes_request_id,
        }
