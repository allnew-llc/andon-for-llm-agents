"""demo_stages.py — Stage demos for the ANDON interactive guided demo.

Four stage triplets (explain_before / run / explain_after):
  Stage 1: ANDON Incident Detection
  Stage 2: Output Safety Guard
  Stage 3: Output Transformation
  Stage 4: Knowledge Packs

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from demo_ui import (
    BOLD,
    DIM,
    GREEN,
    RED,
    RESET,
    YELLOW,
    andon_board,
    beep,
    clear,
    indent_print,
    info,
    narrator_block,
    ok,
    pause,
    progress_bar,
    step_banner,
    t,
    warn,
)

ROOT = Path(__file__).resolve().parent.parent

# ── Demo 1: ANDON Incident ─────────────────────────────────


def explain_andon_before() -> None:
    clear()
    narrator_block(f"\U0001f534 {t('stage1.title')}", t("stage1.before"))

    andon_board([
        (t("andon_board.line_a"), "off"),
        (t("andon_board.line_b"), "off"),
        (t("andon_board.line_c"), "off"),
    ])

    pause()


def run_andon_demo(demo_dir: Path) -> str:
    import tps_kaizen_runtime as runtime
    runtime.WORKSPACE = demo_dir
    runtime.STATE_DIR = demo_dir / ".claude" / "state"
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
        "workspace": str(demo_dir),
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
        print(f"      \U0001f4c4 {f.name}")

    print(f"\n    {DIM}\u2500\u2500 {t('stage1.report_preview')} \u2500\u2500{RESET}")
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

    narrator_block(f"\U0001f534 {t('stage1.after_title')}", after_paragraphs)

    andon_board([
        (t("andon_board.line_a"), "green"),
        (t("andon_board.line_b"), "green"),
        (t("andon_board.line_c"), "green"),
    ])


# ── Demo 2: Output Safety Guard ────────────────────────────

TEST_CASES = [
    {"label_key": "safe",
     "text": "The average temperature in Tokyo in March is 12\u00b0C.",
     "expect": "pass",
     "icon": "\U0001f321\ufe0f"},
    {"label_key": "code",
     "text": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
     "expect": "pass",
     "icon": "\U0001f4bb"},
    {"label_key": "legal",
     "text": "You must file a lawsuit against the company for breach of contract.",
     "expect": "guard",
     "icon": "\u2696\ufe0f"},
    {"label_key": "tax",
     "text": "You should deduct your car expenses from taxes this year.",
     "expect": "guard",
     "icon": "\U0001f4b0"},
    {"label_key": "jp_legal",
     "text": "\u63d0\u8a34\u3059\u3079\u304d\u3067\u3059\u3002\u3053\u306e\u5951\u7d04\u306f\u9055\u6cd5\u3067\u3042\u308b\u305f\u3081\u3001\u6cd5\u7684\u63aa\u7f6e\u3092\u53d6\u308b\u3079\u304d\u3067\u3059\u3002",
     "expect": "guard",
     "icon": "\U0001f1ef\U0001f1f5"},
]


def explain_safety_before() -> None:
    clear()
    narrator_block(f"\U0001f6e1\ufe0f  {t('stage2.title')}", t("stage2.before"))
    pause()


def run_safety_demo() -> dict[str, int]:
    from output_safety_guard import GuardLevel, OutputSafetyGuard

    guard = OutputSafetyGuard()
    stats: dict[str, int] = {"pass": 0, "guard": 0}

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
            print(f"      {RED}\u26a0 {t('common.unexpected', expect=tc['expect'], actual=actual)}{RESET}")

    return stats


def explain_safety_after(stats: dict[str, int]) -> None:
    total = sum(stats.values())
    after_paragraphs = []
    for line in t("stage2.after"):
        after_paragraphs.append(
            line.format(total=total, pass_count=stats["pass"], guard_count=stats["guard"])
        )
    narrator_block(f"\U0001f6e1\ufe0f  {t('stage2.after_title')}", after_paragraphs)


# ── Demo 3: Output Transformation ──────────────────────────


def explain_transform_before() -> None:
    clear()
    narrator_block(f"\U0001f504 {t('stage3.title')}", t("stage3.before"))
    pause()


def run_transform_demo() -> None:
    from output_safety_guard import OutputSafetyGuard

    guard = OutputSafetyGuard()

    # Case 1: GUARD — Legal text
    step_banner(1, 1, t("stage3.step_title"))
    text = ("Under Article 23 of APPI, sharing personal data without "
            "explicit consent constitutes a violation of privacy law. "
            "You should file a complaint with the PPC if your data "
            "was shared without authorization.")
    print(f"\n    {DIM}\u2500\u2500 {t('stage3.before_label')} \u2500\u2500{RESET}")
    indent_print(text)

    result = guard.check(text)
    if result.triggered:
        transformed = guard.apply_guard(text, result)
        print(f"\n    {YELLOW}\u2500\u2500 {t('stage3.after_label')} \u2500\u2500{RESET}")
        indent_print(transformed)
    else:
        print(f"\n    {GREEN}[PASS]{RESET} {t('stage3.pass_msg')}")


def explain_transform_after() -> None:
    narrator_block(f"\U0001f504 {t('stage3.after_title')}", t("stage3.after_text"))


# ── Demo 4: Knowledge Packs ────────────────────────────────


def explain_packs_before() -> None:
    clear()
    narrator_block(f"\U0001f4e6 {t('stage4.title')}", t("stage4.before"))
    pause()


def run_packs_demo() -> dict[str, Any] | None:
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

    print(f"\n    {DIM}\u2500\u2500 {t('stage4.domain_scoring')} \u2500\u2500{RESET}")
    if result["domain_scores"]:
        max_score = max(ds["score"] for ds in result["domain_scores"][:5]) or 1
        for ds in result["domain_scores"][:5]:
            bar_len = int(15 * ds["score"] / max_score) if max_score > 0 else 0
            bar = f"{GREEN}{'█' * bar_len}{DIM}{'░' * (15 - bar_len)}{RESET}"
            winner = f" \u25c0 {t('stage4.winner')}" if ds["domain_id"] == result["domain"] else ""
            print(f"    {bar} {ds['domain_id']:<22} "
                  f"{ds['score']:.1f}  {DIM}{ds['matched']}{RESET}"
                  f"{BOLD}{YELLOW}{winner}{RESET}")

    print()
    ok(f"{t('stage4.selected_domain')} {BOLD}{result['domain']}{RESET}")

    if result["primary"]:
        info(f"{t('stage4.recommended_skills')}")
        for skill in result["primary"]:
            print(f"      \u2192 {BOLD}{skill['ref']}{RESET}: {skill['description']}")
    for skill in result.get("secondary", []):
        print(f"      \u2192 {skill['ref']}: {skill['description']}")
    if not result["primary"] and not result["secondary"]:
        print()
        warn(t("stage4.no_skills"))
        print(f"    {DIM}{t('stage4.no_skills_detail1')}")
        print(f"     {t('stage4.no_skills_detail2', domain=result['domain'])}{RESET}")

    return result


def explain_packs_after(result: dict[str, Any] | None) -> None:
    domain = result["domain"] if result else "unknown"
    after_paragraphs = []
    for line in t("stage4.after"):
        after_paragraphs.append(line.format(domain=domain))
    narrator_block(f"\U0001f4e6 {t('stage4.after_title')}", after_paragraphs)
