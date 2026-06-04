import json
import unittest
from email.message import Message
from io import BytesIO

from services.model_router.providers.devmonster_ollama import ProviderResult
from services.model_router.router import RouteResponse
from services.model_router_adapter.config import AdapterConfig
from services.model_router_adapter.server import make_handler


class FakeRouter:
    def __init__(self):
        self.last_request = None

    def list_models(self):
        return ProviderResult(ok=True, data={"models": [{"name": "gemma4:26b"}]})

    def generate(self, request):
        self.last_request = request
        return RouteResponse(
            provider="devmonster_ollama",
            model=request.model or "gemma4:26b",
            text="Sandbox summary.",
            task_type=request.task_type,
            timestamp="2026-06-04T00:00:00+00:00",
            elapsed_seconds=0.123,
            human_approval_required=False,
        )


class ModelRouterAdapterTest(unittest.TestCase):
    def setUp(self):
        self.router = FakeRouter()
        self.config = AdapterConfig(host="127.0.0.1", port=8088, default_task_type="summary")
        self.handler_cls = make_handler(self.router, self.config)

    def test_default_bind_host_is_localhost(self):
        config = AdapterConfig.from_env({})

        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 8088)

    def test_request_logging_flag_from_env(self):
        config = AdapterConfig.from_env({"MODEL_ROUTER_ADAPTER_LOG_REQUESTS": "true"})

        self.assertTrue(config.log_requests)

    def test_health(self):
        status, payload = self._get("/health")

        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "model_router_adapter")

    def test_models(self):
        status, payload = self._get("/v1/models")

        self.assertEqual(status, 200)
        self.assertEqual(payload["object"], "list")
        self.assertEqual(payload["data"][0]["id"], "gemma4:26b")

    def test_chat_completions(self):
        status, payload = self._post(
            "/v1/chat/completions",
            {
                "model": "gemma4:26b",
                "messages": [{"role": "user", "content": "Summarize sandbox note."}],
            },
        )

        self.assertEqual(status, 200)
        self.assertEqual(payload["object"], "chat.completion")
        self.assertEqual(payload["choices"][0]["message"]["content"], "Sandbox summary.")
        self.assertEqual(self.router.last_request.task_type, "summary")
        self.assertEqual(self.router.last_request.model, "gemma4:26b")
        self.assertIn("Summarize sandbox note.", self.router.last_request.prompt)

    def test_refuses_unknown_get_endpoint(self):
        status, payload = self._get("/v1/embeddings")

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["type"], "not_found")

    def test_chat_completion_request_log_redacts_prompt_content(self):
        self.config = AdapterConfig(host="127.0.0.1", port=8088, default_task_type="summary", log_requests=True)
        self.handler_cls = make_handler(self.router, self.config)

        with self.assertLogs("services.model_router_adapter.server", level="INFO") as logs:
            status, _ = self._post(
                "/v1/chat/completions",
                {
                    "model": "gemma4:26b",
                    "messages": [{"role": "user", "content": "Sensitive sandbox prompt text."}],
                },
            )

        self.assertEqual(status, 200)
        record = self._request_log_record(logs.records)
        self.assertEqual(record.method, "POST")
        self.assertEqual(record.path, "/v1/chat/completions")
        self.assertEqual(record.status, 200)
        self.assertEqual(record.selected_model, "gemma4:26b")
        self.assertGreaterEqual(record.elapsed_seconds, 0)
        self.assertTrue(record.timestamp)
        joined = "\n".join(log.getMessage() for log in logs.records)
        self.assertIn("model_router_adapter.request", joined)
        self.assertNotIn("Sensitive sandbox prompt text", joined)
        self.assertNotIn("messages", joined)

    def test_unknown_endpoint_logs_status_only(self):
        self.config = AdapterConfig(host="127.0.0.1", port=8088, default_task_type="summary", log_requests=True)
        self.handler_cls = make_handler(self.router, self.config)

        with self.assertLogs("services.model_router_adapter.server", level="INFO") as logs:
            status, _ = self._get("/v1/embeddings")

        self.assertEqual(status, 404)
        record = self._request_log_record(logs.records)
        self.assertEqual(record.method, "GET")
        self.assertEqual(record.path, "/v1/embeddings")
        self.assertEqual(record.status, 404)
        self.assertEqual(record.selected_model, "")
        joined = "\n".join(log.getMessage() for log in logs.records)
        self.assertNotIn("prompt", joined.lower())
        self.assertNotIn("secret", joined.lower())

    def test_refuses_unknown_post_endpoint(self):
        status, payload = self._post("/v1/responses", {"input": "not allowed"})

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["type"], "not_found")

    def _get(self, path):
        return self._request("GET", path, None)

    def _post(self, path, payload):
        return self._request("POST", path, payload)

    def _request(self, method, path, payload):
        body = b"" if payload is None else json.dumps(payload).encode("utf-8")
        handler = self.handler_cls.__new__(self.handler_cls)
        handler.command = method
        handler.path = path
        handler.request_version = "HTTP/1.1"
        handler.requestline = f"{method} {path} HTTP/1.1"
        handler.client_address = ("127.0.0.1", 12345)
        handler.rfile = BytesIO(body)
        handler.wfile = BytesIO()
        handler.headers = Message()
        if body:
            handler.headers["Content-Length"] = str(len(body))
            handler.headers["Content-Type"] = "application/json"

        if method == "GET":
            handler.do_GET()
        else:
            handler.do_POST()

        raw = handler.wfile.getvalue()
        header_block, response_body = raw.split(b"\r\n\r\n", 1)
        status_line = header_block.splitlines()[0].decode("utf-8")
        status = int(status_line.split()[1])
        return status, json.loads(response_body.decode("utf-8"))

    def _request_log_record(self, records):
        for record in records:
            if record.getMessage() == "model_router_adapter.request":
                return record
        self.fail("request log record was not emitted")


if __name__ == "__main__":
    unittest.main()
