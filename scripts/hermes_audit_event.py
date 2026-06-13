#!/usr/bin/env python3
"""Create one harmless local Hermes audit event for visibility testing."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(os.environ.get("HERMES_REPO_ROOT", CODE_ROOT)).resolve(strict=False)
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from services.hermes_safety.audit_log import build_audit_event, looks_secret_value, write_audit_event


ALLOWED_ACTION_TYPES = {"observe", "recommend", "dry_run", "fail_closed", "emergency_stop"}
REFUSED_ACTION_TYPES = {"local_command_executed", "external_write", "resident_start"}
VALID_STATUSES = {"ok", "succeeded", "failed", "blocked", "refused", "fail_closed"}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a harmless local Hermes audit event")
    parser.add_argument("--action-type", required=True, choices=sorted(ALLOWED_ACTION_TYPES | REFUSED_ACTION_TYPES))
    parser.add_argument("--status", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--phase", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.action_type in REFUSED_ACTION_TYPES:
        print(f"refused_action_type={args.action_type}", file=sys.stderr)
        return 3
    if args.action_type not in ALLOWED_ACTION_TYPES:
        print("refused_action_type=unsupported", file=sys.stderr)
        return 3
    if args.status not in VALID_STATUSES:
        print("refused_status=unsupported", file=sys.stderr)
        return 3
    if looks_secret_value(args.summary):
        print("refused_summary=secret_like", file=sys.stderr)
        return 3

    event = build_audit_event(
        phase=args.phase,
        actor="human_operator",
        authority_tier="tier_0_observe",
        action_type=args.action_type,
        target_type="local_visibility_test",
        target_identifier="logs/hermes_audit",
        status=args.status,
        risk_level="low",
        rollback_available=True,
        human_summary=args.summary,
        machine_summary="audit_visibility_event_created",
        metadata={"helper": "scripts/hermes_audit_event.py"},
    )
    written = write_audit_event(event, log_dir=REPO_ROOT / "logs" / "hermes_audit")
    print(f"event_id={written['event_id']}")
    print(f"summary={written['human_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
