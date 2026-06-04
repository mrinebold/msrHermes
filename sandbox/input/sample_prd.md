# Sample Sandbox PRD

## Problem

The Helio team needs a safe way to validate the Hermes client after installation without granting it authority over external systems or durable shared state.

## Goals

- Exercise Hermes against local files only.
- Produce summaries into a local sandbox output directory.
- Confirm that the validation does not require Google Workspace, Supabase, Home Assistant, Helio dispatch, or agent bus access.
- Record startup time, execution time, and output quality.

## Non-Goals

- Do not configure model providers with live secrets.
- Do not start a background gateway.
- Do not connect cloud services.
- Do not send messages or dispatch agents.
- Do not read from or write to the Supabase agent bus.

## Acceptance Criteria

- Sandbox input and output directories exist.
- Hermes is invoked from the sandbox context.
- Output files are created under `sandbox/output/`.
- The validation result is documented in the PRD and changelog.
- Any limitation is recorded honestly rather than worked around with external integrations.
