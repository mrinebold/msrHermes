"""Command classification primitive for Hermes safety policy.

This module classifies proposed commands only. It never executes commands.
"""

from __future__ import annotations

import re
import shlex
from pathlib import Path
from urllib.parse import urlparse

from services.hermes_safety.file_zones import classify_path, is_secret_like_path
from services.hermes_safety.policy_result import PolicyResult, allowed_readonly, approval_required, denied, unknown


REPO_ROOT = Path(__file__).resolve().parents[2]
SHELL_AMBIGUITY_RE = re.compile(r"(\||&&|\|\||;|<|>|\$\(|`)")
APPROVED_BASH_N_SCRIPTS = {
    "scripts/run_model_router_adapter.sh",
    "scripts/run_hermes_pilot.sh",
    "scripts/adapter_service_start.sh",
    "scripts/adapter_service_stop.sh",
    "scripts/adapter_service_status.sh",
    "scripts/run_hermes_local_task.sh",
    "scripts/hermes_local_status.sh",
}


def parse_command(command: str | list[str]) -> tuple[list[str], str | None]:
    if isinstance(command, list):
        return [str(part) for part in command], None

    if SHELL_AMBIGUITY_RE.search(command):
        return [], "ambiguous shell syntax fails closed"

    try:
        return shlex.split(command), None
    except ValueError as exc:
        return [], f"command parse failed: {exc}"


def _has_secret_or_forbidden_path(argv: list[str], repo_root: Path) -> bool:
    path_commands = {"cat", "head", "tail", "grep", "cp", "mv", "mkdir", "bash"}
    if not argv or Path(argv[0]).name not in path_commands:
        return any(".hermes" in arg or "Hermes.app" in arg for arg in argv)

    for arg in argv[1:]:
        if arg.startswith("-"):
            continue
        if is_secret_like_path(arg) or ".hermes" in arg or "Hermes.app" in arg:
            return True
        result = classify_path(arg, repo_root=repo_root, operation="read")
        if result["zone"] == "red":
            return True
    return False


def _is_rm_rf(argv: list[str]) -> bool:
    if not argv or argv[0] != "rm":
        return False
    flags = "".join(arg.lstrip("-") for arg in argv[1:] if arg.startswith("-"))
    return "r" in flags and "f" in flags


def _is_external_curl(argv: list[str]) -> bool:
    if not argv or argv[0] != "curl":
        return False
    urls = [arg for arg in argv[1:] if arg.startswith("http://") or arg.startswith("https://")]
    if not urls:
        return True
    for url in urls:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if host in {"127.0.0.1", "localhost"} and parsed.path in {"/health", "/v1/models"}:
            continue
        if host == "100.93.120.124" and parsed.port == 11434 and parsed.path == "/api/version":
            continue
        return True
    return False


def is_denied_command(argv: list[str], repo_root: str | Path | None = None) -> PolicyResult | None:
    root = Path(repo_root or REPO_ROOT).resolve(strict=False)
    if not argv:
        return denied("empty command", matched_rule="empty", command=argv)

    command = argv[0]
    basename = Path(command).name

    if basename == "sudo":
        return denied("sudo is forbidden", matched_rule="sudo", command=argv)
    if _is_rm_rf(argv):
        return denied("rm -rf is forbidden", matched_rule="rm_rf", command=argv)
    if basename == "chmod" and len(argv) > 1 and argv[1] == "777":
        return denied("chmod 777 is forbidden", matched_rule="chmod_777", command=argv)
    if basename == "chown":
        return denied("chown is forbidden", matched_rule="chown", command=argv)
    if basename == "launchctl" and any("com.msr.hermes.resident" in arg or "hermes_resident" in arg for arg in argv):
        return denied("launchctl for Hermes resident service is forbidden", matched_rule="launchctl_resident", command=argv)
    if basename == "security":
        return denied("security command is forbidden", matched_rule="security", command=argv)
    if basename == "osascript":
        return denied("osascript app control is forbidden", matched_rule="osascript", command=argv)
    if basename in {"ssh", "scp", "rsync"}:
        return denied("remote shell/copy commands are forbidden", matched_rule="remote_shell", command=argv)
    if basename == "brew" and len(argv) > 1 and argv[1] in {"install", "uninstall"}:
        return denied("brew install/uninstall is forbidden", matched_rule="brew_install", command=argv)
    if basename in {"pip", "pip3", "npm"} and len(argv) > 1 and argv[1] == "install":
        return denied("global package install is forbidden", matched_rule="global_install", command=argv)
    if argv[:2] == ["git", "push"] and any(arg == "--force" or arg.startswith("--force") for arg in argv[2:]):
        return denied("git push --force is forbidden", matched_rule="git_push_force", command=argv)
    if argv[:3] == ["git", "reset", "--hard"]:
        return denied("git reset --hard is forbidden", matched_rule="git_reset_hard", command=argv)
    if argv[:3] == ["git", "clean", "-fdx"]:
        return denied("git clean -fdx is forbidden", matched_rule="git_clean_fdx", command=argv)
    if basename == "curl" and _is_external_curl(argv):
        return denied("external curl is forbidden", matched_rule="external_curl", command=argv)
    if basename == "open" and any("Hermes" in arg for arg in argv[1:]):
        return denied("Hermes Desktop launch is forbidden", matched_rule="desktop_launch", command=argv)
    if _has_secret_or_forbidden_path(argv, root):
        return denied("secret or forbidden path access is forbidden", matched_rule="secret_path", command=argv)

    return None


def _bounded_git_log(argv: list[str]) -> bool:
    if argv[:3] != ["git", "log", "--oneline"]:
        return False
    if len(argv) == 5 and argv[3] == "-n" and argv[4].isdigit():
        return 1 <= int(argv[4]) <= 100
    if len(argv) == 4 and argv[3].startswith("-n") and argv[3][2:].isdigit():
        return 1 <= int(argv[3][2:]) <= 100
    return False


def _is_bash_n_approved(argv: list[str]) -> bool:
    if len(argv) != 3 or argv[:2] != ["bash", "-n"]:
        return False
    script = argv[2]
    return script in APPROVED_BASH_N_SCRIPTS


def is_allowed_readonly(argv: list[str], repo_root: str | Path | None = None) -> PolicyResult | None:
    root = Path(repo_root or REPO_ROOT).resolve(strict=False)
    if argv == ["pwd"]:
        return allowed_readonly("pwd is read-only", matched_rule="pwd", command=argv)
    if argv == ["git", "status", "--short"]:
        return allowed_readonly("git status --short is read-only", matched_rule="git_status_short", command=argv)
    if argv == ["git", "branch", "--show-current"]:
        return allowed_readonly("git branch --show-current is read-only", matched_rule="git_branch_current", command=argv)
    if argv == ["git", "diff", "--check"]:
        return allowed_readonly("git diff --check is read-only", matched_rule="git_diff_check", command=argv)
    if _bounded_git_log(argv):
        return allowed_readonly("bounded git log is read-only", matched_rule="git_log_bounded", command=argv)
    if argv == ["python3", "-m", "unittest", "discover"]:
        return allowed_readonly("unit test discovery command is allowed read-only/status", matched_rule="unittest_discover", command=argv)
    if _is_bash_n_approved(argv):
        return allowed_readonly("approved bash syntax check is read-only", matched_rule="bash_n_approved", command=argv)
    if argv in (["scripts/hermes_local_status.sh"], ["scripts/adapter_service_status.sh"]):
        return allowed_readonly("approved local status script is read-only", matched_rule="status_script", command=argv)
    if argv[0] == "curl" and not _is_external_curl(argv):
        return allowed_readonly("approved local/DevMonster status curl", matched_rule="approved_curl_status", command=argv)
    if argv[0] in {"cat", "head", "tail", "grep"} and len(argv) >= 2:
        path = argv[-1]
        zone = classify_path(path, repo_root=root, operation="read")
        if zone["decision"] == "allowed_readonly":
            return allowed_readonly("approved read-only file inspection", matched_rule="readonly_file_inspection", command=argv)
    return None


def requires_approval(argv: list[str], repo_root: str | Path | None = None) -> PolicyResult | None:
    root = Path(repo_root or REPO_ROOT).resolve(strict=False)
    if argv == ["scripts/adapter_service_start.sh"]:
        return approval_required("adapter service start requires human approval", matched_rule="adapter_service_start", command=argv)
    if argv and argv[0:2] == ["git", "commit"]:
        return approval_required("git commit requires human approval", matched_rule="git_commit", command=argv)
    if argv == ["git", "push", "origin", "main"]:
        return approval_required("git push origin main requires human approval", matched_rule="git_push_origin_main", command=argv)
    if argv and argv[0] in {"mkdir", "cp", "mv"}:
        paths = [arg for arg in argv[1:] if not arg.startswith("-")]
        if not paths:
            return unknown("path-sensitive write command has no target path", matched_rule="missing_path", command=argv)
        decisions = [classify_path(path, repo_root=root, operation="write")["decision"] for path in paths]
        if all(decision in {"allowed", "approval_required"} for decision in decisions):
            return approval_required("file operation requires human approval", matched_rule="approved_zone_file_write", command=argv)
    return None


def classify_command(command: str | list[str], repo_root: str | Path | None = None) -> PolicyResult:
    argv, error = parse_command(command)
    if error:
        return unknown(error, matched_rule="parse_or_shell_ambiguity", command=argv)

    denied_result = is_denied_command(argv, repo_root=repo_root)
    if denied_result is not None:
        return denied_result

    allowed_result = is_allowed_readonly(argv, repo_root=repo_root)
    if allowed_result is not None:
        return allowed_result

    approval_result = requires_approval(argv, repo_root=repo_root)
    if approval_result is not None:
        return approval_result

    return unknown("command is not in allowlist or approval-required list", matched_rule="unknown_command", command=argv)

