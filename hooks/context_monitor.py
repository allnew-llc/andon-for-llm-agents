# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""context_monitor.py — Proxy-based context degradation detection.

Uses tool call count as a proxy for context window usage and injects
warnings when quality thresholds are exceeded.

Thresholds (configurable via env):
    PEAK       0-29   tool calls
    GOOD      30-59   tool calls
    DEGRADING 60-99   tool calls  (~50% context proxy)
    POOR     100+     tool calls  (~70% context proxy)

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from kaizen_core import ANDON_FILE, load_json, now_utc, write_json

# === Quality level thresholds ===
# Each tuple is (inclusive_lower, exclusive_upper)
QUALITY_LEVELS: dict[str, tuple[int, float]] = {
    "PEAK": (0, 30),
    "GOOD": (30, 60),
    "DEGRADING": (60, 100),
    "POOR": (100, float("inf")),
}

# Override thresholds via environment
_ENV_DEGRADING = os.environ.get("ANDON_CTX_DEGRADING_THRESHOLD")
_ENV_POOR = os.environ.get("ANDON_CTX_POOR_THRESHOLD")
if _ENV_DEGRADING is not None:
    _deg = int(_ENV_DEGRADING)
    QUALITY_LEVELS["GOOD"] = (30, _deg)
    QUALITY_LEVELS["DEGRADING"] = (_deg, QUALITY_LEVELS["POOR"][0])
if _ENV_POOR is not None:
    _poor = int(_ENV_POOR)
    QUALITY_LEVELS["DEGRADING"] = (QUALITY_LEVELS["DEGRADING"][0], _poor)
    QUALITY_LEVELS["POOR"] = (_poor, float("inf"))


# === Warning messages ===

_WARNING_DEGRADING = (
    "[ANDON/Context] Context window is estimated 50%+ used "
    "(~{n} tool calls). Consider delegating subtasks "
    "to fresh Agent sessions."
)

_WARNING_POOR = (
    "[ANDON/Context] Context window is estimated 70%+ used "
    "(~{n} tool calls). Critical decisions should be made "
    "in a fresh session."
)

_WARNING_ANDON_POOR = (
    "[ANDON/Context] Five Whys analysis running in degraded context. "
    "Consider closing this session and resuming root cause analysis "
    "in a fresh session."
)


def _state_file(state_dir: Path) -> Path:
    """Return path to the context monitor state file."""
    return state_dir / "andon-context-monitor.json"


def _level_for_count(count: int) -> str:
    """Determine quality level for a given tool call count."""
    for level, (lo, hi) in QUALITY_LEVELS.items():
        if lo <= count < hi:
            return level
    return "POOR"  # fallback


def _warning_for_transition(
    new_level: str,
    call_count: int,
    warnings_issued: list[str],
) -> str | None:
    """Return a warning message if transitioning to a new level.

    Returns None if the level has already been warned about (warn-once).
    """
    if new_level in ("PEAK", "GOOD"):
        return None
    if new_level in warnings_issued:
        return None  # warn-once: already warned for this level

    if new_level == "DEGRADING":
        return _WARNING_DEGRADING.format(n=call_count)
    if new_level == "POOR":
        return _WARNING_POOR.format(n=call_count)
    return None


def _andon_open_warning(
    new_level: str,
    warnings_issued: list[str],
) -> str | None:
    """Return additional warning if ANDON is open during POOR context.

    Only warns once (tracked via 'ANDON_POOR' pseudo-level).
    """
    if new_level != "POOR":
        return None
    if "ANDON_POOR" in warnings_issued:
        return None  # already warned

    andon = load_json(ANDON_FILE)
    if andon and andon.get("status") == "open":
        return _WARNING_ANDON_POOR
    return None


def increment_and_check(state_dir: Path) -> dict[str, Any]:
    """Increment tool call counter and return quality assessment.

    Returns:
        {
            "level": "DEGRADING",
            "call_count": 65,
            "warning": "..." or None,
            "andon_warning": "..." or None,
        }
    """
    sf = _state_file(state_dir)
    state = load_json(sf)

    # Initialize if empty
    if not state or "session_id" not in state:
        state = {
            "session_id": str(uuid.uuid4()),
            "tool_call_count": 0,
            "quality_level": "PEAK",
            "warnings_issued": [],
        }

    # Increment
    count = int(state.get("tool_call_count", 0)) + 1
    state["tool_call_count"] = count

    old_level = str(state.get("quality_level", "PEAK"))
    new_level = _level_for_count(count)
    state["quality_level"] = new_level
    state["updated_at"] = now_utc()

    warnings_issued: list[str] = state.get("warnings_issued", [])
    if not isinstance(warnings_issued, list):
        warnings_issued = []

    # Determine warnings
    warning: str | None = None
    andon_warning: str | None = None

    if new_level != old_level:
        warning = _warning_for_transition(new_level, count, warnings_issued)
        if warning and new_level not in warnings_issued:
            warnings_issued.append(new_level)

    andon_warning = _andon_open_warning(new_level, warnings_issued)
    if andon_warning and "ANDON_POOR" not in warnings_issued:
        warnings_issued.append("ANDON_POOR")

    state["warnings_issued"] = warnings_issued
    write_json(sf, state)

    return {
        "level": new_level,
        "call_count": count,
        "warning": warning,
        "andon_warning": andon_warning,
    }


def get_state(state_dir: Path) -> dict[str, Any]:
    """Read current context monitor state without modifying it."""
    return load_json(_state_file(state_dir))


def reset_session(state_dir: Path) -> None:
    """Reset counter for a new session."""
    sf = _state_file(state_dir)
    state = {
        "session_id": str(uuid.uuid4()),
        "tool_call_count": 0,
        "quality_level": "PEAK",
        "warnings_issued": [],
        "reset_at": now_utc(),
    }
    write_json(sf, state)
