# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for vault.config — vault.yaml read/write."""
from __future__ import annotations

from pathlib import Path

import pytest
from vault.config import SecretEntry, Target, VaultConfig


@pytest.fixture
def tmp_config(tmp_path: Path) -> Path:
    return tmp_path / "vault.yaml"


@pytest.fixture
def sample_config(tmp_config: Path) -> VaultConfig:
    config = VaultConfig(keychain_service="test-vault")
    config.add_secret(SecretEntry(
        name="openai",
        account="openai",
        env_name="OPENAI_API_KEY",
        description="OpenAI API Key",
        targets=[
            Target(platform="cloudflare-pages", project="my-project"),
            Target(platform="local", file="/tmp/test/.dev.vars"),
        ],
    ))
    config.add_secret(SecretEntry(
        name="gemini",
        account="gemini",
        env_name="GEMINI_API_KEY",
        description="Gemini API Key",
        targets=[
            Target(platform="vercel", project="my-app"),
        ],
    ))
    return config


class TestTarget:
    def test_from_dict_cloudflare(self):
        t = Target.from_dict({"platform": "cloudflare-pages", "project": "myapp"})
        assert t.platform == "cloudflare-pages"
        assert t.project == "myapp"
        assert t.label == "cloudflare-pages:myapp"

    def test_from_dict_local(self):
        t = Target.from_dict({"platform": "local", "file": "/tmp/.dev.vars"})
        assert t.platform == "local"
        assert t.file == "/tmp/.dev.vars"
        assert t.label == "/tmp/.dev.vars"

    def test_to_dict_cloudflare(self):
        t = Target(platform="cloudflare-pages", project="myapp")
        d = t.to_dict()
        assert d == {"platform": "cloudflare-pages", "project": "myapp"}

    def test_to_dict_local(self):
        t = Target(platform="local", file="/tmp/.dev.vars")
        d = t.to_dict()
        assert d == {"platform": "local", "file": "/tmp/.dev.vars"}


class TestSecretEntry:
    def test_from_dict(self):
        data = {
            "account": "my-acct",
            "env_name": "MY_KEY",
            "description": "desc",
            "targets": [
                {"platform": "vercel", "project": "app1"},
            ],
        }
        entry = SecretEntry.from_dict("test", data)
        assert entry.name == "test"
        assert entry.account == "my-acct"
        assert entry.env_name == "MY_KEY"
        assert len(entry.targets) == 1
        assert entry.targets[0].platform == "vercel"

    def test_roundtrip(self):
        entry = SecretEntry(
            name="x", account="x-acct", env_name="X_KEY",
            description="test",
            targets=[Target(platform="local", file="/tmp/x")],
        )
        d = entry.to_dict()
        restored = SecretEntry.from_dict("x", d)
        assert restored.account == entry.account
        assert restored.env_name == entry.env_name
        assert len(restored.targets) == 1


class TestVaultConfig:
    def test_load_nonexistent(self, tmp_path: Path):
        config = VaultConfig.load(tmp_path / "missing.yaml")
        assert config.version == 1
        assert len(config.secrets) == 0

    def test_save_and_load(self, tmp_config: Path, sample_config: VaultConfig):
        sample_config.save(tmp_config)
        assert tmp_config.exists()

        loaded = VaultConfig.load(tmp_config)
        assert loaded.keychain_service == "test-vault"
        assert len(loaded.secrets) == 2
        assert "openai" in loaded.secrets
        assert "gemini" in loaded.secrets

        openai = loaded.secrets["openai"]
        assert openai.env_name == "OPENAI_API_KEY"
        assert len(openai.targets) == 2
        assert openai.targets[0].platform == "cloudflare-pages"

    def test_add_and_remove(self):
        config = VaultConfig()
        entry = SecretEntry(name="test", account="t", env_name="TEST_KEY")
        config.add_secret(entry)
        assert "test" in config.secrets

        removed = config.remove_secret("test")
        assert removed is not None
        assert removed.name == "test"
        assert "test" not in config.secrets

    def test_remove_nonexistent(self):
        config = VaultConfig()
        assert config.remove_secret("nope") is None

    def test_get_secret(self):
        config = VaultConfig()
        config.add_secret(SecretEntry(name="a", account="a", env_name="A"))
        assert config.get_secret("a") is not None
        assert config.get_secret("b") is None

    def test_load_invalid_yaml(self, tmp_path: Path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("just a string\n")
        config = VaultConfig.load(bad)
        assert len(config.secrets) == 0
