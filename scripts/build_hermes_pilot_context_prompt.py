#!/usr/bin/env python3
"""Build a bounded explicit-context prompt for the Hermes pilot harness."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_PRD = Path("docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md")
DEFAULT_CHANGELOG = Path("docs/prd/CHANGELOG.md")
DEFAULT_PILOT_MODE = Path("docs/HERMES_PILOT_MODE.md")
DEFAULT_SECURITY_MODEL = Path("docs/HERMES_SECURITY_MODEL.md")
DEFAULT_MODEL_PROVIDER = Path("docs/HERMES_MODEL_PROVIDER_PLAN.md")
DEFAULT_READINESS = Path("docs/HERMES_OPERATIONAL_READINESS_REVIEW.md")
DEFAULT_LOCAL_VALIDATION = Path("docs/HERMES_LOCAL_VALIDATION_CHECKLIST.md")
DEFAULT_ADAPTER_RUNBOOK = Path("docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md")
DEFAULT_OUTPUT = Path("sandbox/output/hermes_pilot_next_action_phase5ae_prompt.md")


def extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index
            break
    if start is None:
        return ""

    collected = [lines[start]]
    for line in lines[start + 1 :]:
        if line.startswith("## ") and line.strip() != heading:
            break
        collected.append(line)
    return "\n".join(collected).strip()


def first_paragraphs(section: str, count: int) -> str:
    paragraphs = [paragraph.strip() for paragraph in section.split("\n\n") if paragraph.strip()]
    return "\n\n".join(paragraphs[:count])


def leading_block_until(section: str, stop_line: str) -> str:
    selected: list[str] = []
    for line in section.splitlines():
        if line.strip() == stop_line:
            break
        selected.append(line)
    return "\n".join(selected).strip()


def excerpt_from_marker(text: str, marker: str, limit: int) -> str:
    start = text.find(marker)
    if start < 0:
        return ""
    return bounded_text(text[start:], limit)


def matching_lines(text: str, terms: tuple[str, ...], limit: int) -> str:
    selected: list[str] = []
    for line in text.splitlines():
        if any(term in line for term in terms):
            selected.append(line)
    return bounded_text("\n".join(selected), limit)


def bounded_text(text: str, limit: int) -> str:
    clean = "\n".join(line.rstrip() for line in text.strip().splitlines()).strip()
    if len(clean) <= limit:
        return clean
    marker = "\n[...excerpt truncated...]\n"
    if limit <= len(marker) + 40:
        return clean[:limit].rstrip()
    remaining = limit - len(marker)
    head = remaining // 2
    tail = remaining - head
    return f"{clean[:head].rstrip()}{marker}{clean[-tail:].lstrip()}"


def build_prompt(prd_text: str, changelog_text: str, prd_limit: int, changelog_limit: int) -> str:
    status_excerpt = first_paragraphs(extract_section(prd_text, "## Status"), 3)
    next_work_excerpt = first_paragraphs(extract_section(prd_text, "## Next Recommended Work"), 2)
    prd_parts = [
        status_excerpt,
        matching_lines(prd_text, ("| Phase 5AD |", "Phase 5AD controlled"), 260),
        next_work_excerpt,
    ]
    prd_excerpt = bounded_text("\n\n".join(part for part in prd_parts if part), prd_limit)

    changelog_today = extract_section(changelog_text, "## 2026-06-08")
    changelog_excerpt = bounded_text(
        leading_block_until(changelog_today, "- Completed Phase 5AB-AC managed adapter runner plus locked-down Hermes pilot config/harness."),
        changelog_limit,
    )

    return (
        "Summarize the current Hermes pilot status and identify the next safest phase.\n"
        "Use only the bounded local context below. Do not ask to read files. Do not use tools.\n"
        "Return only recommendation text in this exact format:\n"
        "Status: <one sentence>\n"
        "Next safest phase: <phase id and one sentence>\n"
        "Guardrails: <one sentence>\n"
        "Recommendation: <one sentence>\n\n"
        "Document/context:\n"
        "# Bounded local context for Phase 5AE\n\n"
        "## Master PRD excerpt\n"
        "Source: docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md\n"
        f"{prd_excerpt}\n\n"
        "## Changelog excerpt\n"
        "Source: docs/prd/CHANGELOG.md\n"
        f"{changelog_excerpt}\n"
    )


def build_phase5af_prompt(
    prd_text: str,
    changelog_text: str,
    pilot_mode_text: str,
    security_model_text: str,
) -> str:
    prd_excerpt = bounded_text(
        "\n\n".join(
            part
            for part in (
                first_paragraphs(extract_section(prd_text, "## Status"), 2),
                matching_lines(prd_text, ("| Phase 5AE |", "Phase 5AF should preserve"), 260),
            )
            if part
        ),
        330,
    )
    changelog_today = extract_section(changelog_text, "## 2026-06-08")
    changelog_excerpt = bounded_text(
        leading_block_until(changelog_today, "- Completed Phase 5AD controlled Hermes pilot execution."),
        300,
    )
    phase5ae_pilot_section = extract_section(pilot_mode_text, "## Phase 5AE Explicit Local Context Pilot Result")
    pilot_excerpt = bounded_text(
        "\n".join(
            line
            for line in phase5ae_pilot_section.splitlines()
            if any(
                term in line
                for term in (
                    "Phase 5AE ran",
                    "explicit local context",
                    "Adapter prompt mode",
                    "Pilot output usable",
                    "Treat Phase 5AE",
                    "Do not broaden",
                )
            )
        ),
        300,
    )
    security_excerpt = bounded_text(
        excerpt_from_marker(security_model_text, "Phase 5AE security result:", 700),
        300,
    )

    return (
        "Based on the current PRD, changelog, pilot-mode constraints, and security model, "
        "recommend the next safest Hermes operating-system phase after Phase 5AE.\n"
        "Use only the bounded local context below. Do not ask to read files. Do not use tools.\n"
        "Return only recommendation text with these labels:\n"
        "recommended phase name\n"
        "objective\n"
        "why this is safest\n"
        "explicit non-goals\n"
        "acceptance criteria\n"
        "whether human approval is required before execution\n\n"
        "Document/context:\n"
        "# Bounded local context for Phase 5AF\n\n"
        "## Master PRD excerpt\n"
        "Source: docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md\n"
        f"{prd_excerpt}\n\n"
        "## Changelog excerpt\n"
        "Source: docs/prd/CHANGELOG.md\n"
        f"{changelog_excerpt}\n\n"
        "## Pilot mode excerpt\n"
        "Source: docs/HERMES_PILOT_MODE.md\n"
        f"{pilot_excerpt}\n\n"
        "## Security model excerpt\n"
        "Source: docs/HERMES_SECURITY_MODEL.md\n"
        f"{security_excerpt}\n"
    )


def build_phase5ag_prompt(
    prd_text: str,
    changelog_text: str,
    pilot_mode_text: str,
    security_model_text: str,
    model_provider_text: str,
) -> str:
    prd_excerpt = bounded_text(
        "\n\n".join(
            part
            for part in (
                first_paragraphs(extract_section(prd_text, "## Status"), 1),
                matching_lines(prd_text, ("| Phase 5AF |", "Phase 5AG should execute"), 260),
            )
            if part
        ),
        230,
    )
    changelog_today = extract_section(changelog_text, "## 2026-06-08")
    changelog_excerpt = bounded_text(
        leading_block_until(changelog_today, "- Completed Phase 5AE controlled Hermes pilot with explicit local context."),
        220,
    )
    pilot_excerpt = bounded_text(
        excerpt_from_marker(pilot_mode_text, "## Phase 5AF Forward-Looking Pilot Recommendation", 520),
        230,
    )
    security_excerpt = bounded_text(
        excerpt_from_marker(security_model_text, "Phase 5AF security result:", 520),
        230,
    )
    provider_excerpt = bounded_text(
        excerpt_from_marker(model_provider_text, "## Phase 5AF Forward-Looking Pilot Recommendation", 520),
        230,
    )

    return (
        "Review the current Hermes Operating System PRD and supporting context for consistency, "
        "missing gates, stale status, and unclear next steps.\n"
        "Use only the bounded local context below. Do not ask to read files. Do not use tools.\n"
        "Return only recommendation text with these labels:\n"
        "PRD consistency findings\n"
        "missing or weak guardrails\n"
        "stale or contradictory status statements\n"
        "recommended PRD updates\n"
        "next safest phase recommendation\n"
        "whether human approval is required before execution\n\n"
        "Document/context:\n"
        "# Bounded local context for Phase 5AG\n\n"
        "## Master PRD excerpt\n"
        "Source: docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md\n"
        f"{prd_excerpt}\n\n"
        "## Changelog excerpt\n"
        "Source: docs/prd/CHANGELOG.md\n"
        f"{changelog_excerpt}\n\n"
        "## Pilot mode excerpt\n"
        "Source: docs/HERMES_PILOT_MODE.md\n"
        f"{pilot_excerpt}\n\n"
        "## Security model excerpt\n"
        "Source: docs/HERMES_SECURITY_MODEL.md\n"
        f"{security_excerpt}\n\n"
        "## Model provider excerpt\n"
        "Source: docs/HERMES_MODEL_PROVIDER_PLAN.md\n"
        f"{provider_excerpt}\n"
    )


def build_phase5av_prompt(
    prd_text: str,
    changelog_text: str,
    readiness_text: str,
    local_validation_text: str,
    adapter_runbook_text: str,
) -> str:
    prd_excerpt = bounded_text(
        "\n\n".join(
            part
            for part in (
                first_paragraphs(extract_section(prd_text, "## Status"), 2),
                matching_lines(prd_text, ("| Phase 5AU |", "Phase 5AV should"), 320),
            )
            if part
        ),
        360,
    )
    changelog_today = extract_section(changelog_text, "## 2026-06-09")
    changelog_excerpt = bounded_text(
        leading_block_until(changelog_today, "- Completed Phase 5AT manual adapter service operating procedure."),
        320,
    )
    readiness_excerpt = bounded_text(
        "\n\n".join(
            part
            for part in (
                extract_section(readiness_text, "## Current Proven Capabilities"),
                excerpt_from_marker(readiness_text, "## Phase 5AU Manual-Service Hermes Validation Result", 620),
            )
            if part
        ),
        360,
    )
    validation_excerpt = bounded_text(
        "\n\n".join(
            part
            for part in (
                extract_section(local_validation_text, "## Local-Only Invariants"),
                extract_section(local_validation_text, "## Next Gate"),
            )
            if part
        ),
        330,
    )
    runbook_excerpt = bounded_text(
        "\n\n".join(
            part
            for part in (
                extract_section(adapter_runbook_text, "## Phase 5AU Hermes Validation Result"),
                extract_section(adapter_runbook_text, "## Non-Goals"),
            )
            if part
        ),
        330,
    )

    return (
        "Review the current Hermes local-only operating setup.\n"
        "Use only the bounded local context below. Do not ask to read files. Do not use tools. "
        "Do not recommend external integrations, credentials, Desktop launch, Agent Bus activity, "
        "resident mode, RunAtLoad, or KeepAlive.\n"
        "Return only recommendation text with these labels:\n"
        "what is ready\n"
        "what is not ready\n"
        "top 5 risks\n"
        "next safest phase\n"
        "exact non-goals\n"
        "whether human approval is required\n\n"
        "Document/context:\n"
        "# Bounded local context for Phase 5AV\n\n"
        "## Master PRD excerpt\n"
        "Source: docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md\n"
        f"{prd_excerpt}\n\n"
        "## Changelog excerpt\n"
        "Source: docs/prd/CHANGELOG.md\n"
        f"{changelog_excerpt}\n\n"
        "## Operational readiness excerpt\n"
        "Source: docs/HERMES_OPERATIONAL_READINESS_REVIEW.md\n"
        f"{readiness_excerpt}\n\n"
        "## Local validation excerpt\n"
        "Source: docs/HERMES_LOCAL_VALIDATION_CHECKLIST.md\n"
        f"{validation_excerpt}\n\n"
        "## Adapter service runbook excerpt\n"
        "Source: docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md\n"
        f"{runbook_excerpt}\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prd", type=Path, default=DEFAULT_PRD)
    parser.add_argument("--changelog", type=Path, default=DEFAULT_CHANGELOG)
    parser.add_argument("--pilot-mode", type=Path, default=DEFAULT_PILOT_MODE)
    parser.add_argument("--security-model", type=Path, default=DEFAULT_SECURITY_MODEL)
    parser.add_argument("--model-provider", type=Path, default=DEFAULT_MODEL_PROVIDER)
    parser.add_argument("--readiness", type=Path, default=DEFAULT_READINESS)
    parser.add_argument("--local-validation", type=Path, default=DEFAULT_LOCAL_VALIDATION)
    parser.add_argument("--adapter-runbook", type=Path, default=DEFAULT_ADAPTER_RUNBOOK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-prd-chars", type=int, default=700)
    parser.add_argument("--max-changelog-chars", type=int, default=600)
    parser.add_argument("--phase5af", action="store_true", help="Build the forward-looking Phase 5AF prompt.")
    parser.add_argument("--phase5ag", action="store_true", help="Build the bounded PRD-review Phase 5AG prompt.")
    parser.add_argument("--phase5av", action="store_true", help="Build the local setup review Phase 5AV prompt.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    prd_text = args.prd.read_text(encoding="utf-8")
    changelog_text = args.changelog.read_text(encoding="utf-8")
    if args.phase5av:
        readiness_text = args.readiness.read_text(encoding="utf-8")
        local_validation_text = args.local_validation.read_text(encoding="utf-8")
        adapter_runbook_text = args.adapter_runbook.read_text(encoding="utf-8")
        prompt = build_phase5av_prompt(
            prd_text,
            changelog_text,
            readiness_text,
            local_validation_text,
            adapter_runbook_text,
        )
    elif args.phase5ag:
        pilot_mode_text = args.pilot_mode.read_text(encoding="utf-8")
        security_model_text = args.security_model.read_text(encoding="utf-8")
        model_provider_text = args.model_provider.read_text(encoding="utf-8")
        prompt = build_phase5ag_prompt(
            prd_text,
            changelog_text,
            pilot_mode_text,
            security_model_text,
            model_provider_text,
        )
    elif args.phase5af:
        pilot_mode_text = args.pilot_mode.read_text(encoding="utf-8")
        security_model_text = args.security_model.read_text(encoding="utf-8")
        prompt = build_phase5af_prompt(prd_text, changelog_text, pilot_mode_text, security_model_text)
    else:
        prompt = build_prompt(prd_text, changelog_text, args.max_prd_chars, args.max_changelog_chars)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(prompt, encoding="utf-8")
    print(f"hermes_pilot_context_prompt.output={args.output}")
    print(f"hermes_pilot_context_prompt.bytes={len(prompt.encode('utf-8'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
