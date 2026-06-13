"""Local approval record primitive for Hermes safety gates."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from services.hermes_safety.audit_log import format_timestamp, looks_secret_key, looks_secret_value


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_APPROVAL_DIR = REPO_ROOT / "logs" / "hermes_approvals"

REQUIRED_FIELDS = (
    "approval_id",
    "timestamp_requested",
    "requested_by",
    "authority_tier",
    "action_type",
    "target",
    "scope",
    "exact_command_or_operation",
    "allowed_paths",
    "forbidden_paths",
    "expiration",
    "one_time_use",
    "risk_level",
    "rollback_plan",
    "status",
    "human_summary",
)

OPTIONAL_FIELDS = ("timestamp_granted", "approved_by", "audit_event_id")

VALID_STATUSES = {"requested", "granted", "denied", "expired", "used", "revoked"}
MODEL_APPROVERS = {"model", "llm", "hermes", "assistant", "ai"}
PERMANENT_EXPIRATIONS = {"", "never", "none", "null", "permanent", "no expiration"}


def build_approval_id(timestamp: str | None = None) -> str:
    stamp = timestamp or format_timestamp()
    compact_stamp = stamp.replace("-", "").replace(":", "").replace("Z", "Z")
    return f"approval_{compact_stamp}_{uuid.uuid4().hex[:8]}"


def _parse_timestamp(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _redact_value(value: Any) -> tuple[Any, bool]:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        changed = False
        for key, item in value.items():
            if looks_secret_key(str(key)):
                redacted[str(key)] = "[REDACTED]"
                changed = True
                continue
            redacted_item, item_changed = _redact_value(item)
            redacted[str(key)] = redacted_item
            changed = changed or item_changed
        return redacted, changed

    if isinstance(value, list):
        redacted_list = []
        changed = False
        for item in value:
            redacted_item, item_changed = _redact_value(item)
            redacted_list.append(redacted_item)
            changed = changed or item_changed
        return redacted_list, changed

    if isinstance(value, str) and looks_secret_value(value):
        return "[REDACTED]", True

    return value, False


def redact_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    redacted, changed = _redact_value(dict(record))
    if not isinstance(redacted, dict):
        raise TypeError("approval record must redact to a dict")
    return redacted, changed


def create_approval_request(
    *,
    requested_by: str,
    authority_tier: str,
    action_type: str,
    target: str,
    scope: str,
    exact_command_or_operation: str,
    allowed_paths: list[str],
    forbidden_paths: list[str],
    expiration: str,
    one_time_use: bool,
    risk_level: str,
    rollback_plan: str,
    human_summary: str,
    audit_event_id: str | None = None,
    timestamp_requested: str | None = None,
    approval_id: str | None = None,
) -> dict[str, Any]:
    requested_at = timestamp_requested or format_timestamp()
    return {
        "approval_id": approval_id or build_approval_id(requested_at),
        "timestamp_requested": requested_at,
        "requested_by": requested_by,
        "authority_tier": authority_tier,
        "action_type": action_type,
        "target": target,
        "scope": scope,
        "exact_command_or_operation": exact_command_or_operation,
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "expiration": expiration,
        "one_time_use": one_time_use,
        "risk_level": risk_level,
        "rollback_plan": rollback_plan,
        "status": "requested",
        "human_summary": human_summary,
        "timestamp_granted": None,
        "approved_by": None,
        "audit_event_id": audit_event_id,
    }


def _validate_expiration(expiration: Any) -> None:
    if not isinstance(expiration, str):
        raise ValueError("approval expiration must be an ISO timestamp string")
    if expiration.strip().lower() in PERMANENT_EXPIRATIONS:
        raise ValueError("approval expiration must be scoped; permanent approval is not allowed")
    _parse_timestamp(expiration)


def validate_approval_record(record: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        raise ValueError(f"missing required approval record fields: {', '.join(missing)}")

    for field in REQUIRED_FIELDS:
        value = record[field]
        if field == "one_time_use":
            if not isinstance(value, bool):
                raise ValueError("approval record field one_time_use must be boolean")
        elif field in {"allowed_paths", "forbidden_paths"}:
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise ValueError(f"approval record field {field} must be a list of strings")
        elif value is None or value == "":
            raise ValueError(f"approval record field {field} is required")

    unknown = [field for field in record if field not in REQUIRED_FIELDS and field not in OPTIONAL_FIELDS]
    if unknown:
        raise ValueError(f"unsupported approval record fields: {', '.join(unknown)}")

    if record["status"] not in VALID_STATUSES:
        raise ValueError(f"unsupported approval status: {record['status']}")

    _validate_expiration(record["expiration"])

    if str(record["scope"]).strip().lower() in {"*", "all", "everything", "unbounded"}:
        raise ValueError("blanket approval scope is not allowed")

    if record["status"] == "granted":
        approved_by = str(record.get("approved_by") or "").strip().lower()
        if not approved_by or approved_by in MODEL_APPROVERS:
            raise ValueError("granted approvals require a human approver")


def approval_log_path(log_dir: Path | None = None, timestamp: str | None = None) -> Path:
    base_dir = Path(log_dir) if log_dir is not None else DEFAULT_APPROVAL_DIR
    stamp = timestamp or format_timestamp()
    date_part = stamp.split("T", 1)[0]
    return base_dir / f"approvals-{date_part}.jsonl"


def write_approval_record(record: dict[str, Any], log_dir: Path | None = None) -> dict[str, Any]:
    validate_approval_record(record)
    redacted_record, _ = redact_record(record)
    validate_approval_record(redacted_record)

    path = approval_log_path(log_dir=log_dir, timestamp=str(redacted_record["timestamp_requested"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        json.dump(redacted_record, handle, sort_keys=True)
        handle.write("\n")
    return redacted_record


def read_approval_records(log_dir: Path | None = None) -> list[dict[str, Any]]:
    base_dir = Path(log_dir) if log_dir is not None else DEFAULT_APPROVAL_DIR
    if not base_dir.exists():
        return []

    records: list[dict[str, Any]] = []
    for path in sorted(base_dir.glob("approvals-*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))
    return records


def is_approval_valid(record: dict[str, Any], now: datetime | str | None = None) -> bool:
    try:
        validate_approval_record(record)
    except (TypeError, ValueError):
        return False

    if record["status"] != "granted":
        return False

    current = _parse_timestamp(now or format_timestamp())
    expiration = _parse_timestamp(record["expiration"])
    return current < expiration


def mark_approval_used(record: dict[str, Any], log_dir: Path | None = None) -> dict[str, Any]:
    used_record = dict(record)
    used_record["status"] = "used"
    if log_dir is not None:
        return write_approval_record(used_record, log_dir=log_dir)
    validate_approval_record(used_record)
    return used_record

