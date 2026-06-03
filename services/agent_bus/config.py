"""Fail-closed configuration for the Hermes Helio agent bus adapter."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


MODE_DISABLED = "disabled"
MODE_READ_ONLY = "read_only"
MODE_DRY_RUN = "dry_run"
MODE_OUTBOUND_WITH_APPROVAL = "outbound_with_approval"

ALLOWED_MODES = {
    MODE_DISABLED,
    MODE_READ_ONLY,
    MODE_DRY_RUN,
    MODE_OUTBOUND_WITH_APPROVAL,
}


@dataclass(frozen=True)
class AgentBusConfig:
    supabase_url: str
    supabase_anon_key: str
    mode: str
    default_org: str
    default_workspace: str
    agent_id: str

    @property
    def validation_errors(self) -> tuple[str, ...]:
        errors: list[str] = []
        if self.mode not in ALLOWED_MODES:
            errors.append("HELIO_AGENT_BUS_MODE")
        if self.mode == MODE_DISABLED:
            errors.append("HELIO_AGENT_BUS_MODE=disabled")
            return tuple(errors)
        if not self.supabase_url:
            errors.append("SUPABASE_URL")
        if not self.supabase_anon_key:
            errors.append("SUPABASE_ANON_KEY")
        if not self.default_org:
            errors.append("HELIO_DEFAULT_ORG")
        if not self.default_workspace:
            errors.append("HELIO_DEFAULT_WORKSPACE")
        if not self.agent_id:
            errors.append("HELIO_AGENT_ID")
        return tuple(errors)

    @property
    def configured(self) -> bool:
        return not self.validation_errors


def load_config(env: Mapping[str, str] | None = None) -> AgentBusConfig:
    values = env or os.environ
    return AgentBusConfig(
        supabase_url=values.get("SUPABASE_URL", "").strip(),
        supabase_anon_key=values.get("SUPABASE_ANON_KEY", "").strip(),
        mode=values.get("HELIO_AGENT_BUS_MODE", MODE_DISABLED).strip() or MODE_DISABLED,
        default_org=values.get("HELIO_DEFAULT_ORG", "").strip(),
        default_workspace=values.get("HELIO_DEFAULT_WORKSPACE", "").strip(),
        agent_id=values.get("HELIO_AGENT_ID", "hermes").strip(),
    )


def is_configured(config: AgentBusConfig | None = None) -> bool:
    candidate = config or load_config()
    return candidate.configured

