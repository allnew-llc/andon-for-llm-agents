# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""gotcha_candidate.py — Gotcha candidate generation from Five Whys output

Transforms a Five Whys root cause + prevention text into a reviewable Gotcha
candidate YAML file written to gotchas/candidates/.

This module is the first half of the Five Whys -> Gotcha learning loop (v0.4.0
Phase 13). When a Five Whys analysis completes, call generate_candidate() to
auto-generate a candidate that can later be promoted to the live registry via
human review.

Generated YAML Schema
---------------------
Follows the same schema as the core Gotcha registry (gotcha_registry.py).
The generated file is self-validated with validate_gotcha() before being written.

Candidate ID format: GOTCHA-CAND-YYYYMMDD-HHMMSS

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime
from pathlib import Path

import yaml

# Import schema contract from the foundation module
from gotcha_registry import validate_gotcha

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stopword list for pattern extraction
# ---------------------------------------------------------------------------

_STOPWORDS: frozenset[str] = frozenset(
    {
        "the", "a", "an", "is", "was", "were", "are", "in", "on", "at", "to",
        "for", "of", "by", "with", "that", "this", "it", "not", "but", "and",
        "or",
    }
)

# Max characters for the derived name field (truncated at word boundary)
_NAME_MAX_CHARS: int = 50


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_candidate(
    root_cause: str,
    prevention: str,
    *,
    severity: str = "medium",
    source: str = "five-whys",
    gotchas_dir: Path | None = None,
    tags: list[str] | None = None,
) -> Path:
    """Generate a Gotcha candidate YAML file from Five Whys root cause and prevention text.

    The generated YAML is written to ``{gotchas_dir}/candidates/`` and is
    self-validated with :func:`gotcha_registry.validate_gotcha` before being
    persisted.  The function returns the absolute path to the created file.

    Args:
        root_cause:  Root cause text from the Five Whys analysis (non-empty).
        prevention:  Prevention text describing how to avoid the issue (non-empty).
        severity:    Severity level — one of ``critical``, ``high``, ``medium``,
                     ``low``.  Defaults to ``"medium"``.
        source:      Source label.  Defaults to ``"five-whys"``.
        gotchas_dir: Root directory for gotcha files.  The candidates subdirectory
                     (``gotchas_dir/candidates/``) is created automatically if it
                     does not exist.  Defaults to ``./gotchas`` relative to the
                     repository root (derived from this file's location).
        tags:        Optional list of tag strings to include in the YAML.

    Returns:
        Absolute :class:`~pathlib.Path` to the created YAML file.

    Raises:
        ValueError:  If ``root_cause`` or ``prevention`` is empty/whitespace, or
                     if the generated data fails :func:`~gotcha_registry.validate_gotcha`.
    """
    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------
    if not root_cause or not root_cause.strip():
        raise ValueError("root_cause must not be empty or whitespace")
    if not prevention or not prevention.strip():
        raise ValueError("prevention must not be empty or whitespace")

    # ------------------------------------------------------------------
    # Derived fields
    # ------------------------------------------------------------------
    now = datetime.now()  # noqa: DTZ005  (local time intentional for human-readable ID)
    candidate_id = f"GOTCHA-CAND-{now.strftime('%Y%m%d-%H%M%S')}"
    name = _derive_name(root_cause)
    pattern = _extract_pattern(root_cause)
    discovered = date.today().isoformat()

    # ------------------------------------------------------------------
    # Build data dict
    # ------------------------------------------------------------------
    data: dict[str, object] = {
        "id": candidate_id,
        "name": name,
        "pattern": pattern,
        "severity": severity,
        "prevention": prevention.strip(),
        "discovered": discovered,
        "source": source,
    }
    if tags:
        data["tags"] = list(tags)

    # ------------------------------------------------------------------
    # Self-validate before writing
    # ------------------------------------------------------------------
    errors = validate_gotcha(data)
    if errors:
        raise ValueError(
            f"Generated candidate data failed validation: {'; '.join(errors)}"
        )

    # ------------------------------------------------------------------
    # Resolve output directory and write file
    # ------------------------------------------------------------------
    if gotchas_dir is None:
        # Default: <repo-root>/gotchas  (this file lives in hooks/)
        gotchas_dir = Path(__file__).resolve().parent.parent / "gotchas"

    candidates_dir = gotchas_dir / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)

    output_path = (candidates_dir / f"{candidate_id}.yaml").resolve()
    output_path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    logger.info("Generated Gotcha candidate: %s -> %s", candidate_id, output_path)
    return output_path


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _extract_pattern(root_cause: str) -> str:
    """Extract a regex-style pattern from root cause keywords.

    Algorithm:
    1. Tokenise root_cause into words (strip punctuation).
    2. Lowercase and remove English stopwords.
    3. Join remaining keywords with ``.*?`` as a regex connector.

    Args:
        root_cause: Raw root cause text.

    Returns:
        A string of keywords joined by ``.*?``.  If only one keyword remains,
        returns that keyword without a connector.
    """
    # Tokenise: split on non-alphanumeric characters, keep non-empty tokens
    tokens = re.split(r"[^a-zA-Z0-9]+", root_cause)
    keywords = [
        tok.lower()
        for tok in tokens
        if tok and tok.lower() not in _STOPWORDS
    ]
    if not keywords:
        # Fallback: use the full root cause text as-is (trimmed)
        return root_cause.strip()
    return ".*?".join(keywords)


def _derive_name(root_cause: str) -> str:
    """Derive a short human-readable name from the root cause.

    Takes the first ``_NAME_MAX_CHARS`` characters of root_cause, truncates at
    the last word boundary within that limit, and title-cases the result.

    Args:
        root_cause: Raw root cause text.

    Returns:
        Title-cased string of at most ``_NAME_MAX_CHARS`` characters, truncated
        at a word boundary.
    """
    text = root_cause.strip()
    if len(text) <= _NAME_MAX_CHARS:
        return text.title()

    # Truncate at the last space within the limit
    truncated = text[:_NAME_MAX_CHARS]
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated.title()
