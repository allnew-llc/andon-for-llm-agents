# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Sync orchestration — Keychain to platform targets.

Reads secret values from Keychain and deploys them to each configured
target via platform drivers. Values are held only in memory during sync
and never logged.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import audit, keychain
from .config import SecretEntry, Target, VaultConfig
from .drivers import get_driver


@dataclass
class SyncResult:
    """Result of a sync operation for one secret+target pair."""

    secret_name: str
    target_label: str
    success: bool
    message: str = ""


@dataclass
class SyncReport:
    """Aggregate report for a sync run."""

    results: list[SyncResult] = field(default_factory=list)

    @property
    def ok_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if not r.success)

    @property
    def all_ok(self) -> bool:
        return self.fail_count == 0


def _sync_one_target(
    entry: SecretEntry,
    target: Target,
    value: str,
    *,
    audit_log: Path | None = None,
) -> SyncResult:
    """Sync a single secret to a single target."""
    label = target.label
    try:
        driver = get_driver(target.platform)

        project = target.file if target.platform == "local" else target.project
        ok = driver.put(entry.env_name, value, project)

        result_str = "OK" if ok else "FAIL"
        audit.log_event("SYNC", entry.name, label, result_str, log_path=audit_log)
        return SyncResult(
            secret_name=entry.name,
            target_label=label,
            success=ok,
            message="" if ok else "Driver put returned False",
        )
    except FileNotFoundError as e:
        audit.log_event("SYNC", entry.name, label, "CLI_NOT_FOUND", log_path=audit_log)
        return SyncResult(
            secret_name=entry.name,
            target_label=label,
            success=False,
            message=str(e),
        )
    except Exception as e:
        audit.log_event("SYNC", entry.name, label, "ERROR", log_path=audit_log)
        return SyncResult(
            secret_name=entry.name,
            target_label=label,
            success=False,
            message=str(type(e).__name__),
        )


def sync_secret(
    config: VaultConfig,
    secret_name: str,
    *,
    audit_log: Path | None = None,
) -> SyncReport:
    """Sync one secret from Keychain to all its configured targets."""
    report = SyncReport()
    entry = config.get_secret(secret_name)
    if entry is None:
        report.results.append(SyncResult(
            secret_name=secret_name,
            target_label="(config)",
            success=False,
            message=f"Secret '{secret_name}' not found in vault config",
        ))
        return report

    try:
        value = keychain.get(config.keychain_service, entry.account)
    except keychain.KeychainError as e:
        report.results.append(SyncResult(
            secret_name=secret_name,
            target_label="keychain",
            success=False,
            message=str(e),
        ))
        return report

    for target in entry.targets:
        result = _sync_one_target(entry, target, value, audit_log=audit_log)
        report.results.append(result)

    return report


def sync_all(
    config: VaultConfig,
    *,
    audit_log: Path | None = None,
) -> SyncReport:
    """Sync all secrets from Keychain to their configured targets."""
    report = SyncReport()
    for name in config.secrets:
        sub = sync_secret(config, name, audit_log=audit_log)
        report.results.extend(sub.results)
    return report


@dataclass
class StatusEntry:
    """Status of one secret across all its targets."""

    secret_name: str
    env_name: str
    keychain_exists: bool
    target_status: dict[str, bool | None] = field(default_factory=dict)
    # None = not a target for this secret, True = exists, False = missing


def check_status(config: VaultConfig) -> list[StatusEntry]:
    """Check existence of all secrets across Keychain and targets."""
    entries: list[StatusEntry] = []
    for name, secret in config.secrets.items():
        kc_exists = keychain.exists(config.keychain_service, secret.account)
        target_status: dict[str, bool | None] = {}
        for target in secret.targets:
            try:
                driver = get_driver(target.platform)
                project = target.file if target.platform == "local" else target.project
                target_status[target.label] = driver.exists(secret.env_name, project)
            except Exception:
                target_status[target.label] = False
        entries.append(StatusEntry(
            secret_name=name,
            env_name=secret.env_name,
            keychain_exists=kc_exists,
            target_status=target_status,
        ))
    return entries


def remove_secret(
    config: VaultConfig,
    secret_name: str,
    *,
    audit_log: Path | None = None,
) -> SyncReport:
    """Remove a secret from Keychain and all its targets."""
    report = SyncReport()
    entry = config.get_secret(secret_name)
    if entry is None:
        report.results.append(SyncResult(
            secret_name=secret_name,
            target_label="(config)",
            success=False,
            message=f"Secret '{secret_name}' not found in vault config",
        ))
        return report

    # Delete from Keychain
    kc_ok = keychain.delete(config.keychain_service, entry.account)
    audit.log_event(
        "REMOVE", entry.name, "keychain",
        "OK" if kc_ok else "NOT_FOUND",
        log_path=audit_log,
    )

    # Delete from all targets
    for target in entry.targets:
        label = target.label
        try:
            driver = get_driver(target.platform)
            project = target.file if target.platform == "local" else target.project
            ok = driver.delete(entry.env_name, project)
            result_str = "OK" if ok else "NOT_FOUND"
            audit.log_event("REMOVE", entry.name, label, result_str, log_path=audit_log)
            report.results.append(SyncResult(
                secret_name=entry.name, target_label=label,
                success=True, message=result_str,
            ))
        except Exception as e:
            audit.log_event("REMOVE", entry.name, label, "ERROR", log_path=audit_log)
            report.results.append(SyncResult(
                secret_name=entry.name, target_label=label,
                success=False, message=str(type(e).__name__),
            ))

    # Remove from config
    config.remove_secret(secret_name)

    return report
