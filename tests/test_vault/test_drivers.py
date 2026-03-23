# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for vault platform drivers."""
from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from vault.drivers import DRIVER_MAP, get_driver
from vault.drivers.aws_ssm import AWSSSMDriver
from vault.drivers.azure import AzureKeyVaultDriver
from vault.drivers.cloudflare import CloudflarePagesDriver
from vault.drivers.digitalocean import DigitalOceanDriver
from vault.drivers.flyio import FlyIODriver
from vault.drivers.gcp import GCPSecretManagerDriver
from vault.drivers.github import GitHubActionsDriver
from vault.drivers.gitlab import GitLabCIDriver
from vault.drivers.heroku import HerokuDriver
from vault.drivers.local import LocalDriver
from vault.drivers.netlify import NetlifyDriver
from vault.drivers.railway import RailwayDriver
from vault.drivers.supabase import SupabaseDriver
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
        # First call = vercel link (success), second = env ls
        mock_run.side_effect = [
            subprocess.CompletedProcess([], returncode=0),  # link
            subprocess.CompletedProcess(
                [], returncode=0, stdout="OPENAI_API_KEY  production  encrypted\n"
            ),  # env ls
        ]
        driver = VercelDriver()
        assert driver.exists("OPENAI_API_KEY", "my-app") is True

    @patch("vault.drivers.vercel._find_vercel", return_value="/usr/bin/vercel")
    @patch("vault.drivers.vercel.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.side_effect = [
            subprocess.CompletedProcess([], returncode=0),  # link
            subprocess.CompletedProcess([], returncode=0),  # env add
        ]
        driver = VercelDriver()
        assert driver.put("KEY", "val", "app") is True
        # Second call is env add — verify --cwd is passed
        env_add_call = mock_run.call_args_list[1]
        cmd = env_add_call[0][0]
        assert "--cwd" in cmd

    @patch("vault.drivers.vercel._find_vercel", return_value="/usr/bin/vercel")
    @patch("vault.drivers.vercel.subprocess.run")
    def test_delete_success(self, mock_run, _):
        mock_run.side_effect = [
            subprocess.CompletedProcess([], returncode=0),  # link
            subprocess.CompletedProcess([], returncode=0),  # env rm
        ]
        driver = VercelDriver()
        assert driver.delete("KEY", "app") is True

    @patch("vault.drivers.vercel._find_vercel", return_value="/usr/bin/vercel")
    @patch("vault.drivers.vercel.subprocess.run")
    def test_put_link_fails(self, mock_run, _):
        """vercel link が失敗した場合は False"""
        mock_run.return_value = subprocess.CompletedProcess([], returncode=1)
        driver = VercelDriver()
        assert driver.put("KEY", "val", "app") is False

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


class TestGitHubActionsDriver:
    @patch("vault.drivers.github._find_gh", return_value="/usr/bin/gh")
    @patch("vault.drivers.github.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout="OPENAI_API_KEY\tUpdated 2026-01-01\n"
        )
        driver = GitHubActionsDriver()
        assert driver.exists("OPENAI_API_KEY", "owner/repo") is True

    @patch("vault.drivers.github._find_gh", return_value="/usr/bin/gh")
    @patch("vault.drivers.github.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = GitHubActionsDriver()
        assert driver.put("KEY", "val", "owner/repo") is True
        assert mock_run.call_args.kwargs.get("input") == "val"

    @patch("vault.drivers.github._find_gh", return_value="/usr/bin/gh")
    @patch("vault.drivers.github.subprocess.run")
    def test_delete_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = GitHubActionsDriver()
        assert driver.delete("KEY", "owner/repo") is True


class TestHerokuDriver:
    @patch("vault.drivers.heroku._find_heroku", return_value="/usr/bin/heroku")
    @patch("vault.drivers.heroku.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout='{"OPENAI_API_KEY": "..."}'
        )
        driver = HerokuDriver()
        assert driver.exists("OPENAI_API_KEY", "my-app") is True

    @patch("vault.drivers.heroku._find_heroku", return_value="/usr/bin/heroku")
    @patch("vault.drivers.heroku.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = HerokuDriver()
        assert driver.put("KEY", "val", "my-app") is True


class TestNetlifyDriver:
    @patch("vault.drivers.netlify._find_netlify", return_value="/usr/bin/netlify")
    @patch("vault.drivers.netlify.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout="OPENAI_API_KEY=sk-...\nOTHER=123\n"
        )
        driver = NetlifyDriver()
        assert driver.exists("OPENAI_API_KEY", "my-site") is True

    @patch("vault.drivers.netlify._find_netlify", return_value="/usr/bin/netlify")
    @patch("vault.drivers.netlify.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = NetlifyDriver()
        assert driver.put("KEY", "val", "my-site") is True


class TestFlyIODriver:
    @patch("vault.drivers.flyio._find_fly", return_value="/usr/bin/fly")
    @patch("vault.drivers.flyio.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout="OPENAI_API_KEY\t1d ago\tset\n"
        )
        driver = FlyIODriver()
        assert driver.exists("OPENAI_API_KEY", "my-app") is True

    @patch("vault.drivers.flyio._find_fly", return_value="/usr/bin/fly")
    @patch("vault.drivers.flyio.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = FlyIODriver()
        assert driver.put("KEY", "val", "my-app") is True


class TestAWSSSMDriver:
    @patch("vault.drivers.aws_ssm._find_aws", return_value="/usr/bin/aws")
    @patch("vault.drivers.aws_ssm.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = AWSSSMDriver()
        assert driver.exists("OPENAI_API_KEY", "myapp") is True
        # Verify parameter name format
        cmd = mock_run.call_args[0][0]
        assert "/myapp/OPENAI_API_KEY" in cmd

    @patch("vault.drivers.aws_ssm._find_aws", return_value="/usr/bin/aws")
    @patch("vault.drivers.aws_ssm.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = AWSSSMDriver()
        assert driver.put("KEY", "val", "myapp") is True
        cmd = mock_run.call_args[0][0]
        assert "--overwrite" in cmd
        assert "--type" in cmd
        assert "SecureString" in cmd

    @patch("vault.drivers.aws_ssm._find_aws", return_value="/usr/bin/aws")
    @patch("vault.drivers.aws_ssm.subprocess.run")
    def test_delete_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = AWSSSMDriver()
        assert driver.delete("KEY", "myapp") is True


class TestGCPSecretManagerDriver:
    @patch("vault.drivers.gcp._find_gcloud", return_value="/usr/bin/gcloud")
    @patch("vault.drivers.gcp.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = GCPSecretManagerDriver()
        assert driver.exists("OPENAI_API_KEY", "my-project") is True

    @patch("vault.drivers.gcp._find_gcloud", return_value="/usr/bin/gcloud")
    @patch("vault.drivers.gcp.subprocess.run")
    def test_put_creates_new(self, mock_run, _):
        """versions add fails → creates new secret"""
        mock_run.side_effect = [
            subprocess.CompletedProcess([], returncode=1),  # versions add fails
            subprocess.CompletedProcess([], returncode=0),  # create succeeds
        ]
        driver = GCPSecretManagerDriver()
        assert driver.put("KEY", "val", "my-project") is True

    @patch("vault.drivers.gcp._find_gcloud", return_value="/usr/bin/gcloud")
    @patch("vault.drivers.gcp.subprocess.run")
    def test_put_adds_version(self, mock_run, _):
        """versions add succeeds → no create needed"""
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = GCPSecretManagerDriver()
        assert driver.put("KEY", "val", "my-project") is True
        assert mock_run.call_count == 1  # only versions add called


class TestAzureKeyVaultDriver:
    @patch("vault.drivers.azure._find_az", return_value="/usr/bin/az")
    @patch("vault.drivers.azure.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = AzureKeyVaultDriver()
        assert driver.exists("OPENAI_API_KEY", "my-vault") is True

    @patch("vault.drivers.azure._find_az", return_value="/usr/bin/az")
    @patch("vault.drivers.azure.subprocess.run")
    def test_name_normalization(self, mock_run, _):
        """Underscores are converted to hyphens for Azure"""
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = AzureKeyVaultDriver()
        driver.put("OPENAI_API_KEY", "val", "my-vault")
        cmd = mock_run.call_args[0][0]
        assert "OPENAI-API-KEY" in cmd

    @patch("vault.drivers.azure._find_az", return_value="/usr/bin/az")
    @patch("vault.drivers.azure.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = AzureKeyVaultDriver()
        assert driver.put("KEY", "val", "my-vault") is True


class TestDigitalOceanDriver:
    @patch("vault.drivers.digitalocean._find_doctl", return_value="/usr/bin/doctl")
    @patch("vault.drivers.digitalocean.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout='[{"key": "OPENAI_API_KEY", "value": "..."}]'
        )
        driver = DigitalOceanDriver()
        assert driver.exists("OPENAI_API_KEY", "app-id") is True

    @patch("vault.drivers.digitalocean._find_doctl", return_value="/usr/bin/doctl")
    @patch("vault.drivers.digitalocean.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = DigitalOceanDriver()
        assert driver.put("KEY", "val", "app-id") is True


class TestSupabaseDriver:
    @patch("vault.drivers.supabase._find_supabase", return_value="/usr/bin/supabase")
    @patch("vault.drivers.supabase.subprocess.run")
    def test_exists_true(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout="OPENAI_API_KEY\t1d ago\n"
        )
        driver = SupabaseDriver()
        assert driver.exists("OPENAI_API_KEY", "proj-ref") is True

    @patch("vault.drivers.supabase._find_supabase", return_value="/usr/bin/supabase")
    @patch("vault.drivers.supabase.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = SupabaseDriver()
        assert driver.put("KEY", "val", "proj-ref") is True


class TestRailwayDriver:
    @patch("vault.drivers.railway._find_railway", return_value="/usr/bin/railway")
    @patch("vault.drivers.railway.subprocess.run")
    def test_put_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = RailwayDriver()
        assert driver.put("KEY", "val", "proj-id") is True


class TestGitLabCIDriver:
    @patch("vault.drivers.gitlab._find_glab", return_value="/usr/bin/glab")
    @patch("vault.drivers.gitlab.subprocess.run")
    def test_put_update_then_create(self, mock_run, _):
        """update fails → create succeeds"""
        mock_run.side_effect = [
            subprocess.CompletedProcess([], returncode=1),  # update fails
            subprocess.CompletedProcess([], returncode=0),  # set succeeds
        ]
        driver = GitLabCIDriver()
        assert driver.put("KEY", "val", "group/project") is True

    @patch("vault.drivers.gitlab._find_glab", return_value="/usr/bin/glab")
    @patch("vault.drivers.gitlab.subprocess.run")
    def test_delete_success(self, mock_run, _):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        driver = GitLabCIDriver()
        assert driver.delete("KEY", "group/project") is True


class TestGetDriver:
    def test_all_registered_platforms(self):
        """All registered platforms return the correct driver type"""
        expected = {
            "aws-ssm": AWSSSMDriver,
            "azure-keyvault": AzureKeyVaultDriver,
            "cloudflare-pages": CloudflarePagesDriver,
            "digitalocean": DigitalOceanDriver,
            "flyio": FlyIODriver,
            "gcp-secrets": GCPSecretManagerDriver,
            "github-actions": GitHubActionsDriver,
            "gitlab-ci": GitLabCIDriver,
            "heroku": HerokuDriver,
            "local": LocalDriver,
            "netlify": NetlifyDriver,
            "railway": RailwayDriver,
            "supabase": SupabaseDriver,
            "vercel": VercelDriver,
        }
        for name, cls in expected.items():
            assert isinstance(get_driver(name), cls), f"Failed for {name}"
        assert len(DRIVER_MAP) == len(expected)

    def test_unknown_platform(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            get_driver("unknown")
