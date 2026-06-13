#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="${HERMES_REPO_ROOT:-${CODE_ROOT}}"
INBOX_DIR="${REPO_ROOT}/sandbox/hermes_inbox"
OUTBOX_DIR="${REPO_ROOT}/sandbox/hermes_outbox"
FREEZE_FLAG="${REPO_ROOT}/sandbox/hermes_control/FROZEN"

echo "hermes_resident_dry_run=starting"
echo "repo_root=${REPO_ROOT}"
echo "mode=dry_run_only"
echo "command_execution=no"
echo "hermes_live_run=no"
echo "adapter_start=no"

if [[ -f "${FREEZE_FLAG}" ]]; then
  echo "freeze_flag_exists=yes"
  echo "dry_run_result=refused_frozen"
  echo "freeze_flag_path=${FREEZE_FLAG}"
  exit 0
fi

if [[ ! -d "${INBOX_DIR}" ]]; then
  echo "inbox_exists=no"
  echo "dry_run_result=no_inbox"
  exit 0
fi

mkdir -p "${OUTBOX_DIR}"

python3 - "${REPO_ROOT}" "${CODE_ROOT}" <<'PY'
from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(sys.argv[1]).resolve(strict=False)
code_root = Path(sys.argv[2]).resolve(strict=False)
sys.path.insert(0, str(code_root))

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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


for task in tasks:
    classification = classify_path(task, repo_root=repo_root, operation="read")
    task_name = task.name
    stem = task_name
    if stem.endswith(".task.md"):
        stem = stem[: -len(".task.md")]
    proposal = outbox / f"{stem}.dry_run.md"
    body = "\n".join(
        [
            "# Hermes Resident Dry-Run Proposal",
            "",
            f"task_file: {rel(task)}",
            f"file_zone: {classification['zone']}",
            f"file_decision: {classification['decision']}",
            f"file_policy_reason: {classification['reason']}",
            "would_run: no",
            "would_require_adapter: yes",
            "would_require_human_approval: yes",
            "policy_notes: dry-run only; task content redacted; no command execution; no live Hermes run; no adapter start; no archive action",
            "",
        ]
    )
    proposal.write_text(body, encoding="utf-8")
    proposal_count += 1
    print(f"proposal_written={rel(proposal)}")

audit_written = "no"
if build_audit_event is not None and write_audit_event is not None:
    try:
        event = build_audit_event(
            phase="6T",
            actor="codex",
            authority_tier="tier_0_observe",
            action_type="observe",
            target_type="local_inbox",
            target_identifier="sandbox/hermes_inbox",
            status="succeeded",
            risk_level="low",
            rollback_available=True,
            human_summary="Dry-run resident loop inspected inbox task names and wrote redacted proposal files.",
            machine_summary="dry_run_resident_loop_completed",
            metadata={"task_count": len(tasks), "proposal_count": proposal_count},
        )
        write_audit_event(event, log_dir=repo_root / "logs" / "hermes_audit")
        audit_written = "yes"
    except Exception as exc:  # pragma: no cover - defensive reporting only.
        print(f"audit_event_error={type(exc).__name__}")

print(f"tasks_seen={len(tasks)}")
print(f"proposals_written={proposal_count}")
print(f"audit_event_written={audit_written}")
print("dry_run_result=completed")
PY
