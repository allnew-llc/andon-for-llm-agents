# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for vault.keychain — macOS Keychain operations (mocked)."""
from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest
from vault.keychain import KeychainError, delete, exists, get, put


class TestKeychainExists:
    @patch("vault.keychain.subprocess.run")
    def test_exists_true(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        assert exists("andon-vault", "openai") is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "find-generic-password" in args
        assert "-s" in args
        assert "andon-vault" in args

    @patch("vault.keychain.subprocess.run")
    def test_exists_false(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=44)
        assert exists("andon-vault", "openai") is False


class TestKeychainGet:
    @patch("vault.keychain.subprocess.run")
    def test_get_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout="secret-value\n"
        )
        val = get("andon-vault", "openai")
        assert val == "secret-value"

    @patch("vault.keychain.subprocess.run")
    def test_get_not_found(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=44, stdout="", stderr="not found"
        )
        with pytest.raises(KeychainError):
            get("andon-vault", "missing")


class TestKeychainPut:
    @patch("vault.keychain.subprocess.run")
    def test_put_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        put("andon-vault", "openai", "new-value")
        args = mock_run.call_args[0][0]
        assert "add-generic-password" in args
        assert "-U" in args

    @patch("vault.keychain.subprocess.run")
    def test_put_failure(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=1, stdout="", stderr="error"
        )
        with pytest.raises(KeychainError):
            put("andon-vault", "openai", "value")


class TestKeychainDelete:
    @patch("vault.keychain.subprocess.run")
    def test_delete_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=0)
        assert delete("andon-vault", "openai") is True

    @patch("vault.keychain.subprocess.run")
    def test_delete_not_found(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], returncode=44)
        assert delete("andon-vault", "openai") is False
