# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for vault.cli — CLI subcommands."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest
from vault.cli import cmd_add, cmd_audit, cmd_list, cmd_remove, cmd_status, cmd_sync
from vault.config import SecretEntry, Target, VaultConfig


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    config = VaultConfig(keychain_service="test-vault")
    config.add_secret(SecretEntry(
        name="openai",
        account="openai",
        env_name="OPENAI_API_KEY",
        description="OpenAI",
        targets=[
            Target(platform="cloudflare-pages", project="corp"),
            Target(platform="local", file=str(tmp_path / ".dev.vars")),
        ],
    ))
    config.add_secret(SecretEntry(
        name="gemini",
        account="gemini",
        env_name="GEMINI_API_KEY",
        description="Gemini",
        targets=[
            Target(platform="vercel", project="app1"),
        ],
    ))
    cfg_path = tmp_path / "vault.yaml"
    config.save(cfg_path)
    return cfg_path


def _make_args(config_file: Path, **kwargs) -> argparse.Namespace:
    defaults = {
        "config": str(config_file),
        "audit_log": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestCmdStatus:
    @patch("vault.cli.check_status")
    def test_status_empty(self, mock_check, tmp_path):
        cfg_path = tmp_path / "vault.yaml"
        VaultConfig().save(cfg_path)
        args = _make_args(cfg_path)
        ret = cmd_status(args)
        assert ret == 0

    @patch("vault.cli.check_status")
    def test_status_with_secrets(self, mock_check, config_file, capsys):
        from vault.sync import StatusEntry
        mock_check.return_value = [
            StatusEntry(
                secret_name="openai",
                env_name="OPENAI_API_KEY",
                keychain_exists=True,
                target_status={"cloudflare-pages:corp": True, str(config_file.parent / ".dev.vars"): True},
            ),
        ]
        args = _make_args(config_file)
        ret = cmd_status(args)
        assert ret == 0
        out = capsys.readouterr().out
        assert "ANDON VAULT" in out
        assert "OPENAI_API_KEY" in out


class TestCmdSync:
    @patch("vault.cli.sync_all")
    def test_sync_all(self, mock_sync, config_file):
        from vault.sync import SyncReport, SyncResult
        mock_sync.return_value = SyncReport(results=[
            SyncResult(secret_name="openai", target_label="cf:corp", success=True),
        ])
        args = _make_args(config_file, name=None)
        ret = cmd_sync(args)
        assert ret == 0

    @patch("vault.cli.sync_secret")
    def test_sync_one(self, mock_sync, config_file):
        from vault.sync import SyncReport, SyncResult
        mock_sync.return_value = SyncReport(results=[
            SyncResult(secret_name="openai", target_label="cf:corp", success=True),
        ])
        args = _make_args(config_file, name="openai")
        ret = cmd_sync(args)
        assert ret == 0


class TestCmdAdd:
    @patch("vault.cli.sync_secret")
    @patch("vault.cli.keychain")
    def test_add_migrates_from_legacy_keychain(self, mock_kc, mock_sync, tmp_path, capsys):
        """claude-mcp-* に既存キーがあれば自動コピーする"""
        from vault.sync import SyncReport, SyncResult

        cfg_path = tmp_path / "vault.yaml"
        VaultConfig(keychain_service="test-vault").save(cfg_path)

        mock_kc.exists_by_service.return_value = True  # legacy key found
        mock_kc.get_by_service.return_value = "legacy-secret-value"
        mock_kc.put.return_value = None
        mock_kc.KeychainError = Exception

        mock_sync.return_value = SyncReport(results=[
            SyncResult(secret_name="openai", target_label="local:/tmp/x", success=True),
        ])

        args = _make_args(
            cfg_path,
            name="openai",
            account="openai",
            env="OPENAI_API_KEY",
            description="",
            target=["local:/tmp/x"],
        )
        ret = cmd_add(args)
        assert ret == 0

        out = capsys.readouterr().out
        assert "claude-mcp-openai" in out
        assert "andon-vault" in out

        # Verify: legacy key read by service, then stored under andon-vault
        mock_kc.exists_by_service.assert_called_once_with("claude-mcp-openai")
        mock_kc.get_by_service.assert_called_once_with("claude-mcp-openai")
        mock_kc.put.assert_called_once_with("test-vault", "openai", "legacy-secret-value")

    @patch("vault.cli.keychain")
    def test_add_prompts_when_no_legacy(self, mock_kc, tmp_path, capsys):
        """claude-mcp-* に見つからなければ getpass で入力を促す"""
        cfg_path = tmp_path / "vault.yaml"
        VaultConfig(keychain_service="test-vault").save(cfg_path)

        mock_kc.exists_by_service.return_value = False  # no legacy key
        mock_kc.put.return_value = None
        mock_kc.KeychainError = Exception

        args = _make_args(
            cfg_path,
            name="newkey",
            account="newkey",
            env="NEW_KEY",
            description="",
            target=None,
        )
        with patch("vault.cli.getpass.getpass", return_value="typed-value"):
            ret = cmd_add(args)

        assert ret == 0
        mock_kc.put.assert_called_once_with("test-vault", "newkey", "typed-value")


class TestCmdAudit:
    @patch("vault.cli.check_status")
    def test_audit_all_ok(self, mock_check, config_file, capsys):
        from vault.sync import StatusEntry
        mock_check.return_value = [
            StatusEntry(
                secret_name="openai",
                env_name="OPENAI_API_KEY",
                keychain_exists=True,
                target_status={"cf:corp": True},
            ),
        ]
        args = _make_args(config_file)
        ret = cmd_audit(args)
        assert ret == 0
        assert "All secrets in sync" in capsys.readouterr().out

    @patch("vault.cli.check_status")
    def test_audit_drift(self, mock_check, config_file, capsys):
        from vault.sync import StatusEntry
        mock_check.return_value = [
            StatusEntry(
                secret_name="openai",
                env_name="OPENAI_API_KEY",
                keychain_exists=True,
                target_status={"cf:corp": False},
            ),
        ]
        args = _make_args(config_file)
        ret = cmd_audit(args)
        assert ret == 1
        assert "MISSING" in capsys.readouterr().out


class TestCmdList:
    def test_list_secrets(self, config_file, capsys):
        args = _make_args(config_file)
        ret = cmd_list(args)
        assert ret == 0
        out = capsys.readouterr().out
        assert "openai" in out
        assert "OPENAI_API_KEY" in out
        assert "gemini" in out

    def test_list_empty(self, tmp_path, capsys):
        cfg = tmp_path / "vault.yaml"
        VaultConfig().save(cfg)
        args = _make_args(cfg)
        ret = cmd_list(args)
        assert ret == 0
        assert "No secrets" in capsys.readouterr().out


class TestCmdRemove:
    @patch("vault.cli.remove_secret")
    def test_remove_success(self, mock_remove, config_file, capsys):
        from vault.sync import SyncReport, SyncResult
        mock_remove.return_value = SyncReport(results=[
            SyncResult(secret_name="openai", target_label="cf:corp", success=True),
        ])
        args = _make_args(config_file, name="openai")
        ret = cmd_remove(args)
        assert ret == 0

    def test_remove_not_found(self, config_file, capsys):
        args = _make_args(config_file, name="nonexistent")
        ret = cmd_remove(args)
        assert ret == 1
        assert "not found" in capsys.readouterr().out
