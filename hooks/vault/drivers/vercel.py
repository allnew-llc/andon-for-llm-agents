# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Vercel driver — uses `vercel` CLI."""
from __future__ import annotations

import subprocess

from .base import PlatformDriver


class VercelDriver(PlatformDriver):
    """Deploy secrets to Vercel via vercel CLI."""

    def exists(self, env_name: str, project: str) -> bool:
        result = subprocess.run(
            ["vercel", "env", "ls", "production"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False
        return env_name in result.stdout

    def put(self, env_name: str, value: str, project: str) -> bool:
        result = subprocess.run(
            ["vercel", "env", "add", env_name, "production", "--force"],
            input=value,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def delete(self, env_name: str, project: str) -> bool:
        result = subprocess.run(
            ["vercel", "env", "rm", env_name, "production", "--yes"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
