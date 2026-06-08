#!/usr/bin/env python3
"""Build a bounded explicit-context prompt for the Hermes pilot harness."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_PRD = Path("docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md")
DEFAULT_CHANGELOG = Path("docs/prd/CHANGELOG.md")
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prd", type=Path, default=DEFAULT_PRD)
    parser.add_argument("--changelog", type=Path, default=DEFAULT_CHANGELOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-prd-chars", type=int, default=700)
    parser.add_argument("--max-changelog-chars", type=int, default=600)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    prd_text = args.prd.read_text(encoding="utf-8")
    changelog_text = args.changelog.read_text(encoding="utf-8")
    prompt = build_prompt(prd_text, changelog_text, args.max_prd_chars, args.max_changelog_chars)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(prompt, encoding="utf-8")
    print(f"hermes_pilot_context_prompt.output={args.output}")
    print(f"hermes_pilot_context_prompt.bytes={len(prompt.encode('utf-8'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
