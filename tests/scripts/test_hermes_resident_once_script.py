import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RESIDENT_ONCE = REPO_ROOT / "scripts" / "hermes_resident_once.sh"
RESIDENT_STATUS = REPO_ROOT / "scripts" / "hermes_resident_status.sh"
LOCAL_STATUS = REPO_ROOT / "scripts" / "hermes_local_status.sh"


class HermesResidentOnceScriptTest(unittest.TestCase):
    def run_once(self, temp_root: Path):
        env = os.environ.copy()
        env["HERMES_REPO_ROOT"] = str(temp_root)
        return subprocess.run(
            [str(RESIDENT_ONCE)],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_shell_syntax(self):
        for script in (RESIDENT_ONCE, RESIDENT_STATUS):
            with self.subTest(script=script.name):
                result = subprocess.run(
                    ["bash", "-n", str(script)],
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0, result.stderr)

    def test_resident_once_script_guardrails(self):
        content = RESIDENT_ONCE.read_text(encoding="utf-8")

        self.assertNotIn("sudo", content)
        self.assertNotIn("adapter_service_start", content)
        self.assertNotIn("run_hermes_local_task", content)
        self.assertNotIn("hermes -z", content)
        self.assertNotIn("open -a", content)
        self.assertIn("command_execution=no", content)
        self.assertIn("external_integrations=no", content)
        self.assertIn("hermes_live_run=no", content)
        self.assertIn("desktop_launch=no", content)
        self.assertIn("sandbox/hermes_control/FROZEN", content)
        self.assertIn("write_audit_event", content)
        self.assertIn("classify_path", content)
        self.assertIn("classify_command", content)

    def test_resident_once_respects_freeze(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            temp_root = Path(temp_dir)
            control = temp_root / "sandbox" / "hermes_control"
            control.mkdir(parents=True)
            (control / "FROZEN").write_text("frozen\n", encoding="utf-8")

            result = self.run_once(temp_root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("resident_once_result=refused_frozen", result.stdout)
            self.assertFalse((temp_root / "sandbox" / "hermes_outbox").exists())

    def test_resident_once_writes_redacted_proposal_and_audit(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            temp_root = Path(temp_dir)
            inbox = temp_root / "sandbox" / "hermes_inbox"
            inbox.mkdir(parents=True)
            task = inbox / "sample.task.md"
            task.write_text(
                "Task content should stay redacted.\ncommand: sudo whoami\n",
                encoding="utf-8",
            )

            result = self.run_once(temp_root)

            self.assertEqual(result.returncode, 0, result.stderr)
            proposal = temp_root / "sandbox" / "hermes_outbox" / "sample.resident_once.md"
            self.assertTrue(proposal.exists())
            body = proposal.read_text(encoding="utf-8")
            self.assertIn("would_execute_commands: no", body)
            self.assertIn("would_start_adapter: no", body)
            self.assertIn("would_run_hermes_live: no", body)
            self.assertIn("would_launch_desktop: no", body)
            self.assertIn("classification: denied", body)
            self.assertNotIn("sudo whoami", body)
            self.assertNotIn("Task content should stay redacted", body)
            self.assertIn("resident_once_result=fail_closed", result.stdout)
            self.assertTrue((temp_root / "logs" / "hermes_audit").exists())
            self.assertFalse((temp_root / "sandbox" / "hermes_archive").exists())

    def test_status_scripts_report_resident_and_desktop_governance(self):
        for script in (LOCAL_STATUS, RESIDENT_STATUS):
            with self.subTest(script=script.name):
                result = subprocess.run(
                    [str(script)],
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("command_execution_enabled=no", result.stdout)
                self.assertIn("external_integrations_enabled=no", result.stdout)

        local_status = subprocess.run(
            [str(LOCAL_STATUS)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        ).stdout
        self.assertIn("resident_once_script_exists=", local_status)
        self.assertIn("resident_once_launchagent_installed=", local_status)
        self.assertIn("desktop_installed=", local_status)
        self.assertIn("desktop_verified=", local_status)
        self.assertIn("desktop_running=", local_status)


if __name__ == "__main__":
    unittest.main()
