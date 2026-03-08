#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""pack_loader.py — Knowledge Pack Loader

Discovers, validates, and merges Knowledge Packs from the packs/ directory.
Enforces Pack 0 (Output Safety Guard) dependency for regulated domains.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

# Re-export data types from models.py for backward compatibility
from models import (  # noqa: F401
    PackBundle,
    PackManifest,
    ValidationResult,
)

logger = logging.getLogger(__name__)

# Regulated domains that require Pack 0
REGULATED_DOMAINS = frozenset({
    "legal", "medical", "financial", "pharmaceutical",
    "japan_legal", "us_legal", "eu_legal",
})

PACK_0_NAME = "output-safety-guard"


class PackLoader:
    """Load and merge Knowledge Packs from a directory."""

    def __init__(self, pack0_available: bool = True):
        self._pack0_available = pack0_available

    def load_all(self, packs_dir: Path) -> PackBundle:
        """Load all knowledge-pack.yaml files from packs_dir."""
        bundle = PackBundle()
        if not packs_dir.is_dir():
            return bundle

        for pack_dir in sorted(packs_dir.iterdir()):
            manifest_path = pack_dir / "knowledge-pack.yaml"
            if not manifest_path.exists():
                continue

            manifest = self._parse_manifest(manifest_path)
            if manifest is None:
                logger.warning("Failed to parse: %s", manifest_path)
                continue

            # Enforce Pack 0 dependency for regulated domains
            if not self._check_pack0_dependency(manifest):
                logger.warning(
                    "Pack '%s' requires Pack 0 (output-safety-guard) but it is not available. Skipping.",
                    manifest.name,
                )
                continue

            bundle.packs.append(manifest)
            self._merge_into_bundle(bundle, manifest)

        return bundle

    def validate_pack(self, pack_path: Path) -> ValidationResult:
        """Validate a pack directory against the spec."""
        result = ValidationResult()
        manifest_path = pack_path / "knowledge-pack.yaml"

        if not manifest_path.exists():
            result.valid = False
            result.errors.append("knowledge-pack.yaml not found")
            return result

        manifest = self._parse_manifest(manifest_path)
        if manifest is None:
            result.valid = False
            result.errors.append("knowledge-pack.yaml failed to parse")
            return result

        # Required fields
        if not manifest.name:
            result.valid = False
            result.errors.append("metadata.name is required")
        if not manifest.version:
            result.valid = False
            result.errors.append("metadata.version is required")

        # Skills directory
        skills_dir = pack_path / "skills"
        if not skills_dir.is_dir():
            result.warnings.append("skills/ directory not found")
        else:
            skill_files = list(skills_dir.glob("*.md"))
            if not skill_files:
                result.warnings.append("skills/ directory is empty")

        # Regulated domain check
        domain_ids = {d.get("id", "") for d in manifest.domains}
        needs_pack0 = bool(domain_ids & REGULATED_DOMAINS)
        has_pack0_req = any(
            r.get("name") == PACK_0_NAME for r in manifest.requires
        )
        if needs_pack0 and not has_pack0_req:
            result.valid = False
            result.errors.append(
                f"Pack contains regulated domain(s) {domain_ids & REGULATED_DOMAINS} "
                f"but does not declare 'requires: output-safety-guard'"
            )

        # License
        if not manifest.license:
            result.warnings.append("No license specified")

        return result

    # ----------------------------------------------------------
    # Internals
    # ----------------------------------------------------------

    def _parse_manifest(self, path: Path) -> PackManifest | None:
        try:
            with open(path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        except Exception:
            return None

        meta = data.get("metadata", {})
        if not isinstance(meta, dict):
            meta = {}

        return PackManifest(
            name=meta.get("name", ""),
            version=meta.get("version", "0.0.0"),
            description=meta.get("description", ""),
            author=meta.get("author", ""),
            license=meta.get("license", ""),
            tags=meta.get("tags", []),
            requires=data.get("requires", []),
            domains=data.get("domains", []),
            classification_rules=data.get("classification_rules", []),
            cause_to_domain=data.get("cause_to_domain", {}),
            skill_map=data.get("skill_map", {}),
            safety_extensions=data.get("safety_extensions", []),
            quality_criteria=data.get("quality_criteria", []),
            path=path.parent,
        )

    def _check_pack0_dependency(self, manifest: PackManifest) -> bool:
        """Check if Pack 0 is required and available."""
        requires_pack0 = any(
            r.get("name") == PACK_0_NAME for r in manifest.requires
        )
        return not (requires_pack0 and not self._pack0_available)

    def _merge_into_bundle(self, bundle: PackBundle, manifest: PackManifest) -> None:
        """Merge a single pack's data into the bundle."""
        # Merge domain keywords
        for domain in manifest.domains:
            domain_id = domain.get("id", "")
            keywords = domain.get("keywords", [])
            if domain_id and keywords:
                if domain_id not in bundle.extra_keywords:
                    bundle.extra_keywords[domain_id] = []
                bundle.extra_keywords[domain_id].extend(keywords)

        # Merge skill_map
        for domain_id, mapping in manifest.skill_map.items():
            if domain_id not in bundle.skill_map:
                bundle.skill_map[domain_id] = {"primary": [], "secondary": []}
            if isinstance(mapping, dict):
                bundle.skill_map[domain_id]["primary"].extend(mapping.get("primary", []))
                bundle.skill_map[domain_id]["secondary"].extend(mapping.get("secondary", []))

        # Merge classification rules
        bundle.classification_rules.extend(manifest.classification_rules)

        # Merge cause_to_domain
        bundle.cause_to_domain.update(manifest.cause_to_domain)

        # Collect safety extensions
        bundle.safety_extensions.extend(manifest.safety_extensions)
