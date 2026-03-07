"""demo_ui.py — ANSI terminal UI components and i18n for the ANDON demo.

Retro-game-style UI components: CRT frames, ANDON status boards,
progress bars, narrator boxes, and terminal helpers.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
import time
from pathlib import Path
from typing import Any

# ── ANSI colors ──────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
DIM = "\033[2m"
BOLD = "\033[1m"
REVERSE = "\033[7m"
RESET = "\033[0m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_BLACK = "\033[40m"

W = min(os.get_terminal_size().columns if sys.stdout.isatty() else 72, 76)

# ── i18n ─────────────────────────────────────────────────────
_LANG = "en"
_STRINGS: dict[str, Any] = {}


def _load_locale(lang: str) -> None:
    global _LANG, _STRINGS
    locale_file = Path(__file__).parent / "locales" / f"{lang}.json"
    with open(locale_file, encoding="utf-8") as f:
        _STRINGS = json.load(f)
    _LANG = lang


def t(key: str, **kwargs: Any) -> str | list[str]:
    """Lookup translated string. Supports dotted keys and format params."""
    val: Any = _STRINGS
    for part in key.split("."):
        val = val[part]
    if isinstance(val, str) and kwargs:
        return val.format(**kwargs)
    return val


# Load default locale
_load_locale("en")


# ── Terminal helpers ─────────────────────────────────────────

def clear() -> None:
    print("\033[H\033[2J", end="", flush=True)


def pause(msg: str = "") -> None:
    if not msg:
        msg = f"\u25b6 {t('common.enter_continue')}"
    print(f"\n  {DIM}{msg}{RESET}", end="")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print()


def slow(text: str, delay: float = 0.012) -> None:
    """Typewriter effect — retro terminal style."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        if ch not in (" ", "\n"):
            time.sleep(delay)
    if not text.endswith("\n"):
        print()


def beep() -> None:
    """Terminal bell — audible alert."""
    sys.stdout.write("\a")
    sys.stdout.flush()


# ── Retro UI components ─────────────────────────────────────

def crt_frame(lines: list[str], color: str = GREEN, title: str = "") -> None:
    """Draw a CRT monitor-style frame around content."""
    inner = W - 6
    print(f"  {color}\u2554{'═' * inner}\u2557{RESET}")
    if title:
        pad = inner - len(title) - 2
        print(
            f"  {color}\u2551 {BOLD}{WHITE}{title}{RESET}"
            f"{color}{' ' * pad}\u2551{RESET}"
        )
        print(f"  {color}\u2560{'═' * inner}\u2563{RESET}")
    for line in lines:
        print(f"  {color}\u2551{RESET} {line}")
    print(f"  {color}\u255a{'═' * inner}\u255d{RESET}")


def andon_board(statuses: list[tuple[str, str]]) -> None:
    """Draw an ANDON-style status board."""
    color_map = {
        "green": (BG_GREEN, f"\u25cf {t('andon_board.normal')}"),
        "yellow": (BG_YELLOW, f"\u25b2 {t('andon_board.caution')}"),
        "red": (BG_RED, f"\u25a0 {t('andon_board.stopped')}"),
        "off": (DIM, f"\u25cb {t('andon_board.off')}    "),
    }
    unknown_label = f"? {t('andon_board.unknown')}"
    inner = W - 6
    board_title = t("andon_board.title")
    title_pad = inner - len(board_title) - 6
    hline = "\u2500" * inner
    print(f"\n  {WHITE}\u250c{hline}\u2510{RESET}")
    print(
        f"  {WHITE}\u2502{REVERSE}{BOLD}  {board_title}"
        f"{' ' * title_pad}  {RESET}{WHITE}\u2502{RESET}"
    )
    print(f"  {WHITE}\u251c{hline}\u2524{RESET}")
    for label, state in statuses:
        bg, indicator = color_map.get(state, (DIM, unknown_label))
        padded_indicator = f"{indicator:<9}"
        line = f"  {bg}{WHITE} {padded_indicator} {RESET} {label}"
        print(f"  {WHITE}\u2502{RESET}{line}")
    print(f"  {WHITE}\u2514{hline}\u2518{RESET}")


def progress_bar(current: int, total: int, label: str = "") -> None:
    """Retro-style progress bar."""
    bar_w = 30
    filled = int(bar_w * current / total) if total > 0 else 0
    bar = f"{GREEN}{'█' * filled}{DIM}{'░' * (bar_w - filled)}{RESET}"
    pct = int(100 * current / total) if total > 0 else 0
    print(f"    [{bar}] {pct:3d}%  {label}")


def narrator(text: str) -> None:
    """Narrator box — like a retro game dialogue."""
    lines = textwrap.wrap(text, W - 12)
    inner = W - 6
    hline = "\u2500" * inner
    print(f"\n  {CYAN}\u250c{hline}\u2510{RESET}")
    for line in lines:
        padded = f"{line:<{inner - 2}}"
        print(f"  {CYAN}\u2502{RESET} {padded} {CYAN}\u2502{RESET}")
    print(f"  {CYAN}\u2514{hline}\u2518{RESET}")


def narrator_block(title: str, paragraphs: list[str]) -> None:
    """Multi-paragraph narrator with title."""
    inner = W - 6
    all_lines: list[str] = []
    for p in paragraphs:
        if not p.strip():
            all_lines.append("")
        elif p.startswith("  "):
            all_lines.append(p)
        else:
            all_lines.extend(textwrap.wrap(p.strip(), inner - 4))
    print(f"\n  {CYAN}\u2554{'═' * inner}\u2557{RESET}")
    title_pad = inner - len(title) - 2
    print(
        f"  {CYAN}\u2551 {BOLD}{WHITE}{title}{RESET}"
        f"{CYAN}{' ' * title_pad}\u2551{RESET}"
    )
    print(f"  {CYAN}\u2560{'═' * inner}\u2563{RESET}")
    for line in all_lines:
        padded = f"{line:<{inner - 2}}"[:inner - 2]
        print(f"  {CYAN}\u2551{RESET} {padded} {CYAN}\u2551{RESET}")
    print(f"  {CYAN}\u255a{'═' * inner}\u255d{RESET}")


def step_banner(n: int, total: int, desc: str) -> None:
    inner = W - 6
    prefix = f"  STEP {n}/{total}: {desc}"
    print(f"\n  {YELLOW}{'▬' * inner}{RESET}")
    print(f"  {BOLD}{YELLOW}{prefix}{RESET}")
    print(f"  {YELLOW}{'▬' * inner}{RESET}")


def ok(msg: str) -> None:
    print(f"    {GREEN}[OK]{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"    {YELLOW}[!!]{RESET} {msg}")


def fail(msg: str) -> None:
    print(f"    {RED}[XX]{RESET} {msg}")


def info(msg: str) -> None:
    print(f"    {CYAN}[>>]{RESET} {msg}")


def indent_print(text: str, prefix: str = "    ") -> None:
    for line in text.splitlines():
        print(f"{prefix}{line}")


# ── CJK width helpers ───────────────────────────────────────

def _visual_width(s: str) -> int:
    """Calculate visual width accounting for CJK double-width chars."""
    width = 0
    for ch in s:
        cp = ord(ch)
        if (
            0x3000 <= cp <= 0x9FFF
            or 0xF900 <= cp <= 0xFAFF
            or 0xFF01 <= cp <= 0xFF60
        ):
            width += 2
        else:
            width += 1
    return width


def _visual_center(s: str, total: int) -> str:
    """Center string to total visual width, accounting for CJK chars."""
    vw = _visual_width(s)
    pad = total - vw
    if pad <= 0:
        return s
    left = pad // 2
    right = pad - left
    return " " * left + s + " " * right
