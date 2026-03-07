#!/usr/bin/env python3
"""output_safety_guard.py — Pack 0: Output Safety Guard

Detects unauthorized-professional-practice content in LLM coding agent
outputs and injects appropriate disclaimers.

Scope: UPL (unauthorized practice of law) and general unauthorized
professional practice (tax, financial, architectural advice).  Content
moderation categories (violence, self-harm, etc.) are intentionally
excluded — those are handled by the underlying LLM's own safety layer.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml  # PyYAML — listed in requirements

# ============================================================
# Enums & Data
# ============================================================

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
    level: Optional[GuardLevel] = None
    category: Optional[GuardCategory] = None
    reason: str = ""
    matched_pattern: str = ""
    disclaimer: Optional[str] = None
    professional_referral: Optional[str] = None
    helpline: Optional[str] = None


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
    patterns: List[PatternEntry] = field(default_factory=list)
    disclaimer: str = ""
    professional_referral: str = ""
    helpline: str = ""


# ============================================================
# YAML loader
# ============================================================

_CATEGORY_MAP: Dict[str, GuardCategory] = {e.value: e for e in GuardCategory}
_LEVEL_MAP: Dict[str, GuardLevel] = {e.value: e for e in GuardLevel}

PATTERNS_DIR = Path(__file__).parent / "safety_patterns"


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _compile_pattern(raw: str) -> re.Pattern[str]:
    return re.compile(raw, re.IGNORECASE | re.MULTILINE)


def load_category_from_yaml(path: Path) -> Optional[CategoryDef]:
    """Load a single category YAML file into a CategoryDef."""
    data = _load_yaml(path)
    if not data:
        return None

    cat_str = data.get("category", "")
    cat = _CATEGORY_MAP.get(cat_str)
    if cat is None:
        return None

    level_str = data.get("level", "block")
    level = _LEVEL_MAP.get(level_str, GuardLevel.BLOCK)

    patterns: List[PatternEntry] = []
    for entry in data.get("patterns", []):
        raw = entry if isinstance(entry, str) else entry.get("pattern", "")
        weight = float(entry.get("weight", 1.0)) if isinstance(entry, dict) else 1.0
        if raw:
            patterns.append(PatternEntry(
                regex=_compile_pattern(raw),
                weight=weight,
                source="builtin",
            ))

    return CategoryDef(
        category=cat,
        level=level,
        patterns=patterns,
        disclaimer=data.get("disclaimer", ""),
        professional_referral=data.get("professional_referral", ""),
        helpline=data.get("helpline", ""),
    )


def load_all_categories(patterns_dir: Optional[Path] = None) -> Dict[GuardCategory, CategoryDef]:
    """Load all category YAML files from the patterns directory."""
    d = patterns_dir or PATTERNS_DIR
    cats: Dict[GuardCategory, CategoryDef] = {}
    if not d.is_dir():
        return cats
    for yml in sorted(d.glob("*.yaml")):
        cat_def = load_category_from_yaml(yml)
        if cat_def is not None:
            cats[cat_def.category] = cat_def
    return cats


# ============================================================
# Guard Engine
# ============================================================

# Severity ordering: BLOCK > GUARD > WARN
_LEVEL_SEVERITY = {GuardLevel.BLOCK: 3, GuardLevel.GUARD: 2, GuardLevel.WARN: 1}


class OutputSafetyGuard:
    """Pack 0 main class — check text and apply guards."""

    def __init__(
        self,
        categories: Optional[Dict[GuardCategory, CategoryDef]] = None,
        patterns_dir: Optional[Path] = None,
    ):
        if categories is not None:
            self._cats = dict(categories)
        else:
            self._cats = load_all_categories(patterns_dir)

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def check(self, text: str) -> GuardResult:
        """Scan *text* against all loaded categories.

        Returns the **most severe** match found (BLOCK > GUARD > WARN).
        If nothing triggers, returns a safe GuardResult(triggered=False).
        """
        worst: Optional[GuardResult] = None

        for cat_def in self._cats.values():
            result = self._check_category(text, cat_def)
            if result.triggered:
                if worst is None or _LEVEL_SEVERITY.get(result.level, 0) > _LEVEL_SEVERITY.get(worst.level, 0):
                    worst = result

        return worst if worst is not None else GuardResult()

    def check_all(self, text: str) -> List[GuardResult]:
        """Return every triggered result (for audit logging)."""
        results: List[GuardResult] = []
        for cat_def in self._cats.values():
            r = self._check_category(text, cat_def)
            if r.triggered:
                results.append(r)
        return results

    def apply_guard(self, text: str, result: GuardResult) -> str:
        """Transform *text* according to *result*.

        - BLOCK: replace with refusal message
        - GUARD: prepend + append disclaimer
        - WARN:  append advisory
        """
        if not result.triggered or result.level is None:
            return text

        if result.level == GuardLevel.BLOCK:
            parts = [result.reason or "This content cannot be generated."]
            if result.helpline:
                parts.append("")
                parts.append(result.helpline)
            return "\n".join(parts)

        if result.level == GuardLevel.GUARD:
            parts: List[str] = []
            if result.disclaimer:
                parts.append(result.disclaimer)
                parts.append("")
            parts.append(text)
            parts.append("")
            if result.disclaimer:
                parts.append(result.disclaimer)
            if result.professional_referral:
                parts.append(f"\nPlease consult: {result.professional_referral}")
            return "\n".join(parts)

        # WARN
        advisory = (
            result.disclaimer
            or "Note: This is general information. "
               "Please consult a qualified professional for advice specific to your situation."
        )
        return f"{text}\n\n---\n{advisory}"

    def merge_pack_extensions(self, extensions: List[Dict[str, Any]]) -> None:
        """Merge safety_extensions from a Knowledge Pack manifest."""
        for ext in extensions:
            cat_str = ext.get("category", "")
            cat = _CATEGORY_MAP.get(cat_str)
            if cat is None:
                continue

            cat_def = self._cats.get(cat)
            if cat_def is None:
                continue

            for p in ext.get("extra_patterns", []):
                raw = p.get("pattern", "")
                weight = float(p.get("weight", 1.0))
                if raw:
                    cat_def.patterns.append(PatternEntry(
                        regex=_compile_pattern(raw),
                        weight=weight,
                        source="pack",
                    ))

            override = ext.get("disclaimer_override")
            if isinstance(override, dict):
                txt = override.get("text", "")
                attr = override.get("source_attribution", "")
                if txt:
                    cat_def.disclaimer = f"{txt.strip()}\n{attr}".strip()

    # ----------------------------------------------------------
    # Internals
    # ----------------------------------------------------------

    def _check_category(self, text: str, cat_def: CategoryDef) -> GuardResult:
        for pe in cat_def.patterns:
            m = pe.regex.search(text)
            if m:
                return GuardResult(
                    triggered=True,
                    level=cat_def.level,
                    category=cat_def.category,
                    reason=self._build_reason(cat_def),
                    matched_pattern=pe.regex.pattern,
                    disclaimer=cat_def.disclaimer or None,
                    professional_referral=cat_def.professional_referral or None,
                    helpline=cat_def.helpline or None,
                )
        return GuardResult()

    @staticmethod
    def _build_reason(cat_def: CategoryDef) -> str:
        if cat_def.level == GuardLevel.BLOCK:
            return f"Output blocked: {cat_def.category.value}"
        if cat_def.level == GuardLevel.GUARD:
            return f"Output guarded: {cat_def.category.value} — disclaimer required"
        return f"Advisory: {cat_def.category.value}"
