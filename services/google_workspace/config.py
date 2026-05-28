"""Configuration for Google Workspace scaffolding."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_GOOGLE_AUDIT_LOG = "logs/google_workspace_audit.jsonl"


@dataclass(frozen=True)
class GoogleWorkspaceConfig:
    client_secret_file: str
    token_file: str
    oauth_scopes: tuple[str, ...]
    audit_log: str

    @classmethod
    def from_env(cls) -> "GoogleWorkspaceConfig":
        return cls(
            client_secret_file=os.getenv("GOOGLE_CLIENT_SECRET_FILE", ""),
            token_file=os.getenv("GOOGLE_TOKEN_FILE", ""),
            oauth_scopes=_split_scopes(os.getenv("GOOGLE_OAUTH_SCOPES", "")),
            audit_log=os.getenv("GOOGLE_AUDIT_LOG", DEFAULT_GOOGLE_AUDIT_LOG),
        )

    @property
    def client_secret_path(self) -> Path | None:
        if not self.client_secret_file:
            return None
        return Path(self.client_secret_file).expanduser()

    @property
    def token_path(self) -> Path | None:
        if not self.token_file:
            return None
        return Path(self.token_file).expanduser()

    @property
    def audit_log_path(self) -> Path:
        return Path(self.audit_log).expanduser()


def _split_scopes(raw: str) -> tuple[str, ...]:
    return tuple(scope.strip() for scope in raw.split(",") if scope.strip())
