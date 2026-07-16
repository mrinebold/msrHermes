#!/bin/bash
# Show bounded gateway status without printing the gateway token.

set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

python3 - <<'PY'
import json
import os
import urllib.error
import urllib.request

host = os.environ.get("HERMES_GATEWAY_BIND_HOST", "127.0.0.1")
port = os.environ.get("HERMES_GATEWAY_PORT", "8787")
token = os.environ.get("HERMES_GATEWAY_TOKEN", "")
if not token:
    token_path = os.environ.get("HERMES_GATEWAY_TOKEN_FILE", os.path.expanduser("~/Library/Application Support/Helio/hermes-gateway/token"))
    try:
        with open(token_path, encoding="utf-8") as handle:
            token = handle.read().strip()
    except OSError:
        pass
if not token:
    print(json.dumps({"state": "token unavailable", "listener": f"{host}:{port}"}, indent=2))
    raise SystemExit(1)
request = urllib.request.Request(
    f"http://{host}:{port}/api/status",
    headers={"Authorization": f"Bearer {token}"},
)
try:
    with urllib.request.urlopen(request, timeout=3) as response:
        print(response.read().decode("utf-8"))
except (OSError, urllib.error.URLError) as exc:
    print(json.dumps({"state": "unreachable", "detail": type(exc).__name__, "listener": f"{host}:{port}"}, indent=2))
    raise SystemExit(1)
PY
