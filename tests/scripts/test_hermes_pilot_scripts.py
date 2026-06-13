import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_RUNNER = REPO_ROOT / "scripts" / "run_model_router_adapter.sh"
PILOT_RUNNER = REPO_ROOT / "scripts" / "run_hermes_pilot.sh"
PILOT_PROMPT_BUILDER = REPO_ROOT / "scripts" / "build_hermes_pilot_context_prompt.py"
LOCAL_TASK_BUILDER = REPO_ROOT / "scripts" / "build_hermes_local_task.py"
PILOT_ENV = REPO_ROOT / "config" / "hermes-pilot.example.env"
PILOT_MODE_DOC = REPO_ROOT / "docs" / "HERMES_PILOT_MODE.md"
SECURITY_DOC = REPO_ROOT / "docs" / "HERMES_SECURITY_MODEL.md"
LOCAL_VALIDATION_DOC = REPO_ROOT / "docs" / "HERMES_LOCAL_VALIDATION_CHECKLIST.md"
READINESS_DOC = REPO_ROOT / "docs" / "HERMES_OPERATIONAL_READINESS_REVIEW.md"
PERSISTENT_CONFIG_PLAN = REPO_ROOT / "docs" / "HERMES_PERSISTENT_LOCAL_CONFIG_PLAN.md"
RESIDENT_MODE_PLAN = REPO_ROOT / "docs" / "HERMES_RESIDENT_MODE_PLAN.md"
RESIDENT_AUTHORITY_MODEL = REPO_ROOT / "docs" / "HERMES_RESIDENT_AUTHORITY_MODEL.md"
AUDIT_LOG_DESIGN = REPO_ROOT / "docs" / "HERMES_AUDIT_LOG_DESIGN.md"
EMERGENCY_STOP_DESIGN = REPO_ROOT / "docs" / "HERMES_EMERGENCY_STOP_DESIGN.md"
RESIDENT_SERVICE_PROPOSAL = REPO_ROOT / "docs" / "HERMES_RESIDENT_SERVICE_PROPOSAL.md"
HELIO_DELEGATION_INTERFACE = REPO_ROOT / "docs" / "HERMES_HELIO_DELEGATION_INTERFACE.md"
COMMAND_POLICY = REPO_ROOT / "docs" / "HERMES_COMMAND_POLICY.md"
FILE_ZONE_POLICY = REPO_ROOT / "docs" / "HERMES_FILE_ZONE_POLICY.md"
APPROVAL_RECORD_MODEL = REPO_ROOT / "docs" / "HERMES_APPROVAL_RECORD_MODEL.md"
ADAPTER_SERVICE_PLAN = REPO_ROOT / "docs" / "HERMES_ADAPTER_SERVICE_INSTALL_PLAN.md"
ADAPTER_SERVICE_REMEDIATION = REPO_ROOT / "docs" / "HERMES_ADAPTER_SERVICE_PATH_REMEDIATION.md"
ADAPTER_SERVICE_RUNBOOK = REPO_ROOT / "docs" / "HERMES_ADAPTER_SERVICE_RUNBOOK.md"
LOCAL_TASK_INBOX_DOC = REPO_ROOT / "docs" / "HERMES_LOCAL_TASK_INBOX.md"
ADAPTER_SERVICE_START = REPO_ROOT / "scripts" / "adapter_service_start.sh"
ADAPTER_SERVICE_STOP = REPO_ROOT / "scripts" / "adapter_service_stop.sh"
ADAPTER_SERVICE_STATUS = REPO_ROOT / "scripts" / "adapter_service_status.sh"
HERMES_LOCAL_STATUS = REPO_ROOT / "scripts" / "hermes_local_status.sh"
LOCAL_TASK_RUNNER = REPO_ROOT / "scripts" / "run_hermes_local_task.sh"
LOCAL_TASK_SAMPLE = REPO_ROOT / "sandbox" / "hermes_inbox" / "next_step_review.task.md"
LOCAL_TASK_WITH_CONTEXT = REPO_ROOT / "sandbox" / "hermes_inbox" / "next_phase_recommendation_with_context.task.md"
LOCAL_TASK_COMPACT = REPO_ROOT / "sandbox" / "hermes_inbox" / "next_phase_recommendation_compact.task.md"
LOCAL_OPERATIONS_RUNBOOK = REPO_ROOT / "docs" / "HERMES_LOCAL_OPERATIONS_RUNBOOK.md"
LOCAL_ONLY_READY_REPORT = REPO_ROOT / "docs" / "HERMES_LOCAL_ONLY_READY_REPORT.md"

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
        for script in (
            ADAPTER_RUNNER,
            PILOT_RUNNER,
            ADAPTER_SERVICE_START,
            ADAPTER_SERVICE_STOP,
            ADAPTER_SERVICE_STATUS,
            HERMES_LOCAL_STATUS,
            LOCAL_TASK_RUNNER,
        ):
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

    def test_local_task_runner_refuses_paths_outside_inbox(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            outside_task = Path(temp_dir) / "outside.task.md"
            outside_task.write_text("local reasoning only", encoding="utf-8")
            result = subprocess.run(
                ["bash", str(LOCAL_TASK_RUNNER), str(outside_task)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing task path outside sandbox/hermes_inbox", result.stderr)

    def test_local_task_runner_requires_adapter_health_and_outbox_outputs(self):
        content = LOCAL_TASK_RUNNER.read_text(encoding="utf-8")

        self.assertIn('INBOX_DIR="${REPO_ROOT}/sandbox/hermes_inbox"', content)
        self.assertIn('OUTBOX_DIR="${REPO_ROOT}/sandbox/hermes_outbox"', content)
        self.assertIn('ADAPTER_HEALTH_URL="http://127.0.0.1:8088/health"', content)
        self.assertIn('curl -fsS --max-time 10 "${ADAPTER_HEALTH_URL}"', content)
        self.assertIn('OUTPUT_PATH="${OUTBOX_ABS}/${TASK_NAME}.out.md"', content)
        self.assertIn('STDERR_PATH="${OUTBOX_ABS}/${TASK_NAME}.stderr"', content)
        self.assertIn('METRICS_PATH="${OUTBOX_ABS}/${TASK_NAME}.metrics"', content)
        self.assertIn('env -i', content)
        self.assertIn('"${HERMES_BIN}" --ignore-rules -z "${PROMPT_TEXT}"', content)
        self.assertNotIn("sudo", content)
        self.assertNotIn("launchctl", content)
        self.assertNotIn("RunAtLoad=true", content)
        self.assertNotIn("KeepAlive=true", content)

    def test_local_task_docs_keep_external_integrations_and_shell_execution_blocked(self):
        content = LOCAL_TASK_INBOX_DOC.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("sandbox/hermes_inbox/", content)
        self.assertIn("sandbox/hermes_outbox/", content)
        self.assertIn("sandbox/hermes_archive/", content)
        self.assertIn("Hermes may read only the task file passed to the runner", content)
        self.assertIn("Hermes may write output only through the runner to `sandbox/hermes_outbox/`", content)
        self.assertIn("Hermes may not execute shell commands independently", content)
        self.assertIn("Hermes may not launch Desktop", content)
        self.assertIn("No external integrations", content)
        self.assertIn("Phase 5AW does not approve", content)
        self.assertNotIn("agent bus writes are approved", lower_content)
        self.assertNotIn("desktop launch is approved", lower_content)
        self.assertNotIn("real credentials are approved", lower_content)

    def test_local_task_sample_stays_local_only(self):
        content = LOCAL_TASK_SAMPLE.read_text(encoding="utf-8")

        self.assertIn("next safest local-only Hermes phase", content)
        self.assertIn("Do not ask for external integrations", content)
        self.assertIn("Do not request credentials", content)
        self.assertIn("Do not suggest Desktop launch", content)

    def test_local_task_builder_writes_only_under_inbox(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp_dir:
            outside_output = Path(temp_dir) / "outside.task.md"
            result = subprocess.run(
                ["python3", str(LOCAL_TASK_BUILDER), "--output", str(outside_output)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing output outside sandbox/hermes_inbox", result.stderr)

    def test_local_task_builder_refuses_secret_like_source_files(self):
        inbox_output = REPO_ROOT / "sandbox" / "hermes_inbox" / "test_secret_refusal.task.md"
        result = subprocess.run(
            [
                "python3",
                str(LOCAL_TASK_BUILDER),
                "--output",
                str(inbox_output),
                "--source",
                "config/hermes-pilot.example.env:100",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing secret-like source path", result.stderr)

    def test_local_task_builder_includes_approved_context_labels_and_limits(self):
        content = LOCAL_TASK_WITH_CONTEXT.read_text(encoding="utf-8")
        for label in (
            "## Source: docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md",
            "## Source: docs/prd/CHANGELOG.md",
            "## Source: docs/HERMES_OPERATIONAL_READINESS_REVIEW.md",
            "## Source: docs/HERMES_LOCAL_TASK_INBOX.md",
            "## Source: docs/HERMES_LOCAL_VALIDATION_CHECKLIST.md",
            "## Source: docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md",
        ):
            self.assertIn(label, content)
        for limit in ("Character limit: 1800", "Character limit: 1300", "Character limit: 1200", "Character limit: 1000", "Character limit: 900"):
            self.assertIn(limit, content)
        self.assertIn("Using only the embedded local context below", content)
        self.assertIn("recommended phase name", content)
        self.assertIn("acceptance criteria", content)

    def test_generated_context_task_stays_local_only_and_has_no_real_looking_secrets(self):
        content = LOCAL_TASK_WITH_CONTEXT.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Using only the embedded local context below", content)
        self.assertIn("recommend the next safest local-only Hermes phase", content)
        self.assertIn("Do not request external integrations", content)
        self.assertIn("Do not ask to read files. Do not use tools.", content)
        self.assertIn("required human approval", content)
        self.assertNotIn("desktop launch is approved", lower_content)
        self.assertNotIn("agent bus writes are approved", lower_content)
        self.assertNotIn("real credentials are approved", lower_content)
        for marker in ("sk-live-", "sk-proj-", "sk-ant-", "xoxb-", "ghp_", "github_pat_"):
            self.assertNotIn(marker, content)

    def test_compact_context_task_is_smaller_and_budgeted(self):
        compact = LOCAL_TASK_COMPACT.read_text(encoding="utf-8")
        full = LOCAL_TASK_WITH_CONTEXT.read_text(encoding="utf-8")

        self.assertLess(LOCAL_TASK_COMPACT.stat().st_size, LOCAL_TASK_WITH_CONTEXT.stat().st_size)
        self.assertIn("Compact embedded context budget: 1100 chars", compact)
        context = compact.split("Compact local context:\n", 1)[1]
        self.assertLessEqual(len(context), 1200)

    def test_compact_context_task_asks_for_one_local_only_next_phase(self):
        content = LOCAL_TASK_COMPACT.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("recommend the single next safest local-only Hermes phase", content)
        self.assertIn("Keep the answer under 250 words", content)
        self.assertIn("- non-goals", content)
        self.assertIn("- acceptance criteria", content)
        self.assertIn("Do not request external integrations", content)
        self.assertIn("Do not ask to read files. Do not use tools.", content)
        self.assertNotIn("broad PRD review", content)
        self.assertNotIn("desktop launch is approved", lower_content)
        self.assertNotIn("agent bus writes are approved", lower_content)
        self.assertNotIn("real credentials are approved", lower_content)
        for marker in ("sk-live-", "sk-proj-", "sk-ant-", "xoxb-", "ghp_", "github_pat_"):
            self.assertNotIn(marker, content)

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
            RESIDENT_AUTHORITY_MODEL,
            AUDIT_LOG_DESIGN,
            EMERGENCY_STOP_DESIGN,
            RESIDENT_SERVICE_PROPOSAL,
            HELIO_DELEGATION_INTERFACE,
            COMMAND_POLICY,
            FILE_ZONE_POLICY,
            APPROVAL_RECORD_MODEL,
            ADAPTER_SERVICE_PLAN,
            ADAPTER_SERVICE_REMEDIATION,
            ADAPTER_SERVICE_RUNBOOK,
            LOCAL_TASK_INBOX_DOC,
            ADAPTER_SERVICE_START,
            ADAPTER_SERVICE_STOP,
            ADAPTER_SERVICE_STATUS,
            LOCAL_TASK_RUNNER,
            LOCAL_TASK_BUILDER,
            LOCAL_TASK_SAMPLE,
            LOCAL_TASK_WITH_CONTEXT,
            LOCAL_TASK_COMPACT,
            LOCAL_OPERATIONS_RUNBOOK,
            LOCAL_ONLY_READY_REPORT,
            HERMES_LOCAL_STATUS,
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

    def test_local_operations_runbook_keeps_local_only_boundaries(self):
        content = LOCAL_OPERATIONS_RUNBOOK.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("manual adapter service start and stop only", content)
        self.assertIn("Hermes CLI local-only inference through `http://127.0.0.1:8088/v1`", content)
        self.assertIn("context-bearing inbox tasks only", content)
        self.assertIn("Hermes Desktop; it remains fail-closed", content)
        self.assertIn("external integrations", content)
        self.assertIn("Hermes resident/autonomous mode", content)
        self.assertIn("RunAtLoad=true", content)
        self.assertIn("KeepAlive=true", content)
        self.assertNotIn("desktop launch is approved", lower_content)
        self.assertNotIn("external integrations are approved", lower_content)
        self.assertNotIn("resident mode is approved", lower_content)

    def test_local_operations_runbook_documents_commands_and_cleanup(self):
        content = LOCAL_OPERATIONS_RUNBOOK.read_text(encoding="utf-8")

        for command in (
            "scripts/adapter_service_start.sh",
            "scripts/adapter_service_status.sh",
            "scripts/hermes_local_status.sh",
            "scripts/build_hermes_local_task.py",
            "scripts/run_hermes_local_task.sh sandbox/hermes_inbox/next_phase_recommendation_compact.task.md",
            "scripts/adapter_service_stop.sh",
        ):
            self.assertIn(command, content)

        self.assertIn("Verify cleanup", content)
        self.assertIn("no `8088` listener remains", content)
        self.assertIn("no Hermes Desktop process remains", content)
        self.assertIn("no Hermes resident/autonomous process remains", content)

    def test_local_only_ready_report_certifies_narrow_manual_mode(self):
        content = LOCAL_ONLY_READY_REPORT.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("manual local-only use", content)
        self.assertIn("manual adapter service start/stop only", content)
        self.assertIn("Hermes CLI local-only", content)
        self.assertIn("context-bearing or compact inbox tasks only", content)
        self.assertIn("no Desktop", content)
        self.assertIn("no external integrations", content)
        self.assertIn("no resident Hermes mode", content)
        self.assertNotIn("desktop launch is approved", lower_content)
        self.assertNotIn("external integrations are approved", lower_content)
        self.assertNotIn("resident hermes is approved", lower_content)

    def test_local_only_ready_report_includes_final_state_and_blockers(self):
        content = LOCAL_ONLY_READY_REPORT.read_text(encoding="utf-8")

        for expected in (
            "LaunchAgent installed but stopped/unloaded",
            "No `8088` listener",
            "No Hermes process",
            "No adapter process",
            "No Desktop process",
            "Repo clean",
            "Decide resident authority model",
            "Decide `RunAtLoad` and `KeepAlive` policy",
            "Define audit log storage",
            "Decide credential rotation",
            "Define Hermes-to-Helio delegation boundary",
            "Define approved shell/file-operation gate",
        ):
            self.assertIn(expected, content)

    def test_hermes_local_status_script_is_read_only(self):
        content = HERMES_LOCAL_STATUS.read_text(encoding="utf-8")

        self.assertNotIn("sudo", content)
        self.assertNotIn("adapter_service_start.sh", content)
        self.assertNotIn("adapter_service_stop.sh", content)
        self.assertNotIn("launchctl bootstrap", content)
        self.assertNotIn("launchctl kickstart", content)
        self.assertNotIn("launchctl bootout", content)
        self.assertNotIn("RunAtLoad=true", content)
        self.assertNotIn("KeepAlive=true", content)
        self.assertIn("launchctl print", content)
        self.assertIn("http://127.0.0.1:8088/health", content)
        self.assertIn("http://127.0.0.1:8088/v1/models", content)

    def test_hermes_local_status_script_checks_config_and_warnings(self):
        content = HERMES_LOCAL_STATUS.read_text(encoding="utf-8")

        self.assertIn("hermes_config_base_url_localhost", content)
        self.assertIn("base_url:[[:space:]]*http://127\\.0\\.0\\.1:8088/v1", content)
        self.assertIn("forbidden_env_vars_set", content)
        self.assertIn("warning_adapter_non_localhost_listener", content)
        self.assertIn("warning_desktop_running", content)
        self.assertIn("warning_hermes_resident_like_process", content)
        self.assertIn("set_forbidden_names+=(\"$env_name\")", content)
        self.assertNotIn("printenv", content)
        self.assertNotIn("env |", content)

    def test_resident_authority_model_defines_all_tiers(self):
        content = RESIDENT_AUTHORITY_MODEL.read_text(encoding="utf-8")

        for tier in (
            "Tier 0: Observe Only",
            "Tier 1: Recommend",
            "Tier 2: Draft",
            "Tier 3: Local Approved Execution",
            "Tier 4: External Read-Only",
            "Tier 5: External Draft/Propose",
            "Tier 6: External Approved Action",
            "Tier 7: Resident Delegated Operator",
        ):
            self.assertIn(tier, content)

    def test_resident_authority_model_keeps_runtime_disabled(self):
        content = RESIDENT_AUTHORITY_MODEL.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("resident mode not enabled yet", content)
        self.assertIn("This phase does not enable resident mode", content)
        self.assertIn("RunAtLoad=false", content)
        self.assertIn("KeepAlive=false", content)
        self.assertIn("Hermes Desktop remains fail-closed", content)
        self.assertIn("external integrations remain frozen", content)
        self.assertIn("Emergency Stop Requirements", content)
        self.assertIn("Audit Log Requirements", content)
        self.assertNotIn("resident mode is enabled", lower_content)
        self.assertNotIn("desktop launch is approved", lower_content)
        self.assertNotIn("external integrations are approved", lower_content)

    def test_resident_authority_model_preserves_boundaries(self):
        content = RESIDENT_AUTHORITY_MODEL.read_text(encoding="utf-8")

        self.assertIn("Hermes is Michael's Mac mini personal agent", content)
        self.assertIn("Helio/ANO is the governed agent coordination layer", content)
        self.assertIn("Hermes does not own, command, or bypass Helio/ANO governance", content)
        self.assertIn("DevMonster provides model inference through Gemma", content)
        self.assertIn("DevMonster is not an operator", content)
        self.assertIn("Hermes may use DevMonster for local reasoning only", content)

    def test_audit_log_design_has_required_events_and_local_storage(self):
        content = AUDIT_LOG_DESIGN.read_text(encoding="utf-8")

        self.assertIn("no secrets in logs", content)
        self.assertIn("prompt/file contents redacted by default", content)
        self.assertIn("metadata-first logging", content)
        self.assertIn("approval_requested", content)
        self.assertIn("approval_granted", content)
        self.assertIn("approval_denied", content)
        self.assertIn("emergency_stop", content)
        self.assertIn("fail_closed", content)
        self.assertIn("logs/hermes_audit/", content)
        self.assertIn("no cloud sync by default", content)
        self.assertIn("no external writes", content)

    def test_audit_log_design_is_proposal_only(self):
        content = AUDIT_LOG_DESIGN.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("proposal only; audit logging not implemented yet", content)
        self.assertIn("Phase 6B does not approve", content)
        self.assertIn("no secret values", content)
        self.assertNotIn("resident hermes is enabled", lower_content)
        self.assertNotIn("audit writes are implemented", lower_content)

    def test_emergency_stop_design_keeps_runtime_disabled(self):
        content = EMERGENCY_STOP_DESIGN.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("proposal only; emergency stop not implemented yet", content)
        self.assertIn("resident mode not enabled yet", content)
        self.assertIn("stop adapter service", content)
        self.assertIn("require no sudo", content)
        self.assertIn("no deletion", content)
        self.assertIn("safe to run repeatedly", content)
        self.assertIn("Do not create this script in Phase 6C", content)
        self.assertNotIn("resident mode is enabled", lower_content)
        self.assertNotIn("emergency stop script is implemented", lower_content)

    def test_emergency_stop_design_has_triggers_and_acceptance(self):
        content = EMERGENCY_STOP_DESIGN.read_text(encoding="utf-8")

        self.assertIn("non-localhost listener", content)
        self.assertIn("credential exposure suspicion", content)
        self.assertIn("Desktop unexpectedly running", content)
        self.assertIn("resident-like process unexpectedly running", content)
        self.assertIn("scripts/hermes_emergency_stop.sh", content)
        self.assertIn("audit log records `emergency_stop`", content)
        self.assertIn("resident service can be disabled without deleting artifacts", content)

    def test_resident_service_proposal_is_proposal_only(self):
        content = RESIDENT_SERVICE_PROPOSAL.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("proposal only; no resident service created", content)
        self.assertIn("Do not create this script in Phase 6D", content)
        self.assertIn("com.msr.hermes.resident", content)
        self.assertIn("RunAtLoad=false", content)
        self.assertIn("KeepAlive=false", content)
        self.assertIn("manual start only at first", content)
        self.assertNotIn("resident mode is enabled", lower_content)
        self.assertNotIn("resident service created", lower_content.replace("no resident service created", ""))

    def test_resident_service_proposal_preserves_boundaries(self):
        content = RESIDENT_SERVICE_PROPOSAL.read_text(encoding="utf-8")

        self.assertIn("audit logging required before any execution", content)
        self.assertIn("emergency stop compatible", content)
        self.assertIn("no shell execution", content)
        self.assertIn("no external integrations", content)
        self.assertIn("no Desktop", content)
        self.assertIn("no credentials", content)
        self.assertIn("Allowed File Zones", content)
        self.assertIn("Forbidden Zones", content)
        self.assertIn("logs/hermes_audit/", content)

    def test_helio_delegation_interface_preserves_boundaries(self):
        content = HELIO_DELEGATION_INTERFACE.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Agent Bus frozen", content)
        self.assertIn("Hermes owns the Mac mini local operator role", content)
        self.assertIn("Helio/ANO owns agent society and governance", content)
        self.assertIn("DevMonster supplies inference, not operational authority", content)
        self.assertIn("direct Agent Bus writes", content)
        self.assertIn("Supabase writes", content)
        self.assertIn("Hermes impersonating ANO supervisor", content)
        self.assertNotIn("agent bus writes are approved", lower_content)
        self.assertNotIn("supabase writes are approved", lower_content)

    def test_helio_delegation_interface_has_staged_rollout_and_prereqs(self):
        content = HELIO_DELEGATION_INTERFACE.read_text(encoding="utf-8")

        for stage in (
            "Stage 0: Documentation Only",
            "Stage 1: Local File-Based Delegation Drafts",
            "Stage 2: Read-Only Agent Bus Inspection",
            "Stage 3: Draft Agent Bus Messages Only",
            "Stage 4: Human-Approved Agent Bus Writes",
            "Stage 5: Resident Delegated Operator",
        ):
            self.assertIn(stage, content)

        self.assertIn("audit log implemented", content)
        self.assertIn("emergency stop implemented", content)
        self.assertIn("credential rotation decision complete", content)
        self.assertIn("no secrets in messages", content)

    def test_command_policy_blocks_execution_until_prereqs(self):
        content = COMMAND_POLICY.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("Hermes cannot execute commands yet", content)
        self.assertIn("Hermes may only draft or recommend commands", content)
        self.assertIn("Future execution requires human approval, audit log, emergency stop, and allowlist match", content)
        self.assertIn("Initial Allowlist Candidates", content)
        self.assertIn("Initial Denylist", content)
        self.assertNotIn("command execution is enabled", lower_content)

    def test_command_policy_has_denials_and_approval_classes(self):
        content = COMMAND_POLICY.read_text(encoding="utf-8")

        self.assertIn("sudo", content)
        self.assertIn("rm -rf", content)
        self.assertIn("git push --force", content)
        self.assertIn("git reset --hard", content)
        self.assertIn("any command reading `~/.ssh`, `~/.gnupg`, Keychains, `.env`, token, key, or secret files", content)
        self.assertIn("scripts/adapter_service_start.sh` only with explicit human approval", content)
        self.assertIn("approval needed for `git push`", content)
        self.assertIn("audit log implemented", content)
        self.assertIn("emergency stop implemented", content)

    def test_file_zone_policy_defines_zone_classes(self):
        content = FILE_ZONE_POLICY.read_text(encoding="utf-8")

        self.assertIn("Green Read/Write Zones", content)
        self.assertIn("Yellow Read-Only Zones", content)
        self.assertIn("Orange Approval-Required Zones", content)
        self.assertIn("Red Forbidden Zones", content)
        self.assertIn("sandbox/hermes_inbox/", content)
        self.assertIn("sandbox/hermes_outbox/", content)
        self.assertIn("logs/hermes_audit/", content)

    def test_file_zone_policy_blocks_secret_and_broad_paths(self):
        content = FILE_ZONE_POLICY.read_text(encoding="utf-8")

        self.assertIn("~/.ssh", content)
        self.assertIn("~/.gnupg", content)
        self.assertIn("~/Library/Keychains", content)
        self.assertIn(".env", content)
        self.assertIn("token/key/secret files", content)
        self.assertIn("arbitrary Desktop scanning", content)
        self.assertIn("arbitrary Documents scanning", content)
        self.assertIn("path traversal refusal", content)
        self.assertIn("symlink refusal or resolution", content)
        self.assertIn("audit event on every file read/write", content)

    def test_approval_record_model_has_required_fields_and_no_blankets(self):
        content = APPROVAL_RECORD_MODEL.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertIn("expiration", content)
        self.assertIn("audit_event_id", content)
        self.assertIn("no secret values", content)
        self.assertIn("blanket permanent approval", content)
        self.assertIn("approval by model alone", content)
        self.assertNotIn("blanket permanent approval is allowed", lower_content)
        self.assertNotIn("model-only approval is allowed", lower_content)

    def test_approval_record_model_covers_sensitive_action_types(self):
        content = APPROVAL_RECORD_MODEL.read_text(encoding="utf-8")

        for approval_type in (
            "service_start",
            "command_execute",
            "git_push",
            "resident_start",
            "emergency_stop",
        ):
            self.assertIn(approval_type, content)

        self.assertIn("local JSONL", content)
        self.assertIn("no cloud sync by default", content)
        self.assertIn("linked to audit events", content)

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
