# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Vault CLI subcommands — add/sync/status/audit/rotate/remove/list.

All output avoids printing secret values. Status display uses symbols:
  checkmark = exists, cross = missing, dash = not a target.
"""
from __future__ import annotations

import argparse
import getpass
import subprocess
from pathlib import Path

from . import audit, keychain
from .config import DEFAULT_CONFIG_PATH, SecretEntry, Target, VaultConfig
from .history import HistoryStore
from .sync import SyncReport, check_status, remove_secret, sync_all, sync_secret


def _print_report(report: SyncReport) -> None:
    """Print sync report without revealing secret values."""
    for r in report.results:
        mark = "OK" if r.success else "FAIL"
        msg = f"  [{mark}] {r.secret_name} -> {r.target_label}"
        if r.message and not r.success:
            msg += f"  ({r.message})"
        print(msg)
    print(f"\n  {report.ok_count} succeeded, {report.fail_count} failed")


def cmd_status(args: argparse.Namespace) -> int:
    """Show sync status of all vault secrets."""
    config = VaultConfig.load(Path(args.config))
    if not config.secrets:
        print("ANDON VAULT — No secrets configured.")
        print(f"  Config: {args.config}")
        return 0

    entries = check_status(config)

    # Collect all unique target labels
    all_targets: list[str] = []
    for entry in entries:
        for label in entry.target_status:
            if label not in all_targets:
                all_targets.append(label)

    # Shorten target labels for display
    short_labels = []
    for t in all_targets:
        if ":" in t:
            parts = t.split(":", 1)
            platform = parts[0].replace("cloudflare-pages", "CF").replace("vercel", "Vercel")
            short_labels.append(f"{platform}:{parts[1][:12]}")
        else:
            name = Path(t).name if "/" in t else t
            short_labels.append(name[:16])

    print("\nANDON VAULT — Secret Registry\n")
    print(f"  Keychain service: {config.keychain_service} ({len(config.secrets)} keys)\n")

    # Table header
    col_w = max(14, *(len(s) for s in short_labels)) if short_labels else 14
    header = f"  | {'Secret':<20} | {'Keychain':^8} |"
    for sl in short_labels:
        header += f" {sl:^{col_w}} |"
    print(header)
    print(f"  |{'-' * 22}|{'-' * 10}|" + "|".join(f"{'-' * (col_w + 2)}" for _ in short_labels) + "|")

    missing: list[str] = []
    for entry in entries:
        kc = "\u2713" if entry.keychain_exists else "\u2717"
        row = f"  | {entry.env_name:<20} | {kc:^8} |"
        for i, label in enumerate(all_targets):
            status = entry.target_status.get(label)
            if status is None:
                sym = "\u2014"  # em-dash = not a target
            elif status:
                sym = "\u2713"
            else:
                sym = "\u2717"
                missing.append(f"{entry.env_name} -> {short_labels[i]}")
            row += f" {sym:^{col_w}} |"
        print(row)

    if missing:
        print(f"\n  Warning: {len(missing)} secret(s) missing:")
        for m in missing:
            print(f"    {m}")
        print("  Run: andon vault sync")
    else:
        print("\n  All secrets in sync.")

    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync secrets from Keychain to targets."""
    config = VaultConfig.load(Path(args.config))
    audit_log = Path(args.audit_log) if args.audit_log else None

    if args.name:
        report = sync_secret(config, args.name, audit_log=audit_log)
    else:
        report = sync_all(config, audit_log=audit_log)

    _print_report(report)
    return 0 if report.all_ok else 1


def _resolve_secret_value(args: argparse.Namespace) -> str | None:
    """Resolve a secret value from the specified source. Returns None on failure."""
    from_kc = getattr(args, "from_keychain", None)
    from_acct = getattr(args, "from_account", None)
    from_clip = getattr(args, "from_clipboard", False)
    from_cli = getattr(args, "from_cli", None)

    # 1. --from-keychain: import from existing Keychain entry
    if from_kc:
        try:
            if from_acct:
                value = keychain.get(from_kc, from_acct)
                print(f"Keychain からインポート: service={from_kc}, account={from_acct}")
            else:
                value = keychain.get_by_service(from_kc)
                print(f"Keychain からインポート: service={from_kc}")
            print("  -> andon-vault へコピーします")
            return value
        except keychain.KeychainError:
            print(f"Error: Keychain エントリが見つかりません: service={from_kc}")
            return None

    # 2. --from-clipboard: read from macOS clipboard, then clear it
    if from_clip:
        result = subprocess.run(["pbpaste"], capture_output=True, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            print("Error: クリップボードが空です。")
            return None
        value = result.stdout.strip()
        # Clear clipboard immediately for security
        subprocess.run(["pbcopy"], input="", text=True)
        print("クリップボードから取得しました（クリップボードはクリア済み）")
        return value

    # 3. --from-cli: run a command and capture its stdout
    if from_cli:
        import shlex

        try:
            argv = shlex.split(from_cli)
        except ValueError as e:
            print(f"Error: コマンドの解析に失敗: {e}")
            return None
        try:
            result = subprocess.run(
                argv,
                capture_output=True, text=True, timeout=30,
            )
        except FileNotFoundError:
            print(f"Error: コマンドが見つかりません: {argv[0]}")
            return None
        except subprocess.TimeoutExpired:
            print("Error: コマンドがタイムアウトしました")
            return None
        if result.returncode != 0:
            print(f"Error: コマンドが失敗しました (exit {result.returncode})")
            return None
        value = result.stdout.strip()
        if not value:
            print("Error: コマンドの出力が空です")
            return None
        print("コマンドから取得しました")
        return value

    # 4. Fallback: interactive prompt (no echo)
    try:
        value = getpass.getpass(f"Enter value for {args.name}: ")
        if not value:
            print("Error: Empty value.")
            return None
        return value
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return None


def cmd_add(args: argparse.Namespace) -> int:
    """Add a new secret to Keychain + vault config."""
    config = VaultConfig.load(Path(args.config))
    audit_log = Path(args.audit_log) if args.audit_log else None

    if config.get_secret(args.name):
        print(f"Error: Secret '{args.name}' already exists. Use 'rotate' to update.")
        return 1

    account = args.account or args.name

    # Resolve value from one of the sources (priority order)
    value = _resolve_secret_value(args)
    if value is None:
        return 1

    # Parse targets
    targets: list[Target] = []
    for t_str in args.target or []:
        if ":" not in t_str:
            print(f"Error: Target must be platform:project — got '{t_str}'")
            return 1
        platform, project = t_str.split(":", 1)
        if platform == "local":
            targets.append(Target(platform="local", file=project))
        else:
            targets.append(Target(platform=platform, project=project))

    # Store in Keychain under andon-vault service
    try:
        keychain.put(config.keychain_service, account, value)
    except keychain.KeychainError as e:
        print(f"Error: Failed to store in Keychain: {type(e).__name__}")
        return 1

    # Add to config
    entry = SecretEntry(
        name=args.name,
        account=account,
        env_name=args.env,
        description=args.description or "",
        targets=targets,
    )
    config.add_secret(entry)
    config.save(Path(args.config))

    # Record version history
    history = HistoryStore()
    history.record(args.name, value, config.keychain_service)

    audit.log_event("ADD", args.name, "keychain", "OK", log_path=audit_log)

    print(f"Added '{args.name}' ({args.env}) with {len(targets)} target(s).")

    # Sync immediately if targets exist
    if targets:
        print("Syncing to targets...")
        report = sync_secret(config, args.name, audit_log=audit_log)
        _print_report(report)
        return 0 if report.all_ok else 1

    return 0


def cmd_rotate(args: argparse.Namespace) -> int:
    """Rotate a secret — update Keychain and re-sync all targets."""
    config = VaultConfig.load(Path(args.config))
    audit_log = Path(args.audit_log) if args.audit_log else None

    entry = config.get_secret(args.name)
    if entry is None:
        print(f"Error: Secret '{args.name}' not found.")
        return 1

    # Read new secret value
    try:
        value = getpass.getpass(f"Enter new value for {args.name}: ")
        if not value:
            print("Error: Empty value.")
            return 1
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return 1

    # Update Keychain
    try:
        keychain.put(config.keychain_service, entry.account, value)
    except keychain.KeychainError as e:
        print(f"Error: Failed to update Keychain: {type(e).__name__}")
        return 1

    audit.log_event("ROTATE", args.name, "keychain", "OK", log_path=audit_log)

    # Record version history
    history = HistoryStore()
    history.record(args.name, value, config.keychain_service)

    # Re-sync all targets
    print("Re-syncing to all targets...")
    report = sync_secret(config, args.name, audit_log=audit_log)
    _print_report(report)
    return 0 if report.all_ok else 1


def cmd_audit(args: argparse.Namespace) -> int:
    """Show drift audit — check which targets are out of sync."""
    config = VaultConfig.load(Path(args.config))
    audit_log = Path(args.audit_log) if args.audit_log else None

    entries = check_status(config)
    issues: list[str] = []

    for entry in entries:
        if not entry.keychain_exists:
            issues.append(f"  MISSING in Keychain: {entry.env_name}")
        for label, status in entry.target_status.items():
            if status is False:
                issues.append(f"  MISSING {entry.env_name} -> {label}")

    if issues:
        print(f"ANDON VAULT AUDIT — {len(issues)} issue(s) found:\n")
        for issue in issues:
            print(issue)
        audit.log_event("AUDIT", "*", "*", f"DRIFT:{len(issues)}", log_path=audit_log)
        return 1
    else:
        print("ANDON VAULT AUDIT — All secrets in sync.")
        audit.log_event("AUDIT", "*", "*", "OK", log_path=audit_log)
        return 0


def cmd_remove(args: argparse.Namespace) -> int:
    """Remove a secret from Keychain, all targets, and vault config."""
    config = VaultConfig.load(Path(args.config))
    audit_log = Path(args.audit_log) if args.audit_log else None

    if not config.get_secret(args.name):
        print(f"Error: Secret '{args.name}' not found.")
        return 1

    report = remove_secret(config, args.name, audit_log=audit_log)
    config.save(Path(args.config))

    _print_report(report)
    print(f"Removed '{args.name}' from vault config.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List all secrets in the vault config (metadata only)."""
    config = VaultConfig.load(Path(args.config))
    if not config.secrets:
        print("No secrets configured.")
        return 0

    for name, entry in config.secrets.items():
        targets_str = ", ".join(t.label for t in entry.targets)
        desc = f" — {entry.description}" if entry.description else ""
        print(f"  {name}: {entry.env_name}{desc}")
        if targets_str:
            print(f"    targets: {targets_str}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Search Keychain for existing entries matching a pattern."""
    entries = keychain.search(args.pattern)
    if not entries:
        print(f"Keychain に '{args.pattern}' に一致するエントリはありません。")
        return 0

    print(f"\nKeychain 検索結果: '{args.pattern}' ({len(entries)} 件)\n")
    for i, entry in enumerate(entries, 1):
        label_str = f"  label={entry.label}" if entry.label else ""
        print(f"  {i}. service={entry.service}  account={entry.account}{label_str}")

    print("\n使い方:")
    print("  andon vault add <name> --env <ENV_VAR> --from-keychain <service>")
    print("  andon vault add <name> --env <ENV_VAR> --from-keychain <service> --from-account <account>")
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    """Show version history for a secret."""
    history = HistoryStore()
    versions = history.list_versions(args.name)
    if not versions:
        print(f"No history for '{args.name}'.")
        return 0

    print(f"\nVersion history: {args.name}\n")
    for v in reversed(versions):
        current = " (current)" if v.version == versions[-1].version else ""
        print(f"  v{v.version}  {v.timestamp}  fingerprint={v.fingerprint}{current}")
    print(f"\n  {len(versions)} version(s)")
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    """Rollback a secret to a previous version."""
    config = VaultConfig.load(Path(args.config))
    audit_log = Path(args.audit_log) if args.audit_log else None

    entry = config.get_secret(args.name)
    if entry is None:
        print(f"Error: Secret '{args.name}' not found.")
        return 1

    history = HistoryStore()
    value = history.get_version_value(args.name, args.version, config.keychain_service)
    if value is None:
        print(f"Error: Version {args.version} not found for '{args.name}'.")
        return 1

    # Update Keychain
    try:
        keychain.put(config.keychain_service, entry.account, value)
    except keychain.KeychainError as e:
        print(f"Error: Failed to update Keychain: {type(e).__name__}")
        return 1

    # Record as new version
    new_ver = history.record(args.name, value, config.keychain_service)
    audit.log_event(
        "ROLLBACK", args.name, "keychain",
        f"v{args.version}->v{new_ver.version}",
        log_path=audit_log,
    )
    print(f"Rolled back '{args.name}' to v{args.version} (now v{new_ver.version})")

    # Re-sync
    print("Re-syncing to all targets...")
    report = sync_secret(config, args.name, audit_log=audit_log)
    _print_report(report)
    return 0 if report.all_ok else 1


def _resolve_secrets(config: VaultConfig, env_name: str | None) -> dict[str, SecretEntry]:
    """Resolve secrets, applying environment inheritance if specified."""
    if env_name:
        return config.resolve_environment(env_name)
    return dict(config.secrets)


def cmd_ui(args: argparse.Namespace) -> int:
    """Launch the local web UI for vault."""
    from .config import VaultConfig
    from .web import serve

    config = VaultConfig.load(Path(args.config))
    port = getattr(args, "port", 8384)
    serve(config, port=port)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Run a command with vault secrets injected as environment variables."""
    import os

    config = VaultConfig.load(Path(args.config))
    env_name = getattr(args, "env_name", None) or config.default_environment
    secrets = _resolve_secrets(config, env_name)

    if not secrets:
        print("Error: No secrets configured.")
        return 1

    # Build env with secrets from Keychain
    env = os.environ.copy()
    for _name, entry in secrets.items():
        try:
            value = keychain.get(config.keychain_service, entry.account)
            env[entry.env_name] = value
        except keychain.KeychainError:
            print(f"Warning: Could not load '{entry.name}' from Keychain, skipping.")

    if not args.command:
        print("Error: No command specified. Usage: andon vault run -- <command>")
        return 1

    result = subprocess.run(args.command, env=env)
    return result.returncode


def cmd_export(args: argparse.Namespace) -> int:
    """Export secrets in various formats (values from Keychain)."""
    import json as json_mod

    import yaml

    config = VaultConfig.load(Path(args.config))
    env_name = getattr(args, "env_name", None) or config.default_environment
    resolved = _resolve_secrets(config, env_name)

    if not resolved:
        print("No secrets to export.")
        return 0

    secrets: dict[str, str] = {}
    for _name, entry in resolved.items():
        try:
            secrets[entry.env_name] = keychain.get(config.keychain_service, entry.account)
        except keychain.KeychainError:
            secrets[entry.env_name] = ""

    fmt = args.format
    if fmt == "env":
        for k, v in secrets.items():
            if "\n" in v or "#" in v or " " in v:
                v = '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
            print(f"{k}={v}")
    elif fmt == "json":
        print(json_mod.dumps(secrets, indent=2, ensure_ascii=False))
    elif fmt == "yaml":
        print(yaml.dump(secrets, default_flow_style=False, allow_unicode=True), end="")
    elif fmt == "docker":
        # Docker --env-file format (no quoting)
        for k, v in secrets.items():
            print(f"{k}={v}")
    else:
        print(f"Error: Unknown format '{fmt}'. Supported: env, json, yaml, docker")
        return 1

    return 0


def cmd_import_secrets(args: argparse.Namespace) -> int:
    """Import secrets from a file into Keychain + vault config."""
    import json as json_mod

    import yaml

    config = VaultConfig.load(Path(args.config))
    audit_log = Path(args.audit_log) if args.audit_log else None
    history = HistoryStore()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1

    content = file_path.read_text(encoding="utf-8")
    secrets: dict[str, str] = {}

    # Auto-detect format
    ext = file_path.suffix.lower()
    if ext in (".json",):
        secrets = json_mod.loads(content)
    elif ext in (".yaml", ".yml"):
        secrets = yaml.safe_load(content) or {}
    else:
        # Treat as .env format
        import re
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)", line)
            if m:
                key, val = m.group(1), m.group(2)
                # Strip surrounding quotes
                if (val.startswith('"') and val.endswith('"')) or \
                   (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                secrets[key] = val

    if not secrets:
        print("No secrets found in file.")
        return 1

    count = 0
    for env_name, value in secrets.items():
        # Derive a name from the env var
        name = env_name.lower().replace("_", "-")
        if config.get_secret(name):
            print(f"  Skip: {name} (already exists)")
            continue

        try:
            keychain.put(config.keychain_service, name, value)
        except keychain.KeychainError:
            print(f"  Error: Failed to store {name}")
            continue

        entry = SecretEntry(name=name, account=name, env_name=env_name)
        config.add_secret(entry)
        history.record(name, value, config.keychain_service)
        audit.log_event("IMPORT", name, "keychain", "OK", log_path=audit_log)
        count += 1

    config.save(Path(args.config))
    print(f"Imported {count} secret(s) from {file_path.name}.")
    return 0


def register_vault_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'vault' subcommand on the andon CLI parser."""
    vault_parser = subparsers.add_parser("vault", help="Local-first secret management")
    vault_parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to vault.yaml",
    )
    vault_parser.add_argument(
        "--audit-log",
        default=None,
        help="Path to audit log (default: ~/.config/andon/vault-audit.log)",
    )

    vault_sub = vault_parser.add_subparsers(dest="vault_command")

    # status
    vault_sub.add_parser("status", help="Show sync status of all secrets")

    # sync
    sync_p = vault_sub.add_parser("sync", help="Sync secrets to targets")
    sync_p.add_argument("name", nargs="?", default=None, help="Specific secret to sync")

    # add
    add_p = vault_sub.add_parser("add", help="Add a new secret")
    add_p.add_argument("name", help="Secret name (identifier)")
    add_p.add_argument("--account", default=None, help="Keychain account name")
    add_p.add_argument("--env", required=True, help="Environment variable name")
    add_p.add_argument("--description", default="", help="Description")
    add_p.add_argument(
        "--target", action="append",
        help="Target in platform:project format (repeatable)",
    )
    add_p.add_argument(
        "--from-keychain", dest="from_keychain", default=None,
        help="Import from existing Keychain entry (service name)",
    )
    add_p.add_argument(
        "--from-account", dest="from_account", default=None,
        help="Account name for --from-keychain (optional, uses first match if omitted)",
    )
    add_p.add_argument(
        "--from-clipboard", dest="from_clipboard", action="store_true", default=False,
        help="Read value from macOS clipboard (clipboard is cleared after)",
    )
    add_p.add_argument(
        "--from-cli", dest="from_cli", default=None,
        help="Run a command and use its stdout as the value (e.g. 'gh auth token')",
    )

    # rotate
    rotate_p = vault_sub.add_parser("rotate", help="Rotate a secret")
    rotate_p.add_argument("name", help="Secret name to rotate")

    # audit
    vault_sub.add_parser("audit", help="Drift audit — check all targets")

    # remove
    remove_p = vault_sub.add_parser("remove", help="Remove a secret everywhere")
    remove_p.add_argument("name", help="Secret name to remove")

    # list
    vault_sub.add_parser("list", help="List vault config (metadata only)")

    # search
    search_p = vault_sub.add_parser("search", help="Search Keychain for existing entries")
    search_p.add_argument("pattern", help="Search pattern (substring match on service/account)")

    # history
    history_p = vault_sub.add_parser("history", help="Show version history for a secret")
    history_p.add_argument("name", help="Secret name")

    # rollback
    rollback_p = vault_sub.add_parser("rollback", help="Rollback a secret to a previous version")
    rollback_p.add_argument("name", help="Secret name")
    rollback_p.add_argument("version", type=int, help="Version number to rollback to")

    # run
    run_p = vault_sub.add_parser("run", help="Run a command with secrets as env vars")
    run_p.add_argument("--env", dest="env_name", default=None, help="Environment (dev/stg/prd)")
    run_p.add_argument("command", nargs=argparse.REMAINDER, help="Command to run")

    # export
    export_p = vault_sub.add_parser("export", help="Export secrets (json/yaml/env/docker)")
    export_p.add_argument("--env", dest="env_name", default=None, help="Environment (dev/stg/prd)")
    export_p.add_argument(
        "--format", default="env", choices=["env", "json", "yaml", "docker"],
        help="Output format (default: env)",
    )

    # import
    import_p = vault_sub.add_parser("import", help="Import secrets from file")
    import_p.add_argument("file", help="Path to .env, .json, or .yaml file")

    # ui
    ui_p = vault_sub.add_parser("ui", help="Launch local web UI (localhost only)")
    ui_p.add_argument("--port", type=int, default=8384, help="Port number (default: 8384)")
