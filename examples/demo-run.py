#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
# code-health: threshold-exception (interactive demo — self-contained by design)
"""demo-run.py — ANDON for LLM Agents: Interactive Guided Demo

A retro-game-style, menu-driven demo inspired by ANDON status boards
and classic PC adventure games. Each demo is explained before running,
then summarized after.

Usage:
    pip install pyyaml
    python examples/demo-run.py

No external services required. Everything runs locally.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Any

# ── Setup paths ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "hooks"
sys.path.insert(0, str(HOOKS))

DEMO_DIR = Path(tempfile.mkdtemp(prefix="andon-demo-"))
os.environ["ANDON_WORKSPACE"] = str(DEMO_DIR)
os.environ["ANDON_STATE_DIR"] = str(DEMO_DIR / ".claude" / "state")

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
        msg = f"\u25b6 Press {BOLD}ENTER{RESET}{DIM} {t('common.enter_continue')}"
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
        print(f"  {color}\u2551 {BOLD}{WHITE}{title}{RESET}{color}{' ' * pad}\u2551{RESET}")
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
    print(f"  {WHITE}\u2502{REVERSE}{BOLD}  {board_title}{' ' * title_pad}  {RESET}{WHITE}\u2502{RESET}")
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
    print(f"  {CYAN}\u2551 {BOLD}{WHITE}{title}{RESET}{CYAN}{' ' * title_pad}\u2551{RESET}")
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


# ═════════════════════════════════════════════════════════════
#   TITLE SCREEN
# ═════════════════════════════════════════════════════════════

TITLE_ART = f"""\
{RED}     █████╗  ███╗   ██╗██████╗  ██████╗ ███╗   ██╗{RESET}
{RED}    ██╔══██╗ ████╗  ██║██╔══██╗██╔═══██╗████╗  ██║{RESET}
{YELLOW}    ███████║ ██╔██╗ ██║██║  ██║██║   ██║██╔██╗ ██║{RESET}
{YELLOW}    ██╔══██║ ██║╚██╗██║██║  ██║██║   ██║██║╚██╗██║{RESET}
{GREEN}    ██║  ██║ ██║ ╚████║██████╔╝╚██████╔╝██║ ╚████║{RESET}
{GREEN}    ╚═╝  ╚═╝ ╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝{RESET}
{DIM}            f o r   L L M   A g e n t s{RESET}"""


def _visual_width(s: str) -> int:
    """Calculate visual width accounting for CJK double-width chars."""
    width = 0
    for ch in s:
        cp = ord(ch)
        # CJK Unified Ideographs + Katakana + Hiragana + Fullwidth
        if (0x3000 <= cp <= 0x9FFF or 0xF900 <= cp <= 0xFAFF
                or 0xFF01 <= cp <= 0xFF60):
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


def _factory_art() -> str:
    pl = t("pipeline.banner_text")
    # Center the text in the box (29 visual columns)
    padded = _visual_center(pl, 29)
    return f"""\
{DIM}        ┌──────┐  ┌──────┐  ┌──────┐
        │{RED}●{DIM} {GREEN}●{DIM} {YELLOW}●{DIM} │  │{GREEN}●{DIM} {GREEN}●{DIM} {GREEN}●{DIM} │  │{RED}●{DIM} {YELLOW}●{DIM} {GREEN}●{DIM} │
        └──┬───┘  └──┬───┘  └──┬───┘
     ══════╧═════════╧═════════╧══════
     ║{padded}║
     ═════════════════════════════════{RESET}"""


def show_title() -> None:
    clear()
    print()
    print(TITLE_ART)
    print(_factory_art())
    print(f"""
  {BOLD}{WHITE}{t('title.subtitle')}{RESET}

  {DIM}{t('title.tagline')}{RESET}

  {DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}

  {t('title.weaknesses_header')}
    {RED}▪{RESET} {t('title.weakness1')}      {RED}▪{RESET} {t('title.weakness2')}
    {RED}▪{RESET} {t('title.weakness3')}      {RED}▪{RESET} {t('title.weakness4')}

  {t('title.pillars_header')}

    {YELLOW}▶ Jidoka (自働化){RESET}  {t('title.jidoka')}
    {GREEN}▶ Kaizen (改善){RESET}    {t('title.kaizen')}

  {DIM}{t('title.local_only')}{RESET}
""")


# ═════════════════════════════════════════════════════════════
#   LANGUAGE SELECTION
# ═════════════════════════════════════════════════════════════

def select_language() -> None:
    """Show language selection and load the chosen locale."""
    print(f"""
  {BOLD}{WHITE}{t('lang_select.header')} / 言語:{RESET}
    {CYAN}[1]{RESET} {t('lang_select.option1')}
    {CYAN}[2]{RESET} {t('lang_select.option2')}
""")
    try:
        choice = input(f"  {BOLD}\u25b6 {t('lang_select.prompt')}{RESET}").strip()
    except (EOFError, KeyboardInterrupt):
        choice = ""

    if choice == "2":
        _load_locale("ja")


# ═════════════════════════════════════════════════════════════
#   MAIN MENU
# ═════════════════════════════════════════════════════════════

def show_menu() -> str:
    inner = W - 6
    menu_header = t("menu.header")
    header_pad = inner - len(menu_header) - 4
    print(f"  {WHITE}\u2554{'═' * inner}\u2557{RESET}")
    print(f"  {WHITE}\u2551{REVERSE}{BOLD}  {menu_header}{' ' * header_pad}  {RESET}{WHITE}\u2551{RESET}")
    print(f"  {WHITE}\u2560{'═' * inner}\u2563{RESET}")

    items = [
        ("1", f"{RED}●{RESET}", t("menu.item1_title"), t("menu.item1_desc")),
        ("2", f"{YELLOW}▲{RESET}", t("menu.item2_title"), t("menu.item2_desc")),
        ("3", "⟳", t("menu.item3_title"), t("menu.item3_desc")),
        ("4", "📦", t("menu.item4_title"), t("menu.item4_desc")),
    ]
    for key, icon, title, desc in items:
        print(f"  {WHITE}\u2551{RESET}                                                        {WHITE}\u2551{RESET}")
        print(f"  {WHITE}\u2551{RESET}   {CYAN}{BOLD}[{key}]{RESET}  {icon}  {BOLD}{title}{RESET}")
        print(f"  {WHITE}\u2551{RESET}        {DIM}{desc}{RESET}")

    print(f"  {WHITE}\u2551{RESET}                                                        {WHITE}\u2551{RESET}")
    print(f"  {WHITE}\u2560{'═' * inner}\u2563{RESET}")
    print(f"  {WHITE}\u2551{RESET}   {CYAN}{BOLD}[5]{RESET}  🚀  {BOLD}{t('menu.run_all')}{RESET} {DIM}{t('menu.guided_tour')}{RESET}")
    print(f"  {WHITE}\u2551{RESET}   {CYAN}{BOLD}[R]{RESET}  📖  {BOLD}{t('menu.read_readme')}{RESET}")
    print(f"  {WHITE}\u2551{RESET}   {CYAN}{BOLD}[Q]{RESET}  🚪  {BOLD}{t('menu.exit')}{RESET}")
    print(f"  {WHITE}\u2551{RESET}                                                        {WHITE}\u2551{RESET}")
    print(f"  {WHITE}\u255a{'═' * inner}\u255d{RESET}")

    try:
        choice = input(f"\n  {BOLD}\u25b6 {t('menu.prompt')}{RESET}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = "q"
    return choice


# ═════════════════════════════════════════════════════════════
#   DEMO 1: ANDON INCIDENT
# ═════════════════════════════════════════════════════════════

def explain_andon_before() -> None:
    clear()
    narrator_block(f"🔴 {t('stage1.title')}", t("stage1.before"))

    andon_board([
        (t("andon_board.line_a"), "off"),
        (t("andon_board.line_b"), "off"),
        (t("andon_board.line_c"), "off"),
    ])

    pause()


def run_andon_demo() -> str:
    import tps_kaizen_runtime as runtime
    runtime.WORKSPACE = DEMO_DIR
    runtime.STATE_DIR = DEMO_DIR / ".claude" / "state"
    runtime.KAIZEN_DIR = runtime.STATE_DIR / "kaizen"
    runtime.INCIDENTS_DIR = runtime.KAIZEN_DIR / "incidents"
    runtime.HISTORY_DIR = runtime.STATE_DIR / "history"
    runtime.ANDON_FILE = runtime.STATE_DIR / "andon-open.json"
    runtime.STANDARD_REGISTRY = runtime.KAIZEN_DIR / "standardization-registry.json"

    # ── Step 1: Failure ──
    step_banner(1, 4, t("stage1.step1"))
    print(f"\n    {DIM}$ npm install @acme/widget{RESET}")
    time.sleep(0.3)
    beep()
    print(f"    {RED}npm ERR! Cannot find module '@acme/widget'{RESET}")
    print(f"    {RED}npm ERR! code MODULE_NOT_FOUND{RESET}")
    time.sleep(0.3)

    andon_board([
        (t("andon_board.line_a"), "red"),
        (t("andon_board.line_b"), "yellow"),
        (t("andon_board.line_c"), "yellow"),
    ])

    command = "npm install @acme/widget"
    output = ("npm ERR! Cannot find module '@acme/widget'\n"
              "npm ERR! code MODULE_NOT_FOUND")

    # ── Step 2: Classify ──
    step_banner(2, 4, t("stage1.step2"))
    analysis = runtime.classify_failure(command, output)
    print()
    progress_bar(1, 3, t("stage1.scan_patterns"))
    time.sleep(0.2)
    progress_bar(2, 3, t("stage1.match_cause"))
    time.sleep(0.2)
    progress_bar(3, 3, t("stage1.classify_done"))
    print()
    ok(f"{t('stage1.cause_label')}      {analysis['cause_label']}")
    ok(f"{t('stage1.cause_id_label')}   {analysis['cause_id']}")
    ok(f"{t('stage1.confidence_label')} {analysis['confidence']:.0%}")

    # ── Step 3: Incident ──
    step_banner(3, 4, t("stage1.step3"))
    runtime.ensure_dirs()
    incident_id = runtime.incident_id_from(command, runtime.now_utc())
    incident_dir = runtime.INCIDENTS_DIR / incident_id
    incident_dir.mkdir(parents=True, exist_ok=True)

    evidence = {
        "incident_id": incident_id,
        "opened_at": runtime.now_utc(),
        "command": command,
        "exit_code": 1,
        "output_snippet": output,
        "workspace": str(DEMO_DIR),
        "git": {"branch": "main", "head": "abc1234", "status": ""},
    }
    runtime.write_json(incident_dir / "evidence.json", evidence)
    runtime.write_json(incident_dir / "analysis.json", analysis)

    std_result = runtime.apply_standardization(
        incident_id, analysis.get("standardization_actions", []), incident_dir
    )
    actions_data = {
        "incident_id": incident_id,
        "prevention_actions": analysis["prevention_actions"],
        "standardization_actions": analysis["standardization_actions"],
        "standardization_result": std_result,
    }
    runtime.write_json(incident_dir / "actions.json", actions_data)

    report = runtime.write_incident_report(
        incident_id, incident_dir, evidence, analysis, actions_data, std_result,
    )

    print()
    ok(f"{t('stage1.incident_label')} {incident_id}")
    info(t("stage1.artifacts_label"))
    for f in sorted(incident_dir.iterdir()):
        print(f"      📄 {f.name}")

    print(f"\n    {DIM}── {t('stage1.report_preview')} ──{RESET}")
    for line in report.read_text().splitlines()[:18]:
        print(f"    {DIM}{line}{RESET}")
    remaining = len(report.read_text().splitlines()) - 18
    if remaining > 0:
        print(f"    {DIM}{t('stage1.more_lines', count=remaining)}{RESET}")

    # ── Step 4: Standardize ──
    step_banner(4, 4, t("stage1.step4"))
    registry = runtime.load_json(runtime.STANDARD_REGISTRY)
    print()
    for rule in registry.get("rules", []):
        ok(f"{t('stage1.new_rule')} {BOLD}{rule['type']}{RESET} = {rule['value']}")
    print()
    info(t("stage1.proactive_msg"))

    return str(incident_dir)


def explain_andon_after(incident_dir: str) -> None:
    after_paragraphs = []
    for line in t("stage1.after"):
        after_paragraphs.append(line.format(incident_dir=incident_dir))

    narrator_block(f"🔴 {t('stage1.after_title')}", after_paragraphs)

    andon_board([
        (t("andon_board.line_a"), "green"),
        (t("andon_board.line_b"), "green"),
        (t("andon_board.line_c"), "green"),
    ])


# ═════════════════════════════════════════════════════════════
#   DEMO 2: OUTPUT SAFETY GUARD
# ═════════════════════════════════════════════════════════════

def explain_safety_before() -> None:
    clear()
    narrator_block(f"🛡️  {t('stage2.title')}", t("stage2.before"))
    pause()


TEST_CASES = [
    {"label_key": "safe",
     "text": "The average temperature in Tokyo in March is 12°C.",
     "expect": "pass",
     "icon": "🌡️"},
    {"label_key": "code",
     "text": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
     "expect": "pass",
     "icon": "💻"},
    {"label_key": "legal",
     "text": "You must file a lawsuit against the company for breach of contract.",
     "expect": "guard",
     "icon": "⚖️"},
    {"label_key": "tax",
     "text": "You should deduct your car expenses from taxes this year.",
     "expect": "guard",
     "icon": "💰"},
    {"label_key": "jp_legal",
     "text": "提訴すべきです。この契約は違法であるため、法的措置を取るべきです。",
     "expect": "guard",
     "icon": "🇯🇵"},
]


def run_safety_demo() -> dict:
    from output_safety_guard import GuardLevel, OutputSafetyGuard

    guard = OutputSafetyGuard()
    stats = {"pass": 0, "guard": 0}

    for i, tc in enumerate(TEST_CASES, 1):
        label = t(f"stage2.test_labels.{tc['label_key']}")
        step_banner(i, len(TEST_CASES), f"{tc['icon']}  {label}")
        truncated = tc["text"][:60] + ("..." if len(tc["text"]) > 60 else "")
        print(f'\n    Input: "{truncated}"')
        print(f"    {DIM}{t('common.scanning')}{RESET}", end="")
        time.sleep(0.15)

        result = guard.check(tc["text"])

        if not result.triggered:
            print(f"\r    {GREEN}{'█' * 20}{RESET} {t('common.scan_complete')}")
            ok(f"{GREEN}{t('common.pass_label')}{RESET} — {t('common.no_concern')}")
            stats["pass"] += 1
        elif result.level == GuardLevel.GUARD:
            print(f"\r    {YELLOW}{'█' * 20}{RESET} {t('common.guard_active')}")
            warn(f"{YELLOW}GUARD{RESET} — {result.category.value}")
            if result.disclaimer:
                print(f"      {t('stage2.disclaimer_label')} "
                      f"{result.disclaimer.strip().splitlines()[0]}")
            if result.professional_referral:
                print(f"      {t('stage2.referral_label')} "
                      f"{result.professional_referral}")
            stats["guard"] += 1

        # Verify
        actual = "pass"
        if result.triggered:
            actual = "guard"
        if actual != tc["expect"]:
            print(f"      {RED}⚠ {t('common.unexpected', expect=tc['expect'], actual=actual)}{RESET}")

    return stats


def explain_safety_after(stats: dict) -> None:
    total = sum(stats.values())
    after_paragraphs = []
    for line in t("stage2.after"):
        after_paragraphs.append(
            line.format(total=total, pass_count=stats["pass"], guard_count=stats["guard"])
        )
    narrator_block(f"🛡️  {t('stage2.after_title')}", after_paragraphs)


# ═════════════════════════════════════════════════════════════
#   DEMO 3: OUTPUT TRANSFORMATION
# ═════════════════════════════════════════════════════════════

def explain_transform_before() -> None:
    clear()
    narrator_block(f"🔄 {t('stage3.title')}", t("stage3.before"))
    pause()


def run_transform_demo() -> None:
    from output_safety_guard import OutputSafetyGuard

    guard = OutputSafetyGuard()

    # Case 1: GUARD — Legal text
    step_banner(1, 1, t("stage3.step_title"))
    text = ("Under Article 23 of APPI, third-party provision of personal "
            "data requires consent. You must obtain explicit consent "
            "before sharing user data.")
    print(f"\n    {DIM}── {t('stage3.before_label')} ──{RESET}")
    indent_print(text)

    result = guard.check(text)
    if result.triggered:
        transformed = guard.apply_guard(text, result)
        print(f"\n    {YELLOW}── {t('stage3.after_label')} ──{RESET}")
        indent_print(transformed)
    else:
        print(f"\n    {GREEN}[PASS]{RESET} {t('stage3.pass_msg')}")


def explain_transform_after() -> None:
    narrator_block(f"🔄 {t('stage3.after_title')}", t("stage3.after_text"))


# ═════════════════════════════════════════════════════════════
#   DEMO 4: KNOWLEDGE PACKS
# ═════════════════════════════════════════════════════════════

def explain_packs_before() -> None:
    clear()
    narrator_block(f"📦 {t('stage4.title')}", t("stage4.before"))
    pause()


def run_packs_demo() -> dict | None:
    from domain_classifier import recommend_skills
    from pack_loader import PackLoader

    # Step 1: Load
    step_banner(1, 2, t("stage4.step1"))
    sample_pack_dir = ROOT / "examples" / "sample-pack"
    if not sample_pack_dir.exists():
        warn(t("stage4.pack_not_found"))
        return None

    loader = PackLoader(pack0_available=True)
    bundle = loader.load_all(sample_pack_dir.parent)

    if not bundle.packs:
        warn(t("stage4.no_packs"))
        return None

    pack = bundle.packs[0]
    print()
    progress_bar(1, 3, t("stage4.reading_manifest"))
    time.sleep(0.2)
    progress_bar(2, 3, t("stage4.validating_deps"))
    time.sleep(0.2)
    progress_bar(3, 3, t("stage4.pack_loaded"))
    print()
    ok(f"{t('stage4.pack_label')}    {BOLD}{pack.name}{RESET}")
    ok(f"{t('stage4.version_label')} v{pack.version}")
    ok(f"{t('stage4.domains_label')} {[d.get('id') for d in pack.domains]}")

    # Step 2: Classify & recommend
    step_banner(2, 2, t("stage4.step2"))
    print(f"\n    {DIM}$ python -m pytest tests/test_api.py{RESET}")
    time.sleep(0.2)
    print(f"    {RED}FAILED tests/test_api.py::test_auth{RESET}")
    print(f"    {RED}AssertionError: 401 != 200{RESET}")
    print(f"    {RED}Permission denied for endpoint /api/v1/users{RESET}")

    result = recommend_skills(
        cause_id="assertion_failure",
        command="python -m pytest tests/test_api.py",
        output=("FAILED tests/test_api.py::test_auth - AssertionError: 401 != 200\n"
                "Permission denied for endpoint /api/v1/users"),
        skill_map=bundle.skill_map,
        extra_keywords=bundle.extra_keywords,
    )

    print(f"\n    {DIM}── {t('stage4.domain_scoring')} ──{RESET}")
    if result["domain_scores"]:
        max_score = max(ds["score"] for ds in result["domain_scores"][:5]) or 1
        for ds in result["domain_scores"][:5]:
            bar_len = int(15 * ds["score"] / max_score) if max_score > 0 else 0
            bar = f"{GREEN}{'█' * bar_len}{DIM}{'░' * (15 - bar_len)}{RESET}"
            winner = f" ◀ {t('stage4.winner')}" if ds["domain_id"] == result["domain"] else ""
            print(f"    {bar} {ds['domain_id']:<22} "
                  f"{ds['score']:.1f}  {DIM}{ds['matched']}{RESET}"
                  f"{BOLD}{YELLOW}{winner}{RESET}")

    print()
    ok(f"{t('stage4.selected_domain')} {BOLD}{result['domain']}{RESET}")

    if result["primary"]:
        info(f"{t('stage4.recommended_skills')}")
        for skill in result["primary"]:
            print(f"      → {BOLD}{skill['ref']}{RESET}: {skill['description']}")
    for skill in result.get("secondary", []):
        print(f"      → {skill['ref']}: {skill['description']}")
    if not result["primary"] and not result["secondary"]:
        print()
        warn(t("stage4.no_skills"))
        print(f"    {DIM}{t('stage4.no_skills_detail1')}")
        print(f"     {t('stage4.no_skills_detail2', domain=result['domain'])}{RESET}")

    return result


def explain_packs_after(result: dict | None) -> None:
    domain = result["domain"] if result else "unknown"
    after_paragraphs = []
    for line in t("stage4.after"):
        after_paragraphs.append(line.format(domain=domain))
    narrator_block(f"📦 {t('stage4.after_title')}", after_paragraphs)


# ═════════════════════════════════════════════════════════════
#   README VIEWER
# ═════════════════════════════════════════════════════════════

def show_readme() -> None:
    clear()
    readme_path = ROOT / "README.md"
    if not readme_path.exists():
        warn(t("readme_viewer.not_found"))
        pause()
        return

    content = readme_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    sections: list[tuple[str, list[str]]] = []
    sec_title = "Header"
    body: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if body:
                sections.append((sec_title, body))
            sec_title = line[3:].strip()
            body = []
        else:
            body.append(line)
    if body:
        sections.append((sec_title, body))

    inner = W - 6
    readme_title = t("readme_viewer.title")
    title_pad = inner - len(readme_title) - 6
    print(f"\n  {WHITE}\u2554{'═' * inner}\u2557{RESET}")
    print(f"  {WHITE}\u2551{REVERSE}{BOLD}  📖 {readme_title}{' ' * title_pad}  {RESET}{WHITE}\u2551{RESET}")
    print(f"  {WHITE}\u2560{'═' * inner}\u2563{RESET}")
    for i, (sec_t, _) in enumerate(sections, 1):
        print(f"  {WHITE}\u2551{RESET}   {CYAN}[{i:2}]{RESET}  {sec_t}")
    print(f"  {WHITE}\u2551{RESET}")
    print(f"  {WHITE}\u2551{RESET}   {CYAN}[ A]{RESET}  {t('readme_viewer.show_all')}")
    print(f"  {WHITE}\u2551{RESET}   {CYAN}[ Q]{RESET}  {t('readme_viewer.back')}")
    print(f"  {WHITE}\u255a{'═' * inner}\u255d{RESET}")

    while True:
        try:
            ch = input(f"\n  {BOLD}\u25b6 {t('readme_viewer.prompt')}{RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if ch in ("q", ""):
            break
        elif ch == "a":
            for sec_t, b in sections:
                print(f"\n  {BOLD}{CYAN}## {sec_t}{RESET}")
                for bline in b[:25]:
                    print(f"  {bline}")
                if len(b) > 25:
                    print(f"  {DIM}{t('readme_viewer.more_lines', count=len(b) - 25)}{RESET}")
            pause()
        elif ch.isdigit() and 1 <= int(ch) <= len(sections):
            sec_t, b = sections[int(ch) - 1]
            print(f"\n  {BOLD}{CYAN}## {sec_t}{RESET}")
            for bline in b:
                print(f"  {bline}")
            pause()


# ═════════════════════════════════════════════════════════════
#   RUN ALL (Guided Tour)
# ═════════════════════════════════════════════════════════════

def run_all() -> None:
    clear()
    narrator_block(f"🚀 {t('tour.title')}", t("tour.intro"))
    pause(f"\u25b6 {t('common.enter_tour')}")

    # Stage 1
    explain_andon_before()
    incident_dir = run_andon_demo()
    explain_andon_after(incident_dir)
    pause(f"\u25b6 {t('common.enter_stage2')}")

    # Stage 2
    explain_safety_before()
    stats = run_safety_demo()
    explain_safety_after(stats)
    pause(f"\u25b6 {t('common.enter_stage3')}")

    # Stage 3
    explain_transform_before()
    run_transform_demo()
    explain_transform_after()
    pause(f"\u25b6 {t('common.enter_stage4')}")

    # Stage 4
    explain_packs_before()
    result = run_packs_demo()
    explain_packs_after(result)

    # Finale
    clear()
    print(f"""
{GREEN}     ██████╗  ██████╗ ███╗   ███╗██████╗ ██╗     ███████╗████████╗███████╗{RESET}
{GREEN}    ██╔════╝ ██╔═══██╗████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██╔════╝{RESET}
{GREEN}    ██║      ██║   ██║██╔████╔██║██████╔╝██║     █████╗     ██║   █████╗{RESET}
{GREEN}    ██║      ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║   ██╔══╝{RESET}
{GREEN}    ╚██████╗ ╚██████╔╝██║ ╚═╝ ██║██║     ███████╗███████╗   ██║   ███████╗{RESET}
{GREEN}     ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝   ╚══════╝{RESET}
""")

    andon_board([
        (t("tour.stage1_done"), "green"),
        (t("tour.stage2_done"), "green"),
        (t("tour.stage3_done"), "green"),
        (t("tour.stage4_done"), "green"),
    ])

    complete_paragraphs = []
    for line in t("tour.complete"):
        complete_paragraphs.append(line.format(demo_dir=DEMO_DIR))

    narrator_block(f"🎉 {t('tour.complete_title')}", complete_paragraphs)


# ═════════════════════════════════════════════════════════════
#   MAIN LOOP
# ═════════════════════════════════════════════════════════════

def main() -> int:
    show_title()
    select_language()
    # Re-render title in selected language
    show_title()
    pause(f"\u25b6 {t('common.enter_start')}")

    while True:
        clear()
        show_title()
        choice = show_menu()

        if choice == "q":
            clear()
            print(f"""
  {DIM}{t('shutdown.msg')}{RESET}

  {DIM}{t('shutdown.temp_files', demo_dir=DEMO_DIR)}
  {t('shutdown.clean_up', demo_dir=DEMO_DIR)}{RESET}

  {BOLD}{t('shutdown.thanks')}{RESET}
""")
            return 0

        elif choice == "1":
            clear()
            explain_andon_before()
            incident_dir = run_andon_demo()
            explain_andon_after(incident_dir)
            pause(f"\u25b6 {t('common.enter_return')}")

        elif choice == "2":
            clear()
            explain_safety_before()
            stats = run_safety_demo()
            explain_safety_after(stats)
            pause(f"\u25b6 {t('common.enter_return')}")

        elif choice == "3":
            clear()
            explain_transform_before()
            run_transform_demo()
            explain_transform_after()
            pause(f"\u25b6 {t('common.enter_return')}")

        elif choice == "4":
            clear()
            explain_packs_before()
            result = run_packs_demo()
            explain_packs_after(result)
            pause(f"\u25b6 {t('common.enter_return')}")

        elif choice == "5":
            run_all()
            pause(f"\u25b6 {t('common.enter_return')}")

        elif choice == "r":
            show_readme()

        else:
            narrator(t("menu.invalid"))
            pause()

    return 0


if __name__ == "__main__":
    # Register hyphenated module name for import (in-memory, no file write)
    runtime_src = HOOKS / "tps-kaizen-runtime.py"
    if runtime_src.exists():
        import importlib.util

        _spec = importlib.util.spec_from_file_location("tps_kaizen_runtime", str(runtime_src))
        _mod = importlib.util.module_from_spec(_spec)
        sys.modules["tps_kaizen_runtime"] = _mod
        _spec.loader.exec_module(_mod)

    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n  {DIM}{t('shutdown.interrupted', demo_dir=DEMO_DIR)}{RESET}\n")
        sys.exit(0)
