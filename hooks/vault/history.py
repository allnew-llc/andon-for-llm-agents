# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Secret version history — tracks rotations with Keychain-native rollback.

Each version records metadata in a JSON file:
  - timestamp
  - sha256 fingerprint (not the value itself)

Rollback values are stored in macOS Keychain, NOT in the JSON file.
This eliminates the need for application-layer encryption — Keychain
(backed by Secure Enclave) is the sole custodian of secret values.

Keychain storage scheme:
  service: "{vault_service}-history"
  account: "{secret_name}:v{version}"
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import keychain
from .keychain import KeychainError

DEFAULT_HISTORY_PATH = Path.home() / ".config" / "andon" / "vault-history.json"
MAX_VERSIONS_PER_SECRET = 50
HISTORY_SERVICE_SUFFIX = "-history"


@dataclass
class SecretVersion:
    """One version of a secret (metadata only — value stays in Keychain)."""

    version: int
    timestamp: str
    fingerprint: str  # SHA-256 of the value (first 12 chars)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SecretVersion:
        return cls(
            version=data.get("version", 0),
            timestamp=data.get("timestamp", ""),
            fingerprint=data.get("fingerprint", ""),
        )


@dataclass
class SecretHistory:
    """Version history for one secret."""

    name: str
    versions: list[SecretVersion] = field(default_factory=list)

    @property
    def current_version(self) -> int:
        if not self.versions:
            return 0
        return self.versions[-1].version

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "versions": [v.to_dict() for v in self.versions],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SecretHistory:
        return cls(
            name=data.get("name", ""),
            versions=[SecretVersion.from_dict(v) for v in data.get("versions", [])],
        )


def _fingerprint(value: str) -> str:
    """SHA-256 fingerprint (first 12 hex chars). Never reveals the value."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _history_service(vault_service: str) -> str:
    """Derive the Keychain service name for version history storage."""
    return vault_service + HISTORY_SERVICE_SUFFIX


def _version_account(secret_name: str, version: int) -> str:
    """Derive the Keychain account name for a specific version."""
    return f"{secret_name}:v{version}"


class HistoryStore:
    """Manages version history for all secrets.

    Metadata (version, timestamp, fingerprint) is stored in a JSON file.
    Secret values for rollback are stored in macOS Keychain.
    """

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_HISTORY_PATH
        self._data: dict[str, SecretHistory] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            for name, hist_data in raw.get("secrets", {}).items():
                self._data[name] = SecretHistory.from_dict(hist_data)
        except (json.JSONDecodeError, ValueError, OSError):
            self._data = {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "secrets": {name: hist.to_dict() for name, hist in self._data.items()},
        }
        content = json.dumps(data, ensure_ascii=False, indent=2)
        fd = os.open(str(self.path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, content.encode("utf-8"))
        finally:
            os.close(fd)

    def record(
        self, secret_name: str, value: str, vault_service: str,
    ) -> SecretVersion:
        """Record a new version of a secret.

        Stores the value in Keychain and metadata in the JSON file.
        """
        hist = self._data.get(secret_name, SecretHistory(name=secret_name))
        new_version = hist.current_version + 1

        # Store value in Keychain
        svc = _history_service(vault_service)
        acct = _version_account(secret_name, new_version)
        try:
            keychain.put(svc, acct, value)
        except KeychainError:
            pass  # Best-effort: metadata still recorded for fingerprint tracking

        entry = SecretVersion(
            version=new_version,
            timestamp=datetime.now(timezone.utc).astimezone().isoformat(),
            fingerprint=_fingerprint(value),
        )
        hist.versions.append(entry)

        # Trim old versions and clean up their Keychain entries
        if len(hist.versions) > MAX_VERSIONS_PER_SECRET:
            removed = hist.versions[:-MAX_VERSIONS_PER_SECRET]
            hist.versions = hist.versions[-MAX_VERSIONS_PER_SECRET:]
            for old_v in removed:
                old_acct = _version_account(secret_name, old_v.version)
                keychain.delete(svc, old_acct)

        self._data[secret_name] = hist
        self._save()
        return entry

    def get_version_value(
        self, secret_name: str, version: int, vault_service: str,
    ) -> str | None:
        """Retrieve a previous version's value from Keychain for rollback."""
        hist = self._data.get(secret_name)
        if hist is None:
            return None
        # Verify the version exists in our metadata
        if not any(v.version == version for v in hist.versions):
            return None
        svc = _history_service(vault_service)
        acct = _version_account(secret_name, version)
        try:
            return keychain.get(svc, acct)
        except KeychainError:
            return None

    def get_history(self, secret_name: str) -> SecretHistory | None:
        return self._data.get(secret_name)

    def list_versions(self, secret_name: str) -> list[SecretVersion]:
        hist = self._data.get(secret_name)
        if hist is None:
            return []
        return list(hist.versions)

    def remove(self, secret_name: str, vault_service: str = "") -> None:
        """Remove all history for a secret, including Keychain entries."""
        hist = self._data.pop(secret_name, None)
        if hist and vault_service:
            svc = _history_service(vault_service)
            for v in hist.versions:
                acct = _version_account(secret_name, v.version)
                keychain.delete(svc, acct)
        self._save()
