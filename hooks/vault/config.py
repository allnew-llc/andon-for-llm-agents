# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""vault.yaml configuration read/write.

The vault config file (~/.config/andon/vault.yaml) contains secret metadata
only — never secret values. It maps Keychain accounts to environment variable
names and deployment targets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "andon"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "vault.yaml"
DEFAULT_KEYCHAIN_SERVICE = "andon-vault"


@dataclass
class Target:
    """A deployment target for a secret."""

    platform: str  # "cloudflare-pages", "vercel", "local"
    project: str = ""  # project name (cloudflare/vercel) or file path (local)
    file: str = ""  # only for platform=local

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Target:
        return cls(
            platform=data.get("platform", ""),
            project=data.get("project", ""),
            file=data.get("file", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"platform": self.platform}
        if self.platform == "local":
            if self.file:
                d["file"] = self.file
        else:
            if self.project:
                d["project"] = self.project
        return d

    @property
    def label(self) -> str:
        if self.platform == "local":
            return self.file or "local"
        return f"{self.platform}:{self.project}" if self.project else self.platform


@dataclass
class SecretEntry:
    """Metadata for one secret in the vault."""

    name: str
    account: str
    env_name: str
    description: str = ""
    targets: list[Target] = field(default_factory=list)

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> SecretEntry:
        targets = [Target.from_dict(t) for t in data.get("targets", [])]
        return cls(
            name=name,
            account=data.get("account", name),
            env_name=data.get("env_name", ""),
            description=data.get("description", ""),
            targets=targets,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "account": self.account,
            "env_name": self.env_name,
        }
        if self.description:
            d["description"] = self.description
        if self.targets:
            d["targets"] = [t.to_dict() for t in self.targets]
        return d


@dataclass
class VaultConfig:
    """In-memory representation of vault.yaml."""

    version: int = 1
    keychain_service: str = DEFAULT_KEYCHAIN_SERVICE
    secrets: dict[str, SecretEntry] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | None = None) -> VaultConfig:
        config_path = path or DEFAULT_CONFIG_PATH
        if not config_path.exists():
            return cls()
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return cls()
        secrets: dict[str, SecretEntry] = {}
        for name, data in raw.get("secrets", {}).items():
            if isinstance(data, dict):
                secrets[name] = SecretEntry.from_dict(name, data)
        return cls(
            version=raw.get("version", 1),
            keychain_service=raw.get("keychain_service", DEFAULT_KEYCHAIN_SERVICE),
            secrets=secrets,
        )

    def save(self, path: Path | None = None) -> None:
        config_path = path or DEFAULT_CONFIG_PATH
        config_path.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {
            "version": self.version,
            "keychain_service": self.keychain_service,
            "secrets": {name: entry.to_dict() for name, entry in self.secrets.items()},
        }
        config_path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def add_secret(self, entry: SecretEntry) -> None:
        self.secrets[entry.name] = entry

    def remove_secret(self, name: str) -> SecretEntry | None:
        return self.secrets.pop(name, None)

    def get_secret(self, name: str) -> SecretEntry | None:
        return self.secrets.get(name)
