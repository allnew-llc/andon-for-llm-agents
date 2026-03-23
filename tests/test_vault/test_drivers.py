# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for vault platform drivers."""
from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from vault.drivers import get_driver
from vault.drivers.cloudflare import CloudflarePagesDriver
from vault.drivers.local import LocalDriver
from vault.drivers.vercel import VercelDriver


class TestLocalDriver:
    @pytest.fixture
    def env_file(self, tmp_path: Path) -> Path:
        f = tmp_path / ".dev.vars"
        f.write_text("EXISTING_KEY=old_value\nOTHER=123\n")
        return f

    def test_exists_true(self, env_file: Path):
        driver = LocalDriver()
        assert driver.exists("EXISTING_KEY", str(env_file)) is True

    def test_exists_false(self, env_file: Path):
        driver = LocalDriver()
        assert driver.exists("NOPE", str(env_file)) is False

    def test_exists_no_file(self, tmp_path: Path):
        driver = LocalDriver()
        assert driver.exists("KEY", str(tmp_path / "missing")) is False

    def test_put_new_key(self, env_file: Path):
        driver = LocalDriver()
        assert driver.put("NEW_KEY", "new_val", str(env_file)) is True
        content = env_file.read_text()
        assert "NEW_KEY=new_val" in content
        assert "EXISTING_KEY=old_value" in content

    def test_put_update_existing(self, env_file: Path):
        driver = LocalDriver()
        assert driver.put("EXISTING_KEY", "updated", str(env_file)) is True
        content = env_file.read_text()
        assert "EXISTING_KEY=updated" in content
        assert "EXISTING_KEY=old_value" not in content

    def test_put_creates_file(self, tmp_path: Path):
        new_file = tmp_path / "sub" / ".env"
        driver = LocalDriver()
        assert driver.put("KEY", "val", str(new_file)) is True
        assert new_file.exists()
        assert "KEY=val" in new_file.read_text()

    def test_delete_existing(self, env_file: Path):
        driver = LocalDriver()
        assert driver.delete("EXISTING_KEY", str(env_file)) is True
        content = env_file.read_text()
        assert "EXISTING_KEY" not in content
        assert "OTHER=123" in content

    def test_delete_nonexistent(self, env_file: Path):
        driver = LocalDriver()
        assert driver.delete("NOPE", str(env_file)) is False

    def test_delete_no_file(self, tmp_path: Path):
        driver = LocalDriver()
        assert driver.delete("KEY", str(tmp_path / "missing")) is False

    def test_check_gitignore_found(self, tmp_path: Path):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".gitignore").write_text(".dev.vars\n.env\n")
        assert LocalDriver.check_gitignore(str(tmp_path / ".dev.vars")) is True

    def test_check_gitignore_not_found(self, tmp_path: Path):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".gitignore").write_text("*.log\n")
        assert LocalDriver.check_gitignore(str(tmp_path / ".dev.vars")) is False


class TestCloudflareDriver:
    @patch("vault.drivers.cloudflare._find_wrangler", return_value="/usr/bin/wrangler")
    @patch("vault.drivers.cloudflare.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout="OPENAI_API_KEY\nGEMINI_API_KEY\n"
        )
        driver = CloudflarePagesDriver()
        assert driver.exists("OPENAI_API_KEY", "my-project") is True

    @patch("vault.drivers.cloudflare._find_wrangler", return_value="/usr/bin/wrangler")
    @patch("vault.drivers.cloudflare.subprocess.run")
    def test_exists_false(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout="OTHER_KEY\n"
        )
        driver = CloudflarePagesDriver()
        assert driver.exists("OPENAI_API_KEY", "my-project") is False

    @patch("vault.drivers.cloudflare._find_wrangler", return_value="/usr/bin/wrangler")
    @patch("vault.drivers.cloudflare.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = CloudflarePagesDriver()
        assert driver.put("KEY", "val", "proj") is True
        call_args = mock_run.call_args
        assert call_args.kwargs.get("input") == "val"

    @patch("vault.drivers.cloudflare._find_wrangler", return_value="/usr/bin/wrangler")
    @patch("vault.drivers.cloudflare.subprocess.run")
    def test_delete_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = CloudflarePagesDriver()
        assert driver.delete("KEY", "proj") is True

    def test_exists_cli_not_found(self):
        """wrangler がない場合は False を返す"""
        with patch("vault.drivers.cloudflare._find_wrangler", side_effect=FileNotFoundError):
            driver = CloudflarePagesDriver()
            assert driver.exists("KEY", "proj") is False

    def test_put_cli_not_found(self):
        """wrangler がない場合は FileNotFoundError"""
        with patch("vault.drivers.cloudflare._find_wrangler", side_effect=FileNotFoundError("not found")):
            driver = CloudflarePagesDriver()
            with pytest.raises(FileNotFoundError):
                driver.put("KEY", "val", "proj")


class TestVercelDriver:
    @patch("vault.drivers.vercel._find_vercel", return_value="/usr/bin/vercel")
    @patch("vault.drivers.vercel.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout="OPENAI_API_KEY  production  encrypted\n"
        )
        driver = VercelDriver()
        assert driver.exists("OPENAI_API_KEY", "my-app") is True

    @patch("vault.drivers.vercel._find_vercel", return_value="/usr/bin/vercel")
    @patch("vault.drivers.vercel.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = VercelDriver()
        assert driver.put("KEY", "val", "app") is True
        # Verify --project flag is passed
        cmd = mock_run.call_args[0][0]
        assert "--project" in cmd
        assert "app" in cmd

    @patch("vault.drivers.vercel._find_vercel", return_value="/usr/bin/vercel")
    @patch("vault.drivers.vercel.subprocess.run")
    def test_delete_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = VercelDriver()
        assert driver.delete("KEY", "app") is True

    def test_exists_cli_not_found(self):
        """vercel がない場合は False を返す"""
        with patch("vault.drivers.vercel._find_vercel", side_effect=FileNotFoundError):
            driver = VercelDriver()
            assert driver.exists("KEY", "app") is False

    def test_put_cli_not_found(self):
        """vercel がない場合は FileNotFoundError"""
        with patch("vault.drivers.vercel._find_vercel", side_effect=FileNotFoundError("not found")):
            driver = VercelDriver()
            with pytest.raises(FileNotFoundError):
                driver.put("KEY", "val", "app")


class TestGetDriver:
    def test_known_platforms(self):
        assert isinstance(get_driver("cloudflare-pages"), CloudflarePagesDriver)
        assert isinstance(get_driver("vercel"), VercelDriver)
        assert isinstance(get_driver("local"), LocalDriver)

    def test_unknown_platform(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            get_driver("aws-secrets")
