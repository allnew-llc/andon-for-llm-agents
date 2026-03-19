---
phase: 14-analysis-metrics-skill-integration
plan: "01"
subsystem: analytics
tags: [bash, gotcha-registry, metrics, kaizen, posix-shell]

# Dependency graph
requires:
  - phase: 11-gotchas-registry
    provides: gotchas/*.yaml YAML registry with pattern, id, name, discovered fields
  - phase: 12-andon-auto-surfacing
    provides: gotcha_surfacer.py keyword matching algorithm (40% PARTIAL threshold)

provides:
  - POSIX-only bash script computing per-Gotcha hit rates from incident output_snippets
  - Stale Gotcha detection (zero-hit Gotchas flagged POTENTIALLY STALE)
  - Prevention effectiveness heuristic (avg resolution time with vs. without match)

affects:
  - 14-02-SKILL-integration (SKILL.md references gotcha-stats.sh in analysis workflow)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "extract_yaml_value() for block scalar (>) YAML fields via awk state machine"
    - "Cross-platform ISO-to-epoch conversion (GNU date -d / BSD date -j fallback)"
    - "Significant-keyword extraction in bash mirroring Python _significant_words()"
    - "Parallel arrays via line-indexed temp files (same pattern as aggregate-incidents.sh)"

key-files:
  created:
    - skills/tps-kaizen/scripts/gotcha-stats.sh
  modified: []

key-decisions:
  - "CLAUDE_PLUGIN_DATA takes priority over ANDON_STATE_DIR for incidents dir — matches existing hook convention"
  - "PARTIAL match threshold is 40%+ keyword overlap (identical to gotcha_surfacer.py) to ensure consistent hit counting"
  - "Script uses grep -w for whole-word keyword matching (bash-portable alternative to Python re word boundary)"
  - "format_duration() helper formats seconds as human-readable (Xmin, Xh Ymin) for readability"

patterns-established:
  - "extract_yaml_value(): awk state machine handles both inline (key: value) and block scalar (key: >) YAML"
  - "significant_words(): bash pipeline reproducing Python _significant_words() — tr lowercase, awk token split, stopword filter"

requirements-completed: [METRIC-01, METRIC-02, METRIC-03]

# Metrics
duration: 4min
completed: 2026-03-20
---

# Phase 14 Plan 01: Analysis Metrics Skill Integration Summary

**POSIX-only bash script (`gotcha-stats.sh`) reporting per-Gotcha hit rates, staleness flags, and resolution-time effectiveness using the same 40%-keyword-threshold algorithm as `gotcha_surfacer.py`**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-20T06:16:11Z
- **Completed:** 2026-03-20T06:19:52Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Delivered `gotcha-stats.sh` (727 lines) meeting all three metric requirements (METRIC-01 hit rate, METRIC-02 staleness, METRIC-03 effectiveness)
- Implemented `extract_yaml_value()` — an awk state machine parsing YAML block scalar (`>`) multi-line pattern fields without any external YAML parser
- Synthetic test data verification confirmed GOTCHA-001 hit counting, stale detection for zero-hit Gotchas, and prevention effectiveness delta (50% faster for Gotcha-matched incidents in test scenario)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create gotcha-stats.sh** - `d254782` (feat)
2. **Task 2: Verify with synthetic test data** - `15cd579` (test)

## Files Created/Modified

- `skills/tps-kaizen/scripts/gotcha-stats.sh` — Executable POSIX bash script: loads Gotcha registry from YAML, scans incident `output_snippet` fields, counts hits per Gotcha using 40%+ keyword threshold, flags zero-hit Gotchas as potentially stale, computes avg resolution time split by Gotcha-match status

## Decisions Made

- CLAUDE_PLUGIN_DATA takes priority over ANDON_STATE_DIR (matches existing hook convention from aggregate-incidents.sh)
- 40%+ keyword overlap threshold is identical to `gotcha_surfacer.py` PARTIAL match to ensure consistent hit counting between live surfacing and retrospective stats
- Whole-word matching via `grep -w` (bash-portable equivalent of Python `re.search(r"\b...\b", ...)`)
- GOTCHA-004 test incident included explicit "gate-gaming" keyword to ensure reliable keyword overlap — natural language proximity to the YAML pattern is sufficient for 40%+ hit

## Deviations from Plan

None — plan executed exactly as written. The `CLAUDE_PLUGIN_DATA` environment variable priority order was already documented in the plan's interface spec. Test used `CLAUDE_PLUGIN_DATA` directly (rather than `ANDON_STATE_DIR`) to override the hook-injected value — this is the correct approach per script design.

## Issues Encountered

During Task 2 first run, the test used `ANDON_STATE_DIR` but `CLAUDE_PLUGIN_DATA` was set in the shell environment from the hook system, causing the script to read the live data directory instead of the test temp dir. Fixed immediately by switching the test to set `CLAUDE_PLUGIN_DATA` instead — this is the correct env var when the hook environment is active.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `gotcha-stats.sh` is ready for SKILL.md documentation integration (14-02)
- Script is executable and passes syntax check; can be run immediately by any user with access to the repo and incident data
- Requires `git` in PATH for auto-detection of Gotcha registry location (or explicit `GOTCHA_DIR` env var)

---
*Phase: 14-analysis-metrics-skill-integration*
*Completed: 2026-03-20*
