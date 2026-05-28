# Google Workspace Plan

## Objective

Prepare Helio Command Center to manage Google Workspace interfaces safely, starting read-only and draft-only, with human approval required before execution.

Phase 4A is planning only. No Google authentication, OAuth credential creation, Google API calls, or package installation has been performed.

## Required APIs

Planned Google APIs:

- Gmail
- Calendar
- Drive
- Docs
- Sheets
- Contacts/People API

## Phased Rollout

### Phase 4A: Plan Only

Status: current phase.

- Define API surfaces.
- Define permission tiers.
- Define scope strategy.
- Define token storage approach.
- Define audit logging requirements.
- Do not authenticate Google.
- Do not create OAuth credentials.
- Do not call Google APIs.

### Phase 4B: Local OAuth Scaffolding, No Auth

Status: scaffold created; authentication remains disabled.

- Add local connector structure.
- Add OAuth config placeholders.
- Add token storage interfaces.
- Add dry-run audit logging.
- Add scope manifests.
- Do not run OAuth login.
- Do not call Google APIs.

Implemented scaffold:

- `services/google_workspace/config.py`
- `services/google_workspace/auth.py`
- `services/google_workspace/audit.py`
- `services/google_workspace/README.md`

Current behavior:

- Missing local OAuth config returns a clear fail-closed error.
- `authenticate()` always returns disabled.
- Audit helper writes JSON Lines events locally.
- No browser is opened.
- No scopes are requested.
- No Google API is called.

### Phase 4C: Read-Only Gmail, Calendar, and Drive Validation

Requires approval before execution.

- Authenticate with read-only scopes only.
- Validate Gmail read/search.
- Validate Calendar read availability/events.
- Validate Drive metadata and approved file reads.
- Record every read action in the audit log.
- Do not write, send, modify, delete, or share.

### Phase 4D: Draft-Only Gmail and Calendar Proposal Tools

Requires approval before execution.

- Prepare Gmail drafts without sending.
- Prepare calendar event proposals without creating/updating events.
- Render proposed payloads for human review.
- Record draft/proposal events in the audit log.
- Do not execute actions.

### Phase 4E: Human-Approved Execution

Requires approval after prior phases are validated.

- Send email only after explicit approval.
- Create or update calendar events only after explicit approval.
- Modify Drive, Docs, or Sheets only after explicit approval.
- Update contacts only after explicit approval.
- Log approval IDs and final action results.

## Permission Tiers

### Read

- Gmail read/search.
- Calendar read.
- Drive metadata and approved file read.
- Docs read for approved documents.
- Sheets read for approved spreadsheets.
- People/Contacts read for addressing and disambiguation.

### Draft/Prepare

- Gmail draft preparation.
- Calendar event proposal preparation.
- Docs/Sheets edit proposal preparation.
- Drive organization proposal preparation.
- Contact update proposal preparation.

### Execute With Approval

- Gmail send/update.
- Calendar create/update/delete.
- Drive create/update/move/share/delete.
- Docs edit.
- Sheets edit.
- Contact create/update.

## Candidate Scope Progression

Exact scopes will be finalized during implementation, but the progression should stay narrow:

- Phase 4C: read-only Gmail, Calendar, Drive, Docs, Sheets, and People/Contacts scopes.
- Phase 4D: draft/compose scopes only where needed for unsent drafts or proposal workflows.
- Phase 4E: write/modify scopes only after human approval gates and audit logging exist.

## Token Storage

- Store OAuth client config and user tokens only in untracked local files.
- Never commit tokens, refresh tokens, client secrets, or service account keys.
- Prefer OS keychain storage or encrypted local storage before production use.
- Restrict permissions on local token cache files.
- Log token lifecycle events without logging token values.

Phase 4B placeholders:

- `GOOGLE_CLIENT_SECRET_FILE`
- `GOOGLE_TOKEN_FILE`
- `GOOGLE_OAUTH_SCOPES`
- `GOOGLE_AUDIT_LOG`

## Audit Logging

Every Google action must log:

- Timestamp.
- Actor or local process.
- Google account.
- API surface.
- Permission tier.
- Scope or scopes used.
- Action type.
- Target resource identifiers.
- Human approval ID, if required.
- Dry-run/proposal/executed status.
- Result status.
- Error code/message if failed.

Sensitive content such as OAuth tokens, full email bodies, full Docs contents, and full Sheets contents must not be logged by default.

## Package Planning

Potential future Python packages, if approved later:

- `google-auth`
- `google-auth-oauthlib`
- `google-api-python-client`

No packages are installed during Phase 4A.

## Open Questions

- Which Google account should Helio use first?
- Should Helio use user OAuth only, service accounts only, or both for different surfaces?
- Should tokens live in the OS keychain, encrypted local files, or another approved secret store?
- Which Google actions should remain permanently human-only?
