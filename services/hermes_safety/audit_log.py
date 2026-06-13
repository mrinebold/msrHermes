"""Local append-only audit log primitive for Hermes safety events."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOG_DIR = REPO_ROOT / "logs" / "hermes_audit"

REQUIRED_FIELDS = (
    "timestamp",
    "event_id",
    "phase",
    "actor",
    "authority_tier",
    "action_type",
    "target_type",
    "target_identifier",
    "status",
    "risk_level",
    "redaction_applied",
    "rollback_available",
    "human_summary",
    "machine_summary",
)

OPTIONAL_FIELDS = ("approval_id", "artifact_hash", "metadata")

SECRET_KEY_RE = re.compile(
    r"(api[_-]?key|token|secret|credential|private|password|authorization|"
    r"service[_-]?role|client[_-]?secret)",
    re.IGNORECASE,
)
SECRET_VALUE_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_\-]{8,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9_]{8,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{8,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{8,}\b", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_timestamp(value: datetime | None = None) -> str:
    current = value or utc_now()
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_event_id(timestamp: str | None = None) -> str:
    stamp = timestamp or format_timestamp()
    compact_stamp = stamp.replace("-", "").replace(":", "").replace("Z", "Z")
    return f"audit_{compact_stamp}_{uuid.uuid4().hex[:8]}"


def looks_secret_key(key: str) -> bool:
    return bool(SECRET_KEY_RE.search(key))


def looks_secret_value(value: str) -> bool:
    return any(pattern.search(value) for pattern in SECRET_VALUE_PATTERNS)


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

    if isinstance(value, tuple):
        redacted_tuple = []
        changed = False
        for item in value:
            redacted_item, item_changed = _redact_value(item)
            redacted_tuple.append(redacted_item)
            changed = changed or item_changed
        return redacted_tuple, changed

    if isinstance(value, str) and looks_secret_value(value):
        return "[REDACTED]", True

    return value, False


def redact_event(event: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Return a redacted copy of an event and whether redaction changed it."""

    redacted, changed = _redact_value(dict(event))
    if not isinstance(redacted, dict):
        raise TypeError("audit event must redact to a dict")
    if changed:
        redacted["redaction_applied"] = True
    return redacted, changed


def build_audit_event(
    *,
    phase: str,
    actor: str,
    authority_tier: str,
    action_type: str,
    target_type: str,
    target_identifier: str,
    status: str,
    risk_level: str,
    rollback_available: bool,
    human_summary: str,
    machine_summary: str,
    approval_id: str | None = None,
    artifact_hash: str | None = None,
    metadata: dict[str, Any] | None = None,
    timestamp: str | None = None,
    event_id: str | None = None,
) -> dict[str, Any]:
    event_timestamp = timestamp or format_timestamp()
    event = {
        "timestamp": event_timestamp,
        "event_id": event_id or build_event_id(event_timestamp),
        "phase": phase,
        "actor": actor,
        "authority_tier": authority_tier,
        "action_type": action_type,
        "target_type": target_type,
        "target_identifier": target_identifier,
        "approval_id": approval_id,
        "status": status,
        "risk_level": risk_level,
        "redaction_applied": False,
        "rollback_available": rollback_available,
        "human_summary": human_summary,
        "machine_summary": machine_summary,
        "artifact_hash": artifact_hash,
        "metadata": metadata or {},
    }
    return event


def validate_audit_event(event: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in event]
    if missing:
        raise ValueError(f"missing required audit event fields: {', '.join(missing)}")

    for field in REQUIRED_FIELDS:
        value = event[field]
        if field in {"redaction_applied", "rollback_available"}:
            if not isinstance(value, bool):
                raise ValueError(f"audit event field {field} must be boolean")
        elif value is None or value == "":
            raise ValueError(f"audit event field {field} is required")

    for key in event:
        if key not in REQUIRED_FIELDS and key not in OPTIONAL_FIELDS:
            raise ValueError(f"unsupported audit event field: {key}")


def audit_log_path(log_dir: Path | None = None, timestamp: str | None = None) -> Path:
    base_dir = Path(log_dir) if log_dir is not None else DEFAULT_LOG_DIR
    stamp = timestamp or format_timestamp()
    date_part = stamp.split("T", 1)[0]
    return base_dir / f"events-{date_part}.jsonl"


def write_audit_event(event: dict[str, Any], log_dir: Path | None = None) -> dict[str, Any]:
    """Validate, redact, and append an audit event to local JSONL storage."""

    validate_audit_event(event)
    redacted_event, _ = redact_event(event)
    validate_audit_event(redacted_event)

    path = audit_log_path(log_dir=log_dir, timestamp=str(redacted_event["timestamp"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        json.dump(redacted_event, handle, sort_keys=True)
        handle.write("\n")
    return redacted_event

