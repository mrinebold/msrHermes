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
        config = AdapterConfig.from_env(
            {
                "MODEL_ROUTER_ADAPTER_LOG_REQUESTS": "true",
                "MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES": "true",
                "MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE": "true",
            }
        )

        self.assertTrue(config.log_requests)
        self.assertTrue(config.log_response_shapes)
        self.assertTrue(config.log_message_structure)

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

    def test_chat_completions_stream_false_uses_json_response(self):
        status, headers, body = self._post_raw(
            "/v1/chat/completions",
            {
                "model": "gemma4:26b",
                "stream": False,
                "messages": [{"role": "user", "content": "Summarize sandbox note."}],
            },
        )

        self.assertEqual(status, 200)
        self.assertEqual(headers["content-type"], "application/json")
        payload = json.loads(body)
        self.assertEqual(payload["object"], "chat.completion")
        self.assertEqual(payload["choices"][0]["message"]["content"], "Sandbox summary.")

    def test_streaming_chat_completions_returns_event_stream(self):
        status, headers, body = self._post_raw(
            "/v1/chat/completions",
            {
                "model": "gemma4:26b",
                "stream": True,
                "messages": [{"role": "user", "content": "Summarize sandbox note."}],
            },
        )

        self.assertEqual(status, 200)
        self.assertEqual(headers["content-type"], "text/event-stream")
        self.assertEqual(headers["cache-control"], "no-cache")
        self.assertEqual(headers["connection"], "keep-alive")
        self.assertTrue(body.endswith("data: [DONE]\n\n"))

    def test_streaming_chat_completions_includes_delta_content(self):
        status, _, body = self._post_raw(
            "/v1/chat/completions",
            {
                "model": "gemma4:26b",
                "stream": True,
                "messages": [{"role": "user", "content": "Summarize sandbox note."}],
            },
        )

        self.assertEqual(status, 200)
        chunks = self._sse_json_chunks(body)
        self.assertEqual(chunks[0]["object"], "chat.completion.chunk")
        self.assertEqual(chunks[0]["model"], "gemma4:26b")
        self.assertEqual(chunks[0]["choices"][0]["delta"]["content"], "Sandbox summary.")
        self.assertIsNone(chunks[0]["choices"][0]["finish_reason"])
        self.assertEqual(chunks[1]["choices"][0]["delta"], {})
        self.assertEqual(chunks[1]["choices"][0]["finish_reason"], "stop")

    def test_refuses_unknown_get_endpoint(self):
        status, payload = self._get("/v1/embeddings")

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["type"], "not_found")

    def test_chat_completion_request_log_redacts_prompt_content(self):
        self.config = AdapterConfig(host="127.0.0.1", port=8088, default_task_type="summary", log_requests=True)
        self.handler_cls = make_handler(self.router, self.config)

        with self.assertLogs("services.model_router_adapter.server", level="INFO") as logs:
            status, _, _ = self._post_raw(
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

    def test_chat_completion_response_shape_log_redacts_content(self):
        self.config = AdapterConfig(
            host="127.0.0.1",
            port=8088,
            default_task_type="summary",
            log_response_shapes=True,
        )
        self.handler_cls = make_handler(self.router, self.config)

        with self.assertLogs("services.model_router_adapter.server", level="INFO") as logs:
            status, _, _ = self._post_raw(
                "/v1/chat/completions",
                {
                    "model": "gemma4:26b",
                    "stream": True,
                    "messages": [{"role": "user", "content": "Sensitive sandbox prompt text."}],
                },
            )

        self.assertEqual(status, 200)
        record = self._response_shape_log_record(logs.records)
        self.assertEqual(record.path, "/v1/chat/completions")
        self.assertEqual(record.top_level_keys, ["choices", "created", "id", "model", "msr_route", "object", "usage"])
        self.assertEqual(record.choices_count, 1)
        self.assertEqual(record.content_length, len("Sandbox summary."))
        self.assertEqual(record.finish_reason, "stop")
        self.assertTrue(record.streaming_requested)
        joined = "\n".join(log.getMessage() for log in logs.records)
        self.assertIn("model_router_adapter.response_shape", joined)
        self.assertNotIn("Sensitive sandbox prompt text", joined)
        self.assertNotIn("Sandbox summary.", joined)

    def test_message_structure_log_redacts_prompt_and_file_content(self):
        self.config = AdapterConfig(
            host="127.0.0.1",
            port=8088,
            default_task_type="summary",
            log_message_structure=True,
        )
        self.handler_cls = make_handler(self.router, self.config)

        with self.assertLogs("services.model_router_adapter.server", level="INFO") as logs:
            status, _, _ = self._post_raw(
                "/v1/chat/completions",
                {
                    "model": "gemma4:26b",
                    "stream": True,
                    "temperature": 0,
                    "max_tokens": 200,
                    "tool_choice": "auto",
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "read_file",
                                "description": "Do not leak this tool description.",
                            },
                        }
                    ],
                    "messages": [
                        {"role": "system", "content": "Sensitive system instruction."},
                        {
                            "role": "user",
                            "content": "# Sample Local Note\nExternal integrations remain disabled.\nDo not leak this sandbox file content.\n",
                        },
                    ],
                },
            )

        self.assertEqual(status, 200)
        record = self._message_structure_log_record(logs.records)
        self.assertEqual(record.path, "/v1/chat/completions")
        self.assertEqual(record.message_count, 2)
        self.assertEqual(record.roles_present, ["system", "user"])
        self.assertEqual(len(record.message_char_counts), 2)
        self.assertFalse(record.final_user_message_empty)
        self.assertTrue(record.any_message_contains_file_content)
        self.assertTrue(record.tools_present)
        self.assertTrue(record.tool_choice_present)
        self.assertTrue(record.max_tokens_present)
        self.assertTrue(record.temperature_present)
        self.assertTrue(record.stream_present)
        self.assertTrue(record.streaming_requested)
        joined = "\n".join(log.getMessage() for log in logs.records)
        self.assertIn("model_router_adapter.message_structure", joined)
        self.assertNotIn("Sensitive system instruction", joined)
        self.assertNotIn("External integrations remain disabled", joined)
        self.assertNotIn("Do not leak this sandbox file content", joined)
        self.assertNotIn("Do not leak this tool description", joined)

    def test_message_structure_log_detects_empty_final_user_message(self):
        self.config = AdapterConfig(
            host="127.0.0.1",
            port=8088,
            default_task_type="summary",
            log_message_structure=True,
        )
        self.handler_cls = make_handler(self.router, self.config)

        with self.assertLogs("services.model_router_adapter.server", level="INFO") as logs:
            status, _, _ = self._post_raw(
                "/v1/chat/completions",
                {
                    "model": "gemma4:26b",
                    "messages": [
                        {"role": "system", "content": "Hidden context."},
                        {"role": "user", "content": "   "},
                    ],
                },
            )

        self.assertEqual(status, 200)
        record = self._message_structure_log_record(logs.records)
        self.assertTrue(record.final_user_message_empty)
        joined = "\n".join(log.getMessage() for log in logs.records)
        self.assertNotIn("Hidden context", joined)

    def test_phase5q_shape_with_tools_routes_flattened_messages_only(self):
        payload = self._phase5q_payload()

        status, _, _ = self._post_raw("/v1/chat/completions", payload)

        self.assertEqual(status, 200)
        self.assertIn("system: ", self.router.last_request.prompt)
        self.assertIn("user: ", self.router.last_request.prompt)
        self.assertIn("SANITIZED_CONTEXT_LINE", self.router.last_request.prompt)
        self.assertIn("SANITIZED_SUMMARY_REQUEST", self.router.last_request.prompt)
        self.assertNotIn("read_sandbox_file", self.router.last_request.prompt)
        self.assertNotIn("SANITIZED_TOOL_DESCRIPTION", self.router.last_request.prompt)

    def test_phase5q_shape_with_tools_stripped_routes_same_prompt(self):
        payload_with_tools = self._phase5q_payload()
        payload_without_tools = self._phase5q_payload()
        payload_without_tools.pop("tools")

        status, _, _ = self._post_raw("/v1/chat/completions", payload_with_tools)
        prompt_with_tools = self.router.last_request.prompt
        self.assertEqual(status, 200)
        status, _, _ = self._post_raw("/v1/chat/completions", payload_without_tools)
        prompt_without_tools = self.router.last_request.prompt

        self.assertEqual(status, 200)
        self.assertEqual(prompt_with_tools, prompt_without_tools)

    def test_phase5q_shape_with_flattened_messages_routes_single_user_prompt(self):
        payload = self._phase5q_payload()
        payload["messages"] = [
            {
                "role": "user",
                "content": (
                    "Context:\n"
                    + self._sanitized_context()
                    + "\n\nInstruction:\nSANITIZED_SUMMARY_REQUEST"
                ),
            }
        ]

        status, _, _ = self._post_raw("/v1/chat/completions", payload)

        self.assertEqual(status, 200)
        self.assertIn("user: Context:", self.router.last_request.prompt)
        self.assertIn("SANITIZED_CONTEXT_LINE", self.router.last_request.prompt)
        self.assertIn("SANITIZED_SUMMARY_REQUEST", self.router.last_request.prompt)
        self.assertNotIn("system: ", self.router.last_request.prompt)
        self.assertNotIn("read_sandbox_file", self.router.last_request.prompt)

    def test_phase5q_shape_with_tools_stripped_and_flattened_routes_single_user_prompt(self):
        payload = self._phase5q_payload()
        payload.pop("tools")
        payload["messages"] = [
            {
                "role": "user",
                "content": (
                    "Context:\n"
                    + self._sanitized_context()
                    + "\n\nInstruction:\nSANITIZED_SUMMARY_REQUEST"
                ),
            }
        ]

        status, _, _ = self._post_raw("/v1/chat/completions", payload)

        self.assertEqual(status, 200)
        self.assertIn("user: Context:", self.router.last_request.prompt)
        self.assertIn("SANITIZED_CONTEXT_LINE", self.router.last_request.prompt)
        self.assertIn("SANITIZED_SUMMARY_REQUEST", self.router.last_request.prompt)
        self.assertNotIn("system: ", self.router.last_request.prompt)
        self.assertNotIn("read_sandbox_file", self.router.last_request.prompt)

    def test_refuses_unknown_post_endpoint(self):
        status, payload = self._post("/v1/responses", {"input": "not allowed"})

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["type"], "not_found")

    def _get(self, path):
        return self._request("GET", path, None)

    def _post(self, path, payload):
        return self._request("POST", path, payload)

    def _post_raw(self, path, payload):
        return self._request_raw("POST", path, payload)

    def _request(self, method, path, payload):
        status, _, response_body = self._request_raw(method, path, payload)
        return status, json.loads(response_body)

    def _request_raw(self, method, path, payload):
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
        header_lines = [line.decode("utf-8") for line in header_block.splitlines()]
        status_line = header_lines[0]
        status = int(status_line.split()[1])
        headers = {}
        for line in header_lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.lower()] = value.strip()
        return status, headers, response_body.decode("utf-8")

    def _sse_json_chunks(self, body):
        chunks = []
        for frame in body.split("\n\n"):
            if not frame.strip() or frame == "data: [DONE]":
                continue
            self.assertTrue(frame.startswith("data: "))
            chunks.append(json.loads(frame[len("data: ") :]))
        return chunks

    def _request_log_record(self, records):
        for record in records:
            if getattr(record, "event", "") == "model_router_adapter.request":
                return record
        self.fail("request log record was not emitted")

    def _response_shape_log_record(self, records):
        for record in records:
            if getattr(record, "event", "") == "model_router_adapter.response_shape":
                return record
        self.fail("response shape log record was not emitted")

    def _message_structure_log_record(self, records):
        for record in records:
            if getattr(record, "event", "") == "model_router_adapter.message_structure":
                return record
        self.fail("message structure log record was not emitted")

    def _phase5q_payload(self):
        return {
            "model": "gemma4:26b",
            "stream": True,
            "messages": [
                {"role": "system", "content": self._sanitized_context()},
                {"role": "user", "content": "SANITIZED_SUMMARY_REQUEST"},
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "read_sandbox_file",
                        "description": "SANITIZED_TOOL_DESCRIPTION",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            ],
        }

    def _sanitized_context(self):
        return "\n".join(["SANITIZED_CONTEXT_LINE"] * 40)


if __name__ == "__main__":
    unittest.main()
