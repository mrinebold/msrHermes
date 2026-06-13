import tempfile
import unittest
from pathlib import Path

from services.hermes_safety.file_zones import classify_path, is_secret_like_path, normalize_path


class HermesFileZonesTest(unittest.TestCase):
    def test_green_zone_read_write_allowed(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            root = Path(temp_dir)
            path = root / "sandbox" / "hermes_outbox" / "task.out.md"

            self.assertEqual(classify_path(path, repo_root=root, operation="read")["decision"], "allowed")
            self.assertEqual(classify_path(path, repo_root=root, operation="write")["decision"], "allowed")

    def test_yellow_zone_read_allowed_write_requires_approval(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            root = Path(temp_dir)
            path = root / "docs" / "HERMES.md"

            read_result = classify_path(path, repo_root=root, operation="read")
            write_result = classify_path(path, repo_root=root, operation="write")

            self.assertEqual(read_result["zone"], "yellow")
            self.assertEqual(read_result["decision"], "allowed_readonly")
            self.assertEqual(write_result["zone"], "orange")
            self.assertEqual(write_result["decision"], "approval_required")

    def test_orange_launchagent_path_requires_approval(self):
        path = Path.home() / "Library" / "LaunchAgents" / "com.msr.hermes.model-router-adapter.plist"
        result = classify_path(path, operation="write")

        self.assertEqual(result["zone"], "orange")
        self.assertEqual(result["decision"], "approval_required")

    def test_red_forbidden_secret_paths_denied(self):
        for path in (Path.home() / ".ssh" / "id_rsa", Path.home() / ".gnupg" / "private.key"):
            with self.subTest(path=path):
                result = classify_path(path, operation="read")
                self.assertEqual(result["zone"], "red")
                self.assertEqual(result["decision"], "denied")

    def test_path_traversal_denied(self):
        result = classify_path("sandbox/hermes_inbox/../secret.txt", operation="read")

        self.assertEqual(result["zone"], "red")
        self.assertEqual(result["decision"], "denied")
        self.assertIn("traversal", result["reason"])

    def test_symlink_to_forbidden_zone_denied(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            root = Path(temp_dir)
            link = root / "sandbox" / "hermes_inbox" / "ssh_link"
            link.parent.mkdir(parents=True)
            link.symlink_to(Path.home() / ".ssh")

            result = classify_path(link, repo_root=root, operation="read")

            self.assertEqual(result["zone"], "red")
            self.assertEqual(result["decision"], "denied")

    def test_secret_like_filename_denied(self):
        self.assertTrue(is_secret_like_path("sandbox/hermes_inbox/.env"))
        result = classify_path("sandbox/hermes_inbox/google_token.txt", operation="read")

        self.assertEqual(result["zone"], "red")
        self.assertEqual(result["decision"], "denied")

    def test_arbitrary_desktop_documents_and_unknown_paths_fail_closed(self):
        desktop_result = classify_path(Path.home() / "Desktop" / "notes.md", operation="read")
        unknown_result = classify_path("/private/tmp/unapproved-file.txt", operation="read")

        self.assertEqual(desktop_result["decision"], "denied")
        self.assertEqual(desktop_result["zone"], "red")
        self.assertEqual(unknown_result["decision"], "denied")
        self.assertEqual(unknown_result["zone"], "unknown")

    def test_normalize_path_does_not_write_or_require_existing_file(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            root = Path(temp_dir)
            normalized = normalize_path("sandbox/output/missing.out", repo_root=root)

            self.assertEqual(normalized, root / "sandbox" / "output" / "missing.out")
            self.assertFalse(normalized.exists())


if __name__ == "__main__":
    unittest.main()
