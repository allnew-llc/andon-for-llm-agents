---
phase: 12-andon-auto-surfacing
verified: 2026-03-20T00:00:00Z
status: passed
score: 4/4 must-haves verified
re_verification: null
gaps: []
human_verification: []
---

# Phase 12: ANDON Auto-Surfacing Verification Report

**Phase Goal:** When ANDON opens, matching Gotchas are automatically surfaced with confidence scores so Claude can avoid repeating known failures
**Verified:** 2026-03-20
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | ANDON open with a known error pattern surfaces at least one matching Gotcha with prevention advice in additionalContext | VERIFIED | `tps-kaizen-runtime.py:391-402` calls `surface_gotchas(merged_output, ...)` after writing `andon_state`; result appended to Level 2/3/4 messages before `print_hook_context()`. Smoke test confirms real GOTCHA-002 matched. |
| 2 | Match results include a confidence label (exact, partial, or category) so the user can judge relevance | VERIFIED | `ConfidenceLevel` enum (`EXACT`/`PARTIAL`/`CATEGORY`) in `gotcha_surfacer.py:121-126`; `format_surfaced_gotchas` outputs `(exact, score=1.0)` etc. in each line. All 3 label types tested and passing. |
| 3 | Multiple Gotcha matches are ranked by relevance score with highest-confidence match first | VERIFIED | `match_gotchas` returns `results.sort(key=lambda r: r.score, reverse=True)` at line 270. `test_multiple_matches_ranked_descending` and manual ranking verification both pass. |
| 4 | ANDON open with no matching pattern produces no spurious Gotcha output | VERIFIED | `format_surfaced_gotchas([])` returns `""` (line 289); `if gotcha_context:` guard at lines 414/429/456 prevents injection of empty string. No-match test and manual verification confirm clean output. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `hooks/gotcha_surfacer.py` | Pattern matching, confidence scoring, ranking, and additionalContext formatting | VERIFIED | 335 lines. Exports `surface_gotchas`, `match_gotchas`, `format_surfaced_gotchas`, `MatchResult`, `ConfidenceLevel`. Ruff clean. |
| `tests/test_gotcha_surfacer.py` | TDD tests covering exact, partial, category, no-match, ranking, formatting, empty registry, integration | VERIFIED | 305 lines, 12 tests. All 12 pass. Covers all 8 required behaviors plus format-empty, smoke test variants. |
| `hooks/tps-kaizen-runtime.py` | `open_from_payload()` calls `surface_gotchas` and appends result to ANDON message | VERIFIED | `_init_surfacer()` + lazy loader pattern added. `gotcha_context` computed from `merged_output` and appended to Level 2/3/4 messages. |
| `hooks/tps-andon-posttool-guard.sh` | Shell hook merges surfacer output into additionalContext | VERIFIED | No changes needed — surfacer output is already embedded in `ANDON_OUTPUT` via `print_hook_context()`. The existing Python merge at line 107-113 picks it up automatically. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `hooks/gotcha_surfacer.py` | `hooks/gotcha_registry.py` | `from gotcha_registry import GotchaEntry, GotchaValidationError, load_gotchas` | WIRED | Line 35 of `gotcha_surfacer.py`. Confirmed: import exists and used in `surface_gotchas()`. |
| `hooks/tps-kaizen-runtime.py` | `hooks/gotcha_surfacer.py` | `from gotcha_surfacer import surface_gotchas` (lazy, in `_init_surfacer`) | WIRED | Lines 113-124: lazy loader imports `surface_gotchas as _sf`; called at line 392 during `open_from_payload()`. |
| `hooks/gotcha_surfacer.py` | `hooks/kaizen_core.py` | `from kaizen_core import WORKSPACE` | WIRED (via runtime) | `WORKSPACE` is imported in `tps-kaizen-runtime.py` line 46 and used to resolve `gotchas_dir` and `packs_dir` at lines 396-397. `gotcha_surfacer.py` itself does not import `kaizen_core`; paths are resolved by the caller (correct design). |

Note on key link 3: The PLAN specified `from kaizen_core import WORKSPACE` in `gotcha_surfacer.py`, but the implementation correctly resolves paths in the caller (`tps-kaizen-runtime.py`) and passes them as arguments to `surface_gotchas()`. This is a better design (testable without workspace) and `WORKSPACE` is fully wired in the calling module.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| SURF-01 | 12-01-PLAN.md | ANDON open hook auto-loads Gotchas Registry and matches current error against pattern fields | SATISFIED | `_init_surfacer()` loads registry via `surface_gotchas -> load_gotchas` on every ANDON open |
| SURF-02 | 12-01-PLAN.md | Matching Gotchas are injected into additionalContext with prevention advice when ANDON opens | SATISFIED | `gotcha_context` appended to `message` before `print_hook_context()` for L2/L3/L4 |
| SURF-03 | 12-01-PLAN.md | Match results include confidence score (exact match, partial match, category match) | SATISFIED | `ConfidenceLevel` enum with 3 tiers; `format_surfaced_gotchas` includes label and numeric score |
| SURF-04 | 12-01-PLAN.md | Multiple Gotcha matches are ranked by relevance and presented in order | SATISFIED | `results.sort(key=lambda r: r.score, reverse=True)` in `match_gotchas()`; verified by test and manual check |

No orphaned requirements for Phase 12. SURF-01 through SURF-04 are the only requirements mapped to this phase in REQUIREMENTS.md.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `hooks/tps-kaizen-runtime.py` | 35 | `get_action_level` imported but unused (F401) | Info | Pre-existing issue noted in SUMMARY.md as deferred. Not introduced by Phase 12. Ruff reports it, but it pre-dates this phase. |

No blockers or warnings in the two new files (`gotcha_surfacer.py` and `test_gotcha_surfacer.py` both pass ruff clean).

### Human Verification Required

None. All success criteria are verifiable programmatically and were verified.

### Test Results

| Check | Result |
|-------|--------|
| `pytest tests/test_gotcha_surfacer.py -v` (PYTHONPATH=hooks) | 12/12 passed |
| `pytest tests/ -v` full regression (PYTHONPATH=hooks) | 201/201 passed |
| `ruff check hooks/gotcha_surfacer.py tests/test_gotcha_surfacer.py` | Clean |
| Import chain: `from gotcha_surfacer import surface_gotchas, MatchResult, ConfidenceLevel` | OK |
| Smoke test (real gotchas dir, gate-gaming tag match) | PASSED — GOTCHA-002 matched |
| No-match guard (non-matching error produces empty string) | PASSED |
| Ranking order (exact > partial > category by score) | PASSED |
| Commits `cfb9409`, `79d9325`, `a06c58e` in git history | VERIFIED |

### Gaps Summary

No gaps. All four observable truths are verified, all required artifacts exist and are substantive and wired, all four requirements are satisfied, and no blocking anti-patterns were found.

---

_Verified: 2026-03-20_
_Verifier: Claude (gsd-verifier)_
