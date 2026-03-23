# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""macOS Keychain operations via the `security` CLI.

All operations use the generic-password type. Secret values are never
logged, printed, or persisted outside of Keychain.
"""
from __future__ import annotations

import subprocess


class KeychainError(Exception):
    """Raised when a Keychain operation fails."""


def exists(service: str, account: str) -> bool:
    """Check if a generic-password entry exists in Keychain."""
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-a", account],
        capture_output=True,
    )
    return result.returncode == 0


def get(service: str, account: str) -> str:
    """Retrieve a password value from Keychain. Raises KeychainError if not found."""
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise KeychainError(
            f"Secret not found in Keychain: service={service}, account={account}"
        )
    return result.stdout.strip()


def put(service: str, account: str, value: str) -> None:
    """Store or update a password in Keychain. Raises KeychainError on failure."""
    result = subprocess.run(
        [
            "security",
            "add-generic-password",
            "-s", service,
            "-a", account,
            "-w", value,
            "-U",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise KeychainError(
            f"Failed to store secret in Keychain: service={service}, account={account}"
        )


def delete(service: str, account: str) -> bool:
    """Delete a generic-password entry from Keychain. Returns True if deleted."""
    result = subprocess.run(
        ["security", "delete-generic-password", "-s", service, "-a", account],
        capture_output=True,
    )
    return result.returncode == 0


def exists_by_service(service: str) -> bool:
    """Check if any generic-password entry exists for a service (any account)."""
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service],
        capture_output=True,
    )
    return result.returncode == 0


def get_by_service(service: str) -> str:
    """Retrieve a password by service name only (any account). Raises KeychainError."""
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-w"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise KeychainError(f"Secret not found in Keychain: service={service}")
    return result.stdout.strip()
