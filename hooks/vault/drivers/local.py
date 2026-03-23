# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Local file driver — manages .dev.vars / .env.local files."""
from __future__ import annotations

import os
import re
from pathlib import Path

from .base import PlatformDriver

_LINE_PATTERN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


class LocalDriver(PlatformDriver):
    """Deploy secrets to local dotenv-style files."""

    def exists(self, env_name: str, project: str) -> bool:
        """Check if KEY=... line exists in the file. `project` is the file path."""
        path = Path(project)
        if not path.exists():
            return False
        for line in path.read_text(encoding="utf-8").splitlines():
            m = _LINE_PATTERN.match(line)
            if m and m.group(1) == env_name:
                return True
        return False

    def put(self, env_name: str, value: str, project: str) -> bool:
        """Add or update KEY=value in the file. `project` is the file path."""
        path = Path(project)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []
        found = False
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                m = _LINE_PATTERN.match(line)
                if m and m.group(1) == env_name:
                    lines.append(f"{env_name}={value}")
                    found = True
                else:
                    lines.append(line)

        if not found:
            lines.append(f"{env_name}={value}")

        content = "\n".join(lines) + "\n"
        # Write with restrictive permissions
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, content.encode("utf-8"))
        finally:
            os.close(fd)
        return True

    def delete(self, env_name: str, project: str) -> bool:
        """Remove KEY=... line from the file. `project` is the file path."""
        path = Path(project)
        if not path.exists():
            return False

        lines = path.read_text(encoding="utf-8").splitlines()
        new_lines = [
            line for line in lines
            if not (_LINE_PATTERN.match(line) and _LINE_PATTERN.match(line).group(1) == env_name)  # type: ignore[union-attr]
        ]

        if len(new_lines) == len(lines):
            return False  # not found

        content = "\n".join(new_lines) + "\n" if new_lines else ""
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, content.encode("utf-8"))
        finally:
            os.close(fd)
        return True

    @staticmethod
    def check_gitignore(file_path: str) -> bool:
        """Check if the file is covered by .gitignore. Returns True if ignored."""
        path = Path(file_path)
        # Walk up to find a git repo root with .gitignore
        check_dir = path.parent
        for _ in range(20):
            gitignore = check_dir / ".gitignore"
            if gitignore.exists():
                fname = path.name
                content = gitignore.read_text(encoding="utf-8")
                for line in content.splitlines():
                    stripped = line.strip()
                    if (
                        stripped
                        and not stripped.startswith("#")
                        and (fname == stripped or fname.startswith(stripped.rstrip("*")))
                    ):
                        return True
            if (check_dir / ".git").exists():
                break
            parent = check_dir.parent
            if parent == check_dir:
                break
            check_dir = parent
        return False
