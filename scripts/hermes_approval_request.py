#!/usr/bin/env python3
"""Create one requested-only local Hermes approval record for visibility testing."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import timedelta
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(os.environ.get("HERMES_REPO_ROOT", CODE_ROOT)).resolve(strict=False)
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from services.hermes_safety.approval_records import create_approval_request, write_approval_record
from services.hermes_safety.audit_log import format_timestamp, looks_secret_value, utc_now


SENSITIVE_ACTION_TYPES = {
    "local_read",
    "local_write",
    "service_start",
    "service_stop",
    "command_execute",
    "git_commit",
    "git_push",
    "external_read",
    "external_draft",
    "external_write",
    "resident_start",
    "resident_stop",
    "emergency_stop",
}
VALID_RISK_LEVELS = {"low", "medium", "high"}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a requested-only local Hermes approval record")
    parser.add_argument("--action-type", required=True, choices=sorted(SENSITIVE_ACTION_TYPES))
    parser.add_argument("--target", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--risk-level", default="low", choices=sorted(VALID_RISK_LEVELS))
    parser.add_argument("--expires-minutes", type=int, default=15)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    for label, value in (("target", args.target), ("scope", args.scope), ("summary", args.summary)):
        if looks_secret_value(value):
            print(f"refused_{label}=secret_like", file=sys.stderr)
            return 3
    if args.expires_minutes < 1 or args.expires_minutes > 1440:
        print("refused_expiration=out_of_range", file=sys.stderr)
        return 3

    expiration = format_timestamp(utc_now() + timedelta(minutes=args.expires_minutes))
    record = create_approval_request(
        requested_by="human_operator",
        authority_tier="tier_3_local_approved_execution",
        action_type=args.action_type,
        target=args.target,
        scope=args.scope,
        exact_command_or_operation=f"request:{args.action_type}:{args.target}",
        allowed_paths=[],
        forbidden_paths=["secret-like paths", "external integrations", "Hermes Desktop"],
        expiration=expiration,
        one_time_use=True,
        risk_level=args.risk_level,
        rollback_plan="No action executed; requested-only visibility record can expire without rollback.",
        human_summary=args.summary,
    )
    written = write_approval_record(record, log_dir=REPO_ROOT / "logs" / "hermes_approvals")
    print(f"approval_id={written['approval_id']}")
    print(f"status={written['status']}")
    print(f"summary={written['human_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
