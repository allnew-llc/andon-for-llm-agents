# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for vault version history."""
from __future__ import annotations

from pathlib import Path

from vault.history import HistoryStore, _deobfuscate, _fingerprint, _obfuscate


class TestFingerprint:
    def test_deterministic(self):
        assert _fingerprint("hello") == _fingerprint("hello")

    def test_different_values(self):
        assert _fingerprint("a") != _fingerprint("b")

    def test_length(self):
        assert len(_fingerprint("anything")) == 12


class TestObfuscation:
    def test_roundtrip(self):
        key = "my-vault-key"
        value = "sk-secret-value-12345"
        encoded = _obfuscate(value, key)
        decoded = _deobfuscate(encoded, key)
        assert decoded == value

    def test_different_keys(self):
        value = "secret"
        e1 = _obfuscate(value, "key1")
        e2 = _obfuscate(value, "key2")
        assert e1 != e2

    def test_not_plaintext(self):
        encoded = _obfuscate("my-secret", "key")
        assert "my-secret" not in encoded


class TestHistoryStore:
    def test_record_and_list(self, tmp_path: Path):
        store = HistoryStore(path=tmp_path / "history.json")
        v1 = store.record("openai", "value-1", "vault-key")
        assert v1.version == 1
        assert v1.fingerprint == _fingerprint("value-1")

        v2 = store.record("openai", "value-2", "vault-key")
        assert v2.version == 2

        versions = store.list_versions("openai")
        assert len(versions) == 2

    def test_get_version_value(self, tmp_path: Path):
        store = HistoryStore(path=tmp_path / "history.json")
        store.record("test", "original-value", "key")
        store.record("test", "rotated-value", "key")

        # Retrieve v1
        val = store.get_version_value("test", 1, "key")
        assert val == "original-value"

        # Retrieve v2
        val = store.get_version_value("test", 2, "key")
        assert val == "rotated-value"

    def test_get_nonexistent(self, tmp_path: Path):
        store = HistoryStore(path=tmp_path / "history.json")
        assert store.get_version_value("nope", 1, "key") is None

    def test_persistence(self, tmp_path: Path):
        path = tmp_path / "history.json"
        store1 = HistoryStore(path=path)
        store1.record("x", "val", "key")

        # New instance should load persisted data
        store2 = HistoryStore(path=path)
        assert len(store2.list_versions("x")) == 1

    def test_max_versions(self, tmp_path: Path):
        store = HistoryStore(path=tmp_path / "history.json")
        for i in range(60):
            store.record("many", f"val-{i}", "key")
        versions = store.list_versions("many")
        assert len(versions) == 50  # MAX_VERSIONS_PER_SECRET

    def test_remove(self, tmp_path: Path):
        store = HistoryStore(path=tmp_path / "history.json")
        store.record("x", "val", "key")
        store.remove("x")
        assert store.list_versions("x") == []

    def test_get_history_none(self, tmp_path: Path):
        store = HistoryStore(path=tmp_path / "history.json")
        assert store.get_history("nope") is None
