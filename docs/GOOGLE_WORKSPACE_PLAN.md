# Google Workspace Plan

## Objective

Integrate Google Workspace only after explicit approval, using narrow OAuth scopes and clear audit logs.

## Phases

1. Inventory required use cases: Gmail, Calendar, Drive, Docs, Sheets, or Admin APIs.
2. Create or select a Google Cloud project.
3. Configure OAuth consent and authorized local redirect URIs.
4. Implement connector with least-privilege scopes.
5. Store tokens locally only after approval.
6. Add approval gates before sending email, modifying calendar events, changing Drive files, or sharing documents.

## Initial Candidate Scopes

- Gmail read/search only, if needed.
- Calendar read/write only after approval.
- Drive metadata/read only unless write access is explicitly required.

## Open Questions

- Which Workspace account should be used?
- Should access be user OAuth only, service account only, or both?
- Which actions should be allowed autonomously after initial approval?
