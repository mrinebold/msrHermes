# Hermes Helio Delegation Interface

Phase: 6E
Status: proposal only; Agent Bus frozen; no Helio integration enabled

## Purpose

This document defines how Hermes may eventually coordinate with Helio/ANO without confusing ownership boundaries or writing to Agent Bus yet.

Phase 6E is documentation only. It does not connect Helio, write Supabase, read live Agent Bus records, use credentials, dispatch agents, start services, run Hermes live, launch Desktop, modify `~/.hermes`, or broaden Hermes authority.

## Boundary

- Hermes owns the Mac mini local operator role.
- Helio/ANO owns agent society and governance.
- DevMonster supplies inference, not operational authority.
- Agent Bus remains frozen until approved.
- Hermes may request coordination later, but it must not bypass Helio/ANO governance.
- Helio/ANO must not control the Mac shell without explicit future approval.

Hermes is not an ANO supervisor. Hermes must not impersonate Helio, a team lead, or an ANO governance process.

## Delegation Types

Future delegation may support:

- request advice
- request plan
- request review
- request agent routing recommendation
- submit local status summary
- receive task recommendation
- propose external action

Each delegation must declare authority tier, approval requirement, scope, expiration, and audit reference.

## Non-Goals

Phase 6E does not approve:

- direct Agent Bus writes
- Supabase writes
- external credential use
- autonomous Helio dispatch
- Helio control over Mac shell without explicit future approval
- Hermes impersonating ANO supervisor
- live Agent Bus reads
- service-role access
- Google, GitHub, Home Assistant, or cloud provider connection
- Desktop launch

## Future Message Shape Proposal

Future local delegation draft:

```json
{
  "delegation_id": "delegation_YYYYMMDDTHHMMSSZ_shortid",
  "timestamp": "2026-06-12T00:00:00Z",
  "from_agent": "hermes",
  "to_agent_or_team": "helio_or_named_team",
  "purpose": "request_review",
  "local_context_summary": "redacted local summary only",
  "requested_output": "routing recommendation",
  "authority_tier": "tier_1_recommend",
  "approval_required": true,
  "expiration": "2026-06-13T00:00:00Z",
  "audit_event_id": "audit_event_id_or_null",
  "secret_payloads": false
}
```

Rules:

- no secret payloads
- no raw credential values
- no broad local file contents by default
- no private message bodies by default
- include audit event ID once audit logging exists
- include approval requirement
- include expiration

## Future Staged Rollout

### Stage 0: Documentation Only

Define boundaries and message shape. No runtime or integration action.

### Stage 1: Local File-Based Delegation Drafts

Hermes may write local delegation drafts to an approved draft/outbox location. Drafts are not sent and do not touch Agent Bus.

### Stage 2: Read-Only Agent Bus Inspection

After credential decision and scope approval, Hermes may inspect approved Agent Bus records read-only. No writes.

### Stage 3: Draft Agent Bus Messages Only

Hermes may prepare proposed Agent Bus messages locally. No send or insert.

### Stage 4: Human-Approved Agent Bus Writes

Hermes may submit scoped Agent Bus writes only after explicit human approval, audit logging, emergency stop, and credential approval.

### Stage 5: Resident Delegated Operator

Hermes may coordinate recurring delegated work only under resident authority tiers, audit logs, emergency stop, allowlists, rate limits, and explicit human approval.

## Acceptance Criteria Before Any Helio Or Agent Bus Integration

- credential rotation decision complete
- scopes documented
- audit log implemented
- emergency stop implemented
- no secrets in messages
- human approval for writes
- read-only mode validated before writes
- Agent Bus RLS/permissions reviewed
- rollback and revocation documented
- delegation message schema reviewed

## Audit Requirements

Every delegation must eventually produce or link to audit metadata:

- delegation ID
- authority tier
- approval ID if applicable
- target team or agent
- requested output
- status
- expiration
- refusal reason if blocked

## Proposal Conclusion

Hermes may coordinate with Helio/ANO only through staged, audited delegation. Agent Bus remains frozen until a later credential and scope approval phase.
