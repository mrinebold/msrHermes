import json
import os
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from unittest.mock import patch

from services.hermes_gateway import app
from services.hermes_gateway.server import GatewayHandler, create_server


class GatewayPolicyTests(unittest.TestCase):
    def test_gateway_refuses_wildcard_bind(self):
        for host in ("0.0.0.0", "::", "*"):
            with self.subTest(host=host), self.assertRaises(app.GatewayPolicyError):
                app.validate_bind_host(host)

    def test_gateway_defaults_to_localhost(self):
        with patch.dict(os.environ, {"HERMES_GATEWAY_TOKEN": "local-test-token"}, clear=True):
            config = app.load_config()
        self.assertEqual(config.host, "127.0.0.1")
        self.assertFalse(config.gateway_bind_is_tailscale)

    def test_gateway_requires_a_token(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(app.GatewayPolicyError):
            app.load_config()

    def test_tailscale_bind_requires_explicit_opt_in_and_token(self):
        with patch.dict(os.environ, {"HERMES_GATEWAY_BIND_HOST": "100.80.79.75", "HERMES_GATEWAY_TOKEN": "short"}, clear=True):
            with self.assertRaises(app.GatewayPolicyError):
                app.load_config()
        with patch.dict(os.environ, {"HERMES_GATEWAY_BIND_HOST": "100.80.79.75", "HERMES_GATEWAY_ALLOW_TAILSCALE_BIND": "1"}, clear=True):
            with self.assertRaises(app.GatewayPolicyError):
                app.load_config()
        with patch.dict(os.environ, {"HERMES_GATEWAY_BIND_HOST": "100.80.79.75", "HERMES_GATEWAY_ALLOW_TAILSCALE_BIND": "1", "HERMES_GATEWAY_TOKEN": "0123456789abcdef"}, clear=True):
            config = app.load_config()
        self.assertTrue(config.gateway_bind_is_tailscale)

    def test_inbox_filename_sanitization_and_traversal_denial(self):
        self.assertEqual(app.validate_safe_filename("task name.md"), "task_name.md")
        for name in ("../secret", "..\\secret", "/tmp/secret", ".."):
            with self.subTest(name=name), self.assertRaises(app.GatewayPolicyError):
                app.validate_safe_filename(name)

    def test_outbox_read_path_is_safe(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "safe.md").write_text("safe", encoding="utf-8")
            self.assertEqual(app.read_safe_file(directory, "safe.md", 100), "safe")
            with self.assertRaises(app.GatewayPolicyError):
                app.read_safe_file(directory, "../safe.md", 100)

    def test_no_arbitrary_command_endpoint_exists(self):
        self.assertNotIn("/exec", GatewayHandler.do_POST.__code__.co_consts)
        self.assertNotIn("/command", GatewayHandler.do_POST.__code__.co_consts)

    def test_docs_preserve_private_access_policy(self):
        browser_doc = Path("docs/HERMES_BROWSER_GATEWAY.md").read_text(encoding="utf-8")
        ipad_doc = Path("docs/HERMES_REMOTE_IPAD_ACCESS.md").read_text(encoding="utf-8")
        self.assertIn("Public internet exposure", browser_doc)
        self.assertIn("Tailscale Funnel", browser_doc)
        self.assertIn("iPad", ipad_doc)
        self.assertIn("Tailscale", ipad_doc)


class GatewayHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "sandbox" / "hermes_inbox").mkdir(parents=True)
        (self.root / "sandbox" / "hermes_outbox").mkdir(parents=True)
        (self.root / "scripts").mkdir()
        self.token = "gateway-test-token-0123456789"
        self.config = app.GatewayConfig(repo_root=self.root, token=self.token)
        self.server = create_server(self.config)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, method, path, body=None):
        connection = HTTPConnection(self.server.server_address[0], self.server.server_address[1])
        payload = json.dumps(body).encode() if body is not None else None
        headers = {"Authorization": f"Bearer {self.token}"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        connection.request(method, path, payload, headers)
        response = connection.getresponse()
        content = response.read()
        connection.close()
        return response.status, json.loads(content) if content else {}

    def test_status_contains_disabled_and_fail_closed_flags(self):
        status, body = self.request("GET", "/api/status")
        self.assertEqual(status, 200)
        self.assertFalse(body["command_execution"]["enabled"])
        self.assertEqual(body["desktop"]["state"], "fail_closed")

    def test_pilot_readiness_is_private_and_non_executing(self):
        status, body = self.request("GET", "/api/pilot-readiness")
        self.assertEqual(status, 200)
        self.assertEqual(body["private_gemma"]["cloud_fallback"], "disabled_for_phase_1")
        self.assertEqual(body["helio_bridge"]["direct_supabase"], False)
        self.assertEqual(body["helio_bridge"]["direct_agent_bus_writes"], False)
        self.assertFalse(body["browser_chat"]["enabled"])

    def test_inbox_post_and_outbox_path_traversal_denial(self):
        status, body = self.request("POST", "/api/inbox", {"name": "test task.md", "content": "hello"})
        self.assertEqual(status, 201)
        self.assertEqual(body["name"], "test_task.md")
        status, body = self.request("POST", "/api/inbox", {"name": "../escape", "content": "no"})
        self.assertEqual(status, 403)
        status, body = self.request("GET", "/api/outbox/../escape")
        self.assertIn(status, (403, 404))

    def test_resident_and_emergency_use_only_approved_script_paths(self):
        calls = []

        def fake_run(config, name, args=()):
            calls.append((name, list(args)))
            return {"ok": True, "script": name}

        with patch("services.hermes_gateway.server.run_approved_script", side_effect=fake_run):
            status, _ = self.request("POST", "/api/resident/run-once", {})
            self.assertEqual(status, 200)
            status, _ = self.request("POST", "/api/emergency-stop", {"reason": "test"})
            self.assertEqual(status, 200)
        self.assertEqual(calls, [("resident_once", []), ("emergency_stop", ["test"])])


if __name__ == "__main__":
    unittest.main()
