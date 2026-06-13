import unittest

from services.hermes_safety.command_policy import classify_command


class HermesCommandPolicyTest(unittest.TestCase):
    def assertClassification(self, command, expected):
        result = classify_command(command)
        self.assertEqual(result.classification, expected, result)
        return result

    def test_denies_forbidden_commands(self):
        cases = (
            "sudo ls",
            "rm -rf sandbox/output",
            "git push --force",
            "git reset --hard",
            "git clean -fdx",
            "chmod 777 sandbox/output",
            "chown user sandbox/output",
            "security find-generic-password",
            "osascript -e 'tell app \"Finder\" to activate'",
            "ssh example.com",
            "scp a b",
            "rsync a b",
            "brew install example",
            "pip install example",
            "npm install example",
            "open -a /Applications/Hermes.app",
        )
        for command in cases:
            with self.subTest(command=command):
                self.assertClassification(command, "denied")

    def test_allows_readonly_status_commands(self):
        cases = (
            "pwd",
            "git status --short",
            "git branch --show-current",
            "git log --oneline -n 5",
            "git diff --check",
            "python3 -m unittest discover",
            "bash -n scripts/run_model_router_adapter.sh",
            "scripts/hermes_local_status.sh",
            "scripts/adapter_service_status.sh",
        )
        for command in cases:
            with self.subTest(command=command):
                result = self.assertClassification(command, "allowed_readonly")
                self.assertTrue(result.allowed)
                self.assertFalse(result.approval_required)

    def test_requires_approval_for_sensitive_allowed_operations(self):
        cases = (
            "scripts/adapter_service_start.sh",
            ["git", "commit", "-m", "Test"],
            "git push origin main",
            "mkdir -p sandbox/hermes_outbox/new",
            "cp sandbox/hermes_outbox/a sandbox/hermes_archive/a",
            "mv sandbox/hermes_inbox/a sandbox/hermes_archive/a",
        )
        for command in cases:
            with self.subTest(command=command):
                result = self.assertClassification(command, "approval_required")
                self.assertFalse(result.allowed)
                self.assertTrue(result.approval_required)

    def test_curl_classification(self):
        self.assertClassification("curl http://example.com", "denied")
        self.assertClassification("curl --max-time 10 http://127.0.0.1:8088/health", "allowed_readonly")
        self.assertClassification("curl http://127.0.0.1:8088/v1/models", "allowed_readonly")

    def test_secret_path_and_unknown_commands_fail_closed(self):
        self.assertClassification("cat ~/.ssh/token", "denied")
        self.assertClassification("cat sandbox/hermes_inbox/.env", "denied")

        result = self.assertClassification("unknown-tool --do-work", "unknown")
        self.assertFalse(result.allowed)
        self.assertFalse(result.approval_required)

    def test_ambiguous_shell_syntax_fails_closed(self):
        result = self.assertClassification("git status --short && git push origin main", "unknown")
        self.assertFalse(result.allowed)
        self.assertIn("ambiguous", result.reason)

    def test_classifier_does_not_execute_commands(self):
        result = classify_command("echo should-not-run")

        self.assertEqual(result.classification, "unknown")
        self.assertFalse(result.allowed)


if __name__ == "__main__":
    unittest.main()
