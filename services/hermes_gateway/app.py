"""Fail-closed application logic for the Phase 7I Hermes browser gateway.

The gateway is deliberately small and dependency-free.  It exposes only the
approved browser surfaces and invokes only the four approved local Hermes
scripts.  It does not proxy the adapter, execute arbitrary commands, launch
Desktop, or contact external services.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import html
import ipaddress
import json
import os
import re
import secrets
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
MAX_INBOX_BYTES = 64 * 1024
MAX_OUTBOX_BYTES = 256 * 1024
MAX_REASON_CHARS = 500
PRIVATE_CLIENT_NETWORKS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),
)


class GatewayPolicyError(Exception):
    """A request or configuration violates a gateway policy."""


class GatewayDependencyError(Exception):
    """An approved local dependency is unavailable or failed."""


@dataclass(frozen=True)
class GatewayConfig:
    repo_root: Path
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    token: str = ""
    token_source: str = ""
    gateway_bind_is_tailscale: bool = False

    @property
    def inbox_dir(self) -> Path:
        return self.repo_root / "sandbox" / "hermes_inbox"

    @property
    def outbox_dir(self) -> Path:
        return self.repo_root / "sandbox" / "hermes_outbox"

    @property
    def audit_path(self) -> Path:
        return self.repo_root / "sandbox" / "hermes_audit.jsonl"

    @property
    def approvals_path(self) -> Path:
        return self.repo_root / "sandbox" / "hermes_approvals.jsonl"

    @property
    def scripts_dir(self) -> Path:
        return self.repo_root / "scripts"


def _repo_root() -> Path:
    configured = os.environ.get("HERMES_GATEWAY_REPO_ROOT")
    return Path(configured).expanduser().resolve() if configured else Path(__file__).resolve().parents[2]


def _read_token_file() -> str:
    configured = os.environ.get(
        "HERMES_GATEWAY_TOKEN_FILE",
        str(Path.home() / "Library" / "Application Support" / "Helio" / "hermes-gateway" / "token"),
    )
    path = Path(configured).expanduser()
    if not path.is_file() or path.is_symlink():
        return ""
    try:
        token = path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    return token


def _is_tailscale_ip(host: str) -> bool:
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return address in ipaddress.ip_network("100.64.0.0/10")


def validate_bind_host(host: str | None) -> tuple[str, bool]:
    """Validate a bind host and return (host, is_tailscale_bind).

    Only loopback or an explicitly opted-in Tailscale CGNAT address is valid.
    Wildcard, unspecified, public, hostname, and LAN binds are rejected.
    """

    value = (host or DEFAULT_HOST).strip()
    if value in {"", "0.0.0.0", "::", "*", "0", "localhost.localdomain"}:
        raise GatewayPolicyError("gateway bind host must be loopback or an approved Tailscale IP")
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise GatewayPolicyError("gateway bind host must be a literal IP address") from exc
    if address.is_unspecified or address.is_multicast or address.is_link_local:
        raise GatewayPolicyError("unspecified, multicast, and link-local binds are refused")
    if address.is_loopback:
        return value, False
    if _is_tailscale_ip(value):
        if os.environ.get("HERMES_GATEWAY_ALLOW_TAILSCALE_BIND") != "1":
            raise GatewayPolicyError(
                "Tailscale bind requires HERMES_GATEWAY_ALLOW_TAILSCALE_BIND=1"
            )
        return value, True
    raise GatewayPolicyError("only loopback or an approved Tailscale IP may be used")


def load_config() -> GatewayConfig:
    host, is_tailscale = validate_bind_host(os.environ.get("HERMES_GATEWAY_BIND_HOST"))
    raw_port = os.environ.get("HERMES_GATEWAY_PORT", str(DEFAULT_PORT))
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise GatewayPolicyError("gateway port must be an integer") from exc
    if not 1024 <= port <= 65535:
        raise GatewayPolicyError("gateway port must be between 1024 and 65535")

    token = os.environ.get("HERMES_GATEWAY_TOKEN", "").strip()
    source = "environment" if token else "token file"
    if not token:
        token = _read_token_file()
    if not token:
        raise GatewayPolicyError(
            "gateway token is required; set HERMES_GATEWAY_TOKEN or create the local token file"
        )
    if is_tailscale and len(token) < 16:
        raise GatewayPolicyError("Tailscale gateway binding requires a token of at least 16 characters")
    return GatewayConfig(
        repo_root=_repo_root(),
        host=host,
        port=port,
        token=token,
        token_source=source,
        gateway_bind_is_tailscale=is_tailscale,
    )


def validate_safe_filename(name: Any) -> str:
    if not isinstance(name, str) or not name.strip():
        raise GatewayPolicyError("filename is required")
    raw = name.strip()
    if raw in {".", ".."} or "/" in raw or "\\" in raw or Path(raw).name != raw:
        raise GatewayPolicyError("path traversal is denied")
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", raw).lstrip(".")
    if not cleaned:
        raise GatewayPolicyError("filename becomes empty after sanitization")
    return cleaned[:160]


def safe_child_path(directory: Path, name: Any) -> Path:
    safe_name = validate_safe_filename(name)
    directory = directory.resolve()
    candidate = (directory / safe_name).resolve()
    try:
        candidate.relative_to(directory)
    except ValueError as exc:
        raise GatewayPolicyError("path traversal is denied") from exc
    if candidate.is_symlink():
        raise GatewayPolicyError("symlink paths are denied")
    return candidate


def _safe_output(text: str, limit: int = 4000) -> str:
    """Return bounded script output with likely credential values removed."""
    patterns = (
        (re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s]+"), r"\1[redacted]"),
        (re.compile(r"(?i)(\b(?:token|secret|password|api[_-]?key)\b\s*[:=]\s*)[^\s,]+"), r"\1[redacted]"),
        (re.compile(r"(?i)(sk-[A-Za-z0-9_-]{8,})"), "[redacted]"),
    )
    result = text
    for pattern, replacement in patterns:
        result = pattern.sub(replacement, result)
    return result[:limit]


def _safe_env() -> dict[str, str]:
    allowed = {"PATH", "HOME", "USER", "SHELL", "LANG", "LC_ALL", "TMPDIR"}
    result = {key: value for key, value in os.environ.items() if key in allowed or key.startswith("HERMES_")}
    for key in list(result):
        if any(marker in key.upper() for marker in ("TOKEN", "SECRET", "PASSWORD", "API_KEY", "CREDENTIAL")):
            result.pop(key, None)
    result["HERMES_GATEWAY_CALLER"] = "private-browser-gateway"
    return result


def run_approved_script(config: GatewayConfig, script_name: str, args: Iterable[str] = ()) -> dict[str, Any]:
    approved = {
        "local_status": "hermes_local_status.sh",
        "resident_status": "hermes_resident_status.sh",
        "resident_once": "hermes_resident_once.sh",
        "emergency_stop": "hermes_emergency_stop.sh",
    }
    if script_name not in approved:
        raise GatewayPolicyError("script is not approved")
    script = (config.scripts_dir / approved[script_name]).resolve()
    try:
        script.relative_to(config.scripts_dir.resolve())
    except ValueError as exc:
        raise GatewayPolicyError("approved script escaped scripts directory") from exc
    if not script.is_file() or script.is_symlink() or not os.access(script, os.X_OK):
        raise GatewayDependencyError(f"approved script unavailable: {approved[script_name]}")
    try:
        completed = subprocess.run(
            [str(script), *list(args)],
            cwd=str(config.repo_root),
            env=_safe_env(),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=120 if script_name in {"resident_once", "emergency_stop"} else 20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GatewayDependencyError(f"approved script did not complete: {type(exc).__name__}") from exc
    return {
        "script": approved[script_name],
        "returncode": completed.returncode,
        "ok": completed.returncode == 0,
        "stdout": _safe_output(completed.stdout),
        "stderr": _safe_output(completed.stderr),
    }


def _append_audit(config: GatewayConfig, action: str, outcome: str, detail: str = "") -> None:
    config.audit_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": int(time.time()),
        "action": action,
        "outcome": outcome,
    }
    if detail:
        event["detail"] = _safe_output(detail, 500)
    with config.audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, separators=(",", ":")) + "\n")


def _read_summaries(path: Path, limit: int = 20) -> list[dict[str, Any]]:
    if not path.is_file() or path.is_symlink():
        return []
    summaries: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
    except OSError:
        return []
    for line in lines:
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            summaries.append({key: item[key] for key in ("timestamp", "action", "outcome") if key in item})
    return summaries


def list_files(directory: Path) -> list[dict[str, Any]]:
    directory.mkdir(parents=True, exist_ok=True)
    result = []
    for item in sorted(directory.iterdir(), key=lambda candidate: candidate.name.lower()):
        if item.is_symlink() or not item.is_file():
            continue
        try:
            result.append({"name": validate_safe_filename(item.name), "bytes": item.stat().st_size})
        except GatewayPolicyError:
            continue
    return result


def read_safe_file(directory: Path, name: str, max_bytes: int) -> str:
    path = safe_child_path(directory, name)
    if not path.is_file() or path.is_symlink():
        raise GatewayPolicyError("file does not exist or is not a safe regular file")
    if path.stat().st_size > max_bytes:
        raise GatewayPolicyError("file exceeds gateway read limit")
    return path.read_text(encoding="utf-8", errors="replace")


def adapter_state() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.15)
    try:
        return "listening" if sock.connect_ex(("127.0.0.1", 8088)) == 0 else "stopped"
    finally:
        sock.close()



def private_gemma_status() -> dict[str, Any]:
    """Describe the Phase 1 private model route without probing the network."""
    from services.model_router.config import ModelRouterConfig

    router = ModelRouterConfig.from_env()
    adapter_host = os.environ.get("MODEL_ROUTER_ADAPTER_HOST", "127.0.0.1").strip()
    adapter_port = os.environ.get("MODEL_ROUTER_ADAPTER_PORT", "8088").strip()
    endpoint = urlsplit(router.devmonster_ollama_url)
    private_worker = False
    try:
        private_worker = bool(endpoint.hostname) and ipaddress.ip_address(endpoint.hostname) in ipaddress.ip_network("100.64.0.0/10")
    except ValueError:
        private_worker = False
    configured = (
        endpoint.scheme == "http"
        and private_worker
        and router.devmonster_default_model == "gemma4:26b"
        and adapter_host == "127.0.0.1"
    )
    return {
        "state": "configured_not_probed" if configured else "configuration_refused",
        "route": "hermes_local_adapter_to_private_gemma",
        "provider": "devmonster_ollama",
        "model": router.devmonster_default_model,
        "private_tailscale_worker": private_worker,
        "local_adapter_only": adapter_host == "127.0.0.1",
        "adapter_port": adapter_port,
        "live_probe": "not_run",
        "cloud_fallback": "disabled_for_phase_1",
    }


def helio_bridge_status() -> dict[str, Any]:
    """Report only the fail-closed Phase 1 test-bridge state."""
    from services.agent_bus.config import load_config as load_agent_bus_config

    bridge = load_agent_bus_config()
    return {
        "state": "ready_for_inprocess_test" if bridge.configured else "disabled_or_unconfigured",
        "mode": bridge.mode,
        "transport": bridge.transport,
        "direct_supabase": False,
        "direct_agent_bus_writes": False,
        "task_execution": False,
        "helio_is_sole_router": True,
    }

def status(config: GatewayConfig) -> dict[str, Any]:
    local: dict[str, Any]
    resident: dict[str, Any]
    try:
        local = run_approved_script(config, "local_status")
    except GatewayDependencyError as exc:
        local = {"ok": False, "state": "unavailable", "detail": str(exc)}
    try:
        resident = run_approved_script(config, "resident_status")
    except GatewayDependencyError as exc:
        resident = {"ok": False, "state": "unavailable", "detail": str(exc)}
    return {
        "gateway": {"state": "running", "host": config.host, "port": config.port, "token_auth": True},
        "hermes_local": local,
        "resident": resident,
        "adapter": {"state": adapter_state(), "endpoint_exposed": False},
        "private_gemma": private_gemma_status(),
        "helio_bridge": helio_bridge_status(),
        "resident_once": {"state": "manual_only", "launch_agent": "stopped_or_unloaded"},
        "desktop": {"state": "fail_closed", "launch_allowed": False},
        "command_execution": {"enabled": False},
        "external_integrations": {"state": "frozen"},
        "public_exposure": {"approved": False, "tailscale_funnel": False, "wildcard_bind": False},
    }


def _session_value(token: str) -> str:
    digest = hmac.new(token.encode("utf-8"), b"hermes-browser-session", hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def session_cookie(token: str) -> str:
    return _session_value(token)


def valid_session(token: str, value: str) -> bool:
    return bool(value) and hmac.compare_digest(_session_value(token), value)


def client_allowed(config: GatewayConfig, client_ip: str) -> bool:
    if not config.gateway_bind_is_tailscale:
        return client_ip in {"127.0.0.1", "::1"}
    try:
        address = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    return any(address in network for network in PRIVATE_CLIENT_NETWORKS)


def _page(title: str, body: str, script: str = "") -> bytes:
    script_tag = f"<script>{script}</script>" if script else ""
    document = f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)}</title><style>body{{font-family:system-ui,sans-serif;max-width:920px;margin:2rem auto;padding:0 1rem;background:#10151c;color:#edf2f7}}a{{color:#8bd5ff}}button,input,textarea{{font:inherit;padding:.55rem;border-radius:.4rem;border:1px solid #52606d;background:#18212b;color:#edf2f7}}textarea{{width:100%;min-height:8rem}}pre{{white-space:pre-wrap;background:#18212b;padding:1rem;border-radius:.5rem;overflow:auto}}.grid{{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}}.card{{background:#18212b;padding:1rem;border-radius:.6rem}}</style></head><body><h1>{html.escape(title)}</h1>{body}{script_tag}</body></html>"
    return document.encode("utf-8")


def login_page() -> bytes:
    return _page(
        "Hermes Gateway Login",
        "<p>Private local/Tailscale gateway. Enter the gateway token; it is sent only to this gateway.</p><form id='login'><input id='token' type='password' autocomplete='current-password' placeholder='Gateway token' required><button>Sign in</button></form><p id='message'></p>",
        "document.getElementById('login').addEventListener('submit',async(e)=>{e.preventDefault();const r=await fetch('/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:document.getElementById('token').value})});const d=await r.json();document.getElementById('message').textContent=d.message||d.error||'';if(r.ok)location.href='/';});",
    )


def home_page(config: GatewayConfig) -> bytes:
    return _page(
        "Hermes Gateway",
        f"<p>Private, governed browser surface for the local Hermes stack.</p><div class='grid'><div class='card'><h2>Status</h2><a href='/status'>View status</a></div><div class='card'><h2>Work surfaces</h2><a href='/inbox'>Inbox</a> · <a href='/outbox'>Outbox</a></div><div class='card'><h2>Governance</h2><a href='/audit'>Audit</a> · <a href='/approvals'>Approvals</a></div><div class='card'><h2>Phase 1 readiness</h2><a href='/api/pilot-readiness'>Private Gemma4 + Helio bridge</a><p>Configured only; browser chat is not enabled yet.</p></div><div class='card'><h2>Controlled actions</h2><button id='resident'>Run resident once</button> <button id='stop'>Emergency stop</button><pre id='result'></pre></div></div><p><strong>Command execution:</strong> disabled · <strong>External integrations:</strong> frozen · <strong>Desktop:</strong> fail-closed</p><p>Bound to <code>{html.escape(config.host)}:{config.port}</code>. Public exposure and Tailscale Funnel are not approved.</p>",
        "async function post(path,body){const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})});const d=await r.json();document.getElementById('result').textContent=JSON.stringify(d,null,2);};document.getElementById('resident').onclick=()=>post('/api/resident/run-once',{});document.getElementById('stop').onclick=()=>{const reason=prompt('Emergency-stop reason');if(reason)post('/api/emergency-stop',{reason});};",
    )


def status_page(data: dict[str, Any]) -> bytes:
    return _page("Hermes Status", f"<p><a href='/'>Home</a></p><pre>{html.escape(json.dumps(data, indent=2))}</pre>")


def files_page(kind: str, files: list[dict[str, Any]], config: GatewayConfig) -> bytes:
    links = "".join(f"<li><a href='/{kind}/{html.escape(item['name'])}'>{html.escape(item['name'])}</a> ({item['bytes']} bytes)</li>" for item in files)
    form = "" if kind == "outbox" else "<h2>Create task</h2><form id='create'><input id='name' placeholder='task.md' required><br><textarea id='content' placeholder='Task content' required></textarea><br><button>Create inbox task</button></form><pre id='result'></pre>"
    script = "" if kind == "outbox" else "document.getElementById('create').onsubmit=async(e)=>{e.preventDefault();const r=await fetch('/api/inbox',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('name').value,content:document.getElementById('content').value})});document.getElementById('result').textContent=JSON.stringify(await r.json(),null,2);if(r.ok)setTimeout(()=>location.reload(),500);};"
    return _page(f"Hermes {kind.title()}", f"<p><a href='/'>Home</a></p><ul>{links or '<li>empty</li>'}</ul>{form}", script)


def file_page(kind: str, name: str, content: str) -> bytes:
    return _page(f"Hermes {kind.title()} · {name}", f"<p><a href='/{kind}'>Back</a></p><pre>{html.escape(content)}</pre>")


def summaries_page(kind: str, entries: list[dict[str, Any]]) -> bytes:
    return _page(f"Hermes {kind.title()}", f"<p><a href='/'>Home</a></p><pre>{html.escape(json.dumps(entries, indent=2))}</pre>")


def temporary_test_token() -> str:
    """Create a token for a caller's process without printing its value."""
    return secrets.token_urlsafe(32)
