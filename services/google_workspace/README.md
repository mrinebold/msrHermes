# Google Workspace Scaffolding

This package is Phase 4B scaffolding only.

It does not:

- authenticate Google
- open a browser
- request OAuth scopes
- call Gmail, Calendar, Drive, Docs, Sheets, or People APIs
- store real secrets

## Environment

- `GOOGLE_CLIENT_SECRET_FILE`
- `GOOGLE_TOKEN_FILE`
- `GOOGLE_OAUTH_SCOPES`
- `GOOGLE_AUDIT_LOG`

## Current Behavior

`GoogleWorkspaceAuth.check_ready()` fails closed when required local config is missing. Even when config paths and scopes are present, `authenticate()` remains disabled until a later approved phase.

`write_audit_event()` writes JSON Lines audit entries with timestamp, action, permission tier, target service, status, and optional details.
