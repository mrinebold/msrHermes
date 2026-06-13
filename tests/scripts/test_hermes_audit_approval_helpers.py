import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_HELPER = REPO_ROOT / "scripts" / "hermes_audit_event.py"
APPROVAL_HELPER = REPO_ROOT / "scripts" / "hermes_approval_request.py"
LOCAL_STATUS = REPO_ROOT / "scripts" / "hermes_local_status.sh"


class HermesAuditApprovalHelpersTest(unittest.TestCase):
    def run_with_temp_root(self, command: list[str], temp_root: Path):
        env = os.environ.copy()
        env["HERMES_REPO_ROOT"] = str(temp_root)
        return subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_audit_helper_creates_local_event(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            result = self.run_with_temp_root(
                [
                    "python3",
                    str(AUDIT_HELPER),
                    "--action-type",
                    "dry_run",
                    "--status",
                    "ok",
                    "--summary",
                    "Visibility test",
                    "--phase",
                    "6V",
                ],
                Path(temp_dir),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("event_id=audit_", result.stdout)
            events = list((Path(temp_dir) / "logs" / "hermes_audit").glob("events-*.jsonl"))
            self.assertEqual(len(events), 1)
            record = json.loads(events[0].read_text(encoding="utf-8").strip())
            self.assertEqual(record["action_type"], "dry_run")
            self.assertEqual(record["status"], "ok")

    def test_audit_helper_refuses_executed_external_resident_actions(self):
        for action_type in ("local_command_executed", "external_write", "resident_start"):
            with self.subTest(action_type=action_type), tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
                result = self.run_with_temp_root(
                    [
                        "python3",
                        str(AUDIT_HELPER),
                        "--action-type",
                        action_type,
                        "--status",
                        "ok",
                        "--summary",
                        "Visibility test",
                        "--phase",
                        "6V",
                    ],
                    Path(temp_dir),
                )

                self.assertEqual(result.returncode, 3)
                self.assertFalse((Path(temp_dir) / "logs" / "hermes_audit").exists())

    def test_approval_helper_creates_requested_approval_only(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            result = self.run_with_temp_root(
                [
                    "python3",
                    str(APPROVAL_HELPER),
                    "--action-type",
                    "service_start",
                    "--target",
                    "adapter",
                    "--scope",
                    "manual-test",
                    "--summary",
                    "Visibility test",
                    "--risk-level",
                    "low",
                    "--expires-minutes",
                    "15",
                ],
                Path(temp_dir),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("approval_id=approval_", result.stdout)
            self.assertIn("status=requested", result.stdout)
            records = list((Path(temp_dir) / "logs" / "hermes_approvals").glob("approvals-*.jsonl"))
            self.assertEqual(len(records), 1)
            record = json.loads(records[0].read_text(encoding="utf-8").strip())
            self.assertEqual(record["status"], "requested")
            self.assertIsNone(record["approved_by"])

    def test_approval_helper_has_no_grant_option(self):
        content = APPROVAL_HELPER.read_text(encoding="utf-8")

        self.assertNotIn("--status", content)
        self.assertNotIn("status: granted", content)

    def test_helpers_do_not_execute_commands_or_print_secrets(self):
        for helper in (AUDIT_HELPER, APPROVAL_HELPER):
            with self.subTest(helper=helper.name):
                content = helper.read_text(encoding="utf-8")
                self.assertNotIn("subprocess", content)
                self.assertNotIn("os.system", content)
                self.assertNotIn("sudo", content)
                self.assertNotIn("sk-live-", content)
                self.assertNotIn("ghp_", content)

    def test_status_reports_latest_temp_audit_and_approval(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            temp_root = Path(temp_dir)
            self.run_with_temp_root(
                [
                    "python3",
                    str(AUDIT_HELPER),
                    "--action-type",
                    "dry_run",
                    "--status",
                    "ok",
                    "--summary",
                    "Visibility test",
                    "--phase",
                    "6V",
                ],
                temp_root,
            )
            self.run_with_temp_root(
                [
                    "python3",
                    str(APPROVAL_HELPER),
                    "--action-type",
                    "service_start",
                    "--target",
                    "adapter",
                    "--scope",
                    "manual-test",
                    "--summary",
                    "Visibility test",
                    "--risk-level",
                    "low",
                    "--expires-minutes",
                    "15",
                ],
                temp_root,
            )

            status = self.run_with_temp_root([str(LOCAL_STATUS)], temp_root)

            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertIn("latest_audit_action=dry_run", status.stdout)
            self.assertIn("latest_audit_status=ok", status.stdout)
            self.assertIn("latest_approval_action=service_start", status.stdout)
            self.assertIn("latest_approval_status=requested", status.stdout)


if __name__ == "__main__":
    unittest.main()
