"""demo_meta_andon.py — Stage 5: Meta-ANDON Pattern Detection demo.

Demonstrates Meta-ANDON: detecting repeated failure patterns
(whack-a-mole loops) and enforcing plan mode before further runs.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from demo_ui import (
    andon_board,
    beep,
    clear,
    fail,
    info,
    narrator_block,
    ok,
    pause,
    progress_bar,
    step_banner,
    t,
    warn,
)

from meta_andon_guard import (
    META_ANDON_REQUIRED_ARTIFACTS,
    evaluate_meta_andon,
)


# ── Demo 5: Meta-ANDON Pattern Detection ─────────────────


def explain_meta_andon_before() -> None:
    clear()
    narrator_block(f"\U0001f6a8 {t('stage5.title')}", t("stage5.before"))

    andon_board([
        (t("stage5.board_run1"), "green"),
        (t("stage5.board_run2"), "yellow"),
        (t("stage5.board_run3"), "red"),
    ])
    pause(f"\u25b6 {t('common.enter_continue')}")


def run_meta_andon_demo(demo_dir: Path) -> dict[str, Any]:
    clear()
    artifacts_dir = demo_dir / "meta-andon"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Simulate 3 consecutive failures at different phases
    step_banner(1, 4, t("stage5.step1"))
    failure_phases = ["Phase 2a", "Phase 2b", "Phase 3"]
    failure_ids = []
    for i, phase in enumerate(failure_phases):
        time.sleep(0.3)
        fail(t("stage5.failure_at", phase=phase, n=i + 1))
        failure_ids.append(f"run-{i + 1}")
        progress_bar(i + 1, 3, t("stage5.consecutive", n=i + 1))
    beep()
    warn(t("stage5.threshold_hit"))
    time.sleep(0.5)

    # Step 2: Evaluate — should be blocked (no artifacts yet)
    step_banner(2, 4, t("stage5.step2"))
    time.sleep(0.3)
    result = evaluate_meta_andon(
        artifacts_dir=artifacts_dir,
        consecutive_failures=3,
        failure_run_ids=failure_ids,
    )
    info(t("stage5.eval_blocked", blocked=result["blocked"]))
    info(t("stage5.missing_label"))
    for name in result["missing_artifacts"]:
        fail(f"  \u2718 {name}")
    time.sleep(0.5)

    # Step 3: Create required artifacts
    step_banner(3, 4, t("stage5.step3"))
    _create_demo_artifacts(artifacts_dir)
    ok(t("stage5.artifacts_created", n=len(META_ANDON_REQUIRED_ARTIFACTS)))
    time.sleep(0.3)

    # Step 4: Re-evaluate — should be unblocked
    step_banner(4, 4, t("stage5.step4"))
    time.sleep(0.3)
    result2 = evaluate_meta_andon(
        artifacts_dir=artifacts_dir,
        consecutive_failures=3,
        failure_run_ids=failure_ids,
    )
    ok(t("stage5.eval_unblocked", blocked=result2["blocked"]))
    info(t("stage5.artifacts_dir", path=str(artifacts_dir)))

    return {"first": result, "second": result2, "artifacts_dir": str(artifacts_dir)}


def explain_meta_andon_after(result: dict[str, Any]) -> None:
    narrator_block(
        f"\U0001f50d {t('stage5.after_title')}",
        t("stage5.after"),
    )


def _create_demo_artifacts(artifacts_dir: Path) -> None:
    """Create sample meta-andon artifacts for the demo."""
    five_whys = """\
# Pattern Five Whys

## Why 1
Why do failures occur at different phases each time?
→ Each fix addresses a local symptom, not the structural root cause.

## Why 2
Why are fixes local rather than structural?
→ The agent tackles the immediate error without surveying other phases.

## Why 3
Why doesn't the agent survey other phases?
→ No rule forces a horizontal sweep before re-running.

## Why 4
Why is there no horizontal sweep rule?
→ The process assumed each failure is independent.

## Why 5
Why was that assumed?
→ Lack of pattern tracking across runs. Meta-ANDON now addresses this.
"""

    risk_table = """\
# Risk Table

| Phase | Risk? | Evidence | Action |
|-------|-------|----------|--------|
| 1a    | None  | —        | —      |
| 2a    | Yes   | Schema mismatch with Phase 1 output | Fix schema mapping |
| 2b    | Yes   | Build flag contradicts gate condition | Add exception |
| 3     | TBD   | No test path for xcodebuild | Add xcodeproj support |
| 4     | None  | —        | —      |
"""

    sweep = """\
# Horizontal Sweep Report

| Phase | Risk? | Evidence | Action |
|-------|-------|----------|--------|
| 1a    | No    | —        | —      |
| 1b    | Yes   | Same schema branching as quick_actions | Fixed |
| 2a    | TBD   | output_markers unverified | Desk check pending |
| 2b    | No    | —        | —      |
"""

    batch_plan = """\
# Batch Fix Plan

## Objective
Fix all structural issues discovered during desk walk-through
to prevent recurring whack-a-mole failures.

## Changes
1. Fix schema mapping between Phase 1 output and Phase 2a input
2. Add compile-only exception to Phase 2b gate
3. Add xcodeproj support for Phase 3 test path
4. Align output_markers across all phase gates

## Verification
- Run full pipeline end-to-end after all fixes
- Verify each phase gate passes with correct artifacts
- Confirm no regressions in previously passing phases
"""

    files = {
        "meta-andon-five-whys.md": five_whys,
        "meta-andon-risk-table.md": risk_table,
        "horizontal-sweep-report.md": sweep,
        "meta-andon-batch-fix-plan.md": batch_plan,
    }
    for name, content in files.items():
        (artifacts_dir / name).write_text(content, encoding="utf-8")
        time.sleep(0.15)
        info(f"  \u2714 {name}")
