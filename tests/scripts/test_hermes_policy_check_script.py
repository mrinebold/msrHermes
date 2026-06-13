import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_CHECK = REPO_ROOT / "scripts" / "hermes_policy_check.py"


class HermesPolicyCheckScriptTest(unittest.TestCase):
    def run_policy_check(self, *args):
        return subprocess.run(
            ["python3", str(POLICY_CHECK), *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_command_sudo_denied(self):
        result = self.run_policy_check("--command", "sudo whoami")

        self.assertEqual(result.returncode, 3)
        self.assertIn("classification=denied", result.stdout)
        self.assertIn("denied=yes", result.stdout)

    def test_command_git_status_allowed(self):
        result = self.run_policy_check("--command", "git status --short")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("classification=allowed_readonly", result.stdout)
        self.assertIn("approval_required=no", result.stdout)

    def test_command_adapter_start_requires_approval(self):
        result = self.run_policy_check("--command", "scripts/adapter_service_start.sh")

        self.assertEqual(result.returncode, 2)
        self.assertIn("classification=approval_required", result.stdout)
        self.assertIn("approval_required=yes", result.stdout)

    def test_path_outbox_write_allowed(self):
        result = self.run_policy_check("--path", "sandbox/hermes_outbox/example.md", "--operation", "write")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("classification=allowed", result.stdout)
        self.assertIn("zone=green", result.stdout)

    def test_path_secret_home_key_denied(self):
        result = self.run_policy_check("--path", "~/.ssh/id_rsa", "--operation", "read")

        self.assertEqual(result.returncode, 3)
        self.assertIn("classification=denied", result.stdout)
        self.assertIn("denied=yes", result.stdout)

    def test_path_docs_read_allowed_readonly(self):
        result = self.run_policy_check("--path", "docs/HERMES_COMMAND_POLICY.md", "--operation", "read")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("classification=allowed_readonly", result.stdout)
        self.assertIn("zone=yellow", result.stdout)

    def test_json_output_valid(self):
        result = self.run_policy_check("--command", "git status --short", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["classification"], "allowed_readonly")
        self.assertFalse(payload["approval_required"])

    def test_command_string_is_not_executed(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            marker = Path(temp_dir) / "policy_check_side_effect"
            result = self.run_policy_check("--command", f"touch {marker}")

            self.assertEqual(result.returncode, 3)
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
