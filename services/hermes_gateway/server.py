"""HTTP server for the private Phase 7I Hermes browser gateway."""

from __future__ import annotations

import json
import hmac
import sys
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

from .app import (
    GatewayConfig,
    GatewayDependencyError,
    GatewayPolicyError,
    MAX_INBOX_BYTES,
    MAX_REASON_CHARS,
    MAX_OUTBOX_BYTES,
    _append_audit,
    client_allowed,
    file_page,
    files_page,
    home_page,
    list_files,
    load_config,
    login_page,
    read_safe_file,
    run_approved_script,
    _read_summaries,
    session_cookie,
    status,
    private_gemma_status,
    helio_bridge_status,
    status_page,
    summaries_page,
    valid_session,
    validate_safe_filename,
)


class GatewayHandler(BaseHTTPRequestHandler):
    server_version = "HermesGateway/7I"

    @property
    def config(self) -> GatewayConfig:
        return self.server.gateway_config  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: object) -> None:
        # Do not log request paths: a caller must never be able to place a
        # credential in a query string and have it echoed into logs.
        sys.stderr.write("hermes-gateway: request completed\n")

    def _send(self, status_code: int, body: bytes, content_type: str = "text/html; charset=utf-8", headers: dict[str, str] | None = None) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status_code: int, value: object, headers: dict[str, str] | None = None) -> None:
        self._send(status_code, json.dumps(value, separators=(",", ":")).encode("utf-8"), "application/json; charset=utf-8", headers)

    def _read_json(self) -> dict[str, object]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise GatewayPolicyError("invalid content length") from exc
        if length > MAX_INBOX_BYTES:
            raise GatewayPolicyError("request body exceeds limit")
        try:
            value = json.loads(self.rfile.read(length) or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise GatewayPolicyError("request must be JSON") from exc
        if not isinstance(value, dict):
            raise GatewayPolicyError("request JSON must be an object")
        return value

    def _authenticated(self) -> bool:
        client_ip = self.client_address[0]
        if not client_allowed(self.config, client_ip):
            self._json(HTTPStatus.FORBIDDEN, {"error": "client network is not approved"})
            return False
        authorization = self.headers.get("Authorization", "")
        bearer = authorization[7:].strip() if authorization.startswith("Bearer ") else ""
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        browser_session = cookie.get("hermes_gateway_session")
        if hmac.compare_digest(bearer, self.config.token) or valid_session(self.config.token, browser_session.value if browser_session else ""):
            return True
        self._json(HTTPStatus.UNAUTHORIZED, {"error": "gateway authentication required", "login": "/login"})
        return False

    def _protected_page(self, producer) -> None:
        if self._authenticated():
            self._send(HTTPStatus.OK, producer())

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/login":
            self._send(HTTPStatus.OK, login_page())
            return
        if not self._authenticated():
            return
        try:
            if path == "/" or path == "/status":
                data = status(self.config)
                self._send(HTTPStatus.OK, home_page(self.config) if path == "/" else status_page(data))
            elif path == "/api/status":
                self._json(HTTPStatus.OK, status(self.config))
            elif path == "/api/pilot-readiness":
                self._json(
                    HTTPStatus.OK,
                    {
                        "private_gemma": private_gemma_status(),
                        "helio_bridge": helio_bridge_status(),
                        "browser_chat": {"enabled": False, "next_phase": "workbench_chat"},
                    },
                )
            elif path == "/inbox":
                self._send(HTTPStatus.OK, files_page("inbox", list_files(self.config.inbox_dir), self.config))
            elif path == "/api/inbox":
                self._json(HTTPStatus.OK, {"files": list_files(self.config.inbox_dir)})
            elif path == "/outbox":
                self._send(HTTPStatus.OK, files_page("outbox", list_files(self.config.outbox_dir), self.config))
            elif path == "/api/outbox":
                self._json(HTTPStatus.OK, {"files": list_files(self.config.outbox_dir)})
            elif path.startswith("/outbox/"):
                name = unquote(path.removeprefix("/outbox/"))
                self._send(HTTPStatus.OK, file_page("outbox", validate_safe_filename(name), read_safe_file(self.config.outbox_dir, name, MAX_OUTBOX_BYTES)))
            elif path.startswith("/api/outbox/"):
                name = unquote(path.removeprefix("/api/outbox/"))
                self._json(HTTPStatus.OK, {"name": validate_safe_filename(name), "content": read_safe_file(self.config.outbox_dir, name, MAX_OUTBOX_BYTES)})
            elif path == "/audit":
                entries = _read_summaries(self.config.audit_path)
                self._send(HTTPStatus.OK, summaries_page("audit", entries))
            elif path == "/api/audit":
                entries = _read_summaries(self.config.audit_path)
                self._json(HTTPStatus.OK, {"entries": entries})
            elif path == "/approvals":
                entries = _read_summaries(self.config.approvals_path)
                self._send(HTTPStatus.OK, summaries_page("approvals", entries))
            elif path == "/api/approvals":
                entries = _read_summaries(self.config.approvals_path)
                self._json(HTTPStatus.OK, {"entries": entries})
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
        except GatewayPolicyError as exc:
            _append_audit(self.config, "gateway_policy_violation", "denied", str(exc))
            self._json(HTTPStatus.FORBIDDEN, {"error": str(exc)})
        except GatewayDependencyError as exc:
            self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(exc)})
        except OSError:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "safe file operation failed"})

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path == "/login":
            if not client_allowed(self.config, self.client_address[0]):
                self._json(HTTPStatus.FORBIDDEN, {"error": "client network is not approved"})
                return
            try:
                body = self._read_json()
                token = body.get("token")
                # Constant-time comparison without logging or returning the submitted token.
                if not isinstance(token, str) or not __import__("hmac").compare_digest(token, self.config.token):
                    self._json(HTTPStatus.UNAUTHORIZED, {"error": "invalid gateway token"})
                    return
                self._json(HTTPStatus.OK, {"message": "signed in"}, {"Set-Cookie": f"hermes_gateway_session={session_cookie(self.config.token)}; HttpOnly; SameSite=Strict; Path=/"})
            except GatewayPolicyError as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return
        if not self._authenticated():
            return
        try:
            body = self._read_json()
            if path == "/api/inbox" or path == "/inbox":
                name = validate_safe_filename(body.get("name"))
                content = body.get("content")
                if not isinstance(content, str) or not content.strip():
                    raise GatewayPolicyError("inbox content is required")
                encoded = content.encode("utf-8")
                if len(encoded) > MAX_INBOX_BYTES:
                    raise GatewayPolicyError("inbox content exceeds limit")
                destination = self.config.inbox_dir / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination = destination.resolve()
                if destination.parent != self.config.inbox_dir.resolve() or destination.is_symlink():
                    raise GatewayPolicyError("inbox path is unsafe")
                destination.write_bytes(encoded)
                _append_audit(self.config, "inbox_task_created", "ok", name)
                self._json(HTTPStatus.CREATED, {"created": True, "name": name})
            elif path == "/api/resident/run-once" or path == "/resident/run-once":
                _append_audit(self.config, "resident_run_requested", "requested")
                result = run_approved_script(self.config, "resident_once")
                _append_audit(self.config, "resident_run_requested", "ok" if result["ok"] else "failed")
                self._json(HTTPStatus.OK if result["ok"] else HTTPStatus.BAD_GATEWAY, result)
            elif path == "/api/emergency-stop" or path == "/emergency-stop":
                reason = body.get("reason")
                if not isinstance(reason, str) or not reason.strip() or len(reason) > MAX_REASON_CHARS:
                    raise GatewayPolicyError("a bounded emergency-stop reason is required")
                _append_audit(self.config, "emergency_stop_requested", "requested")
                result = run_approved_script(self.config, "emergency_stop", [reason.strip()])
                _append_audit(self.config, "emergency_stop_requested", "ok" if result["ok"] else "failed")
                self._json(HTTPStatus.OK if result["ok"] else HTTPStatus.BAD_GATEWAY, result)
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
        except GatewayPolicyError as exc:
            _append_audit(self.config, "gateway_policy_violation", "denied", str(exc))
            self._json(HTTPStatus.FORBIDDEN, {"error": str(exc)})
        except GatewayDependencyError as exc:
            self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(exc)})


def create_server(config: GatewayConfig) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((config.host, config.port), GatewayHandler)
    server.gateway_config = config  # type: ignore[attr-defined]
    return server


def main() -> int:
    try:
        config = load_config()
        httpd = create_server(config)
    except (GatewayPolicyError, OSError) as exc:
        print(f"Hermes gateway refused to start: {exc}", file=sys.stderr)
        return 2
    print(f"Hermes gateway started at http://{config.host}:{config.port}", flush=True)
    if config.gateway_bind_is_tailscale:
        print(f"Approved Tailscale access URL: http://{config.host}:{config.port}", flush=True)
    print("Public internet exposure and Tailscale Funnel are disabled; Ctrl-C stops the gateway.", flush=True)
    try:
        httpd.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    print("Hermes gateway stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
