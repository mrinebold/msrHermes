#!/usr/bin/env python3
"""Print remote-machine SSH setup instructions for Mac mini Hermes access."""

from __future__ import annotations

MACHINES = ("DevMonster", "civic-main", "civic-dev")
MACMINI_HOST = "michaels-mac-mini"
MACMINI_TAILSCALE_IP = "100.80.79.75"
MACMINI_USER = "michael"


def main() -> int:
    print("# Remote SSH Setup Instructions For Mac mini Hermes")
    print()
    print("These instructions generate keys on the remote machines only.")
    print("Do not copy private keys to the Mac mini or into the repo.")
    print()
    print(f"Preferred HostName: {MACMINI_HOST} or {MACMINI_TAILSCALE_IP}")
    print()

    for machine in MACHINES:
        safe_name = machine.lower().replace(" ", "-")
        comment = f"{safe_name}-to-macmini-hermes"
        print(f"## {machine}")
        print()
        print("Generate a key on the remote machine if one does not already exist:")
        print()
        print("```sh")
        print(f'ssh-keygen -t ed25519 -f ~/.ssh/msr_macmini_ed25519 -C "{comment}"')
        print("```")
        print()
        print("Show the public key only:")
        print()
        print("```sh")
        print("cat ~/.ssh/msr_macmini_ed25519.pub")
        print("```")
        print()
        print("Install by pasting the public key into a temp file on the Mac mini, then run:")
        print()
        print("```sh")
        print(
            f"scripts/install_approved_ssh_key.sh --name {safe_name} "
            "--pubkey-file /private/tmp/<public-key-file>.pub"
        )
        print("```")
        print()
        print("If password SSH is already available, copy only the public key and install it:")
        print()
        print("```sh")
        print(
            f"scp ~/.ssh/msr_macmini_ed25519.pub {MACMINI_USER}@{MACMINI_TAILSCALE_IP}:/private/tmp/{safe_name}.pub"
        )
        print(
            f'ssh {MACMINI_USER}@{MACMINI_TAILSCALE_IP} '
            f'"cd /Users/michaelrinebold/Documents/Helio/helio-command-center && '
            f'scripts/install_approved_ssh_key.sh --name {safe_name} --pubkey-file /private/tmp/{safe_name}.pub"'
        )
        print("```")
        print()
        print("Test access:")
        print()
        print("```sh")
        print(
            f'ssh -i ~/.ssh/msr_macmini_ed25519 {MACMINI_USER}@{MACMINI_TAILSCALE_IP} '
            '"hostname && whoami"'
        )
        print("```")
        print()
        print("Suggested ~/.ssh/config entry:")
        print()
        print("```sshconfig")
        print("Host macmini-hermes")
        print(f"  HostName {MACMINI_TAILSCALE_IP}")
        print(f"  User {MACMINI_USER}")
        print("  IdentityFile ~/.ssh/msr_macmini_ed25519")
        print("  IdentitiesOnly yes")
        print("```")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
