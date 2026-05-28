"""Fail-closed Google OAuth scaffolding.

This module intentionally does not authenticate, open a browser, request scopes,
or call Google APIs. It only validates whether future auth inputs are present.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import GoogleWorkspaceConfig


@dataclass(frozen=True)
class AuthCheckResult:
    ok: bool
    status: str
    error: str = ""


class GoogleWorkspaceAuth:
    def __init__(self, config: GoogleWorkspaceConfig | None = None) -> None:
        self.config = config or GoogleWorkspaceConfig.from_env()

    def check_ready(self) -> AuthCheckResult:
        missing = []
        client_secret_path = self.config.client_secret_path
        token_path = self.config.token_path

        if client_secret_path is None:
            missing.append("GOOGLE_CLIENT_SECRET_FILE")
        elif not client_secret_path.exists():
            missing.append(f"client_secret_file_not_found:{client_secret_path}")

        if token_path is None:
            missing.append("GOOGLE_TOKEN_FILE")

        if not self.config.oauth_scopes:
            missing.append("GOOGLE_OAUTH_SCOPES")

        if missing:
            return AuthCheckResult(
                ok=False,
                status="not_ready",
                error="Missing Google OAuth configuration: " + ", ".join(missing),
            )

        return AuthCheckResult(
            ok=False,
            status="configured_but_auth_disabled",
            error="Google OAuth scaffolding is present, but authentication is intentionally disabled.",
        )

    def authenticate(self) -> AuthCheckResult:
        return AuthCheckResult(
            ok=False,
            status="disabled",
            error="Google authentication is not approved in Phase 4B.",
        )
