#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_CODE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CODE_ROOT="${HERMES_CODE_ROOT:-${DEFAULT_CODE_ROOT}}"
REPO_ROOT="${HERMES_REPO_ROOT:-${CODE_ROOT}}"
INBOX_DIR="${REPO_ROOT}/sandbox/hermes_inbox"
OUTBOX_DIR="${REPO_ROOT}/sandbox/hermes_outbox"
FREEZE_FLAG="${REPO_ROOT}/sandbox/hermes_control/FROZEN"

echo "hermes_resident_once=starting"
echo "repo_root=${REPO_ROOT}"
echo "mode=observe_recommend_dry_run"
echo "command_execution=no"
echo "external_integrations=no"
echo "hermes_live_run=no"
echo "adapter_start=no"
echo "desktop_launch=no"

if [[ -f "${FREEZE_FLAG}" ]]; then
  echo "freeze_flag_exists=yes"
  echo "resident_once_result=refused_frozen"
  echo "freeze_flag_path=${FREEZE_FLAG}"
  exit 0
fi

if [[ ! -d "${INBOX_DIR}" ]]; then
  echo "inbox_exists=no"
  echo "resident_once_result=no_inbox"
  exit 0
fi

mkdir -p "${OUTBOX_DIR}"

python3 - "${REPO_ROOT}" "${CODE_ROOT}" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

repo_root = Path(sys.argv[1]).resolve(strict=False)
code_root = Path(sys.argv[2]).resolve(strict=False)
sys.path.insert(0, str(code_root))

from services.hermes_safety.command_policy import classify_command
from services.hermes_safety.file_zones import classify_path

try:
    from services.hermes_safety.audit_log import build_audit_event, write_audit_event
except Exception:  # pragma: no cover - shell script reports this path.
    build_audit_event = None
    write_audit_event = None

inbox = repo_root / "sandbox" / "hermes_inbox"
outbox = repo_root / "sandbox" / "hermes_outbox"
tasks = sorted(path for path in inbox.glob("*.task.md") if path.is_file())
proposal_count = 0
blocked_count = 0
command_pattern = re.compile(r"^\s*(?:command|proposed_command)\s*:\s*(.+?)\s*$", re.IGNORECASE)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def extract_proposed_commands(path: Path) -> list[str]:
    commands: list[str] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                match = command_pattern.match(line)
                if match:
                    commands.append(match.group(1)[:300])
                if len(commands) >= 20:
                    break
    except OSError:
        commands.append("[unreadable task command metadata]")
    return commands


for task in tasks:
    classification = classify_path(task, repo_root=repo_root, operation="read")
    if classification["decision"] not in {"allowed", "allowed_readonly"}:
        blocked_count += 1
        print(f"task_blocked={rel(task)}")
        print(f"task_block_reason={classification['reason']}")
        continue

    stem = task.name
    if stem.endswith(".task.md"):
        stem = stem[: -len(".task.md")]
    proposal = outbox / f"{stem}.resident_once.md"

    proposed_commands = extract_proposed_commands(task)
    command_lines: list[str] = []
    command_policy_denied = 0
    command_policy_approval = 0
    if proposed_commands:
        command_lines.append("## Proposed Command Classifications")
        command_lines.append("")
    for index, command in enumerate(proposed_commands, start=1):
        result = classify_command(command, repo_root=repo_root)
        if result.classification in {"denied", "unknown"}:
            command_policy_denied += 1
        if result.approval_required:
            command_policy_approval += 1
        command_lines.extend(
            [
                f"- proposed_command_{index}: redacted_command_metadata_only",
                f"  classification: {result.classification}",
                f"  reason: {result.reason}",
                f"  approval_required: {'yes' if result.approval_required else 'no'}",
                f"  matched_rule: {result.matched_rule or 'none'}",
            ]
        )

    if command_policy_denied:
        blocked_count += command_policy_denied

    body = "\n".join(
        [
            "# Hermes Resident Once Proposal",
            "",
            f"task_file: {rel(task)}",
            f"file_zone: {classification['zone']}",
            f"file_decision: {classification['decision']}",
            f"file_policy_reason: {classification['reason']}",
            "would_run: no",
            "would_execute_commands: no",
            "would_start_adapter: no",
            "would_run_hermes_live: no",
            "would_launch_desktop: no",
            "would_touch_external_integrations: no",
            f"proposed_command_count: {len(proposed_commands)}",
            f"proposed_command_policy_denied_or_unknown: {command_policy_denied}",
            f"proposed_command_policy_approval_required: {command_policy_approval}",
            "policy_notes: governed resident shell; observe/recommend/dry-run only; task content redacted; no archive action",
            "",
            *command_lines,
            "",
        ]
    )
    proposal.write_text(body, encoding="utf-8")
    proposal_count += 1
    print(f"proposal_written={rel(proposal)}")

audit_written = "no"
status = "succeeded" if blocked_count == 0 else "fail_closed"
risk_level = "low" if blocked_count == 0 else "medium"
if build_audit_event is not None and write_audit_event is not None:
    try:
        event = build_audit_event(
            phase="7A",
            actor="hermes_resident_once",
            authority_tier="tier_1_recommend",
            action_type="dry_run",
            target_type="local_inbox",
            target_identifier="sandbox/hermes_inbox",
            status=status,
            risk_level=risk_level,
            rollback_available=True,
            human_summary="Resident once shell inspected approved inbox task metadata and wrote redacted dry-run proposals.",
            machine_summary="resident_once_completed",
            metadata={"task_count": len(tasks), "proposal_count": proposal_count, "blocked_count": blocked_count},
        )
        write_audit_event(event, log_dir=repo_root / "logs" / "hermes_audit")
        audit_written = "yes"
    except Exception as exc:  # pragma: no cover - defensive reporting only.
        print(f"audit_event_error={type(exc).__name__}")

print(f"tasks_seen={len(tasks)}")
print(f"proposals_written={proposal_count}")
print(f"policy_blocks={blocked_count}")
print(f"audit_event_written={audit_written}")
print(f"resident_once_result={status}")
PY
