#!/usr/bin/env python3
"""Print suggested Mac mini outbound SSH config blocks without writing files."""

from __future__ import annotations

NODES = [
    {
        "host": "devmonster",
        "hostname": "devmonster-4.taila2da57.ts.net",
        "user": "<remote-user>",
        "identity": "~/.ssh/msr_devmonster_ed25519",
        "note": "Known Tailscale IP: 100.93.120.124",
    },
    {
        "host": "civic-main",
        "hostname": "<civic-main-tailscale-name-or-ip>",
        "user": "<remote-user>",
        "identity": "~/.ssh/msr_civic_main_ed25519",
        "note": "Previously known LAN IP: 192.168.68.100; prefer Tailscale.",
    },
    {
        "host": "civic-dev",
        "hostname": "<civic-dev-tailscale-name-or-ip>",
        "user": "<remote-user>",
        "identity": "~/.ssh/msr_civic_dev_ed25519",
        "note": "Previously known LAN IP conflicts with Mac mini discovery; verify before LAN fallback.",
    },
]


def main() -> int:
    print("# Suggested ~/.ssh/config entries for Mac mini outbound access")
    print("# This script prints only. It does not modify ~/.ssh/config.")
    print("# Do not store private keys in the repo.")
    print()
    for node in NODES:
        print(f"# {node['note']}")
        print(f"Host {node['host']}")
        print(f"  HostName {node['hostname']}")
        print(f"  User {node['user']}")
        print(f"  IdentityFile {node['identity']}")
        print("  IdentitiesOnly yes")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
