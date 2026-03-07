"""models.py — Shared data types for ANDON safety and pack systems.

Enums and dataclasses used by output_safety_guard.py and pack_loader.py.
Extracted for single-responsibility compliance.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# === Output Safety Guard types ===


class GuardLevel(Enum):
    """Severity of the guard action."""
    BLOCK = "block"   # Refuse output entirely
    GUARD = "guard"   # Allow info but inject disclaimer + referral
    WARN  = "warn"    # Append advisory note


class GuardCategory(Enum):
    """Categories of output safety concern.

    Scoped to unauthorized professional practice — categories relevant
    to LLM coding agents that may generate professional-domain text.
    Content moderation (violence, self-harm, etc.) is out of scope;
    the underlying LLM handles those.
    """
    UPL        = "unauthorized_practice_of_law"
    UNQUALIFIED    = "unauthorized_professional_practice"


@dataclass
class GuardResult:
    """Result of a safety check against one or more categories."""
    triggered: bool = False
    level: GuardLevel | None = None
    category: GuardCategory | None = None
    reason: str = ""
    matched_pattern: str = ""
    disclaimer: str | None = None
    professional_referral: str | None = None
    helpline: str | None = None


@dataclass
class PatternEntry:
    """A single detection pattern inside a category."""
    regex: re.Pattern[str]
    weight: float = 1.0
    source: str = "builtin"


@dataclass
class CategoryDef:
    """Full definition for one guard category."""
    category: GuardCategory
    level: GuardLevel
    patterns: list[PatternEntry] = field(default_factory=list)
    disclaimer: str = ""
    professional_referral: str = ""
    helpline: str = ""


# === Knowledge Pack types ===


@dataclass
class PackManifest:
    """Parsed knowledge-pack.yaml manifest."""
    name: str = ""
    version: str = "0.0.0"
    description: str = ""
    author: str = ""
    license: str = ""
    tags: list[str] = field(default_factory=list)
    requires: list[dict[str, str]] = field(default_factory=list)
    domains: list[dict[str, Any]] = field(default_factory=list)
    classification_rules: list[dict[str, Any]] = field(default_factory=list)
    cause_to_domain: dict[str, str] = field(default_factory=dict)
    skill_map: dict[str, Any] = field(default_factory=dict)
    safety_extensions: list[dict[str, Any]] = field(default_factory=list)
    quality_criteria: list[str] = field(default_factory=list)
    path: Path = field(default_factory=lambda: Path("."))


@dataclass
class PackBundle:
    """Merged result of all loaded packs."""
    packs: list[PackManifest] = field(default_factory=list)
    extra_keywords: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    skill_map: dict[str, dict[str, list[dict[str, str]]]] = field(default_factory=dict)
    classification_rules: list[dict[str, Any]] = field(default_factory=list)
    cause_to_domain: dict[str, str] = field(default_factory=dict)
    safety_extensions: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def empty(cls) -> PackBundle:
        return cls()


@dataclass
class ValidationResult:
    """Result of pack validation."""
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
