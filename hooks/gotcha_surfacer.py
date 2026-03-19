# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""gotcha_surfacer.py — Gotcha pattern matching, confidence scoring, and surfacing.

Matches an ANDON error text against the Gotcha registry to surface relevant
anti-pattern prevention advice in additionalContext when an incident opens.

Matching is keyword/substring based (not regex), because Gotcha `pattern`
fields contain natural language prose descriptions of anti-patterns.

Three confidence levels:
  EXACT    — full pattern text (normalised) appears as substring of error text
  PARTIAL  — 40%+ of significant pattern words appear in error text
  CATEGORY — error text contains a Gotcha tag (whole-word) or severity keyword

Public API:
  surface_gotchas(error_text, gotchas_dir, packs_dir) -> str
  match_gotchas(error_text, gotchas)                   -> list[MatchResult]
  format_surfaced_gotchas(matches)                     -> str
  MatchResult
  ConfidenceLevel

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from gotcha_registry import GotchaEntry, GotchaValidationError, load_gotchas

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stop-words excluded from partial-match word counting
# ---------------------------------------------------------------------------

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "but",
        "by",
        "do",
        "does",
        "for",
        "from",
        "had",
        "has",
        "have",
        "he",
        "her",
        "him",
        "his",
        "how",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "no",
        "not",
        "of",
        "on",
        "or",
        "our",
        "out",
        "per",
        "so",
        "some",
        "than",
        "that",
        "the",
        "their",
        "them",
        "then",
        "there",
        "they",
        "this",
        "those",
        "to",
        "too",
        "up",
        "us",
        "was",
        "we",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "will",
        "with",
        "you",
        "your",
    }
)

# Minimum word length for significance in partial matching
_MIN_WORD_LEN = 3


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class ConfidenceLevel(Enum):
    """Confidence level of a Gotcha match."""

    EXACT = "exact"
    PARTIAL = "partial"
    CATEGORY = "category"


@dataclass
class MatchResult:
    """A single Gotcha match result."""

    gotcha: GotchaEntry
    confidence: ConfidenceLevel
    score: float


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace."""
    return " ".join(text.lower().split())


def _significant_words(text: str) -> list[str]:
    """Extract significant words (3+ chars, not stopwords) from text."""
    words = re.findall(r"[a-z0-9_-]+", text.lower())
    return [w for w in words if len(w) >= _MIN_WORD_LEN and w not in _STOPWORDS]


def _whole_word_in_text(word: str, text_lower: str) -> bool:
    """Return True if `word` appears as a whole word in `text_lower`."""
    pattern = r"\b" + re.escape(word.lower()) + r"\b"
    return bool(re.search(pattern, text_lower))


# ---------------------------------------------------------------------------
# Core matching
# ---------------------------------------------------------------------------


def _try_exact(error_norm: str, pattern_norm: str) -> float | None:
    """Return 1.0 if pattern_norm is a substring of error_norm, else None."""
    if pattern_norm and pattern_norm in error_norm:
        return 1.0
    return None


def _try_partial(error_norm: str, pattern: str) -> float | None:
    """Return a partial match score if 40%+ of significant pattern words appear in error.

    Score = 0.5 + 0.3 * (matching_words / total_words), capped at 0.8.
    Returns None if below threshold.
    """
    sig_words = _significant_words(pattern)
    if not sig_words:
        return None
    matching = sum(1 for w in sig_words if w in error_norm)
    ratio = matching / len(sig_words)
    if ratio >= 0.40:
        score = min(0.5 + 0.3 * ratio, 0.8)
        return score
    return None


def _try_category(error_lower: str, entry: GotchaEntry) -> float | None:
    """Return category match score if any tag or severity keyword matches.

    Tag whole-word match → score 0.3
    Severity keyword match → score 0.2
    Returns the highest applicable score, or None if no match.
    """
    scores: list[float] = []

    # Tag whole-word matching
    for tag in entry.tags:
        if _whole_word_in_text(tag, error_lower):
            scores.append(0.3)
            break  # one tag is enough

    # Severity keyword matching (whole word)
    if entry.severity and _whole_word_in_text(entry.severity, error_lower):
        scores.append(0.2)

    return max(scores) if scores else None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def match_gotchas(error_text: str, gotchas: list[GotchaEntry]) -> list[MatchResult]:
    """Match error_text against all gotchas and return ranked results.

    Tries EXACT → PARTIAL → CATEGORY for each gotcha (in priority order).
    Returns results sorted descending by score.

    Args:
        error_text: The error text from an ANDON incident.
        gotchas:    The loaded Gotcha registry entries.

    Returns:
        List of MatchResult objects sorted descending by score.
    """
    error_norm = _normalize(error_text)
    error_lower = error_text.lower()

    results: list[MatchResult] = []

    for entry in gotchas:
        pattern_norm = _normalize(entry.pattern)

        # Priority: EXACT > PARTIAL > CATEGORY
        exact_score = _try_exact(error_norm, pattern_norm)
        if exact_score is not None:
            results.append(
                MatchResult(
                    gotcha=entry,
                    confidence=ConfidenceLevel.EXACT,
                    score=exact_score,
                )
            )
            continue

        partial_score = _try_partial(error_norm, entry.pattern)
        if partial_score is not None:
            results.append(
                MatchResult(
                    gotcha=entry,
                    confidence=ConfidenceLevel.PARTIAL,
                    score=partial_score,
                )
            )
            continue

        category_score = _try_category(error_lower, entry)
        if category_score is not None:
            results.append(
                MatchResult(
                    gotcha=entry,
                    confidence=ConfidenceLevel.CATEGORY,
                    score=category_score,
                )
            )

    results.sort(key=lambda r: r.score, reverse=True)
    return results


def format_surfaced_gotchas(matches: list[MatchResult]) -> str:
    """Format a list of MatchResult objects into a human-readable string.

    Format per match:
      [Gotcha {id}] {name} ({confidence_label}, score={score:.1f}): {prevention}

    Prefixed with a header line. Returns empty string if matches is empty.

    Args:
        matches: List of MatchResult objects (should be pre-sorted).

    Returns:
        Formatted string, or empty string if no matches.
    """
    if not matches:
        return ""

    lines = ["[GOTCHA_MATCH] Matching Gotchas found:"]
    for m in matches:
        lines.append(
            f"[Gotcha {m.gotcha.id}] {m.gotcha.name} "
            f"({m.confidence.value}, score={m.score:.1f}): {m.gotcha.prevention}"
        )
    return "\n".join(lines)


def surface_gotchas(
    error_text: str,
    gotchas_dir: Path,
    packs_dir: Path | None = None,
) -> str:
    """Load the Gotcha registry and surface matching entries for error_text.

    Loads all Gotcha YAML files from gotchas_dir (and optionally from
    packs/{name}/gotchas/ under packs_dir), matches error_text against them,
    and returns a formatted string of matching results.

    Surfacing never blocks ANDON: GotchaValidationError is caught and logged
    as a warning. Any other unexpected exception is also caught.

    Args:
        error_text:  The error text from an ANDON incident.
        gotchas_dir: Core directory of Gotcha YAML files.
        packs_dir:   Optional packs root for Knowledge Pack gotchas.

    Returns:
        Formatted match string (non-empty if matches found), or empty string.
    """
    try:
        gotchas = load_gotchas(gotchas_dir, packs_dir=packs_dir)
    except GotchaValidationError as exc:
        logger.warning("gotcha_surfacer: registry load failed: %s", exc)
        return ""
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "gotcha_surfacer: unexpected error loading registry: %s",
            type(exc).__name__,
        )
        return ""

    matches = match_gotchas(error_text, gotchas)
    return format_surfaced_gotchas(matches)
