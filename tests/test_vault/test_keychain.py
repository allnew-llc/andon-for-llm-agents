# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for vault.keychain — macOS Keychain operations (mocked)."""
from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest
from vault.keychain import KeychainError, delete, exists, get, put, search


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
        # sh -c wrapper — verify the shell command contains security add
        args = mock_run.call_args[0][0]
        assert args[0] == "sh"
        assert "add-generic-password" in args[2]
        # Verify value is NOT in argv (security fix)
        assert "new-value" not in args

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


DUMP_OUTPUT = '''\
keychain: "/Users/user/Library/Keychains/login.keychain-db"
version: 512
class: "genp"
    attributes:
        "acct"<blob>="testuser"
        "labl"<blob>="OpenAI Key"
        "svce"<blob>="claude-mcp-openai"
class: "genp"
    attributes:
        "acct"<blob>="testuser"
        "labl"<blob>="Gemini Key"
        "svce"<blob>="claude-mcp-gemini"
class: "genp"
    attributes:
        "acct"<blob>="user1"
        "svce"<blob>="my-stripe-key"
class: "inet"
    attributes:
        "acct"<blob>="unrelated"
        "svce"<blob>="openai-web"
'''


class TestKeychainSearch:
    @patch("vault.keychain.subprocess.run")
    def test_search_by_service(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout=DUMP_OUTPUT
        )
        results = search("openai")
        assert len(results) == 1
        assert results[0].service == "claude-mcp-openai"
        assert results[0].account == "testuser"
        assert results[0].label == "OpenAI Key"

    @patch("vault.keychain.subprocess.run")
    def test_search_by_account(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout=DUMP_OUTPUT
        )
        results = search("user1")
        assert len(results) == 1
        assert results[0].service == "my-stripe-key"

    @patch("vault.keychain.subprocess.run")
    def test_search_multiple_matches(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout=DUMP_OUTPUT
        )
        results = search("claude-mcp")
        assert len(results) == 2

    @patch("vault.keychain.subprocess.run")
    def test_search_case_insensitive(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout=DUMP_OUTPUT
        )
        results = search("OPENAI")
        assert len(results) == 1

    @patch("vault.keychain.subprocess.run")
    def test_search_no_match(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout=DUMP_OUTPUT
        )
        results = search("nonexistent")
        assert len(results) == 0

    @patch("vault.keychain.subprocess.run")
    def test_search_excludes_inet_class(self, mock_run):
        """class: 'inet' のエントリは含まない（genp のみ）"""
        mock_run.return_value = subprocess.CompletedProcess(
            [], returncode=0, stdout=DUMP_OUTPUT
        )
        # "openai-web" is inet class, should not be returned
        results = search("openai-web")
        assert len(results) == 0
