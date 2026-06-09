# Credential Rotation Checklist

## Status

Phase SECURITY-2 post-exposure tracking only. No credentials were rotated by this document. No external APIs were called.

Phase 5AI recorded explicit human deferral of credential rotation on 2026-06-08 for the next bounded local-only phase. This deferral does not mark any credential rotated, revoked, reviewed, or safe.

No further live bus reads/writes until rotation is confirmed or a separate phase explicitly approves a narrow read-only scope under the documented deferral.

## Exposure Summary

During Phase 6H, live credential material was pasted into the chat context. Treat the affected credentials as exposed and rotate them from the provider consoles.

Do not copy secret values into this repository, issues, pull requests, logs, or future chat messages.

## Exposed Credential Types

| Credential type | Risk | Required action | Status |
| --- | --- | --- | --- |
| Supabase service-role key | Critical | Revoke or rotate immediately. | Pending user confirmation |
| OpenAI API key | High | Revoke or rotate immediately. | Pending user confirmation |
| Anthropic/Claude API key | High | Revoke or rotate immediately. | Pending user confirmation |
| GitHub token | Critical | Revoke or rotate immediately. | Pending user confirmation |
| Supabase anon key | Low | Review after service-role rotation; rotate if project policy requires it. | Pending user confirmation |

The Supabase anon key is lower risk because it is designed for client-side use and should be constrained by RLS. It is still reviewable because it appeared in chat with other sensitive material.

## Current Rotation Status

| Item | Current status | Basis | Next required confirmation |
| --- | --- | --- | --- |
| Supabase service-role key | Deferred for Phase 5AI local-only scope; pending before use | No rotation was performed by Helio, and provider state was not checked. | User confirms revoked/rotated, or approves a separate credential-family-specific deferral before any use. |
| OpenAI key | Deferred for Phase 5AI local-only scope; pending before use | No rotation was performed by Helio, and provider state was not checked. | User confirms revoked/rotated, or approves a separate credential-family-specific deferral before any use. |
| Anthropic/Claude key | Deferred for Phase 5AI local-only scope; pending before use | No rotation was performed by Helio, and provider state was not checked. | User confirms revoked/rotated, or approves a separate credential-family-specific deferral before any use. |
| GitHub token | Deferred for Phase 5AI local-only scope; pending before use | No rotation was performed by Helio, and provider state was not checked. | User confirms revoked/rotated, or approves a separate credential-family-specific deferral before any use. |
| Supabase anon key review | Deferred for Phase 5AI local-only scope; pending before use | No review or rotation decision was confirmed in this phase. | User confirms review complete, or approves a separate credential-family-specific deferral before any use. |

## Phase 5AI Deferral Record

On 2026-06-08, the human owner explicitly deferred credential rotation and approved proceeding only within a bounded local validation/configuration planning scope.

Deferral applies only to documenting the decision and preparing a later local-only validation phase. It does not approve:

- live Agent Bus reads
- Agent Bus writes
- Supabase service-role use
- provider console/API calls
- Google, GitHub, Home Assistant, Helio, or cloud-provider operations
- credential storage, replacement, deletion, or modification
- Hermes Desktop launch
- background or resident services

The exposed credential families remain pending until the owner later confirms rotation, revocation, review completion, or a narrower credential-family-specific deferral.

## Immediate Actions

- [ ] Revoke or rotate the Supabase service-role key.
- [ ] Revoke or rotate the OpenAI API key.
- [ ] Revoke or rotate the Anthropic/Claude API key.
- [ ] Revoke or rotate the GitHub token.
- [ ] Review whether the Supabase anon key should also be rotated.
- [ ] Update `config/local.env` after rotation using only the minimum keys needed for the next approved phase.
- [ ] Verify `config/local.env` remains gitignored and is not staged.
- [ ] Remove any stale local secret files that are no longer needed.
- [x] Record explicit Phase 5AI deferral before any next local-only validation/configuration phase.
- [ ] Confirm rotation, revocation, or credential-family-specific deferral before any further live bus read or write.

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

Do not run live read commands until the exposed high-risk credentials have been rotated or a new phase explicitly approves a narrow read-only scope under the documented deferral.

Blocked until rotation or separate narrow read-only approval:

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
