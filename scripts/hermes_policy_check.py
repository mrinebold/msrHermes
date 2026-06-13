#!/usr/bin/env python3
"""Dry-run Hermes policy checker.

Classifies proposed commands or file operations only. It does not execute
commands, read target file contents, start services, or call external systems.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.hermes_safety.command_policy import classify_command
from services.hermes_safety.file_zones import classify_path


def bool_text(value: bool) -> str:
    return "yes" if value else "no"


def command_payload(command: str) -> dict[str, object]:
    result = classify_command(command, repo_root=REPO_ROOT)
    denied = result.classification in {"denied", "unknown"}
    return {
        "type": "command",
        "classification": result.classification,
        "reason": result.reason,
        "approval_required": result.approval_required,
        "denied": denied,
        "matched_rule": result.matched_rule,
    }


def path_payload(path: str, operation: str) -> dict[str, object]:
    result = classify_path(path, repo_root=REPO_ROOT, operation=operation)
    denied = result["decision"] in {"denied"} or result["zone"] in {"red", "unknown"}
    return {
        "type": "path",
        "classification": result["decision"],
        "zone": result["zone"],
        "reason": result["reason"],
        "approval_required": result["decision"] == "approval_required",
        "denied": denied,
        "matched_rule": result["zone"],
    }


def exit_code(payload: dict[str, object]) -> int:
    classification = str(payload["classification"])
    zone = str(payload.get("zone", ""))
    if classification in {"allowed_readonly", "allowed"} or (zone in {"green", "yellow"} and classification != "approval_required"):
        return 0
    if classification == "approval_required":
        return 2
    return 3


def print_text(payload: dict[str, object]) -> None:
    for key in ("type", "classification", "zone", "reason", "approval_required", "denied", "matched_rule"):
        if key not in payload:
            continue
        value = payload[key]
        if isinstance(value, bool):
            value = bool_text(value)
        print(f"{key}={value}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run Hermes policy checker")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--command", help="Command string to classify without execution")
    group.add_argument("--path", help="Path to classify without reading or writing")
    parser.add_argument("--operation", choices=("read", "write"), default="read")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args(argv)

    if args.command is not None:
        payload = command_payload(args.command)
    else:
        payload = path_payload(args.path, args.operation)

    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print_text(payload)
    return exit_code(payload)


if __name__ == "__main__":
    raise SystemExit(main())
