#!/usr/bin/env python3
"""Print non-secret gateway bind information."""

import os

host = os.environ.get("HERMES_GATEWAY_BIND_HOST", "127.0.0.1")
port = os.environ.get("HERMES_GATEWAY_PORT", "8787")
print(f"local_url=http://127.0.0.1:{port}")
if host != "127.0.0.1":
    print(f"configured_url=http://{host}:{port}")
print("public_exposure=disabled")
print("tailscale_funnel=disabled")
print("wildcard_bind=refused")
