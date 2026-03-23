# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Cloudflare Pages driver — uses `wrangler` CLI."""
from __future__ import annotations

import subprocess

from .base import PlatformDriver


class CloudflarePagesDriver(PlatformDriver):
    """Deploy secrets to Cloudflare Pages via wrangler CLI."""

    def exists(self, env_name: str, project: str) -> bool:
        result = subprocess.run(
            ["wrangler", "pages", "secret", "list", "--project-name", project],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False
        return env_name in result.stdout

    def put(self, env_name: str, value: str, project: str) -> bool:
        result = subprocess.run(
            [
                "wrangler", "pages", "secret", "put", env_name,
                "--project-name", project,
            ],
            input=value,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def delete(self, env_name: str, project: str) -> bool:
        result = subprocess.run(
            [
                "wrangler", "pages", "secret", "delete", env_name,
                "--project-name", project, "--force",
            ],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
