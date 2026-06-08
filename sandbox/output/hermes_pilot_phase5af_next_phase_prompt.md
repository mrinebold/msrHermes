Based on the current PRD, changelog, pilot-mode constraints, and security model, recommend the next safest Hermes operating-system phase after Phase 5AE.
Use only the bounded local context below. Do not ask to read files. Do not use tools.
Return only recommendation text with these labels:
recommended phase name
objective
why this is safest
explicit non-goals
acceptance criteria
whether human approval is required before execution

Document/context:
# Bounded local context for Phase 5AF

## Master PRD excerpt
Source: docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md
## Status

Phase 5AE validated the first usable controlled Hermes next-action pilot by supplying bounded PRD/changelog excerpts as explicit local conte
[...excerpt truncated...]
`; outpu
[...excerpt truncated...]
l. Also confirm or explicitly defer exposed credential rotation before any additional live Agent Bus reads or writes.

## Changelog excerpt
Source: docs/prd/CHANGELOG.md
## 2026-06-08

- Completed Phase 5AE controlled Hermes pilot with explicit local context.
- Added `scripts/build_hermes_pilot_context_pr
[...excerpt truncated...]
ing pilot using the same explicit-context and `local_summary` baseline to ask for the next Hermes operating-system phase after Phase 5AE.

## Pilot mode excerpt
Source: docs/HERMES_PILOT_MODE.md
Phase 5AE ran a second bounded pilot task on 2026-06-08 using explicit local context.
| Adapter prompt mode | `local_summary` |
| Pilot
[...excerpt truncated...]
rompt to produce forward-looking Phase 5AF text or use the same harness for one bounded PRD-review task. Do not broaden Hermes authority.

## Security model excerpt
Source: docs/HERMES_SECURITY_MODEL.md
Phase 5AE security result:

- built a bounded explicit-context prompt from local PRD/changelog excerpts under Codex control
- did not as
[...excerpt truncated...]
ment
- shell command scope
- file edit scope
- gateway service behavior
- Google scopes
- Home Assistant token
- agent dispatch interface
