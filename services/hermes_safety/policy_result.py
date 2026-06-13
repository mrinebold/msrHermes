"""Shared policy classification result objects."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class PolicyResult:
    classification: str
    allowed: bool
    approval_required: bool
    reason: str
    risk_level: str = "low"
    matched_rule: str | None = None
    command: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def allowed_readonly(reason: str, *, matched_rule: str | None = None, command: list[str] | None = None) -> PolicyResult:
    return PolicyResult(
        classification="allowed_readonly",
        allowed=True,
        approval_required=False,
        reason=reason,
        risk_level="low",
        matched_rule=matched_rule,
        command=command or [],
    )


def approval_required(reason: str, *, matched_rule: str | None = None, command: list[str] | None = None) -> PolicyResult:
    return PolicyResult(
        classification="approval_required",
        allowed=False,
        approval_required=True,
        reason=reason,
        risk_level="medium",
        matched_rule=matched_rule,
        command=command or [],
    )


def denied(reason: str, *, matched_rule: str | None = None, command: list[str] | None = None) -> PolicyResult:
    return PolicyResult(
        classification="denied",
        allowed=False,
        approval_required=False,
        reason=reason,
        risk_level="high",
        matched_rule=matched_rule,
        command=command or [],
    )


def unknown(reason: str, *, matched_rule: str | None = None, command: list[str] | None = None) -> PolicyResult:
    return PolicyResult(
        classification="unknown",
        allowed=False,
        approval_required=False,
        reason=reason,
        risk_level="medium",
        matched_rule=matched_rule,
        command=command or [],
    )

