#!/usr/bin/env python3
"""Build context-bearing local Hermes task files under sandbox/hermes_inbox."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INBOX_DIR = REPO_ROOT / "sandbox" / "hermes_inbox"
DEFAULT_OUTPUT = INBOX_DIR / "next_phase_recommendation_with_context.task.md"
DEFAULT_COMPACT_OUTPUT = INBOX_DIR / "next_phase_recommendation_compact.task.md"
COMPACT_CONTEXT_BUDGET = 1100

SECRET_PATH_TERMS = (
    ".env",
    "secret",
    "secrets",
    "token",
    "tokens",
    "credential",
    "credentials",
    "private_key",
    "apikey",
    "api_key",
)

REAL_SECRET_PATTERNS = (
    re.compile(r"sk-(?:live|proj|ant|or)-[A-Za-z0-9_-]{12,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{12,}"),
    re.compile("g" + r"hp_[A-Za-z0-9_]{20,}"),
    re.compile("github" + r"_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)(?:service_role|hass_token|access_token|refresh_token)\s*[:=]\s*eyJ[A-Za-z0-9_-]{20,}"),
)


@dataclass(frozen=True)
class ContextSource:
    path: Path
    char_limit: int


DEFAULT_SOURCES = (
    ContextSource(Path("docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md"), 1800),
    ContextSource(Path("docs/prd/CHANGELOG.md"), 1300),
    ContextSource(Path("docs/HERMES_OPERATIONAL_READINESS_REVIEW.md"), 1200),
    ContextSource(Path("docs/HERMES_LOCAL_TASK_INBOX.md"), 1000),
    ContextSource(Path("docs/HERMES_LOCAL_VALIDATION_CHECKLIST.md"), 1000),
    ContextSource(Path("docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md"), 900),
)

COMPACT_SOURCES = (
    ContextSource(Path("docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md"), 280),
    ContextSource(Path("docs/prd/CHANGELOG.md"), 220),
    ContextSource(Path("docs/HERMES_OPERATIONAL_READINESS_REVIEW.md"), 220),
    ContextSource(Path("docs/HERMES_LOCAL_TASK_INBOX.md"), 200),
    ContextSource(Path("docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md"), 180),
)


def repo_relative(path: Path) -> Path:
    resolved = path if path.is_absolute() else REPO_ROOT / path
    try:
        return resolved.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"Refusing source outside repo: {path}") from exc


def resolve_inbox_output(path: Path) -> Path:
    candidate = path if path.is_absolute() else REPO_ROOT / path
    parent = candidate.parent
    parent.mkdir(parents=True, exist_ok=True)
    resolved_parent = parent.resolve()
    inbox = INBOX_DIR.resolve()
    if resolved_parent != inbox:
        raise ValueError(f"Refusing output outside sandbox/hermes_inbox: {path}")
    return resolved_parent / candidate.name


def looks_secret_like_path(path: Path) -> bool:
    name = str(path).lower()
    return any(term in name for term in SECRET_PATH_TERMS)


def ensure_safe_source(path: Path) -> Path:
    relative = repo_relative(path)
    if looks_secret_like_path(relative):
        raise ValueError(f"Refusing secret-like source path: {relative}")
    source = REPO_ROOT / relative
    if not source.is_file():
        raise ValueError(f"Source file not found: {relative}")
    return relative


def contains_real_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in REAL_SECRET_PATTERNS)


def bounded_text(text: str, limit: int) -> str:
    clean = "\n".join(line.rstrip() for line in text.strip().splitlines()).strip()
    if len(clean) <= limit:
        return clean
    marker = "\n[...excerpt truncated...]\n"
    remaining = limit - len(marker)
    if remaining <= 40:
        return clean[:limit].rstrip()
    head = remaining // 2
    tail = remaining - head
    return f"{clean[:head].rstrip()}{marker}{clean[-tail:].lstrip()}"


def extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index
            break
    if start is None:
        return ""

    selected = [lines[start]]
    for line in lines[start + 1 :]:
        if line.startswith("## ") and line.strip() != heading:
            break
        selected.append(line)
    return "\n".join(selected).strip()


def matching_lines(text: str, terms: tuple[str, ...], limit: int) -> str:
    selected = [line for line in text.splitlines() if any(term in line for term in terms)]
    return bounded_text("\n".join(selected), limit)


def read_source_excerpt(source: ContextSource) -> tuple[Path, str]:
    relative = ensure_safe_source(source.path)
    text = (REPO_ROOT / relative).read_text(encoding="utf-8")
    if contains_real_secret(text):
        raise ValueError(f"Refusing source with real-looking secret marker: {relative}")
    return relative, bounded_text(text, source.char_limit)


def read_compact_source_excerpt(source: ContextSource) -> tuple[Path, str]:
    relative = ensure_safe_source(source.path)
    text = (REPO_ROOT / relative).read_text(encoding="utf-8")
    if contains_real_secret(text):
        raise ValueError(f"Refusing source with real-looking secret marker: {relative}")

    source_name = str(relative)
    if source_name == "docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md":
        excerpt = "\n".join(
            part
            for part in (
                extract_section(text, "## Status"),
                matching_lines(text, ("| Phase 5AZ |", "compact context-bearing task remediation"), 160),
            )
            if part
        )
    elif source_name == "docs/prd/CHANGELOG.md":
        excerpt = matching_lines(text, ("Phase 5AZ", "Phase 5AY", "failed closed", "context-bearing"), 260)
    elif source_name == "docs/HERMES_OPERATIONAL_READINESS_REVIEW.md":
        excerpt = matching_lines(text, ("Phase 5AZ", "Readiness position", "local-only operations remain safe"), 260)
    elif source_name == "docs/HERMES_LOCAL_TASK_INBOX.md":
        excerpt = matching_lines(text, ("Phase 5AZ", "Compact", "does not approve", "local-only"), 260)
    elif source_name == "docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md":
        excerpt = matching_lines(text, ("RunAtLoad=false", "KeepAlive=false", "adapter binds only", "Phase 5AZ"), 260)
    else:
        excerpt = text

    return relative, bounded_text(excerpt, source.char_limit)


def build_next_phase_recommendation(sources: tuple[ContextSource, ...]) -> str:
    sections: list[str] = []
    for source in sources:
        relative, excerpt = read_source_excerpt(source)
        sections.append(
            "\n".join(
                (
                    f"## Source: {relative}",
                    f"Character limit: {source.char_limit}",
                    "",
                    excerpt,
                )
            )
        )

    body = "\n\n".join(sections)
    return (
        "Using only the embedded local context below, recommend the next safest local-only Hermes phase.\n"
        "Do not request external integrations, credentials, Desktop launch, Agent Bus access, Google, "
        "Supabase, Home Assistant, GitHub, or Helio.\n"
        "Do not ask to read files. Do not use tools. Do not execute shell commands.\n"
        "Return exactly these fields:\n"
        "recommended phase name\n"
        "objective\n"
        "why it is safe\n"
        "required human approval\n"
        "non-goals\n"
        "acceptance criteria\n"
        "\n"
        "Embedded local context:\n"
        f"{body}\n"
    )


def compact_sections(sources: tuple[ContextSource, ...]) -> str:
    sections: list[str] = []
    for source in sources:
        relative, excerpt = read_compact_source_excerpt(source)
        sections.append(
            "\n".join(
                (
                    f"## Source: {relative}",
                    f"Character limit: {source.char_limit}",
                    excerpt,
                )
            )
        )
    body = "\n\n".join(sections)
    return bounded_text(body, COMPACT_CONTEXT_BUDGET)


def build_next_phase_recommendation_compact(sources: tuple[ContextSource, ...]) -> str:
    body = compact_sections(sources)
    return (
        "Using only the compact local context below, recommend the single next safest local-only Hermes phase.\n"
        "Keep the answer under 250 words. Do not request external integrations, credentials, Desktop launch, "
        "Agent Bus access, Google, Supabase, Home Assistant, GitHub, or Helio.\n"
        "Do not ask to read files. Do not use tools. Do not execute shell commands.\n"
        "Return:\n"
        "- phase name\n"
        "- objective\n"
        "- why safe\n"
        "- human approval required: yes/no\n"
        "- non-goals\n"
        "- acceptance criteria\n"
        "\n"
        f"Compact embedded context budget: {COMPACT_CONTEXT_BUDGET} chars\n"
        "Compact local context:\n"
        f"{body}\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-type", default="next_phase_recommendation", choices=("next_phase_recommendation",))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--compact", action="store_true", help="Build a compact next-phase recommendation task.")
    parser.add_argument(
        "--source",
        action="append",
        default=None,
        help="Optional source in path:char_limit form. Intended for tests; default uses approved sources.",
    )
    return parser.parse_args()


def parse_sources(raw_sources: list[str] | None) -> tuple[ContextSource, ...]:
    if not raw_sources:
        return DEFAULT_SOURCES
    parsed: list[ContextSource] = []
    for raw in raw_sources:
        if ":" not in raw:
            raise ValueError(f"Source must be path:char_limit: {raw}")
        path_part, limit_part = raw.rsplit(":", 1)
        try:
            limit = int(limit_part)
        except ValueError as exc:
            raise ValueError(f"Invalid source char limit: {raw}") from exc
        if limit <= 0:
            raise ValueError(f"Source char limit must be positive: {raw}")
        parsed.append(ContextSource(Path(path_part), limit))
    return tuple(parsed)


def main() -> int:
    args = parse_args()
    output_arg = DEFAULT_COMPACT_OUTPUT if args.compact and args.output == DEFAULT_OUTPUT else args.output
    output = resolve_inbox_output(output_arg)
    sources = parse_sources(args.source) if args.source else (COMPACT_SOURCES if args.compact else DEFAULT_SOURCES)
    if args.task_type == "next_phase_recommendation":
        if args.compact:
            task = build_next_phase_recommendation_compact(sources)
        else:
            task = build_next_phase_recommendation(sources)
    else:
        raise ValueError(f"Unsupported task type: {args.task_type}")
    if contains_real_secret(task):
        raise ValueError("Refusing to write task with real-looking secret marker")
    output.write_text(task, encoding="utf-8")
    print(f"hermes_local_task_builder.output={output.relative_to(REPO_ROOT)}")
    print(f"hermes_local_task_builder.bytes={len(task.encode('utf-8'))}")
    print(f"hermes_local_task_builder.sources={len(sources)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
