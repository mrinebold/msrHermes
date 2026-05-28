# Google OAuth Setup Guide

## Purpose

This guide explains how a human should prepare Google OAuth credentials for Helio Command Center. It is documentation only.

Do not authenticate, open a browser login, call Google APIs, store real secrets in Git, or request execute scopes during this phase.

## Google Cloud Project

1. Open Google Cloud Console.
2. Create a new project or select a dedicated Helio project.
3. Use a clear project name, such as `Helio Command Center`.
4. Confirm the project is associated with the intended Google account or Workspace organization.
5. Configure the OAuth consent screen for local development.
6. Add only the test users needed for local validation.

## APIs To Enable

Enable these APIs in the project:

- Gmail API
- Google Calendar API
- Google Drive API
- Google Docs API
- Google Sheets API
- People API

## OAuth Client Type

Recommended client type for this local Mac mini phase:

- Desktop app OAuth client.

Rationale:

- Helio is running locally.
- Local browser-based user OAuth is the expected future validation path.
- No public redirect URI or hosted web callback is needed for this phase.

## Initial Read-Only Scopes

Approved initial scopes are read-only only:

- Gmail metadata/read-only.
- Calendar read-only.
- Drive metadata/read-only.
- Docs read-only.
- Sheets read-only.
- People/Contacts read-only.

Exact scope strings should be finalized in the implementation phase, but they must remain read-only for Phase 4C.

## Explicitly Excluded Scopes

Do not request scopes that allow:

- Sending email.
- Modifying Gmail messages.
- Creating, updating, or deleting calendar events.
- Modifying Drive files or permissions.
- Editing Docs.
- Editing Sheets.
- Creating, updating, or deleting contacts.

Draft, modify, send, delete, and sharing scopes are excluded until later phases are approved.

## Credential File Location

After creating the Desktop app OAuth client, download the client secret JSON and place it here:

```text
config/google/client_secret.json
```

This file is ignored by Git and must contain real secrets only on the local machine.

A redacted sample shape is available at:

```text
config/google/client_secret.sample.json
```

## Future Token Location

When OAuth login is approved in a later phase, Helio will store the local token here:

```text
config/google/token.json
```

This file is ignored by Git.

## Environment Values

Future local environment values:

```text
GOOGLE_CLIENT_SECRET_FILE=config/google/client_secret.json
GOOGLE_TOKEN_FILE=config/google/token.json
GOOGLE_OAUTH_SCOPES=<read-only scopes only>
GOOGLE_AUDIT_LOG=logs/google_workspace_audit.jsonl
```

Do not place real client secrets or token values directly in environment files.

## Verification Before Phase 4C

Before any authentication is attempted:

1. Confirm `config/google/client_secret.json` exists locally.
2. Confirm it is ignored by Git.
3. Confirm requested scopes are read-only.
4. Confirm `config/google/token.json` does not exist unless created by an approved OAuth validation.
5. Confirm audit logging is configured.

## Current Boundary

This setup guide does not authorize:

- Google authentication.
- Browser login.
- Google API calls.
- Execute scopes.
- Real secret storage in Git.
