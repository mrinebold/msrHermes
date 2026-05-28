# Helio Model Router

This package is the first local-first model routing layer for Helio Command Center.

## Routing Rules

Prefer DevMonster Gemma4:26b for:

- private brainstorming
- summarization
- brainstorming
- PRD drafting
- internal planning
- internal reasoning
- low-risk agent reasoning

DevMonster Gemma4:26b is not yet approved for:

- autonomous execution decisions
- sending emails
- editing production code without review
- Google Workspace actions
- Home Assistant control

Reserve cloud providers for future approved use:

- advanced coding
- large-context analysis
- fallback handling

Cloud provider files are placeholders only. They do not authenticate or send requests.
Cloud-reserved routes fail closed through placeholders until cloud routing is explicitly approved.

See `docs/MODEL_ROUTING_POLICY.md` for the full policy.

## Route Records

Route decisions and generation responses record:

- task type
- selected provider
- selected model
- timestamp
- elapsed time for generation calls
- whether human approval is required

## Environment

- `DEVMONSTER_OLLAMA_URL`
- `DEVMONSTER_DEFAULT_MODEL`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

Legacy planning variables such as `GEMMA_BASE_URL`, `GEMMA_MODEL`, and `GEMMA_TIMEOUT` are still read as fallbacks.

## Safety

- No autonomous task execution.
- No Google integration.
- No Home Assistant integration.
- No prompt routing to cloud providers.
- DevMonster requests use explicit timeouts.

## Phase 3B Live Validation

Validation date: 2026-05-27.

Environment:

- `DEVMONSTER_OLLAMA_URL=http://100.93.120.124:11434`
- `DEVMONSTER_DEFAULT_MODEL=gemma4:26b`

Results:

- Health check succeeded in `0.119s`.
- Model listing succeeded in `0.109s`.
- `gemma4:26b` was present in the model list.
- Generate test prompt: `Reply with exactly: Router operational.`
- Generate test response: `Router operational.`
- Generate elapsed time: `68.697s`.

No autonomous routing, cloud provider execution, Google integration, Home Assistant integration, SSH enablement, or sensitive prompt data was used during validation.

Latency note: treat `gemma4:26b` as a deliberate reasoning worker, not a low-latency chat worker. A smaller model should be considered later for quick classification and command routing.
