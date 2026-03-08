# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""kaizen_core.py — Configuration, JSON I/O, text sanitization, and hook output.

Shared infrastructure for the ANDON/Kaizen runtime modules.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import datetime
import json
import os
import re
from pathlib import Path
from typing import Any

# === Configuration ===
# Override WORKSPACE by setting ANDON_WORKSPACE environment variable
WORKSPACE = (
    Path(os.environ.get("ANDON_WORKSPACE", "")).resolve()
    if os.environ.get("ANDON_WORKSPACE")
    else Path(__file__).resolve().parents[1]
)
STATE_DIR = (
    Path(os.environ.get("ANDON_STATE_DIR", "")).resolve()
    if os.environ.get("ANDON_STATE_DIR")
    else WORKSPACE / ".claude" / "state"
)
KAIZEN_DIR = STATE_DIR / "kaizen"
INCIDENTS_DIR = KAIZEN_DIR / "incidents"
HISTORY_DIR = STATE_DIR / "history"
ANDON_FILE = STATE_DIR / "andon-open.json"
STANDARD_REGISTRY = KAIZEN_DIR / "standardization-registry.json"

# Confidence thresholds
CONFIDENCE_AUTOMATION_THRESHOLD = float(
    os.environ.get("ANDON_CONFIDENCE_AUTO", "0.70")
)
CONFIDENCE_MANUAL_REVIEW_THRESHOLD = float(
    os.environ.get("ANDON_CONFIDENCE_MANUAL", "0.70")
)


# === Time ===

def now_utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# === Directory setup ===

def ensure_dirs() -> None:
    INCIDENTS_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    KAIZEN_DIR.mkdir(parents=True, exist_ok=True)


# === JSON I/O ===

def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    # Use explicit file mode (owner rw, group r, no other) to avoid
    # umask-dependent world-readable permissions on incident data.
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o640)
    try:
        os.write(fd, content.encode("utf-8"))
    finally:
        os.close(fd)


def append_json_event(path: Path, data: dict[str, Any]) -> None:
    existing: dict[str, Any] = load_json(path)
    events: list[dict[str, Any]] = []
    if isinstance(existing.get("events"), list):
        events = existing["events"]
    events.append(data)
    write_json(path, {"events": events})


# === Text sanitization ===

def safe_snippet(text: str, limit: int = 2400) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


# Secret redaction patterns — applied before any output is persisted
_SECRET_PATTERNS: list[re.Pattern[str]] = [
    # Bearer / Authorization headers
    re.compile(r"(Bearer\s+)[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(
        r"(Authorization:\s*(?:Bearer|Basic|Token)\s+)[^\s'\"]+", re.IGNORECASE
    ),
    # Common API key prefixes (OpenAI, Anthropic, Google, Stripe, AWS, GitHub)
    re.compile(r"(sk-(?:proj-|live-|test-)?)[A-Za-z0-9]{8,}"),
    re.compile(r"(sk-ant-)[A-Za-z0-9\-]{8,}"),
    re.compile(r"(AIza)[A-Za-z0-9\-_]{30,}"),
    re.compile(r"(sk_(?:live|test)_)[A-Za-z0-9]{8,}"),
    re.compile(r"(AKIA)[A-Z0-9]{12,}"),
    re.compile(r"(ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9]{30,}"),
    re.compile(r"(xai-)[A-Za-z0-9]{20,}"),
    # Generic export KEY=value in shell output
    re.compile(
        r"((?:API_KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|AUTH)[\w]*\s*=\s*)[^\s'\"]+",
        re.IGNORECASE,
    ),
    # Key-value in JSON-like output
    re.compile(
        r'("(?:api_?key|secret|token|password|credential|auth)[^"]*"\s*:\s*")[^"]{8,}(")',
        re.IGNORECASE,
    ),
]


def redact_secrets(text: str) -> str:
    """Mask potential secrets/tokens in text before persisting to incident files."""
    result = text
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub(
            lambda m: m.group(1)
            + "<REDACTED>"
            + (m.group(2) if m.lastindex and m.lastindex >= 2 else ""),
            result,
        )
    return result


# === Hook output ===

def print_hook_context(message: str, block: bool) -> None:
    payload: dict[str, Any] = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        }
    }
    if block:
        payload["decision"] = "block"
        payload["reason"] = message
    print(json.dumps(payload, ensure_ascii=False))


def print_empty() -> None:
    print("{}")
