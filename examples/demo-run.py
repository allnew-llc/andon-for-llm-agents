#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
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

import os
import sys
import tempfile
from pathlib import Path

# ── Setup paths ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "hooks"
sys.path.insert(0, str(HOOKS))
# Add examples/ so demo_ui and demo_stages can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

DEMO_DIR = Path(tempfile.mkdtemp(prefix="andon-demo-"))
os.environ["ANDON_WORKSPACE"] = str(DEMO_DIR)
os.environ["ANDON_STATE_DIR"] = str(DEMO_DIR / ".claude" / "state")

from demo_meta_andon import (  # noqa: E402
    explain_meta_andon_after,
    explain_meta_andon_before,
    run_meta_andon_demo,
)
from demo_stages import (  # noqa: E402
    explain_andon_after,
    explain_andon_before,
    explain_packs_after,
    explain_packs_before,
    explain_safety_after,
    explain_safety_before,
    explain_transform_after,
    explain_transform_before,
    run_andon_demo,
    run_packs_demo,
    run_safety_demo,
    run_transform_demo,
)
from demo_ui import (  # noqa: E402
    BOLD,
    CYAN,
    DIM,
    GREEN,
    RED,
    RESET,
    REVERSE,
    WHITE,
    YELLOW,
    W,
    _load_locale,
    _visual_center,
    andon_board,
    clear,
    narrator,
    narrator_block,
    pause,
    t,
    warn,
)

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


def _factory_art() -> str:
    pl = t("pipeline.banner_text")
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
        choice = input(f"  {BOLD}▶ {t('lang_select.prompt')}{RESET}").strip()
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
    print(f"  {WHITE}╔{'═' * inner}╗{RESET}")
    print(f"  {WHITE}║{REVERSE}{BOLD}  {menu_header}{' ' * header_pad}  {RESET}{WHITE}║{RESET}")
    print(f"  {WHITE}╠{'═' * inner}╣{RESET}")

    items = [
        ("1", f"{RED}●{RESET}", t("menu.item1_title"), t("menu.item1_desc")),
        ("2", f"{YELLOW}▲{RESET}", t("menu.item2_title"), t("menu.item2_desc")),
        ("3", "⟳", t("menu.item3_title"), t("menu.item3_desc")),
        ("4", "📦", t("menu.item4_title"), t("menu.item4_desc")),
        ("5", "\U0001f6a8", t("menu.item5_title"), t("menu.item5_desc")),
    ]
    for key, icon, title, desc in items:
        print(f"  {WHITE}║{RESET}                                                        {WHITE}║{RESET}")
        print(f"  {WHITE}║{RESET}   {CYAN}{BOLD}[{key}]{RESET}  {icon}  {BOLD}{title}{RESET}")
        print(f"  {WHITE}║{RESET}        {DIM}{desc}{RESET}")

    print(f"  {WHITE}║{RESET}                                                        {WHITE}║{RESET}")
    print(f"  {WHITE}╠{'═' * inner}╣{RESET}")
    print(f"  {WHITE}║{RESET}   {CYAN}{BOLD}[6]{RESET}  🚀  {BOLD}{t('menu.run_all')}{RESET} {DIM}{t('menu.guided_tour')}{RESET}")
    print(f"  {WHITE}║{RESET}   {CYAN}{BOLD}[R]{RESET}  📖  {BOLD}{t('menu.read_readme')}{RESET}")
    print(f"  {WHITE}║{RESET}   {CYAN}{BOLD}[Q]{RESET}  🚪  {BOLD}{t('menu.exit')}{RESET}")
    print(f"  {WHITE}║{RESET}                                                        {WHITE}║{RESET}")
    print(f"  {WHITE}╚{'═' * inner}╝{RESET}")

    try:
        choice = input(f"\n  {BOLD}▶ {t('menu.prompt')}{RESET}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = "q"
    return choice


# ═════════════════════════════════════════════════════════════
#   README VIEWER
# ═════════════════════════════════════════════════════════════

def show_readme() -> None:
    clear()
    import demo_ui
    readme_path = ROOT / ("README.ja.md" if demo_ui._LANG == "ja" else "README.md")
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
    print(f"\n  {WHITE}╔{'═' * inner}╗{RESET}")
    print(f"  {WHITE}║{REVERSE}{BOLD}  📖 {readme_title}{' ' * title_pad}  {RESET}{WHITE}║{RESET}")
    print(f"  {WHITE}╠{'═' * inner}╣{RESET}")
    for i, (sec_t, _) in enumerate(sections, 1):
        print(f"  {WHITE}║{RESET}   {CYAN}[{i:2}]{RESET}  {sec_t}")
    print(f"  {WHITE}║{RESET}")
    print(f"  {WHITE}║{RESET}   {CYAN}[ A]{RESET}  {t('readme_viewer.show_all')}")
    print(f"  {WHITE}║{RESET}   {CYAN}[ Q]{RESET}  {t('readme_viewer.back')}")
    print(f"  {WHITE}╚{'═' * inner}╝{RESET}")

    while True:
        try:
            ch = input(f"\n  {BOLD}▶ {t('readme_viewer.prompt')}{RESET}").strip().lower()
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
    pause(f"▶ {t('common.enter_tour')}")

    # Stage 1
    explain_andon_before()
    incident_dir = run_andon_demo(DEMO_DIR)
    explain_andon_after(incident_dir)
    pause(f"▶ {t('common.enter_stage2')}")

    # Stage 2
    explain_safety_before()
    stats = run_safety_demo()
    explain_safety_after(stats)
    pause(f"▶ {t('common.enter_stage3')}")

    # Stage 3
    explain_transform_before()
    run_transform_demo()
    explain_transform_after()
    pause(f"▶ {t('common.enter_stage4')}")

    # Stage 4
    explain_packs_before()
    result = run_packs_demo()
    explain_packs_after(result)
    pause(f"▶ {t('common.enter_stage5')}")

    # Stage 5
    explain_meta_andon_before()
    meta_result = run_meta_andon_demo(DEMO_DIR)
    explain_meta_andon_after(meta_result)

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
        (t("tour.stage5_done"), "green"),
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
    pause(f"▶ {t('common.enter_start')}")

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

        elif choice in ("1", "2", "3", "4", "5"):
            _stages = {
                "1": (explain_andon_before, lambda: run_andon_demo(DEMO_DIR), explain_andon_after),
                "2": (explain_safety_before, run_safety_demo, explain_safety_after),
                "3": (explain_transform_before, run_transform_demo, lambda *_: explain_transform_after()),
                "4": (explain_packs_before, run_packs_demo, explain_packs_after),
                "5": (explain_meta_andon_before, lambda: run_meta_andon_demo(DEMO_DIR), explain_meta_andon_after),
            }
            before_fn, run_fn, after_fn = _stages[choice]
            clear()
            before_fn()
            after_fn(run_fn())
            pause(f"▶ {t('common.enter_return')}")

        elif choice == "6":
            run_all()
            pause(f"▶ {t('common.enter_return')}")

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
