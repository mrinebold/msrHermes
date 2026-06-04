# Credential Rotation Checklist

## Status

Phase SECURITY-1 tracking only. No credentials were rotated by this document. No external APIs were called.

## Exposure Summary

During Phase 6H, live credential material was pasted into the chat context. Treat the affected credentials as exposed and rotate them from the provider consoles.

Do not copy secret values into this repository, issues, pull requests, logs, or future chat messages.

## Exposed Credential Types

| Credential type | Risk | Required action | Status |
| --- | --- | --- | --- |
| Supabase service-role key | Critical | Revoke or rotate immediately. | Pending |
| OpenAI API key | High | Revoke or rotate immediately. | Pending |
| Anthropic/Claude API key | High | Revoke or rotate immediately. | Pending |
| GitHub token | Critical | Revoke or rotate immediately. | Pending |
| Supabase anon key | Low | Review after service-role rotation; rotate if project policy requires it. | Review |

The Supabase anon key is lower risk because it is designed for client-side use and should be constrained by RLS. It is still reviewable because it appeared in chat with other sensitive material.

## Immediate Actions

- [ ] Revoke or rotate the Supabase service-role key.
- [ ] Revoke or rotate the OpenAI API key.
- [ ] Revoke or rotate the Anthropic/Claude API key.
- [ ] Revoke or rotate the GitHub token.
- [ ] Review whether the Supabase anon key should also be rotated.
- [ ] Update `config/local.env` after rotation using only the minimum keys needed for the next approved phase.
- [ ] Verify `config/local.env` remains gitignored and is not staged.
- [ ] Remove any stale local secret files that are no longer needed.
- [ ] Avoid further live reads until the high-risk credentials are rotated.

## Post-Rotation Validation

After rotation, run local validation only:

```sh
python3 -m unittest discover
git diff --check
```

Then run config validation only, after loading the updated local env:

```sh
set -a
. config/local.env
set +a
python3 scripts/agent_bus_readonly_preflight.py verify-config
```

Do not run live read commands until the exposed high-risk credentials have been rotated and the next phase is explicitly approved.

Blocked until rotation:

- `list-org-configs`
- `read-hermes-messages`
- `read-outbound-audit`
- any future write, dispatch, task, or acknowledgement operation

## Handling Rules

- Never store real secrets in tracked files.
- Never print secrets in terminal output or docs.
- Never use `SUPABASE_SERVICE_ROLE_KEY` in the Hermes adapter.
- Never use broad provider keys for Agent Bus validation.
- Prefer short-lived or scoped tokens where providers support them.
- Keep `config/local.env` mode restricted to owner read/write when used locally.

## Recovery Notes

If any secret is suspected to have reached a public repository, CI logs, shared paste, or external issue tracker, treat rotation as urgent and review provider audit logs for unexpected access.

Phase SECURITY-1 does not perform that review automatically.
