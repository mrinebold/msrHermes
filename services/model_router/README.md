# Helio Model Router

This package is the first local-first model routing layer for Helio Command Center.

## Routing Rules

Prefer DevMonster Gemma for:

- summaries
- brainstorming
- PRD drafting
- internal reasoning

Reserve cloud providers for future approved use:

- advanced coding
- large-context analysis
- fallback handling

Cloud provider files are placeholders only. They do not authenticate or send requests.
Cloud-reserved routes fail closed through placeholders until cloud routing is explicitly approved.

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
