import importlib.util
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "agent_bus_readonly_preflight.py"
SPEC = importlib.util.spec_from_file_location("agent_bus_readonly_preflight", SCRIPT_PATH)
preflight = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = preflight
SPEC.loader.exec_module(preflight)


def configured_env(mode="read_only"):
    return {
        "SUPABASE_URL": "https://example.supabase.co",
        "SUPABASE_ANON_KEY": "anon-secret-value",
        "HELIO_AGENT_BUS_MODE": mode,
        "HELIO_AGENT_ID": "hermes",
        "HELIO_DEFAULT_ORG": "msr",
        "HELIO_DEFAULT_WORKSPACE": "default",
    }


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class RecordingOpener:
    def __init__(self, payload):
        self.payload = payload
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append((request, timeout))
        return FakeResponse(self.payload)


class PermissionDeniedOpener:
    def __call__(self, request, timeout):
        body = b'{"message":"permission denied for table","token":"anon-secret-value"}'
        raise HTTPError(request.full_url, 403, "Forbidden", hdrs=None, fp=io.BytesIO(body))


class ReadOnlyPreflightTest(unittest.TestCase):
    def test_missing_env_fails_closed(self):
        config = preflight.load_config({})

        with self.assertRaises(preflight.PreflightError) as caught:
            preflight.verify_config(config)

        self.assertEqual(caught.exception.reason, "missing_or_invalid_config")
        self.assertIn("HELIO_AGENT_BUS_MODE=read_only", caught.exception.detail)
        self.assertIn("HELIO_AGENT_ID=hermes", caught.exception.detail)

    def test_non_read_only_mode_fails_closed(self):
        config = preflight.load_config(configured_env(mode="dry_run"))

        with self.assertRaises(preflight.PreflightError) as caught:
            preflight.verify_config(config)

        self.assertEqual(caught.exception.reason, "missing_or_invalid_config")
        self.assertIn("HELIO_AGENT_BUS_MODE=read_only", caught.exception.detail)

    def test_agent_id_must_be_hermes(self):
        env = configured_env()
        env["HELIO_AGENT_ID"] = "byte"
        config = preflight.load_config(env)

        with self.assertRaises(preflight.PreflightError) as caught:
            preflight.verify_config(config)

        self.assertEqual(caught.exception.reason, "missing_or_invalid_config")
        self.assertIn("HELIO_AGENT_ID=hermes", caught.exception.detail)

    def test_org_config_query_is_scoped_and_get_only(self):
        config = preflight.load_config(configured_env())
        opener = RecordingOpener(
            [
                {
                    "org_id": "msr",
                    "config_type": "agent_roster",
                    "config_data": {"agents": ["helio", "hermes"]},
                    "updated_at": "2026-06-03T12:00:00Z",
                }
            ]
        )

        result = preflight.list_org_configs(config, opener=opener)

        self.assertEqual(result["row_count"], 1)
        request, timeout = opener.requests[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(timeout, 10)
        parsed = urlparse(request.full_url)
        params = parse_qs(parsed.query)
        self.assertEqual(parsed.path, "/rest/v1/org_messaging_config")
        self.assertEqual(params["org_id"], ["eq.msr"])
        self.assertEqual(params["limit"], ["25"])

    def test_hermes_messages_query_is_scoped_to_agent(self):
        config = preflight.load_config(configured_env())
        opener = RecordingOpener(
            [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "org_id": "msr",
                    "to_agent": "hermes",
                    "status": "pending",
                    "created_at": "2026-06-03T12:00:00Z",
                    "payload": {"directive": "secret-ish work detail"},
                }
            ]
        )

        result = preflight.read_hermes_messages(config, opener=opener)

        self.assertEqual(result["status_counts"], {"pending": 1})
        request, _timeout = opener.requests[0]
        params = parse_qs(urlparse(request.full_url).query)
        self.assertEqual(params["org_id"], ["eq.msr"])
        self.assertEqual(params["to_agent"], ["eq.hermes"])

    def test_non_get_request_is_blocked(self):
        config = preflight.load_config(configured_env())

        with self.assertRaises(preflight.PreflightError) as caught:
            preflight.request_json(config, "/rest/v1/agent_messages", method="POST")

        self.assertEqual(caught.exception.reason, "non_get_request_blocked")

    def test_samples_redact_payloads_and_message_text(self):
        config = preflight.load_config(configured_env())
        rows = [
            {
                "org_id": "msr",
                "to_agent": "hermes",
                "payload": {"directive": "private"},
                "message_text": "private outbound text",
                "chat_id": "12345",
                "status": "pending",
            }
        ]

        result = preflight.summarize_rows("sample", rows, config, include_samples=True)

        sample = result["samples"][0]
        self.assertEqual(sample["payload"], "[redacted]")
        self.assertEqual(sample["message_text"], "[redacted]")
        self.assertEqual(sample["chat_id"], "[redacted]")

    def test_anon_key_is_not_printed_on_success_or_permission_error(self):
        config = preflight.load_config(configured_env())
        stdout = io.StringIO()

        with patch.dict(os.environ, configured_env(), clear=True), redirect_stdout(stdout):
            exit_code = preflight.main(["verify-config"])

        self.assertEqual(exit_code, 0)
        self.assertNotIn("anon-secret-value", stdout.getvalue())

        with self.assertRaises(preflight.PreflightError) as caught:
            preflight.list_org_configs(config, opener=PermissionDeniedOpener())

        self.assertEqual(caught.exception.reason, "rls_or_permission_denied")
        self.assertNotIn("anon-secret-value", caught.exception.detail)

    def test_out_of_scope_records_fail_closed(self):
        config = preflight.load_config(configured_env())
        rows = [{"org_id": "other", "to_agent": "hermes"}]

        with self.assertRaises(preflight.PreflightError) as caught:
            preflight.summarize_rows("agent_messages_to_hermes", rows, config)

        self.assertEqual(caught.exception.reason, "out_of_scope_records_returned")


if __name__ == "__main__":
    unittest.main()
