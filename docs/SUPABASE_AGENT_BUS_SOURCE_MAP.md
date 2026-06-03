# Supabase Agent Bus Source Map

Phase 6A found no single canonical PRD that fully defines the Supabase agent messaging, chat, task, approval, and audit bus. Phase 6B elevated `/Users/michaelrinebold/dev/msrresearch/msrresearch/packages/ano-messaging` as the primary canonical source candidate for the portable message bus contract.

For Helio/Hermes planning, treat the references this way:

- Portable message bus authority: `/Users/michaelrinebold/dev/msrresearch/msrresearch/packages/ano-messaging`.
- Live MSR schema authority: Supabase migrations under `/Users/michaelrinebold/dev/msrresearch/msrresearch/database/supabase/migrations/`.
- Runtime behavior authority: backend services and route clients under `/Users/michaelrinebold/dev/msrresearch/msrresearch/backend/app/` and bot clients under `/Users/michaelrinebold/dev/msrresearch/msrresearch/summit-bot/service/tools/`.
- Intent and governance authority: shared PRDs under `/Users/michaelrinebold/dev/shared/prds/active/` and shared agent skills under `/Users/michaelrinebold/dev/shared/skills/`.

## Search Scope

Reviewed local Helio docs, local `docs/`, local `PRDs/` paths when present, `/Users/michaelrinebold/dev/shared/prds`, `/Users/michaelrinebold/dev/msrresearch/msrresearch`, exported Codex architecture material, and existing CivicGrantsAI/MSR agent documents available on disk. No Google Drive connector or Supabase connection was used.

## Source Documents

| Source | What it contributes |
| --- | --- |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/packages/ano-messaging/README.md` | Primary Phase 6B canonical source candidate. Defines the portable package, setup, components, table list, and dependency-injection architecture. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/packages/ano-messaging/ano_messaging/migrations/001_agent_messages.sql` | Package DDL for `agent_messages`, message enums, indexes, RLS, `claim_agent_message()`, and `expire_stale_agent_messages()`. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/packages/ano-messaging/ano_messaging/migrations/002_bot_outbound_messages.sql` | Package DDL for `bot_outbound_messages`, outbound statuses, indexes, and service-role RLS. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/packages/ano-messaging/ano_messaging/migrations/003_org_scope_and_config.sql` | Package DDL for `org_id` extensions, `org_messaging_config`, seeded MSR rosters, ACLs, and safety thresholds. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/packages/ano-messaging/ano_messaging/*.py` | Implemented service contract for config lookup, message send/claim/complete/fail/get, outbound send/ack/poll, directive scanning, and baseline computation. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/prds/2026-03-25-1600_ano-portable-messaging-layer.prd.md` | Found during Phase 6B. Explains the org-scoped portable messaging plan and confirms package extraction as the portability target. |
| `/Users/michaelrinebold/dev/shared/prds/active/msrresearch/2026-02-21-2200_inter-agent-messaging.prd.md` | Primary PRD for the database-backed `agent_messages` queue, REST API, risk gating, atomic claim behavior, and audit intent. It says the feature is deployed and active. |
| `/Users/michaelrinebold/dev/shared/prds/active/civicgrants/2026-02-27-1800_inter-agent-messaging-bridge.prd.md` | Bridge PRD for routing real work through `agent_messages`, including CLI-tier execution, cross-environment notification, and preserving an audit trail. |
| `/Users/michaelrinebold/dev/shared/prds/active/msrresearch/2026-03-04-1400_agent-messaging-prd-execution-verification.prd.md` | Explains the failure mode where PRDs disappeared after assignment and motivates durable task tracking, completion verification, and escalation. |
| `/Users/michaelrinebold/dev/shared/prds/active/civicgrants/2025-12-17-1626_distributed-agent-mesh-architecture.prd.md` | Defines distributed agent mesh principles, repository/server scoping, cross-agent communication queues, and Helio as the orchestrator. |
| `/Users/michaelrinebold/Documents/Codex/2026-05-07/stories-reader-availability-worktree/architecture/agent-messaging.md` | Most complete technical reference found. It describes `agent_messages`, `bot_outbound_messages`, `agent_tasks`, safety infrastructure, producer/consumer lifecycle, and the boundary between tasks and messages. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/database/supabase/migrations/20260221_agent_messages.sql` | Creates `agent_messages`, indexes, RLS, `claim_agent_message()`, and `expire_stale_agent_messages()`. This is the live DDL anchor for the message queue. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/database/supabase/migrations/004_chat_reception_schema.sql` | Creates `chat_sessions` and `chat_messages`. Useful for the conversation/message abstraction, but not enough by itself for agent task dispatch. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/database/supabase/migrations/20260325_bot_outbound_messages.sql` | Defines the outbound bot bus used to bridge local/Claude Code systems to leadership bots on civic-main. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/database/supabase/migrations/20260325_ano_messaging_phase1_org_scope.sql` | Adds `org_id`, org-scoped indexes, `org_messaging_config`, agent roster, bot roster, bot ACLs, and safety thresholds. Migration references the portable messaging PRD found in Phase 6B. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/database/supabase/migrations/20260329_activation_layer_phase0.sql` | Adds `agent_messages.initiation_type` and activation/governance tables for self-initiated agent work. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/database/supabase/migrations/20260307_agent_task_cascade_trigger.sql` | Shows how `agent_tasks` completion cascades dependent tasks into `agent_messages`. Clarifies the PRD-task bridge lifecycle. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/database/supabase/migrations/20260308_state_machine_updated_at.sql` | Enforces allowed status transitions for `agent_tasks` and `agent_messages`. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/backend/app/services/prd_task_bridge_service.py` | Runtime bridge from PRD assignments to `agent_tasks` and `agent_messages`, including `task_id`, `agent_name`, `task_type`, `status`, `priority`, `parent_prd_id`, `task_data`, dispatch, completion, failure, and cascade behavior. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/backend/app/database/messaging_client.py` | States that operational messaging writes to production Supabase, while schema/DDL development stays in dev. This is a critical environment boundary for Hermes. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/summit-bot/service/tools/ask_agent_client.py` | Shows the existing client contract for sending an agent directive through `/api/v1/agent-messages` and polling by message ID. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/summit-bot/service/tools/dispatch_client.py` | Shows leadership dispatch to Helio as the orchestrator, which matches the Hermes-owned Mac mini decision. |
| `/Users/michaelrinebold/dev/msrresearch/msrresearch/summit-bot/service/tools/agent_tasks_client.py` and `/Users/michaelrinebold/dev/msrresearch/msrresearch/backend/app/routes/agent_tasks_visibility.py` | Shows status/result visibility patterns for leadership bots, using `agent_messages` as the status source for dispatched work. |
| `/Users/michaelrinebold/dev/shared/skills/helio-orchestrator/SKILL.md` | Defines Helio as the orchestrator, quality gate enforcer, and multi-agent dispatch coordinator. |
| `/Users/michaelrinebold/dev/shared/skills/agents-reference/SKILL.md` | Lists the 34-agent roster and capabilities used by Helio when resolving specialist work. |

## Canonicality Finding

There is no single canonical source that covers all of the objects Phase 6A needs: conversations, messages, `agent_tasks`, `agent_task_events`, approvals, and audit logs.

Phase 6B finding: `packages/ano-messaging` is the canonical source candidate for the portable message bus, not for the full task bus. It clearly defines `agent_messages`, `bot_outbound_messages`, `org_messaging_config`, config caching, message methods, outbound polling, directive scanning, and baseline computation. It does not implement `agent_tasks`, approvals, or full conversation records.

## Implementation Consequence

Phase 6B produced [Agent Bus Contract](AGENT_BUS_CONTRACT.md). Do not scaffold `services/agent_bus/` yet. The contract is clear enough to propose a future Helio gateway scaffold, but implementation should wait until the Hermes-facing task and approval contract is pinned down.
