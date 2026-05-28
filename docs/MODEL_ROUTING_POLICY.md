# Model Routing Policy

## Purpose

Helio routes model work to private/local inference first. DevMonster Gemma4:26b is the approved private reasoning worker. Cloud providers remain disabled and fail-closed until explicitly approved.

## Approved DevMonster Uses

DevMonster Gemma4:26b is approved for:

- private brainstorming
- summarization
- PRD drafting
- internal planning
- low-risk agent reasoning

## Optional Fast Local Model

`FAST_LOCAL_MODEL` defaults to `gemma3:4b` as a placeholder.

The fast model is intended for:

- classification
- routing
- short command interpretation
- quick summaries

The fast model is optional until installed and validated. Do not pull `gemma3:4b` or route live prompts to it until a separate validation phase approves it.

## Deep Reasoning Model

DevMonster Gemma4:26b remains the deeper reasoning worker for:

- PRDs
- internal reasoning
- long summaries
- planning

## Not Yet Approved

DevMonster Gemma4:26b is not yet approved for:

- autonomous execution decisions
- sending emails
- editing production code without review
- Google Workspace actions
- Home Assistant control

These task types require human approval and must not trigger external writes, shell execution, Home Assistant actions, email sending, or production code edits without a separate policy gate.

## Cloud Providers

Cloud providers remain disabled and fail-closed until explicit approval.

Reserved future cloud categories:

- advanced coding
- large-context analysis
- fallback handling

The current OpenAI and Anthropic providers are placeholders only. They do not authenticate and do not send requests.

## Routing Record

Every route decision should record:

- task type
- selected provider
- selected model
- timestamp
- elapsed time for generation calls
- whether human approval is required

The initial router logs these fields through structured logging events and returns them in `RouteResponse` for generation calls.

## Latency Note

The live DevMonster Gemma4:26b validation succeeded, but one generate call took `68.697s`.

Treat Gemma4:26b as a deliberate reasoning worker, not a low-latency chat worker. A smaller/faster model should be used later for quick classification, command routing, triage, and other latency-sensitive control-plane tasks after it is installed and validated.

## Current Default

- Prefer DevMonster Gemma4:26b for approved private reasoning tasks.
- Prefer `FAST_LOCAL_MODEL` for `classify`, `route`, `quick_summary`, and `command_parse` if configured.
- Fall back to `DEVMONSTER_DEFAULT_MODEL` when no fast model is configured.
- Fail closed for cloud-reserved tasks.
- Require human approval for action-oriented or external-write task categories.
- Do not enable autonomous task execution until a separate supervisor policy is approved.
