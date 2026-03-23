# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for vault.cli — CLI subcommands."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest
from vault.cli import cmd_add, cmd_audit, cmd_list, cmd_remove, cmd_search, cmd_status, cmd_sync
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
    def test_add_from_keychain_with_service(self, mock_kc, mock_sync, tmp_path, capsys):
        """--from-keychain でサービス名を指定してインポートする"""
        from vault.sync import SyncReport, SyncResult

        cfg_path = tmp_path / "vault.yaml"
        VaultConfig(keychain_service="test-vault").save(cfg_path)

        mock_kc.get_by_service.return_value = "imported-value"
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
            from_keychain="my-custom-service",
            from_account=None,
            from_clipboard=False, from_cli=None,
        )
        ret = cmd_add(args)
        assert ret == 0

        out = capsys.readouterr().out
        assert "my-custom-service" in out
        assert "andon-vault" in out

        mock_kc.get_by_service.assert_called_once_with("my-custom-service")
        mock_kc.put.assert_called_once_with("test-vault", "openai", "imported-value")

    @patch("vault.cli.sync_secret")
    @patch("vault.cli.keychain")
    def test_add_from_keychain_with_account(self, mock_kc, mock_sync, tmp_path, capsys):
        """--from-keychain + --from-account で正確に指定する"""
        from vault.sync import SyncReport

        cfg_path = tmp_path / "vault.yaml"
        VaultConfig(keychain_service="test-vault").save(cfg_path)

        mock_kc.get.return_value = "precise-value"
        mock_kc.put.return_value = None
        mock_kc.KeychainError = Exception
        mock_sync.return_value = SyncReport()

        args = _make_args(
            cfg_path,
            name="openai",
            account="openai",
            env="OPENAI_API_KEY",
            description="",
            target=None,
            from_keychain="my-service",
            from_account="my-acct",
            from_clipboard=False, from_cli=None,
        )
        ret = cmd_add(args)
        assert ret == 0

        mock_kc.get.assert_called_once_with("my-service", "my-acct")

    @patch("vault.cli.keychain")
    def test_add_prompts_when_no_from_keychain(self, mock_kc, tmp_path, capsys):
        """--from-keychain なしなら getpass で入力を促す"""
        cfg_path = tmp_path / "vault.yaml"
        VaultConfig(keychain_service="test-vault").save(cfg_path)

        mock_kc.put.return_value = None
        mock_kc.KeychainError = Exception

        args = _make_args(
            cfg_path,
            name="newkey",
            account="newkey",
            env="NEW_KEY",
            description="",
            target=None,
            from_keychain=None,
            from_account=None,
            from_clipboard=False, from_cli=None,
        )
        with patch("vault.cli.getpass.getpass", return_value="typed-value"):
            ret = cmd_add(args)

        assert ret == 0
        mock_kc.put.assert_called_once_with("test-vault", "newkey", "typed-value")

    @patch("vault.cli.subprocess.run")
    @patch("vault.cli.keychain")
    def test_add_from_clipboard(self, mock_kc, mock_run, tmp_path, capsys):
        """--from-clipboard でクリップボードから値を取得する"""
        import subprocess as sp

        cfg_path = tmp_path / "vault.yaml"
        VaultConfig(keychain_service="test-vault").save(cfg_path)

        # pbpaste returns the value, pbcopy clears it
        mock_run.side_effect = [
            sp.CompletedProcess([], returncode=0, stdout="clipboard-secret\n"),  # pbpaste
            sp.CompletedProcess([], returncode=0),  # pbcopy (clear)
        ]
        mock_kc.put.return_value = None
        mock_kc.KeychainError = Exception

        args = _make_args(
            cfg_path, name="mykey", account="mykey", env="MY_KEY",
            description="", target=None,
            from_keychain=None, from_account=None,
            from_clipboard=True, from_cli=None,
        )
        ret = cmd_add(args)
        assert ret == 0
        mock_kc.put.assert_called_once_with("test-vault", "mykey", "clipboard-secret")
        out = capsys.readouterr().out
        assert "クリップボード" in out

    @patch("vault.cli.subprocess.run")
    @patch("vault.cli.keychain")
    def test_add_from_cli(self, mock_kc, mock_run, tmp_path, capsys):
        """--from-cli でコマンド出力から値を取得する"""
        import subprocess as sp

        cfg_path = tmp_path / "vault.yaml"
        VaultConfig(keychain_service="test-vault").save(cfg_path)

        mock_run.return_value = sp.CompletedProcess(
            [], returncode=0, stdout="gh-token-value\n"
        )
        mock_kc.put.return_value = None
        mock_kc.KeychainError = Exception

        args = _make_args(
            cfg_path, name="github", account="github", env="GITHUB_TOKEN",
            description="", target=None,
            from_keychain=None, from_account=None,
            from_clipboard=False, from_cli="gh auth token",
        )
        ret = cmd_add(args)
        assert ret == 0
        mock_kc.put.assert_called_once_with("test-vault", "github", "gh-token-value")
        out = capsys.readouterr().out
        assert "gh auth token" in out

    @patch("vault.cli.subprocess.run")
    @patch("vault.cli.keychain")
    def test_add_from_cli_failure(self, mock_kc, mock_run, tmp_path, capsys):
        """--from-cli のコマンドが失敗した場合"""
        import subprocess as sp

        cfg_path = tmp_path / "vault.yaml"
        VaultConfig(keychain_service="test-vault").save(cfg_path)

        mock_run.return_value = sp.CompletedProcess(
            [], returncode=1, stdout="", stderr="error"
        )
        mock_kc.KeychainError = Exception

        args = _make_args(
            cfg_path, name="fail", account="fail", env="FAIL_KEY",
            description="", target=None,
            from_keychain=None, from_account=None,
            from_clipboard=False, from_cli="false",
        )
        ret = cmd_add(args)
        assert ret == 1


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


class TestCmdSearch:
    @patch("vault.cli.keychain")
    def test_search_found(self, mock_kc, capsys):
        from vault.keychain import KeychainEntry
        mock_kc.search.return_value = [
            KeychainEntry(service="my-api-openai", account="user1", label="OpenAI"),
            KeychainEntry(service="openai-key", account="user2"),
        ]
        args = argparse.Namespace(pattern="openai")
        ret = cmd_search(args)
        assert ret == 0
        out = capsys.readouterr().out
        assert "2 件" in out
        assert "my-api-openai" in out
        assert "--from-keychain" in out

    @patch("vault.cli.keychain")
    def test_search_empty(self, mock_kc, capsys):
        mock_kc.search.return_value = []
        args = argparse.Namespace(pattern="nonexistent")
        ret = cmd_search(args)
        assert ret == 0
        assert "一致するエントリはありません" in capsys.readouterr().out
