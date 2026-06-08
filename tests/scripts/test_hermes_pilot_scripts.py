import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_RUNNER = REPO_ROOT / "scripts" / "run_model_router_adapter.sh"
PILOT_RUNNER = REPO_ROOT / "scripts" / "run_hermes_pilot.sh"
PILOT_PROMPT_BUILDER = REPO_ROOT / "scripts" / "build_hermes_pilot_context_prompt.py"
PILOT_ENV = REPO_ROOT / "config" / "hermes-pilot.example.env"


class HermesPilotScriptsTest(unittest.TestCase):
    def test_shell_scripts_pass_syntax_check(self):
        for script in (ADAPTER_RUNNER, PILOT_RUNNER):
            with self.subTest(script=script.name):
                result = subprocess.run(
                    ["bash", "-n", str(script)],
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0, result.stderr)

    def test_pilot_prompt_builder_creates_explicit_local_context_prompt(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            output = Path(temp_dir) / "phase5ae_prompt.md"
            result = subprocess.run(
                ["python3", str(PILOT_PROMPT_BUILDER), "--output", str(output)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            prompt = output.read_text(encoding="utf-8")
            self.assertIn("Document/context:", prompt)
            self.assertIn("## Master PRD excerpt", prompt)
            self.assertIn("## Changelog excerpt", prompt)
            self.assertIn("Return only recommendation text", prompt)
            self.assertIn("Phase 5AD", prompt)
            self.assertNotIn("Read these local repo documents only", prompt)
            self.assertNotIn("Task:", prompt)

    def test_adapter_runner_refuses_non_localhost_bind(self):
        env = os.environ.copy()
        env["MODEL_ROUTER_ADAPTER_HOST"] = "0.0.0.0"
        result = subprocess.run(
            ["bash", str(ADAPTER_RUNNER), "--dry-run"],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to bind", result.stderr)

    def test_adapter_runner_dry_run_uses_pilot_defaults(self):
        result = subprocess.run(
            ["bash", str(ADAPTER_RUNNER), "--dry-run"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("host=127.0.0.1", result.stdout)
        self.assertIn("port=8088", result.stdout)
        self.assertIn("gemma_prompt_mode=instruction_context", result.stdout)
        self.assertIn("prompt_text_logging=disabled", result.stdout)
        self.assertIn("file_content_logging=disabled", result.stdout)
        self.assertNotIn("OPENAI_API_KEY", result.stdout)

    def test_pilot_config_points_only_to_localhost_adapter(self):
        content = PILOT_ENV.read_text(encoding="utf-8")

        self.assertIn("HERMES_PILOT_BASE_URL=http://127.0.0.1:8088/v1", content)
        self.assertIn("HERMES_PILOT_MODEL=gemma4:26b", content)
        self.assertIn("HERMES_PILOT_API_KEY=dummy-local-adapter-key", content)
        self.assertNotIn("sk-", content)

    def test_pilot_harness_writes_isolated_localhost_config_in_dry_run(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            hermes_home = Path(temp_dir) / "hermes-home"
            env = os.environ.copy()
            env["HERMES_HOME"] = str(hermes_home)
            result = subprocess.run(
                ["bash", str(PILOT_RUNNER), "--dry-run", "--stdout", "--prompt", "local reasoning only"],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            config = (hermes_home / "config.yaml").read_text(encoding="utf-8")
            self.assertIn("provider: custom", config)
            self.assertIn("default: gemma4:26b", config)
            self.assertIn("base_url: http://127.0.0.1:8088/v1", config)
            self.assertIn("api_key: dummy-local-adapter-key", config)
            self.assertIn("platform_toolsets:", config)
            self.assertIn("  cli: []", config)
            self.assertNotIn("100.93.120.124", config)

    def test_pilot_harness_can_send_runner_config_to_stderr(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            hermes_home = Path(temp_dir) / "hermes-home"
            env = os.environ.copy()
            env["HERMES_HOME"] = str(hermes_home)
            result = subprocess.run(
                [
                    "bash",
                    str(PILOT_RUNNER),
                    "--dry-run",
                    "--stdout",
                    "--config-to-stderr",
                    "--prompt",
                    "local reasoning only",
                ],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertIn("hermes_pilot.runner_config", result.stderr)
            self.assertIn("hermes_pilot.dry_run_complete", result.stderr)

    def test_pilot_harness_dry_run_does_not_emit_sensitive_env_values(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            env = os.environ.copy()
            env["HERMES_HOME"] = str(Path(temp_dir) / "hermes-home")
            secret_values = {
                "OPENAI_API_KEY": "sk-real-openai-secret",
                "ANTHROPIC_API_KEY": "anthropic-real-secret",
                "OPENROUTER_API_KEY": "openrouter-real-secret",
                "SUPABASE_URL": "https://example.supabase.co",
                "SUPABASE_ANON_KEY": "supabase-anon-secret",
                "SUPABASE_SERVICE_ROLE_KEY": "supabase-service-secret",
                "GOOGLE_CLIENT_SECRET_FILE": "/tmp/google-secret.json",
                "GOOGLE_TOKEN_FILE": "/tmp/google-token.json",
                "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_real_secret",
                "HASS_URL": "http://homeassistant.local:8123",
                "HASS_TOKEN": "hass-real-secret",
                "HELIO_GATEWAY_URL": "https://helio.example",
                "HELIO_DISPATCHER_MCP_URL": "https://helio.example/mcp",
            }
            env.update(secret_values)

            result = subprocess.run(
                ["bash", str(PILOT_RUNNER), "--dry-run", "--stdout", "--prompt", "local reasoning only"],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            combined = f"{result.stdout}\n{result.stderr}"
            self.assertEqual(result.returncode, 0, combined)
            self.assertIn("sensitive_env=unset_in_child_process", result.stdout)
            for value in secret_values.values():
                self.assertNotIn(value, combined)

    def test_pilot_harness_refuses_non_localhost_base_url(self):
        env = os.environ.copy()
        env["HERMES_PILOT_BASE_URL"] = "http://100.93.120.124:11434/v1"
        result = subprocess.run(
            ["bash", str(PILOT_RUNNER), "--dry-run", "--stdout", "--prompt", "local reasoning only"],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing non-pilot Hermes base URL", result.stderr)


if __name__ == "__main__":
    unittest.main()
