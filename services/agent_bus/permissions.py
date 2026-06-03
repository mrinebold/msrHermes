"""Permission checks for the read-only Hermes Helio agent bus scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from .config import AgentBusConfig, MODE_DRY_RUN, MODE_OUTBOUND_WITH_APPROVAL, MODE_READ_ONLY


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    reason: str


def can_read(config: AgentBusConfig) -> PermissionDecision:
    if not config.configured:
        return PermissionDecision(False, "agent bus config is not complete")
    if config.mode in {MODE_READ_ONLY, MODE_DRY_RUN, MODE_OUTBOUND_WITH_APPROVAL}:
        return PermissionDecision(True, "read allowed")
    return PermissionDecision(False, f"read denied in mode {config.mode}")


def can_dry_run(config: AgentBusConfig) -> PermissionDecision:
    if not config.configured:
        return PermissionDecision(False, "agent bus config is not complete")
    if config.mode in {MODE_DRY_RUN, MODE_OUTBOUND_WITH_APPROVAL}:
        return PermissionDecision(True, "dry run allowed")
    return PermissionDecision(False, f"dry run denied in mode {config.mode}")


def can_write(config: AgentBusConfig) -> PermissionDecision:
    if not config.configured:
        return PermissionDecision(False, "agent bus config is not complete")
    return PermissionDecision(False, "write denied by default in scaffold")


def can_execute_tasks(config: AgentBusConfig) -> PermissionDecision:
    if not config.configured:
        return PermissionDecision(False, "agent bus config is not complete")
    return PermissionDecision(False, "task execution denied in scaffold")

