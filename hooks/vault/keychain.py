# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""macOS Keychain operations via the `security` CLI.

All operations use the generic-password type. Secret values are never
logged, printed, or persisted outside of Keychain.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass


class KeychainError(Exception):
    """Raised when a Keychain operation fails."""


@dataclass
class KeychainEntry:
    """Metadata for a Keychain generic-password entry (no value)."""

    service: str
    account: str
    label: str = ""


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


# Pattern to extract quoted values from `security dump-keychain` output
_ATTR_RE = re.compile(r'"(\w+)"<blob>="([^"]*)"')


def search(pattern: str) -> list[KeychainEntry]:
    """Search Keychain for generic-password entries matching a pattern.

    Parses `security dump-keychain` output (which never includes passwords)
    and filters by substring match on service or account fields.

    Returns a list of KeychainEntry with metadata only — no values.
    """
    result = subprocess.run(
        ["security", "dump-keychain"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []

    entries: list[KeychainEntry] = []
    current_attrs: dict[str, str] = {}
    in_generic = False
    pattern_lower = pattern.lower()

    for line in result.stdout.splitlines():
        stripped = line.strip()

        if stripped.startswith("class:"):
            # Save previous entry if it was a generic password
            if in_generic and current_attrs:
                _maybe_add_entry(entries, current_attrs, pattern_lower)
            # Check if this is a generic password entry
            in_generic = '"genp"' in stripped
            current_attrs = {}
            continue

        if in_generic:
            m = _ATTR_RE.search(stripped)
            if m:
                current_attrs[m.group(1)] = m.group(2)

    # Don't forget the last entry
    if in_generic and current_attrs:
        _maybe_add_entry(entries, current_attrs, pattern_lower)

    return entries


def _maybe_add_entry(
    entries: list[KeychainEntry],
    attrs: dict[str, str],
    pattern_lower: str,
) -> None:
    """Add entry to list if service or account matches the pattern."""
    service = attrs.get("svce", "")
    account = attrs.get("acct", "")
    label = attrs.get("labl", "")

    if pattern_lower in service.lower() or pattern_lower in account.lower():
        entries.append(KeychainEntry(service=service, account=account, label=label))
