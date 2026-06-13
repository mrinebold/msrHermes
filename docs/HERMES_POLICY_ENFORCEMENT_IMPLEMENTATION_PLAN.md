# Hermes Policy Enforcement Implementation Plan

Phase: 6K
Status: file-zone classifier primitive implemented in Phase 6O; command classifier primitive implemented in Phase 6P; dry-run policy check CLI implemented in Phase 6S

## Purpose

This plan defines how Hermes should later implement file-zone and command-policy classification before any resident loop, command executor, file write, service control, or external integration is enabled.

Phase 6K is planning only. It does not create `services/hermes_safety/`, implement classifiers, execute commands, enforce file access, start services, run Hermes live, enable resident mode, create a Hermes launchd service, connect integrations, use credentials, modify `~/.hermes`, or broaden Hermes authority.

## Proposed Modules

Future modules:

- `services/hermes_safety/file_zones.py`
- `services/hermes_safety/command_policy.py`
- `services/hermes_safety/policy_result.py`

Module responsibilities:

- `file_zones.py`: classify paths against green/yellow/orange/red zones.
- `command_policy.py`: classify command argv into allowed, approval-required, denied, or ambiguous outcomes.
- `policy_result.py`: define shared result types, denial reasons, risk levels, approval requirements, and audit metadata.

No module is implemented in Phase 6K.

Phase 6S provides the first operational integration point: `scripts/hermes_policy_check.py`. It calls the classifiers in dry-run mode and reports classifications, reasons, approval requirements, denial state, and matched policy rules. It does not enforce access, execute commands, create approvals, start services, write audit logs by default, run Hermes, or connect external systems.

## Phase 6S Dry-Run CLI

The dry-run CLI supports:

- `--command "<command string>"`
- `--path "<path>"`
- `--operation read|write`
- `--json`

Exit-code contract:

- `0`: allowed read-only command or allowed green/yellow path classification
- `2`: approval-required command or path classification
- `3`: denied, red, unknown, or fail-closed classification
- `1`: script usage/runtime error

## File-Zone Classifier

Future file-zone classification should:

- normalize paths before classification
- resolve symlinks safely or refuse symlinks until explicitly approved
- detect path traversal attempts
- classify paths as green, yellow, orange, or red
- refuse secret-like files and paths by default
- fail closed on ambiguity
- include the matched zone and reason in the policy result
- avoid reading file contents unless a later phase explicitly approves content inspection

Initial classification sources:

- `docs/HERMES_FILE_ZONE_POLICY.md`
- approved repo root
- approved sandbox paths
- approved log paths after audit implementation

## Command Classifier

Future command classification should:

- parse commands as argv, not raw shell strings
- avoid shell expansion where possible
- apply denylist rules first
- match allowlist exact commands and bounded patterns second
- classify service starts, writes, commits, pushes, and risky reads as approval-required when not denied
- fail closed on ambiguous syntax, unrecognized commands, shell metacharacters, redirection, subshells, pipes, and environment-variable expansion unless a later phase explicitly supports them
- return a policy result only
- never execute commands

Initial command outcomes:

- `allowed_read_only`
- `approval_required`
- `denied`
- `ambiguous_fail_closed`

## Denylist-First Rules

The classifier must deny before allowlist matching when a command includes:

- `sudo`
- destructive delete patterns
- mode or ownership changes on sensitive paths
- force push
- hard reset
- clean worktree deletion
- credential-store reads
- `.env`, token, key, secret, or private file access
- Hermes Desktop launch
- external integration start
- non-localhost listener creation
- broad filesystem scan

## Allowlist And Approval-Required Rules

Allowlist candidates remain candidates until implemented and tested.

Read-only commands such as status checks may classify as `allowed_read_only` only when:

- argv matches an exact or bounded pattern
- working directory is approved
- target paths are non-secret and in green or yellow zones
- no shell metacharacters are present
- output redaction is known

Commands that write, start services, stop services, commit, push, or touch orange zones must classify as `approval_required` unless denylisted.

## Integration Points

Future integration points:

- local task runner: classify proposed task paths and output paths before reading/writing
- future dry-run resident loop: classify tasks before processing
- future resident loop: classify every file and command request before execution is considered
- approval lookup: require matching approval records for approval-required outcomes
- audit log: record every classification, denial, approval requirement, and fail-closed event
- emergency stop: freeze or deny work after policy violations

## Test Strategy

Future tests should cover:

- path traversal attempts
- symlink escapes
- secret filenames
- red forbidden zones
- green/yellow/orange classification
- `sudo`
- destructive delete patterns
- force push
- hard reset
- safe status commands
- approved script syntax checks
- approval-required adapter service start
- approval-required `git push`
- shell metacharacter refusal
- ambiguous command fail-closed behavior
- audit/approval metadata in policy results

## Rollback

If classifiers are implemented incorrectly in a future phase:

- disable classifier integration
- keep command execution disabled
- fail closed on all policy decisions
- preserve audit and approval artifacts
- revert code changes through normal git rollback

## Acceptance Criteria Before Implementation

- this implementation plan is reviewed
- audit and approval implementation plan is complete
- file-zone and command policies are stable enough for first classifier tests
- tests are written before integration
- classifiers return policy results only
- no command execution exists
- denied and ambiguous cases fail closed
- audit and approval integration points are documented

## Plan Conclusion

The next implementation step after audit and approval planning should be classifier-only file-zone and command-policy modules. Those modules must classify and fail closed; they must not execute commands, edit files, start services, or enable resident mode.

Phase 6O implements the file-zone classifier primitive in `services/hermes_safety/file_zones.py`. Phase 6P implements the command-policy classifier primitive in `services/hermes_safety/command_policy.py` and shared `services/hermes_safety/policy_result.py`. Runtime enforcement, command execution, service control, resident mode, and external integrations remain disabled.
