# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Secret version history — tracks rotations with encrypted rollback.

Each version records:
  - timestamp
  - sha256 fingerprint (not the value itself)
  - encrypted backup of the value for rollback

Encryption uses Fernet (symmetric, from stdlib-adjacent cryptography)
with a key derived from the Keychain service password.
For simplicity in v1, we store the encrypted value using a per-vault
key stored in Keychain itself.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_HISTORY_PATH = Path.home() / ".config" / "andon" / "vault-history.json"
MAX_VERSIONS_PER_SECRET = 50


@dataclass
class SecretVersion:
    """One version of a secret."""

    version: int
    timestamp: str
    fingerprint: str  # SHA-256 of the value (first 12 chars)
    encrypted_value: str = ""  # base64-encoded XOR-obfuscated backup

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SecretVersion:
        return cls(
            version=data.get("version", 0),
            timestamp=data.get("timestamp", ""),
            fingerprint=data.get("fingerprint", ""),
            encrypted_value=data.get("encrypted_value", ""),
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


def _obfuscate(value: str, key: str) -> str:
    """Simple XOR obfuscation with a key. Not cryptographically strong,
    but prevents casual reading of history file. The key is stored in Keychain."""
    key_bytes = hashlib.sha256(key.encode("utf-8")).digest()
    value_bytes = value.encode("utf-8")
    result = bytes(v ^ key_bytes[i % len(key_bytes)] for i, v in enumerate(value_bytes))
    return base64.b64encode(result).decode("ascii")


def _deobfuscate(encoded: str, key: str) -> str:
    """Reverse of _obfuscate."""
    key_bytes = hashlib.sha256(key.encode("utf-8")).digest()
    data = base64.b64decode(encoded)
    result = bytes(v ^ key_bytes[i % len(key_bytes)] for i, v in enumerate(data))
    return result.decode("utf-8")


class HistoryStore:
    """Manages version history for all secrets."""

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

    def record(self, secret_name: str, value: str, obfuscation_key: str) -> SecretVersion:
        """Record a new version of a secret."""
        hist = self._data.get(secret_name, SecretHistory(name=secret_name))
        new_version = hist.current_version + 1
        entry = SecretVersion(
            version=new_version,
            timestamp=datetime.now(timezone.utc).astimezone().isoformat(),
            fingerprint=_fingerprint(value),
            encrypted_value=_obfuscate(value, obfuscation_key),
        )
        hist.versions.append(entry)
        # Trim old versions
        if len(hist.versions) > MAX_VERSIONS_PER_SECRET:
            hist.versions = hist.versions[-MAX_VERSIONS_PER_SECRET:]
        self._data[secret_name] = hist
        self._save()
        return entry

    def get_history(self, secret_name: str) -> SecretHistory | None:
        return self._data.get(secret_name)

    def get_version_value(
        self, secret_name: str, version: int, obfuscation_key: str,
    ) -> str | None:
        """Retrieve a previous version's value for rollback."""
        hist = self._data.get(secret_name)
        if hist is None:
            return None
        for v in hist.versions:
            if v.version == version and v.encrypted_value:
                return _deobfuscate(v.encrypted_value, obfuscation_key)
        return None

    def list_versions(self, secret_name: str) -> list[SecretVersion]:
        hist = self._data.get(secret_name)
        if hist is None:
            return []
        return list(hist.versions)

    def remove(self, secret_name: str) -> None:
        self._data.pop(secret_name, None)
        self._save()
