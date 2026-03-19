# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""gotcha_registry.py — Gotcha Registry schema, loader, and pack discovery

Defines the GotchaEntry dataclass and loader functions for reading Gotcha
YAML files from the core gotchas/ directory and Knowledge Pack directories
(packs/{pack-name}/gotchas/).

This module is the foundation of the Gotchas Engine (v0.4.0). Phase 12
(auto-surfacing) and Phase 13 (Five Whys loop) both import from here.

Gotcha YAML Schema
------------------
Required fields:
  id:          str   Unique identifier, e.g. "GOTCHA-001"
  name:        str   Short human-readable label, e.g. "Human Error Stop"
  pattern:     str   Description of the anti-pattern to detect
  severity:    str   One of: critical, high, medium, low
  prevention:  str   How to prevent this gotcha
  discovered:  str   Date string when first observed, e.g. "2026-03-19"
  source:      str   Where it was discovered, e.g. "tps-kaizen"

Optional fields:
  tags:        list[str]   Categorisation labels
  examples:    list[str]   Concrete examples of the anti-pattern
  references:  list[str]   Related docs or rules, e.g. "70-kaizen-learning.md"

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

VALID_SEVERITIES = frozenset({"critical", "high", "medium", "low"})
REQUIRED_FIELDS = ("id", "name", "pattern", "severity", "prevention", "discovered", "source")


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class GotchaEntry:
    """A single Gotcha — a documented anti-pattern that agents must avoid."""

    # Required
    id: str
    name: str
    pattern: str
    severity: str
    prevention: str
    discovered: str
    source: str

    # Optional
    tags: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


class GotchaValidationError(Exception):
    """Raised when a Gotcha YAML file fails schema validation.

    The ``errors`` attribute holds a list of all validation error messages.
    """

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors: list[str] = errors or []


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_gotcha(data: dict) -> list[str]:
    """Validate a raw Gotcha dict and return a list of error strings.

    Returns an empty list if ``data`` is valid.  All errors are collected
    before returning — callers receive the full list, not just the first.

    Args:
        data: Parsed YAML dict representing a single Gotcha.

    Returns:
        List of human-readable error messages (empty list = valid).
    """
    errors: list[str] = []

    for field_name in REQUIRED_FIELDS:
        value = data.get(field_name)
        if not value or not str(value).strip():
            errors.append(f"Required field '{field_name}' is missing or empty")

    # Severity check (only if the field was present and non-empty)
    severity = str(data.get("severity", "")).strip()
    if severity and severity not in VALID_SEVERITIES:
        errors.append(
            f"Invalid severity '{severity}'; must be one of: "
            + ", ".join(sorted(VALID_SEVERITIES))
        )

    return errors


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_gotchas(
    gotchas_dir: Path,
    *,
    packs_dir: Path | None = None,
) -> list[GotchaEntry]:
    """Load and validate all Gotcha YAML files.

    Discovers ``*.yaml`` files from ``gotchas_dir`` and, optionally, from
    ``packs/{pack-name}/gotchas/`` under ``packs_dir``.

    Raises:
        GotchaValidationError: If any YAML file fails validation, or if
            duplicate IDs are detected across sources.  The file path is
            included in the error message so callers can pinpoint the problem.

    Args:
        gotchas_dir: Core directory of Gotcha YAML files.
        packs_dir:   Optional root directory that contains pack subdirectories.
                     Each pack may have a ``gotchas/`` subdirectory.

    Returns:
        List of validated :class:`GotchaEntry` objects, merged from all sources.
    """
    entries: list[GotchaEntry] = []
    seen_ids: dict[str, str] = {}  # id -> file path (for duplicate detection)

    # 1. Load from core gotchas/ directory
    if gotchas_dir.is_dir():
        for yaml_path in sorted(gotchas_dir.glob("*.yaml")):
            entry = _load_single(yaml_path)
            _check_duplicate(entry.id, str(yaml_path), seen_ids)
            seen_ids[entry.id] = str(yaml_path)
            entries.append(entry)
            logger.debug("Loaded gotcha %s from %s", entry.id, yaml_path)

    # 2. Discover and load from packs/{name}/gotchas/
    if packs_dir is not None and packs_dir.is_dir():
        for pack_dir in sorted(packs_dir.iterdir()):
            if not pack_dir.is_dir():
                continue
            pack_gotchas_dir = pack_dir / "gotchas"
            if not pack_gotchas_dir.is_dir():
                continue
            for yaml_path in sorted(pack_gotchas_dir.glob("*.yaml")):
                entry = _load_single(yaml_path)
                _check_duplicate(entry.id, str(yaml_path), seen_ids)
                seen_ids[entry.id] = str(yaml_path)
                entries.append(entry)
                logger.debug(
                    "Loaded gotcha %s from pack %s",
                    entry.id,
                    pack_dir.name,
                )

    return entries


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _load_single(yaml_path: Path) -> GotchaEntry:
    """Parse, validate, and return a single GotchaEntry from a YAML file.

    Raises:
        GotchaValidationError: with the file path included in the message.
    """
    try:
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise GotchaValidationError(
            f"Failed to parse {yaml_path}: {type(exc).__name__}"
        ) from exc

    if not isinstance(raw, dict):
        raise GotchaValidationError(
            f"Expected a YAML mapping in {yaml_path}, got {type(raw).__name__}"
        )

    errors = validate_gotcha(raw)
    if errors:
        raise GotchaValidationError(
            f"Validation failed for {yaml_path.name} ({yaml_path}): "
            + "; ".join(errors),
            errors=errors,
        )

    return GotchaEntry(
        id=str(raw["id"]).strip(),
        name=str(raw["name"]).strip(),
        pattern=str(raw["pattern"]).strip(),
        severity=str(raw["severity"]).strip(),
        prevention=str(raw["prevention"]).strip(),
        discovered=str(raw["discovered"]).strip(),
        source=str(raw["source"]).strip(),
        tags=list(raw.get("tags") or []),
        examples=list(raw.get("examples") or []),
        references=list(raw.get("references") or []),
    )


def _check_duplicate(
    gotcha_id: str,
    file_path: str,
    seen_ids: dict[str, str],
) -> None:
    """Raise GotchaValidationError if gotcha_id is already registered.

    Args:
        gotcha_id:  ID of the Gotcha being loaded.
        file_path:  Source file path (for error messages).
        seen_ids:   Mapping of already-seen IDs to their source file paths.
    """
    if gotcha_id in seen_ids:
        raise GotchaValidationError(
            f"Duplicate Gotcha ID '{gotcha_id}' found in '{file_path}'; "
            f"already registered from '{seen_ids[gotcha_id]}'"
        )
