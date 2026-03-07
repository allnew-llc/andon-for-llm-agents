#!/usr/bin/env python3
"""andon_cli.py — ANDON Knowledge Pack CLI

Commands:
  andon pack list              List installed packs
  andon pack validate <path>   Validate a pack directory
  andon pack install <path>    Install a pack to packs/
  andon pack info <name>       Show pack details

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# Resolve imports relative to this file's directory
_HOOKS_DIR = Path(__file__).parent
sys.path.insert(0, str(_HOOKS_DIR))

from pack_loader import PackLoader, PackBundle, REGULATED_DOMAINS  # noqa: E402


PACKS_DIR = _HOOKS_DIR.parent / "packs"


def cmd_list(args: argparse.Namespace) -> int:
    """List installed packs."""
    packs_dir = Path(args.packs_dir)
    if not packs_dir.is_dir():
        print(f"No packs directory found: {packs_dir}")
        return 0

    loader = PackLoader(pack0_available=True)
    bundle = loader.load_all(packs_dir)

    if not bundle.packs:
        print("No packs installed.")
        return 0

    print(f"{'Name':<35} {'Version':<10} {'Domains':<20} {'Skills'}")
    print("-" * 80)
    for pack in bundle.packs:
        domain_ids = [d.get("id", "?") for d in pack.domains]
        domains_str = ", ".join(domain_ids[:3])
        if len(domain_ids) > 3:
            domains_str += f" (+{len(domain_ids) - 3})"

        skills_dir = pack.path / "skills"
        skill_count = len(list(skills_dir.glob("*.md"))) if skills_dir.is_dir() else 0

        print(f"{pack.name:<35} {pack.version:<10} {domains_str:<20} {skill_count} skills")

    print(f"\n{len(bundle.packs)} pack(s) loaded.")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a pack directory."""
    pack_path = Path(args.path).resolve()
    if not pack_path.is_dir():
        print(f"Error: {pack_path} is not a directory.")
        return 1

    loader = PackLoader(pack0_available=True)
    result = loader.validate_pack(pack_path)

    manifest_path = pack_path / "knowledge-pack.yaml"
    if manifest_path.exists():
        manifest = loader._parse_manifest(manifest_path)
        if manifest:
            print(f"Pack: {manifest.name} v{manifest.version}")
            print(f"Description: {manifest.description}")
            print()

    # Show results
    if result.errors:
        for err in result.errors:
            print(f"  ERROR: {err}")
    if result.warnings:
        for warn in result.warnings:
            print(f"  WARNING: {warn}")

    if result.valid and not result.warnings:
        print("  Result: VALID")
    elif result.valid:
        print(f"\n  Result: VALID ({len(result.warnings)} warning(s))")
    else:
        print(f"\n  Result: INVALID ({len(result.errors)} error(s))")

    return 0 if result.valid else 1


def cmd_install(args: argparse.Namespace) -> int:
    """Install a pack to packs/ directory."""
    source = Path(args.path).resolve()
    if not source.is_dir():
        print(f"Error: {source} is not a directory.")
        return 1

    # Validate first
    loader = PackLoader(pack0_available=True)
    result = loader.validate_pack(source)
    if not result.valid:
        print("Pack validation failed:")
        for err in result.errors:
            print(f"  ERROR: {err}")
        print("\nFix errors before installing.")
        return 1

    # Get pack name
    manifest = loader._parse_manifest(source / "knowledge-pack.yaml")
    if not manifest:
        print("Error: Failed to parse manifest.")
        return 1

    packs_dir = Path(args.packs_dir).resolve()
    packs_dir.mkdir(parents=True, exist_ok=True)

    # Guard: pack name must be a simple identifier (no path traversal)
    safe_name = manifest.name.replace("/", "").replace("\\", "").replace("..", "")
    if safe_name != manifest.name or not manifest.name:
        print(f"Error: Pack name '{manifest.name}' contains invalid characters.")
        return 1

    dest = packs_dir / safe_name
    # Verify dest is actually inside packs_dir
    if not dest.resolve().is_relative_to(packs_dir):
        print(f"Error: Pack destination escapes packs directory.")
        return 1

    if dest.exists():
        if not args.force:
            print(f"Pack '{manifest.name}' already installed at {dest}.")
            print("Use --force to overwrite.")
            return 1
        shutil.rmtree(dest)

    shutil.copytree(source, dest)
    print(f"Installed '{manifest.name}' v{manifest.version} to {dest}")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Show detailed pack information."""
    packs_dir = Path(args.packs_dir).resolve()

    # Guard: reject names with path traversal characters
    name = args.name
    if "/" in name or "\\" in name or ".." in name or not name:
        print(f"Error: Pack name '{name}' contains invalid characters.")
        return 1

    pack_path = packs_dir / name

    if not pack_path.is_dir():
        # Try with andon-pack- prefix
        pack_path = packs_dir / f"andon-pack-{name}"
        if not pack_path.is_dir():
            print(f"Pack '{args.name}' not found in {packs_dir}")
            return 1

    loader = PackLoader(pack0_available=True)
    manifest = loader._parse_manifest(pack_path / "knowledge-pack.yaml")
    if not manifest:
        print(f"Error: Failed to parse manifest at {pack_path}")
        return 1

    print(f"Name:        {manifest.name}")
    print(f"Version:     {manifest.version}")
    print(f"Description: {manifest.description}")
    print(f"Author:      {manifest.author or '(not specified)'}")
    print(f"License:     {manifest.license or '(not specified)'}")
    print(f"Tags:        {', '.join(manifest.tags) if manifest.tags else '(none)'}")

    # Domains
    domain_ids = [d.get("id", "") for d in manifest.domains]
    regulated = set(domain_ids) & REGULATED_DOMAINS
    print(f"\nDomains:     {', '.join(domain_ids)}")
    if regulated:
        print(f"Regulated:   {', '.join(regulated)} (Pack 0 required)")

    # Dependencies
    if manifest.requires:
        print("\nDependencies:")
        for req in manifest.requires:
            print(f"  - {req.get('name', '?')} {req.get('version', '')}")

    # Skills
    skills_dir = pack_path / "skills"
    if skills_dir.is_dir():
        skills = sorted(skills_dir.glob("*.md"))
        print(f"\nSkills ({len(skills)}):")
        for skill in skills:
            print(f"  - {skill.stem}")

    # Safety extensions
    if manifest.safety_extensions:
        print(f"\nSafety Extensions: {len(manifest.safety_extensions)} category extension(s)")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="andon",
        description="ANDON Knowledge Pack Manager",
    )
    parser.add_argument(
        "--packs-dir",
        default=str(PACKS_DIR),
        help=f"Packs directory (default: {PACKS_DIR})",
    )

    sub = parser.add_subparsers(dest="command")

    # pack subcommand
    pack_parser = sub.add_parser("pack", help="Manage Knowledge Packs")
    pack_sub = pack_parser.add_subparsers(dest="pack_command")

    pack_sub.add_parser("list", help="List installed packs")

    validate_p = pack_sub.add_parser("validate", help="Validate a pack")
    validate_p.add_argument("path", help="Path to pack directory")

    install_p = pack_sub.add_parser("install", help="Install a pack")
    install_p.add_argument("path", help="Path to pack directory")
    install_p.add_argument("--force", action="store_true", help="Overwrite existing")

    info_p = pack_sub.add_parser("info", help="Show pack details")
    info_p.add_argument("name", help="Pack name")

    args = parser.parse_args()

    if args.command == "pack":
        if args.pack_command == "list":
            return cmd_list(args)
        elif args.pack_command == "validate":
            return cmd_validate(args)
        elif args.pack_command == "install":
            return cmd_install(args)
        elif args.pack_command == "info":
            return cmd_info(args)
        else:
            pack_parser.print_help()
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
