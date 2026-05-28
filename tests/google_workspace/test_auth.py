import tempfile
import unittest
from pathlib import Path

from services.google_workspace.audit import GoogleAuditEvent, write_audit_event
from services.google_workspace.auth import GoogleWorkspaceAuth
from services.google_workspace.config import GoogleWorkspaceConfig


class GoogleWorkspaceAuthTest(unittest.TestCase):
    def test_missing_credentials_fail_closed(self):
        config = GoogleWorkspaceConfig(
            client_secret_file="",
            token_file="",
            oauth_scopes=(),
            audit_log="logs/google_workspace_audit.jsonl",
        )
        result = GoogleWorkspaceAuth(config).check_ready()

        self.assertFalse(result.ok)
        self.assertEqual(result.status, "not_ready")
        self.assertIn("GOOGLE_CLIENT_SECRET_FILE", result.error)
        self.assertIn("GOOGLE_TOKEN_FILE", result.error)
        self.assertIn("GOOGLE_OAUTH_SCOPES", result.error)

    def test_authenticate_is_disabled_even_with_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            client_secret = Path(tmp) / "client_secret.json"
            client_secret.write_text("{}", encoding="utf-8")
            config = GoogleWorkspaceConfig(
                client_secret_file=str(client_secret),
                token_file=str(Path(tmp) / "token.json"),
                oauth_scopes=("scope-a",),
                audit_log=str(Path(tmp) / "audit.jsonl"),
            )

            result = GoogleWorkspaceAuth(config).authenticate()

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "disabled")

    def test_audit_log_writes_expected_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit_path = Path(tmp) / "google_audit.jsonl"
            event = GoogleAuditEvent(
                action="check_ready",
                permission_tier="Read",
                target_service="Gmail",
                status="dry_run",
                details={"phase": "4B"},
            )

            write_audit_event(audit_path, event)

            line = audit_path.read_text(encoding="utf-8").strip()
            self.assertIn('"action": "check_ready"', line)
            self.assertIn('"permission_tier": "Read"', line)
            self.assertIn('"target_service": "Gmail"', line)
            self.assertIn('"status": "dry_run"', line)
            self.assertIn('"timestamp":', line)


if __name__ == "__main__":
    unittest.main()
