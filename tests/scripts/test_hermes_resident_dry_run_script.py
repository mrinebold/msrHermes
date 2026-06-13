import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DRY_RUN_SCRIPT = REPO_ROOT / "scripts" / "hermes_resident_dry_run.sh"


class HermesResidentDryRunScriptTest(unittest.TestCase):
    def run_dry_run(self, temp_root: Path):
        env = os.environ.copy()
        env["HERMES_REPO_ROOT"] = str(temp_root)
        return subprocess.run(
            [str(DRY_RUN_SCRIPT)],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_shell_syntax(self):
        result = subprocess.run(
            ["bash", "-n", str(DRY_RUN_SCRIPT)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_script_is_dry_run_only(self):
        content = DRY_RUN_SCRIPT.read_text(encoding="utf-8")

        self.assertNotIn("sudo", content)
        self.assertNotIn("adapter_service_start", content)
        self.assertNotIn("run_hermes_local_task", content)
        self.assertNotIn("hermes -z", content)
        self.assertNotIn("rm ", content)
        self.assertNotIn("mv ", content)
        self.assertIn("command_execution=no", content)
        self.assertIn("hermes_live_run=no", content)
        self.assertIn("adapter_start=no", content)
        self.assertIn("sandbox/hermes_inbox", content)
        self.assertIn("sandbox/hermes_outbox", content)

    def test_respects_freeze_flag(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            temp_root = Path(temp_dir)
            control = temp_root / "sandbox" / "hermes_control"
            control.mkdir(parents=True)
            (control / "FROZEN").write_text("frozen\n", encoding="utf-8")

            result = self.run_dry_run(temp_root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("dry_run_result=refused_frozen", result.stdout)
            self.assertFalse((temp_root / "sandbox" / "hermes_outbox").exists())

    def test_writes_redacted_dry_run_proposal_to_outbox(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            temp_root = Path(temp_dir)
            inbox = temp_root / "sandbox" / "hermes_inbox"
            inbox.mkdir(parents=True)
            task = inbox / "sample.task.md"
            task.write_text("This task body should not appear in the proposal.\n", encoding="utf-8")

            result = self.run_dry_run(temp_root)

            self.assertEqual(result.returncode, 0, result.stderr)
            proposal = temp_root / "sandbox" / "hermes_outbox" / "sample.dry_run.md"
            self.assertTrue(proposal.exists())
            body = proposal.read_text(encoding="utf-8")
            self.assertIn("would_run: no", body)
            self.assertIn("would_require_adapter: yes", body)
            self.assertIn("would_require_human_approval: yes", body)
            self.assertIn("task content redacted", body)
            self.assertNotIn("This task body should not appear", body)
            self.assertFalse((temp_root / "sandbox" / "hermes_archive").exists())
            self.assertIn("audit_event_written=yes", result.stdout)


if __name__ == "__main__":
    unittest.main()
