# Security Model

## Permission Gates

The system should require explicit approval before:

- Installing or upgrading packages.
- Running commands with `sudo`.
- Modifying shell profiles or login items.
- Opening inbound network services.
- Accessing Google Workspace data.
- Sending commands to Home Assistant.
- Persisting credentials or API tokens.
- Deleting files or changing backups.

## Access Principles

- Localhost first.
- Tailscale-only for trusted remote access.
- Least privilege for OAuth scopes and service tokens.
- Human-readable logs for every significant action.
- Separate read-only inspection from mutating bootstrap phases.

## Secret Handling

- Never commit real secrets.
- Use `config/example.env` only for placeholder values.
- Store local secrets in an untracked environment file after approval.
- Prefer short-lived or revocable tokens.

## Audit Expectations

Every bootstrap phase should append to `logs/bootstrap.log`:

- Timestamp.
- Command or action summary.
- Whether approval was required.
- Outcome.
- Any follow-up required.
