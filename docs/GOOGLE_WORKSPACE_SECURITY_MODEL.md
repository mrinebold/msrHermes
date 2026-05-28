# Google Workspace Security Model

## Objective

Helio Command Center will integrate with Google Workspace only through explicit approval gates, narrow OAuth scopes, local audit logs, and staged capability rollout.

Phase 4B has local scaffolding only. No Google authentication, OAuth credential creation, API calls, browser login, scope request, or package installation has been performed.

## Required Interfaces

Planned Google interfaces:

- Gmail
- Calendar
- Drive
- Docs
- Sheets
- Contacts/People API

## Permission Tiers

### Read

Allowed after approval for read-only validation:

- Search and summarize Gmail metadata and message bodies.
- Read calendar events and availability.
- Read Drive file metadata and approved file contents.
- Read Docs and Sheets content for approved files.
- Read People/Contacts metadata needed for addressing and disambiguation.

Restrictions:

- No message sending.
- No calendar modification.
- No Drive, Docs, or Sheets writes.
- No sharing changes.
- No contact edits.

### Draft/Prepare

Allowed after approval for draft-only tooling:

- Prepare Gmail drafts.
- Prepare calendar event proposals.
- Prepare Docs or Sheets change plans.
- Prepare Drive organization proposals.
- Prepare contact update proposals.

Restrictions:

- Drafts and proposals must remain unexecuted until a human approves.
- Generated content must clearly identify the intended account, recipients, files, calendars, and side effects.

### Execute With Approval

Allowed only after a human approves a specific action:

- Send or update Gmail messages.
- Create, update, or delete calendar events.
- Create, update, move, or share Drive files.
- Edit Docs or Sheets.
- Create or update contacts.

Restrictions:

- Approval must bind to the exact action payload or a clearly rendered diff.
- No broad approval for unrestricted future Google actions.
- High-impact actions require fresh approval even if similar actions were previously approved.

## Token Storage

Initial local storage approach:

- Store OAuth client config and user tokens only in untracked local files.
- Never commit tokens, refresh tokens, client secrets, or service account keys.
- Prefer OS keychain storage or encrypted local storage before production use.
- Keep token files outside `docs/`, `logs/`, and tracked source directories.
- Restrict file permissions for any local token cache.

Phase 4B scaffold variables:

- `GOOGLE_CLIENT_SECRET_FILE`
- `GOOGLE_TOKEN_FILE`
- `GOOGLE_OAUTH_SCOPES`
- `GOOGLE_AUDIT_LOG`

The scaffold must fail closed when credential paths or scopes are missing. Even when local config paths exist, authentication remains disabled until a later approved phase.

Future hardening:

- Use revocable OAuth clients with narrow scopes.
- Separate development and production OAuth clients.
- Rotate credentials after testing.
- Record token creation, refresh, revocation, and scope changes in the audit log without logging token values.

## Audit Logging

Every Google action must append an audit event with:

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

Phase 4B audit helper records at minimum:

- Timestamp.
- Action.
- Permission tier.
- Target service.
- Status.

Sensitive handling:

- Do not log OAuth tokens.
- Do not log full email bodies by default.
- Do not log full Docs or Sheets contents by default.
- Prefer metadata, hashes, summaries, and resource IDs.

## Scope Strategy

Use incremental OAuth scopes. Start read-only and add write scopes only when the next phase is approved.

Scope groups should map to permission tiers:

- Read scopes for Phase 4C.
- Draft or compose scopes for Phase 4D.
- Write/modify scopes for Phase 4E after approval gates exist.

## Safety Defaults

- No Google API calls before explicit approval.
- No OAuth login before explicit approval.
- No autonomous Google actions.
- No email sending without human approval.
- No calendar writes without human approval.
- No Drive sharing changes without human approval.
- No Docs or Sheets edits without human approval.
