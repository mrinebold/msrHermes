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

## Trusted AI Worker Nodes

DevMonster is designated as a trusted private AI worker node for Gemma4 inference on the Tailscale mesh.

Security expectations:

- Reach DevMonster only through private Tailscale or equivalent private network addressing.
- Do not expose DevMonster inference endpoints publicly.
- Prefer OpenAI-compatible API semantics where possible to simplify auditing and fallback controls.
- Store `GEMMA_API_KEY` only in approved local secret storage, never in tracked files.
- Keep `GEMMA_BASE_URL`, `GEMMA_MODEL`, and `GEMMA_TIMEOUT` configurable per environment.
- Log routing decisions and worker errors without logging prompt contents or secrets by default.
- Require explicit approval before allowing any model output to trigger shell commands, external API writes, Home Assistant actions, or file deletion.
- Treat cloud AI APIs as fallback routes that require policy approval when private inference is feasible.

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
