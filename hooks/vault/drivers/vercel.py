# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Vercel driver — uses `vercel` CLI."""
from __future__ import annotations

import shutil
import subprocess

from .base import PlatformDriver

_CLI_NOT_FOUND = "vercel CLI が見つかりません。npm i -g vercel でインストールしてください。"


def _find_vercel() -> str:
    """Resolve the vercel binary path, raising FileNotFoundError with guidance."""
    path = shutil.which("vercel")
    if path is None:
        raise FileNotFoundError(_CLI_NOT_FOUND)
    return path


class VercelDriver(PlatformDriver):
    """Deploy secrets to Vercel via vercel CLI."""

    def _base_cmd(self, project: str) -> list[str]:
        return [_find_vercel(), "--yes", "--scope", project]

    def exists(self, env_name: str, project: str) -> bool:
        try:
            result = subprocess.run(
                [_find_vercel(), "env", "ls", "production", "--project", project],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            return False
        if result.returncode != 0:
            return False
        return env_name in result.stdout

    def put(self, env_name: str, value: str, project: str) -> bool:
        result = subprocess.run(
            [
                _find_vercel(), "env", "add", env_name, "production",
                "--force", "--project", project,
            ],
            input=value,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def delete(self, env_name: str, project: str) -> bool:
        result = subprocess.run(
            [
                _find_vercel(), "env", "rm", env_name, "production",
                "--yes", "--project", project,
            ],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
