import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_NETWORK_DOC = REPO_ROOT / "docs" / "HERMES_PRIVATE_NETWORK_ACCESS.md"
SSH_ACCESS_DOC = REPO_ROOT / "docs" / "HERMES_SSH_ACCESS_MODEL.md"
ENDPOINT_ACCESS_DOC = REPO_ROOT / "docs" / "HERMES_ENDPOINT_ACCESS_MODEL.md"
OUTBOUND_ACCESS_DOC = REPO_ROOT / "docs" / "HERMES_OUTBOUND_NODE_ACCESS.md"
REMOTE_IPAD_DOC = REPO_ROOT / "docs" / "HERMES_REMOTE_IPAD_ACCESS.md"
SSH_STATUS = REPO_ROOT / "scripts" / "ssh_access_status.sh"
INSTALL_KEY = REPO_ROOT / "scripts" / "install_approved_ssh_key.sh"
REMOTE_SETUP = REPO_ROOT / "scripts" / "generate_remote_ssh_setup_instructions.py"
OUTBOUND_CONFIG = REPO_ROOT / "scripts" / "generate_macmini_outbound_ssh_config.py"
TUNNEL_EXAMPLES = REPO_ROOT / "scripts" / "hermes_endpoint_tunnel_examples.sh"
REMOTE_IPAD_INSTRUCTIONS = REPO_ROOT / "scripts" / "remote_ipad_access_instructions.sh"
LOCAL_STATUS = REPO_ROOT / "scripts" / "hermes_local_status.sh"


class HermesPrivateRemoteAccessTest(unittest.TestCase):
    def test_access_docs_exist_and_preserve_private_boundaries(self):
        for path in (
            PRIVATE_NETWORK_DOC,
            SSH_ACCESS_DOC,
            ENDPOINT_ACCESS_DOC,
            OUTBOUND_ACCESS_DOC,
            REMOTE_IPAD_DOC,
        ):
            with self.subTest(path=path.name):
                self.assertTrue(path.exists())

        endpoint = ENDPOINT_ACCESS_DOC.read_text(encoding="utf-8")
        remote = REMOTE_IPAD_DOC.read_text(encoding="utf-8")
        combined = "\n".join([endpoint, remote])

        self.assertIn("adapter remains localhost-only", combined)
        self.assertIn("SSH Tunnel", combined)
        self.assertIn("127.0.0.1:8088", combined)
        self.assertIn("public internet exposure", combined)
        self.assertIn("Tailscale Funnel", combined)
        self.assertIn("not approved", combined)
        self.assertIn("iPad SSH Workflow", remote)
        self.assertIn("Tailscale-only", remote)
        self.assertIn("Future Tailscale-Only Gateway", remote)

    def test_remote_ipad_instruction_script_is_read_only_text(self):
        content = REMOTE_IPAD_INSTRUCTIONS.read_text(encoding="utf-8")

        self.assertNotIn("sudo", content)
        self.assertNotIn("adapter_service_start", content)
        self.assertNotIn("launchctl", content)
        self.assertIn("no public internet exposure", content)
        self.assertIn("no Tailscale Funnel", content)

        result = subprocess.run(
            ["bash", str(REMOTE_IPAD_INSTRUCTIONS)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Hermes remote and iPad access is Tailscale SSH only", result.stdout)
        self.assertIn("ssh -N -L 18088:127.0.0.1:8088 macmini-hermes", result.stdout)

    def test_install_approved_ssh_key_refuses_private_keys(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            temp_path = Path(temp_dir)
            ssh_home = temp_path / "ssh-home"
            private_key = temp_path / "remote_key.pub"
            private_key.write_text(
                "-----BEGIN OPENSSH PRIVATE KEY-----\nredacted\n-----END OPENSSH PRIVATE KEY-----\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["HERMES_SSH_HOME"] = str(ssh_home)

            result = subprocess.run(
                [
                    "bash",
                    str(INSTALL_KEY),
                    "--name",
                    "civic-dev",
                    "--pubkey-file",
                    str(private_key),
                ],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing_private_key_file", result.stderr)

    def test_install_approved_ssh_key_validates_public_key_format_and_writes_temp_home(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            temp_path = Path(temp_dir)
            ssh_home = temp_path / "ssh-home"
            public_key = temp_path / "remote_key.pub"
            key_material = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMockKeyForHermesAccessOnly1234567890abc"
            public_key.write_text(f"{key_material} civic-main-to-macmini-hermes\n", encoding="utf-8")
            env = os.environ.copy()
            env["HERMES_SSH_HOME"] = str(ssh_home)

            result = subprocess.run(
                [
                    "bash",
                    str(INSTALL_KEY),
                    "--name",
                    "civic-main",
                    "--pubkey-file",
                    str(public_key),
                ],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=installed", result.stdout)
            self.assertNotIn("AAAAC3NzaC1lZDI1NTE5", result.stdout)
            authorized = ssh_home / "authorized_keys"
            self.assertTrue(authorized.exists())
            content = authorized.read_text(encoding="utf-8")
            self.assertIn("# hermes-access civic-main", content)
            self.assertIn(key_material, content)

            duplicate = subprocess.run(
                [
                    "bash",
                    str(INSTALL_KEY),
                    "--name",
                    "civic-main",
                    "--pubkey-file",
                    str(public_key),
                ],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(duplicate.returncode, 0, duplicate.stderr)
            self.assertIn("status=already_present", duplicate.stdout)

    def test_ssh_status_does_not_print_authorized_keys_contents(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            ssh_home = Path(temp_dir) / "ssh-home"
            ssh_home.mkdir()
            key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAITestStatusKeyShouldNotPrint"
            (ssh_home / "authorized_keys").write_text(f"{key} status-test\n", encoding="utf-8")
            env = os.environ.copy()
            env["HERMES_SSH_HOME"] = str(ssh_home)

            result = subprocess.run(
                ["bash", str(SSH_STATUS)],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("authorized_keys_line_count=1", result.stdout)
            self.assertIn("public_exposure_detected=", result.stdout)
            self.assertNotIn("AAAAC3NzaC1lZDI1NTE5", result.stdout)
            self.assertNotIn("status-test", result.stdout)

    def test_tunnel_examples_default_to_dry_run(self):
        content = TUNNEL_EXAMPLES.read_text(encoding="utf-8")
        self.assertNotIn("sudo", content)
        self.assertIn("--run", content)
        self.assertIn("HERMES_TUNNEL_CONFIRM=RUN", content)

        result = subprocess.run(
            ["bash", str(TUNNEL_EXAMPLES)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ssh -N -L 18088:127.0.0.1:8088 macmini-hermes", result.stdout)
        self.assertIn("no 0.0.0.0 bind", result.stdout)

    def test_generators_print_instructions_without_writing_files(self):
        remote = subprocess.run(
            ["python3", str(REMOTE_SETUP)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(remote.returncode, 0, remote.stderr)
        self.assertIn("DevMonster", remote.stdout)
        self.assertIn("civic-main", remote.stdout)
        self.assertIn("civic-dev", remote.stdout)
        self.assertIn("ssh-keygen -t ed25519", remote.stdout)
        self.assertIn("Do not copy private keys", remote.stdout)

        outbound = subprocess.run(
            ["python3", str(OUTBOUND_CONFIG)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(outbound.returncode, 0, outbound.stderr)
        self.assertIn("This script prints only. It does not modify ~/.ssh/config.", outbound.stdout)
        self.assertIn("devmonster-4.taila2da57.ts.net", outbound.stdout)

    def test_local_status_reports_remote_readiness_without_secrets(self):
        content = LOCAL_STATUS.read_text(encoding="utf-8")
        self.assertIn("tailscale_command_available", content)
        self.assertIn("ssh_listener_22", content)
        self.assertIn("adapter_direct_public_exposure", content)
        self.assertIn("ipad_access_mode", content)
        self.assertIn("endpoint_remote_mode", content)
        self.assertNotIn("authorized_keys |", content)
        self.assertNotIn("cat ~/.ssh/authorized_keys", content)

    def test_new_private_remote_surfaces_have_no_private_keys_or_tokens(self):
        disallowed = (
            "BEGIN OPENSSH PRIVATE KEY",
            "BEGIN RSA PRIVATE KEY",
            "sk-live-",
            "sk-proj-",
            "sk-ant-",
            "xoxb-",
            "ghp_",
            "github_pat_",
        )
        for path in (
            PRIVATE_NETWORK_DOC,
            SSH_ACCESS_DOC,
            ENDPOINT_ACCESS_DOC,
            OUTBOUND_ACCESS_DOC,
            REMOTE_IPAD_DOC,
            SSH_STATUS,
            INSTALL_KEY,
            REMOTE_SETUP,
            OUTBOUND_CONFIG,
            TUNNEL_EXAMPLES,
            REMOTE_IPAD_INSTRUCTIONS,
        ):
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                for marker in disallowed:
                    self.assertNotIn(marker, content)


if __name__ == "__main__":
    unittest.main()
