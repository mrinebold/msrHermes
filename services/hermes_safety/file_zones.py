"""File-zone classification primitive for Hermes safety policy."""

from __future__ import annotations

from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

SECRET_NAME_MARKERS = ("secret", "token", "key", "credential")
GREEN_RELATIVE_ZONES = (
    "sandbox/hermes_inbox",
    "sandbox/hermes_outbox",
    "sandbox/hermes_archive",
    "sandbox/output",
    "logs/hermes_audit",
    "logs/hermes_approvals",
)
YELLOW_RELATIVE_ZONES = ("docs", "scripts", "tests")


def _home() -> Path:
    return Path.home().resolve(strict=False)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def is_secret_like_path(path: str | Path) -> bool:
    candidate = Path(path)
    parts = [part.lower() for part in candidate.parts]
    name = candidate.name.lower()

    if name == ".env" or name.endswith(".env"):
        return True

    if "private" in name:
        return True

    return any(marker in part for part in parts for marker in SECRET_NAME_MARKERS)


def _has_traversal(path: str | Path) -> bool:
    return any(part == ".." for part in Path(path).parts)


def normalize_path(path: str | Path, repo_root: str | Path | None = None) -> Path:
    root = Path(repo_root or REPO_ROOT).expanduser().resolve(strict=False)
    raw = Path(path).expanduser()
    if not raw.is_absolute():
        raw = root / raw
    return raw.resolve(strict=False)


def _result(
    *,
    zone: str,
    decision: str,
    reason: str,
    path: Path | None = None,
    operation: str,
) -> dict[str, Any]:
    return {
        "zone": zone,
        "decision": decision,
        "reason": reason,
        "path": str(path) if path is not None else None,
        "operation": operation,
    }


def _classify_home_forbidden(path: Path, operation: str) -> dict[str, Any] | None:
    home = _home()
    forbidden = (
        home / ".ssh",
        home / ".gnupg",
        home / ".aws",
        home / "Library" / "Keychains",
        home / "Library" / "Application Support" / "Google",
        home / "Library" / "Application Support" / "Firefox",
        home / "Library" / "Application Support" / "Google" / "Chrome",
        home / "Library" / "Application Support" / "Chromium",
    )
    for forbidden_path in forbidden:
        if _is_relative_to(path, forbidden_path):
            return _result(zone="red", decision="denied", reason="forbidden home credential or browser zone", path=path, operation=operation)

    if _is_relative_to(path, home / ".hermes"):
        if operation == "read" and path.name == "config.yaml":
            return _result(zone="orange", decision="approval_required", reason="approved config read requires explicit approval", path=path, operation=operation)
        return _result(zone="red", decision="denied", reason="~/.hermes is forbidden except approved config read", path=path, operation=operation)

    if _is_relative_to(path, home / ".config") and is_secret_like_path(path):
        return _result(zone="red", decision="denied", reason="credential-like ~/.config path", path=path, operation=operation)

    if _is_relative_to(path, home / "Desktop") or _is_relative_to(path, home / "Documents"):
        if not _is_relative_to(path, REPO_ROOT.resolve(strict=False)):
            return _result(zone="red", decision="denied", reason="arbitrary Desktop/Documents scanning is forbidden", path=path, operation=operation)

    if _is_relative_to(path, home / "Downloads"):
        return _result(zone="red", decision="denied", reason="Downloads requires explicit artifact approval", path=path, operation=operation)

    if _is_relative_to(path, home / "Pictures") or _is_relative_to(path, home / "Movies"):
        return _result(zone="red", decision="denied", reason="private media zone", path=path, operation=operation)

    return None


def classify_path(path: str | Path, repo_root: str | Path | None = None, operation: str = "read") -> dict[str, Any]:
    """Classify a path without reading or writing it."""

    if operation not in {"read", "write"}:
        return _result(zone="unknown", decision="denied", reason="unsupported operation", path=None, operation=operation)

    if _has_traversal(path):
        return _result(zone="red", decision="denied", reason="path traversal is forbidden", path=None, operation=operation)

    root = Path(repo_root or REPO_ROOT).expanduser().resolve(strict=False)
    normalized = normalize_path(path, repo_root=root)

    if Path(path).expanduser().is_symlink() and not _is_relative_to(normalized, root):
        return _result(zone="red", decision="denied", reason="symlink escapes approved root", path=normalized, operation=operation)

    if is_secret_like_path(normalized):
        return _result(zone="red", decision="denied", reason="secret-like path is forbidden", path=normalized, operation=operation)

    home_forbidden = _classify_home_forbidden(normalized, operation)
    if home_forbidden is not None:
        return home_forbidden

    if _is_relative_to(normalized, Path("/System")) or _is_relative_to(normalized, Path("/Library")):
        return _result(zone="red", decision="denied", reason="system directories are forbidden", path=normalized, operation=operation)

    green_zones = tuple((root / rel).resolve(strict=False) for rel in GREEN_RELATIVE_ZONES)
    for zone_path in green_zones:
        if _is_relative_to(normalized, zone_path):
            return _result(zone="green", decision="allowed", reason="green read/write zone", path=normalized, operation=operation)

    yellow_zones = tuple((root / rel).resolve(strict=False) for rel in YELLOW_RELATIVE_ZONES)
    for zone_path in yellow_zones:
        if _is_relative_to(normalized, zone_path):
            if operation == "read":
                return _result(zone="yellow", decision="allowed_readonly", reason="yellow read-only zone", path=normalized, operation=operation)
            return _result(zone="orange", decision="approval_required", reason="writes to docs/scripts/tests require approval", path=normalized, operation=operation)

    launch_agents = _home() / "Library" / "LaunchAgents"
    app_support = _home() / "Library" / "Application Support" / "Helio" / "hermes-adapter-service"
    if _is_relative_to(normalized, launch_agents) or _is_relative_to(normalized, app_support):
        return _result(zone="orange", decision="approval_required", reason="service support path requires approval", path=normalized, operation=operation)

    return _result(zone="unknown", decision="denied", reason="unknown path fails closed", path=normalized, operation=operation)
