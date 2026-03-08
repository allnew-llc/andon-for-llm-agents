# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""kaizen_payload.py — Payload extraction, command parsing, and git context.

Handles incoming hook payloads: extract commands, detect exit codes,
filter read-only/tolerant commands, and collect git repository context.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any

from kaizen_core import WORKSPACE

# === Payload extraction ===

def get_payload_from_env() -> dict[str, Any]:
    raw = os.environ.get("INPUT_JSON", "")
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
        return {}
    except Exception:
        return {}


def get_command(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command.strip()
    return ""


def get_workdir(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        workdir = tool_input.get("workdir")
        if isinstance(workdir, str) and workdir.strip():
            return workdir.strip()
    return str(WORKSPACE)


# === Exit code detection ===

def find_exit_code(obj: Any) -> int | None:
    if isinstance(obj, dict):
        for key in (
            "exit_code", "exitCode", "status_code",
            "statusCode", "code", "returncode",
        ):
            value = obj.get(key)
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.lstrip("-").isdigit():
                return int(value)
        for value in obj.values():
            child = find_exit_code(value)
            if child is not None:
                return child
    elif isinstance(obj, list):
        for item in obj:
            child = find_exit_code(item)
            if child is not None:
                return child
    return None


def collect_text_blobs(payload: dict[str, Any]) -> list[str]:
    blobs: list[str] = []
    for key in ("tool_response", "tool_output", "output", "stdout", "stderr"):
        value = payload.get(key)
        if isinstance(value, str):
            blobs.append(value)
        elif isinstance(value, dict):
            for nested in ("stdout", "stderr", "output", "text", "message"):
                nested_value = value.get(nested)
                if isinstance(nested_value, str):
                    blobs.append(nested_value)
    return blobs


def derive_exit_code(payload: dict[str, Any]) -> int | None:
    code = find_exit_code(payload)
    if code is not None:
        return code
    merged = "\n".join(collect_text_blobs(payload))
    match = re.search(
        r"(?:exit(?:ed)?\s+with\s+code|exit[_ ]code)\s*[:=]?\s*(-?\d+)",
        merged,
        re.IGNORECASE,
    )
    if match:
        try:
            return int(match.group(1))
        except Exception:
            return None
    return None


# === Command filtering ===

def is_tolerant_command(command: str) -> bool:
    lower = command.lower()
    return "|| true" in lower or "||true" in lower


def is_readonly_failure(command: str) -> bool:
    readonly = {
        "ls", "cat", "sed", "head", "tail", "find", "rg", "grep",
        "pwd", "echo", "date", "which", "whoami", "wc", "sort",
        "cut", "awk", "tr", "jq", "stat", "uname",
    }
    try:
        argv = shlex.split(command, posix=True)
    except Exception:
        argv = command.split()
    first = os.path.basename(argv[0]) if argv else ""
    return first in readonly


# === Git context ===

def run_git(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=6,
            check=False,
        )
    except Exception:
        return ""
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    if out:
        return out
    return err


def collect_git_context(cwd: Path) -> dict[str, str]:
    repo = WORKSPACE if (WORKSPACE / ".git").exists() else cwd
    return {
        "repo": str(repo),
        "branch": run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo),
        "head": run_git(["rev-parse", "--short", "HEAD"], repo),
        "status": run_git(["status", "--short"], repo),
    }
