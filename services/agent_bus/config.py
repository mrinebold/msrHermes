"""Fail-closed configuration for the Hermes-to-Helio Phase 1 bridge.

Phase 1 admits only an in-process test gateway.  It never reads Supabase
configuration and never establishes a network connection.  A later, separately
approved phase may add a Helio-owned private gateway transport.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


MODE_DISABLED = "disabled"
MODE_READ_ONLY = "read_only"
MODE_DRY_RUN = "dry_run"
MODE_OUTBOUND_WITH_APPROVAL = "outbound_with_approval"
TEST_GATEWAY_URL = "inprocess://helio-test"

ALLOWED_MODES = {
    MODE_DISABLED,
    MODE_READ_ONLY,
    MODE_DRY_RUN,
    MODE_OUTBOUND_WITH_APPROVAL,
}


@dataclass(frozen=True)
class AgentBusConfig:
    helio_gateway_url: str
    mode: str
    default_org: str
    default_workspace: str
    agent_id: str
    test_gateway_enabled: bool = False

    @property
    def validation_errors(self) -> tuple[str, ...]:
        errors: list[str] = []
        if self.mode not in ALLOWED_MODES:
            errors.append("HELIO_AGENT_BUS_MODE")
        if self.mode == MODE_DISABLED:
            errors.append("HELIO_AGENT_BUS_MODE=disabled")
            return tuple(errors)
        if not self.helio_gateway_url:
            errors.append("HELIO_GATEWAY_URL")
        elif self.helio_gateway_url != TEST_GATEWAY_URL:
            errors.append(f"HELIO_GATEWAY_URL={TEST_GATEWAY_URL}")
        if not self.test_gateway_enabled:
            errors.append("HERMES_HELIO_TEST_GATEWAY=1")
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

    @property
    def transport(self) -> str:
        return "inprocess_test_gateway" if self.configured else "disabled"


def _enabled(values: Mapping[str, str], name: str) -> bool:
    return values.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def load_config(env: Mapping[str, str] | None = None) -> AgentBusConfig:
    values = env or os.environ
    return AgentBusConfig(
        helio_gateway_url=values.get("HELIO_GATEWAY_URL", "").strip(),
        mode=values.get("HELIO_AGENT_BUS_MODE", MODE_DISABLED).strip() or MODE_DISABLED,
        default_org=values.get("HELIO_DEFAULT_ORG", "").strip(),
        default_workspace=values.get("HELIO_DEFAULT_WORKSPACE", "").strip(),
        agent_id=values.get("HELIO_AGENT_ID", "hermes").strip(),
        test_gateway_enabled=_enabled(values, "HERMES_HELIO_TEST_GATEWAY"),
    )


def is_configured(config: AgentBusConfig | None = None) -> bool:
    candidate = config or load_config()
    return candidate.configured
