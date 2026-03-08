#!/bin/bash
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
# tps-andon-pretool-guard.sh — PreToolUse hook for enforcing ANDON stop
#
# Behavior:
# - When ANDON is open, deny high-risk "forward progress" commands
# - Allow diagnostic/fix work and explicit ANDON close command
# - Also catches shell quote mismatches and brittle inline JSON patterns
#
# Copyright 2026 AllNew LLC — Apache License 2.0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
_WORKSPACE="${ANDON_WORKSPACE:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
STATE_FILE="$_WORKSPACE/.claude/state/andon-open.json"
INPUT_JSON="$(cat)"

INPUT_JSON="$INPUT_JSON" python3 - "$STATE_FILE" <<'PYEOF'
import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any


state_file = Path(sys.argv[1])

try:
    payload = json.loads(os.environ.get("INPUT_JSON", ""))
except Exception:
    print("{}")
    raise SystemExit(0)


def get_command(data: dict[str, Any]) -> str:
    tool_input = data.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command.strip()
    return ""


tool_name = payload.get("tool_name")
if isinstance(tool_name, str) and tool_name and tool_name != "Bash":
    print("{}")
    raise SystemExit(0)

command = get_command(payload)
if not command:
    print("{}")
    raise SystemExit(0)

lower = command.lower()


def deny(reason: str) -> None:
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0)


# Guard 1: catch obvious unmatched quote errors before execution.
try:
    shlex.split(command, posix=True)
except ValueError:
    deny(
        "Shell quote mismatch detected before execution. Use a heredoc script:\n"
        "f=$(mktemp); cat <<'SH' >\"$f\" ... SH; bash -n \"$f\" && bash \"$f\"; rm \"$f\""
    )

# Guard 2: block brittle long inline JSON + escaping patterns.
if (
    len(command) > 120
    and re.search(r"\becho\s+['\"]\{", command)
    and "|" in command
    and '\\"' in command
    and "jq -n" not in lower
    and "<<'" not in command
    and '<<"' not in command
):
    deny(
        "Brittle inline JSON command detected. Use heredoc or `jq -n` to build JSON safely before piping."
    )

if not state_file.exists():
    print("{}")
    raise SystemExit(0)

# Allow explicit control commands while ANDON is open.
if re.search(r"tps-andon-control\.sh\s+(status|close|rollback)\b", lower):
    print("{}")
    raise SystemExit(0)

# Allow kaizen report commits to capture learning and checkpoint the fix.
if re.search(r"\bgit\s+commit\b", lower):
    if "kaizen:" in lower:
        print("{}")
        raise SystemExit(0)
    deny(
        "ANDON open: git commit is blocked. Use a `kaizen:` commit after five-whys and recurrence prevention."
    )

# Block forward-progress commands while ANDON is open
block_patterns = [
    r"\bgit\s+push\b",
    r"\bgit\s+merge\b",
    r"\bgit\s+rebase\b",
    r"\bgit\s+cherry-pick\b",
    r"\bgit\s+tag\b",
    r"\bgh\s+pr\s+(create|merge)\b",
    r"\b(vercel|firebase|netlify)\s+deploy\b",
    r"\bnpm\s+publish\b",
    r"\bpnpm\s+publish\b",
    r"\byarn\s+publish\b",
    r"\btwine\s+upload\b",
    r"\bxcodebuild\b.*\b(-exportArchive|archive)\b",
]

for pattern in block_patterns:
    if re.search(pattern, lower):
        deny(
            "ANDON open: forward-progress command blocked until five-whys and recurrence prevention are complete."
        )

print("{}")
PYEOF
