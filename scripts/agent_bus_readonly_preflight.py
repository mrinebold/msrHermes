#!/usr/bin/env python3
"""Read-only Supabase Agent Bus preflight for Hermes.

This script uses only Python stdlib and reads configuration from the
process environment. It does not load local env files and never writes
to Supabase.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


READ_ONLY_MODE = "read_only"
DEFAULT_LIMIT = 25
REDACTED = "[redacted]"


class PreflightError(RuntimeError):
    """Raised when the preflight must fail closed."""

    def __init__(self, reason: str, detail: str | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.detail = detail


@dataclass(frozen=True)
class PreflightConfig:
    supabase_url: str
    supabase_anon_key: str
    mode: str
    org_id: str
    workspace: str
    agent_id: str

    @property
    def validation_errors(self) -> tuple[str, ...]:
        errors: list[str] = []
        if self.mode != READ_ONLY_MODE:
            errors.append("HELIO_AGENT_BUS_MODE=read_only")
        if not self.supabase_url:
            errors.append("SUPABASE_URL")
        if not self.supabase_anon_key:
            errors.append("SUPABASE_ANON_KEY")
        if not self.org_id:
            errors.append("HELIO_DEFAULT_ORG")
        if not self.workspace:
            errors.append("HELIO_DEFAULT_WORKSPACE")
        if self.agent_id != "hermes":
            errors.append("HELIO_AGENT_ID=hermes")
        return tuple(errors)

    @property
    def configured(self) -> bool:
        return not self.validation_errors


def load_config(env: Mapping[str, str] | None = None) -> PreflightConfig:
    values = env if env is not None else os.environ
    return PreflightConfig(
        supabase_url=values.get("SUPABASE_URL", "").strip().rstrip("/"),
        supabase_anon_key=values.get("SUPABASE_ANON_KEY", "").strip(),
        mode=values.get("HELIO_AGENT_BUS_MODE", "").strip(),
        org_id=values.get("HELIO_DEFAULT_ORG", "").strip(),
        workspace=values.get("HELIO_DEFAULT_WORKSPACE", "").strip(),
        agent_id=values.get("HELIO_AGENT_ID", "").strip(),
    )


def require_config(config: PreflightConfig) -> None:
    if not config.configured:
        raise PreflightError("missing_or_invalid_config", ", ".join(config.validation_errors))


def build_path(table: str, params: Mapping[str, str | int]) -> str:
    return f"/rest/v1/{table}?{urlencode(params)}"


def org_config_path(config: PreflightConfig, limit: int = DEFAULT_LIMIT) -> str:
    return build_path(
        "org_messaging_config",
        {
            "select": "org_id,config_type,config_data,updated_at",
            "org_id": f"eq.{config.org_id}",
            "order": "config_type.asc",
            "limit": limit,
        },
    )


def hermes_messages_path(config: PreflightConfig, limit: int = DEFAULT_LIMIT) -> str:
    return build_path(
        "agent_messages",
        {
            "select": (
                "id,from_agent,to_agent,message_type,payload,risk_level,status,priority,"
                "parent_message_id,result,error,created_at,claimed_at,completed_at,expires_at,org_id"
            ),
            "org_id": f"eq.{config.org_id}",
            "to_agent": f"eq.{config.agent_id}",
            "order": "created_at.desc",
            "limit": limit,
        },
    )


def outbound_audit_path(config: PreflightConfig, limit: int = DEFAULT_LIMIT) -> str:
    return build_path(
        "bot_outbound_messages",
        {
            "select": (
                "id,bot_name,chat_id,message_text,parse_mode,reply_to_message_id,"
                "status,error,requested_by,created_at,sent_at,org_id"
            ),
            "org_id": f"eq.{config.org_id}",
            "order": "created_at.desc",
            "limit": limit,
        },
    )


def request_json(
    config: PreflightConfig,
    path: str,
    method: str = "GET",
    opener=urlopen,
) -> Any:
    require_config(config)
    if method.upper() != "GET":
        raise PreflightError("non_get_request_blocked", method.upper())

    url = urljoin(f"{config.supabase_url}/", path.lstrip("/"))
    request = Request(
        url,
        method="GET",
        headers={
            "apikey": config.supabase_anon_key,
            "Authorization": f"Bearer {config.supabase_anon_key}",
            "Accept": "application/json",
        },
    )
    try:
        with opener(request, timeout=10) as response:
            body = response.read().decode("utf-8")
    except HTTPError as error:
        detail = _read_error_body(error, config.supabase_anon_key)
        if error.code in (401, 403):
            raise PreflightError("rls_or_permission_denied", detail) from error
        raise PreflightError("supabase_read_failed", f"HTTP {error.code}: {detail}") from error

    try:
        return json.loads(body) if body else []
    except json.JSONDecodeError as error:
        raise PreflightError("invalid_json_response", str(error)) from error


def _read_error_body(error: HTTPError, secret: str) -> str:
    try:
        body = error.read().decode("utf-8")
    except Exception:
        body = ""
    if not body:
        return f"HTTP {error.code}"
    return redact_text(body, secret)


def redact_value(key: str, value: Any) -> Any:
    lowered = key.lower()
    if lowered in {"payload", "message_text", "chat_id", "result", "error"}:
        return REDACTED
    if any(token in lowered for token in ("key", "token", "secret", "password", "credential", "authorization")):
        return REDACTED
    if isinstance(value, dict):
        return {child_key: redact_value(child_key, child_value) for child_key, child_value in value.items()}
    if isinstance(value, list):
        return [redact_value(key, item) for item in value]
    return value


def redact_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {key: redact_value(key, value) for key, value in row.items()}


def redact_text(text: str, secret: str) -> str:
    return text.replace(secret, REDACTED) if secret else text


def summarize_rows(name: str, rows: Any, config: PreflightConfig, include_samples: bool = False) -> dict[str, Any]:
    if not isinstance(rows, list):
        raise PreflightError("unexpected_response_shape", f"{name} did not return a list")

    status_counts: dict[str, int] = {}
    latest_created_at: str | None = None
    config_types: list[str] = []
    out_of_scope = 0

    for row in rows:
        if not isinstance(row, dict):
            raise PreflightError("unexpected_response_shape", f"{name} row is not an object")
        if row.get("org_id") and row.get("org_id") != config.org_id:
            out_of_scope += 1
        if row.get("to_agent") and row.get("to_agent") != config.agent_id:
            out_of_scope += 1
        status = row.get("status")
        if isinstance(status, str):
            status_counts[status] = status_counts.get(status, 0) + 1
        created_at = row.get("created_at")
        if isinstance(created_at, str) and (latest_created_at is None or created_at > latest_created_at):
            latest_created_at = created_at
        config_type = row.get("config_type")
        if isinstance(config_type, str):
            config_types.append(config_type)

    if out_of_scope:
        raise PreflightError("out_of_scope_records_returned", str(out_of_scope))

    summary: dict[str, Any] = {
        "name": name,
        "row_count": len(rows),
        "status_counts": status_counts,
        "latest_created_at": latest_created_at,
        "config_types": sorted(set(config_types)),
    }
    if include_samples:
        summary["samples"] = [redact_row(row) for row in rows[:3]]
    return summary


def verify_config(config: PreflightConfig) -> dict[str, Any]:
    require_config(config)
    return {
        "status": "ok",
        "mode": config.mode,
        "org_id": config.org_id,
        "workspace": config.workspace,
        "agent_id": config.agent_id,
        "supabase_url_configured": bool(config.supabase_url),
        "supabase_anon_key_configured": bool(config.supabase_anon_key),
    }


def list_org_configs(config: PreflightConfig, limit: int = DEFAULT_LIMIT, opener=urlopen) -> dict[str, Any]:
    rows = request_json(config, org_config_path(config, limit), opener=opener)
    return summarize_rows("org_messaging_config", rows, config)


def read_hermes_messages(config: PreflightConfig, limit: int = DEFAULT_LIMIT, opener=urlopen) -> dict[str, Any]:
    rows = request_json(config, hermes_messages_path(config, limit), opener=opener)
    return summarize_rows("agent_messages_to_hermes", rows, config)


def read_outbound_audit(config: PreflightConfig, limit: int = DEFAULT_LIMIT, opener=urlopen) -> dict[str, Any]:
    rows = request_json(config, outbound_audit_path(config, limit), opener=opener)
    return summarize_rows("bot_outbound_messages_audit", rows, config)


def run_all(config: PreflightConfig, limit: int = DEFAULT_LIMIT, opener=urlopen) -> dict[str, Any]:
    return {
        "status": "ok",
        "checks": [
            verify_config(config),
            list_org_configs(config, limit=limit, opener=opener),
            read_hermes_messages(config, limit=limit, opener=opener),
            read_outbound_audit(config, limit=limit, opener=opener),
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run read-only Hermes Agent Bus preflight checks.")
    parser.add_argument(
        "command",
        choices=("verify-config", "list-org-configs", "read-hermes-messages", "read-outbound-audit", "run-all"),
    )
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    return parser


def run_command(command: str, config: PreflightConfig, limit: int = DEFAULT_LIMIT, opener=urlopen) -> dict[str, Any]:
    if command == "verify-config":
        return verify_config(config)
    if command == "list-org-configs":
        return list_org_configs(config, limit=limit, opener=opener)
    if command == "read-hermes-messages":
        return read_hermes_messages(config, limit=limit, opener=opener)
    if command == "read-outbound-audit":
        return read_outbound_audit(config, limit=limit, opener=opener)
    if command == "run-all":
        return run_all(config, limit=limit, opener=opener)
    raise PreflightError("unknown_command", command)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config()
    try:
        result = run_command(args.command, config=config, limit=args.limit)
    except PreflightError as error:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "reason": error.reason,
                    "detail": error.detail,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
