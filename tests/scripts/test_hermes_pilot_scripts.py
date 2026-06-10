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
PILOT_MODE_DOC = REPO_ROOT / "docs" / "HERMES_PILOT_MODE.md"
SECURITY_DOC = REPO_ROOT / "docs" / "HERMES_SECURITY_MODEL.md"
LOCAL_VALIDATION_DOC = REPO_ROOT / "docs" / "HERMES_LOCAL_VALIDATION_CHECKLIST.md"
READINESS_DOC = REPO_ROOT / "docs" / "HERMES_OPERATIONAL_READINESS_REVIEW.md"
PERSISTENT_CONFIG_PLAN = REPO_ROOT / "docs" / "HERMES_PERSISTENT_LOCAL_CONFIG_PLAN.md"
RESIDENT_MODE_PLAN = REPO_ROOT / "docs" / "HERMES_RESIDENT_MODE_PLAN.md"
ADAPTER_SERVICE_PLAN = REPO_ROOT / "docs" / "HERMES_ADAPTER_SERVICE_INSTALL_PLAN.md"
ADAPTER_SERVICE_REMEDIATION = REPO_ROOT / "docs" / "HERMES_ADAPTER_SERVICE_PATH_REMEDIATION.md"
ADAPTER_SERVICE_RUNBOOK = REPO_ROOT / "docs" / "HERMES_ADAPTER_SERVICE_RUNBOOK.md"
ADAPTER_SERVICE_START = REPO_ROOT / "scripts" / "adapter_service_start.sh"
ADAPTER_SERVICE_STOP = REPO_ROOT / "scripts" / "adapter_service_stop.sh"
ADAPTER_SERVICE_STATUS = REPO_ROOT / "scripts" / "adapter_service_status.sh"

SENSITIVE_ENV_VARS = {
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "OPENROUTER_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "GOOGLE_CLIENT_SECRET_FILE",
    "GOOGLE_TOKEN_FILE",
    "GITHUB_PERSONAL_ACCESS_TOKEN",
    "HASS_URL",
    "HASS_TOKEN",
    "HELIO_GATEWAY_URL",
    "HELIO_DISPATCHER_MCP_URL",
}


class HermesPilotScriptsTest(unittest.TestCase):
    def test_shell_scripts_pass_syntax_check(self):
        for script in (ADAPTER_RUNNER, PILOT_RUNNER, ADAPTER_SERVICE_START, ADAPTER_SERVICE_STOP, ADAPTER_SERVICE_STATUS):
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

    def test_pilot_prompt_builder_creates_phase5af_forward_prompt(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            output = Path(temp_dir) / "phase5af_prompt.md"
            result = subprocess.run(
                ["python3", str(PILOT_PROMPT_BUILDER), "--phase5af", "--output", str(output)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            prompt = output.read_text(encoding="utf-8")
            self.assertIn("Document/context:", prompt)
            self.assertIn("# Bounded local context for Phase 5AF", prompt)
            self.assertIn("Source: docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md", prompt)
            self.assertIn("Source: docs/prd/CHANGELOG.md", prompt)
            self.assertIn("Source: docs/HERMES_PILOT_MODE.md", prompt)
            self.assertIn("Source: docs/HERMES_SECURITY_MODEL.md", prompt)
            self.assertIn("recommended phase name", prompt)
            self.assertIn("acceptance criteria", prompt)
            self.assertIn("whether human approval is required before execution", prompt)
            self.assertNotIn("Read these local repo documents only", prompt)
            self.assertNotIn("Task:", prompt)

    def test_pilot_prompt_builder_creates_phase5ag_prd_review_prompt(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            output = Path(temp_dir) / "phase5ag_prompt.md"
            result = subprocess.run(
                ["python3", str(PILOT_PROMPT_BUILDER), "--phase5ag", "--output", str(output)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            prompt = output.read_text(encoding="utf-8")
            self.assertIn("Document/context:", prompt)
            self.assertIn("# Bounded local context for Phase 5AG", prompt)
            self.assertIn("Source: docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md", prompt)
            self.assertIn("Source: docs/prd/CHANGELOG.md", prompt)
            self.assertIn("Source: docs/HERMES_PILOT_MODE.md", prompt)
            self.assertIn("Source: docs/HERMES_SECURITY_MODEL.md", prompt)
            self.assertIn("Source: docs/HERMES_MODEL_PROVIDER_PLAN.md", prompt)
            self.assertIn("PRD consistency findings", prompt)
            self.assertIn("missing or weak guardrails", prompt)
            self.assertIn("next safest phase recommendation", prompt)
            self.assertNotIn("Read these local repo documents only", prompt)
            self.assertNotIn("Task:", prompt)

    def test_pilot_prompt_builder_creates_phase5av_local_setup_review_prompt(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            output = Path(temp_dir) / "phase5av_prompt.md"
            result = subprocess.run(
                ["python3", str(PILOT_PROMPT_BUILDER), "--phase5av", "--output", str(output)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            prompt = output.read_text(encoding="utf-8")
            self.assertIn("Document/context:", prompt)
            self.assertIn("# Bounded local context for Phase 5AV", prompt)
            self.assertIn("Source: docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md", prompt)
            self.assertIn("Source: docs/prd/CHANGELOG.md", prompt)
            self.assertIn("Source: docs/HERMES_OPERATIONAL_READINESS_REVIEW.md", prompt)
            self.assertIn("Source: docs/HERMES_LOCAL_VALIDATION_CHECKLIST.md", prompt)
            self.assertIn("Source: docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md", prompt)
            self.assertIn("what is ready", prompt)
            self.assertIn("top 5 risks", prompt)
            self.assertIn("whether human approval is required", prompt)
            self.assertIn("Do not ask to read files. Do not use tools.", prompt)
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

    def test_pilot_env_stripping_list_matches_documented_credential_services(self):
        env_content = PILOT_ENV.read_text(encoding="utf-8")
        pilot_doc = PILOT_MODE_DOC.read_text(encoding="utf-8")
        runner = PILOT_RUNNER.read_text(encoding="utf-8")
        sanitized_env = runner.split("SANITIZED_ENV=(", 1)[1].split(")", 1)[0]

        for variable in SENSITIVE_ENV_VARS:
            with self.subTest(variable=variable):
                self.assertIn(f"{variable}=", env_content)
                self.assertIn(f"`{variable}`", pilot_doc)

        for variable in SENSITIVE_ENV_VARS - {"OPENAI_API_KEY"}:
            with self.subTest(stripped_variable=variable):
                self.assertNotIn(variable, sanitized_env)

        self.assertIn('"OPENAI_API_KEY=${HERMES_PILOT_API_KEY}"', sanitized_env)
        self.assertNotIn("${OPENAI_API_KEY}", sanitized_env)

    def test_local_validation_docs_preserve_credential_deferral_freeze(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                SECURITY_DOC,
                LOCAL_VALIDATION_DOC,
                READINESS_DOC,
                PERSISTENT_CONFIG_PLAN,
                RESIDENT_MODE_PLAN,
                ADAPTER_SERVICE_PLAN,
                ADAPTER_SERVICE_REMEDIATION,
                ADAPTER_SERVICE_RUNBOOK,
            )
        )

        self.assertIn("Phase 5AI", combined)
        self.assertIn("credential rotation", combined)
        self.assertIn("local-only", combined)
        self.assertIn("live Agent Bus reads/writes", combined)
        self.assertIn("Desktop launch", combined)

    def test_readiness_doc_does_not_claim_live_integrations_are_approved(self):
        content = READINESS_DOC.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Phase 5AK", content)
        self.assertIn("Current Blocked Capabilities", content)
        self.assertIn("Credential rotation", content)
        self.assertIn("Human approval is required before", content)
        self.assertIn("Hermes is ready only for continued local-only", content)

        forbidden_claims = (
            "google workspace is approved",
            "supabase agent bus is approved",
            "agent bus writes are approved",
            "home assistant control is approved",
            "github token use is approved",
            "desktop relaunch is approved",
            "credential rotation is complete",
            "resident operation is approved",
        )
        for claim in forbidden_claims:
            self.assertNotIn(claim, lower_content)

    def test_readiness_doc_keeps_desktop_fail_closed(self):
        content = READINESS_DOC.read_text(encoding="utf-8")

        self.assertIn("Hermes Desktop | Not ready; fail-closed", content)
        self.assertIn("Desktop Relaunch", content)
        self.assertIn("Resolve release-channel/signature questions", content)
        self.assertIn("new phase-specific human approval gate", content)

    def test_persistent_config_plan_preserves_localhost_only_adapter(self):
        content = PERSISTENT_CONFIG_PLAN.read_text(encoding="utf-8")

        self.assertIn("Status: persistent local config live-local validated", content)
        self.assertIn("http://127.0.0.1:8088/v1", content)
        self.assertIn("gemma4:26b", content)
        self.assertIn("provider: custom", content)
        self.assertIn("platform_toolsets:", content)
        self.assertIn("cli: []", content)
        self.assertIn("phase5am-20260608T232816", content)
        self.assertIn("Phase 5AN Live Local Validation Result", content)
        self.assertIn("Persistent local Hermes config works.", content)

    def test_persistent_config_plan_excludes_credentials_and_live_integrations(self):
        content = PERSISTENT_CONFIG_PLAN.read_text(encoding="utf-8")
        lower_content = content.lower()

        required_phrases = (
            "no real openai key",
            "no real anthropic key",
            "no real openrouter key",
            "no google credentials",
            "no supabase credentials",
            "no github token",
            "no home assistant token",
            "no helio gateway or dispatcher token",
            "no cloud provider",
            "no cloud provider, google, supabase, home assistant, github, helio, or agent bus integration was contacted",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, lower_content)

    def test_persistent_config_plan_includes_backup_and_rollback(self):
        content = PERSISTENT_CONFIG_PLAN.read_text(encoding="utf-8")

        self.assertIn("## Backup Plan Used", content)
        self.assertIn("## Rollback", content)
        self.assertIn("/Users/michaelrinebold/.hermes/backups/phase5am-20260608T232816/config.yaml.bak", content)
        self.assertIn("Restore `/Users/michaelrinebold/.hermes/backups/phase5am-20260608T232816/config.yaml.bak`", content)
        self.assertIn("Confirm no `8088` listener remains", content)

    def test_persistent_config_plan_keeps_desktop_and_resident_modes_blocked(self):
        content = PERSISTENT_CONFIG_PLAN.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Desktop dependency: none", content)
        self.assertIn("Hermes Desktop was not launched", content)
        self.assertIn("launchd", content)
        self.assertIn("background service", content)
        self.assertIn("resident mode", content)
        self.assertNotIn("launchd is approved", lower_content)
        self.assertNotIn("resident mode is approved", lower_content)
        self.assertNotIn("desktop launch is approved", lower_content)

    def test_resident_plan_is_adapter_service_first_not_hermes_resident(self):
        content = RESIDENT_MODE_PLAN.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Status: manual adapter service operation validated; Hermes resident mode disabled", content)
        self.assertIn("Adapter service only first", content)
        self.assertIn("Hermes remains manually invoked at first", content)
        self.assertIn("Future Hermes resident/autonomous mode requires a separate approval phase", content)
        self.assertNotIn("hermes autonomous resident mode is approved", lower_content)
        self.assertNotIn("hermes resident mode is approved", lower_content)

    def test_resident_plan_requires_localhost_only_binding(self):
        content = RESIDENT_MODE_PLAN.read_text(encoding="utf-8")

        self.assertIn("127.0.0.1:8088", content)
        self.assertIn("MODEL_ROUTER_ADAPTER_HOST=127.0.0.1", content)
        self.assertIn("MODEL_ROUTER_ADAPTER_PORT=8088", content)
        self.assertIn("no `0.0.0.0` listener", content)
        self.assertIn("no LAN/public/Tailscale bind", content)

    def test_resident_plan_includes_health_stop_and_rollback(self):
        content = RESIDENT_MODE_PLAN.read_text(encoding="utf-8")

        self.assertIn("curl -sS http://127.0.0.1:8088/health", content)
        self.assertIn("curl -sS http://127.0.0.1:8088/v1/models", content)
        self.assertIn("launchctl bootout", content)
        self.assertIn("Rollback candidate", content)
        self.assertIn("verify stop command works", content)
        self.assertIn("verify rollback command works", content)

    def test_resident_plan_keeps_integrations_frozen_and_desktop_fail_closed(self):
        content = RESIDENT_MODE_PLAN.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Hermes Desktop remains fail-closed", content)
        self.assertIn("Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, and cloud-provider integrations remain frozen", content)
        self.assertIn("no real credentials are added", content)
        self.assertIn("Phase 5AO does not approve", content)
        self.assertNotIn("desktop launch is approved", lower_content)
        self.assertNotIn("agent bus reads are approved", lower_content)
        self.assertNotIn("real credentials are approved", lower_content)

    def test_adapter_service_plan_is_adapter_only_not_hermes_resident(self):
        content = ADAPTER_SERVICE_PLAN.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Status: adapter LaunchAgent wrapper service validated and stopped", content)
        self.assertIn("The future service is adapter-only", content)
        self.assertIn("Hermes remains manually invoked", content)
        self.assertIn("Hermes autonomous resident mode is not approved", content)
        self.assertIn("Phase 5AP did not create a plist", content)
        self.assertIn("service is adapter-only", content)
        self.assertIn("service running: no", content)
        self.assertNotIn("hermes autonomous resident mode is approved", lower_content)
        self.assertNotIn("hermes resident mode is approved", lower_content)

    def test_adapter_service_plan_contains_localhost_only_launchagent(self):
        content = ADAPTER_SERVICE_PLAN.read_text(encoding="utf-8")

        self.assertIn("com.msr.hermes.model-router-adapter", content)
        self.assertIn("~/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist", content)
        self.assertIn("/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter", content)
        self.assertIn("/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current", content)
        self.assertIn("<key>RunAtLoad</key>", content)
        self.assertIn("<false/>", content)
        self.assertIn("<key>KeepAlive</key>", content)
        self.assertIn("/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stdout.log", content)
        self.assertIn("/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stderr.log", content)
        self.assertIn("<key>MODEL_ROUTER_ADAPTER_HOST</key>", content)
        self.assertIn("<string>127.0.0.1</string>", content)
        self.assertIn("<key>MODEL_ROUTER_ADAPTER_PORT</key>", content)
        self.assertIn("<string>8088</string>", content)
        self.assertIn("no `0.0.0.0` listener exists", content)
        self.assertIn("no LAN/public/Tailscale bind exists", content)

    def test_adapter_service_plan_includes_health_stop_and_rollback(self):
        content = ADAPTER_SERVICE_PLAN.read_text(encoding="utf-8")

        self.assertIn("curl -sS http://127.0.0.1:8088/health", content)
        self.assertIn("curl -sS http://127.0.0.1:8088/v1/models", content)
        self.assertIn("lsof -nP -iTCP:8088 -sTCP:LISTEN", content)
        self.assertIn("launchctl print", content)
        self.assertIn("launchctl bootout", content)
        self.assertIn("Rollback/removal commands", content)
        self.assertIn("$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist.disabled.$(date +%Y%m%dT%H%M%S)", content)
        self.assertIn("health result: passed during manual start", content)
        self.assertIn("models result: passed during manual start and included `gemma4:26b`", content)
        self.assertIn("no `8088` listener remains", content)

    def test_adapter_service_plan_keeps_desktop_and_integrations_frozen(self):
        content = ADAPTER_SERVICE_PLAN.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Hermes Desktop is not a dependency and remains fail-closed", content)
        self.assertIn("Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, and cloud-provider integrations remain frozen", content)
        self.assertIn("no real credentials or secret-like values belong in the plist", content)
        self.assertIn("Phase 5AP does not approve", content)
        self.assertNotIn("desktop launch is approved", lower_content)
        self.assertNotIn("agent bus reads are approved", lower_content)
        self.assertNotIn("real credentials are approved", lower_content)

    def test_adapter_service_remediation_recommends_minimal_wrapper(self):
        content = ADAPTER_SERVICE_REMEDIATION.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Status: wrapper plus self-contained runtime validated; service stopped", content)
        self.assertIn("Recommend Option A", content)
        self.assertIn("/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter", content)
        self.assertIn("avoids broad macOS privacy permissions", content)
        self.assertIn("avoids moving the entire repo", content)
        self.assertIn("/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current", content)
        self.assertIn("Successful validation", content)
        self.assertIn("service unloaded: yes", content)
        self.assertNotIn("full disk access is approved", lower_content)
        self.assertNotIn("move the whole repo is approved", lower_content)

    def test_adapter_service_remediation_preserves_localhost_only(self):
        content = ADAPTER_SERVICE_REMEDIATION.read_text(encoding="utf-8")

        self.assertIn("adapter binds only to `127.0.0.1:8088`", content)
        self.assertIn("no `0.0.0.0`, LAN, public, or Tailscale listener", content)
        self.assertIn("MODEL_ROUTER_ADAPTER_HOST=127.0.0.1", content)
        self.assertIn("MODEL_ROUTER_ADAPTER_PORT=8088", content)
        self.assertIn("service binds only `127.0.0.1:8088`", content)
        self.assertIn("listener inspection showed only `TCP 127.0.0.1:8088 (LISTEN)`", content)

    def test_adapter_service_remediation_keeps_hermes_resident_disabled(self):
        content = ADAPTER_SERVICE_REMEDIATION.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Hermes remains manually invoked", content)
        self.assertIn("Hermes resident/autonomous mode remains disabled", content)
        self.assertIn("no Hermes resident/autonomous process exists", content)
        self.assertIn("enabling Hermes resident/autonomous mode", content)
        self.assertNotIn("hermes resident mode is approved", lower_content)
        self.assertNotIn("hermes autonomous resident mode is approved", lower_content)

    def test_adapter_service_remediation_includes_rollback_without_live_integration_approval(self):
        content = ADAPTER_SERVICE_REMEDIATION.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("## Future Stop And Rollback", content)
        self.assertIn("launchctl bootout", content)
        self.assertIn("msr-hermes-model-router-adapter.disabled.$(date +%Y%m%dT%H%M%S)", content)
        self.assertIn("Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, and cloud-provider integrations remain frozen", content)
        self.assertNotIn("google workspace is approved", lower_content)
        self.assertNotIn("supabase agent bus is approved", lower_content)
        self.assertNotIn("agent bus writes are approved", lower_content)
        self.assertNotIn("home assistant control is approved", lower_content)
        self.assertNotIn("github token use is approved", lower_content)

    def test_adapter_service_helpers_are_scoped_to_existing_launchagent(self):
        helper_contents = {
            "start": ADAPTER_SERVICE_START.read_text(encoding="utf-8"),
            "stop": ADAPTER_SERVICE_STOP.read_text(encoding="utf-8"),
            "status": ADAPTER_SERVICE_STATUS.read_text(encoding="utf-8"),
        }

        for name, content in helper_contents.items():
            with self.subTest(helper=name):
                self.assertIn('LABEL="com.msr.hermes.model-router-adapter"', content)
                self.assertIn('PLIST="${HOME}/Library/LaunchAgents/${LABEL}.plist"', content)
                self.assertNotIn("sudo", content)
                self.assertNotIn("RunAtLoad=true", content)
                self.assertNotIn("KeepAlive=true", content)
                self.assertNotIn("~/.hermes", content)

        self.assertIn("launchctl bootstrap", helper_contents["start"])
        self.assertIn("launchctl kickstart", helper_contents["start"])
        self.assertIn("launchctl bootout", helper_contents["stop"])
        self.assertNotIn("plistlib.dump", helper_contents["start"])
        self.assertNotIn("plistlib.dump", helper_contents["stop"])
        self.assertNotIn("plistlib.dump", helper_contents["status"])

    def test_adapter_service_runbook_keeps_manual_only_policy(self):
        content = ADAPTER_SERVICE_RUNBOOK.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Status: manual adapter service operating procedure", content)
        self.assertIn("RunAtLoad=false", content)
        self.assertIn("KeepAlive=false", content)
        self.assertIn("Hermes resident/autonomous mode remains disabled", content)
        self.assertIn("Hermes Desktop remains fail-closed", content)
        self.assertIn("Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, and cloud-provider integrations remain frozen", content)
        self.assertIn("scripts/adapter_service_start.sh", content)
        self.assertIn("scripts/adapter_service_stop.sh", content)
        self.assertIn("scripts/adapter_service_status.sh", content)
        self.assertIn("The service was not left running after validation.", content)
        self.assertIn("Phase 5AT does not approve", content)
        self.assertNotIn("runatload=true is approved", lower_content)
        self.assertNotIn("keepalive=true is approved", lower_content)
        self.assertNotIn("hermes resident mode is approved", lower_content)
        self.assertNotIn("desktop launch is approved", lower_content)
        self.assertNotIn("agent bus writes are approved", lower_content)

    def test_local_validation_surfaces_do_not_contain_real_looking_secrets(self):
        surfaces = [
            PILOT_ENV,
            ADAPTER_RUNNER,
            PILOT_RUNNER,
            REPO_ROOT / "services" / "model_router_adapter" / "README.md",
            PILOT_MODE_DOC,
            SECURITY_DOC,
            LOCAL_VALIDATION_DOC,
            READINESS_DOC,
            PERSISTENT_CONFIG_PLAN,
            RESIDENT_MODE_PLAN,
            ADAPTER_SERVICE_PLAN,
            ADAPTER_SERVICE_REMEDIATION,
            ADAPTER_SERVICE_RUNBOOK,
            ADAPTER_SERVICE_START,
            ADAPTER_SERVICE_STOP,
            ADAPTER_SERVICE_STATUS,
        ]
        disallowed_markers = (
            "sk-live-",
            "sk-proj-",
            "sk-ant-",
            "xoxb-",
            "ghp_",
            "github_pat_",
            "SUPABASE_SERVICE_ROLE_KEY=ey",
            "HASS_TOKEN=ey",
            "OPENAI_API_KEY=sk-",
            "ANTHROPIC_API_KEY=sk-",
            "OPENROUTER_API_KEY=sk-",
        )

        for path in surfaces:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                content = path.read_text(encoding="utf-8")
                for marker in disallowed_markers:
                    self.assertNotIn(marker, content)

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
