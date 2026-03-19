---
phase: 07-tps-kaizen-scripts-persistent-data
plan: 01
subsystem: tooling
tags: [bash, tps-kaizen, incident-analysis, quality-trend, kaizen, shell-scripts]

# Dependency graph
requires:
  - phase: 06-tps-kaizen-core-quality
    provides: SKILL.md with trigger descriptions, incident/QC data format contracts
provides:
  - "skills/tps-kaizen/scripts/aggregate-incidents.sh — CLI tool that clusters past incidents by cause_id with occurrence counts and recurring pattern detection"
  - "skills/tps-kaizen/scripts/quality-trend.sh — CLI tool that outputs time-series quality self-assessment table with improving/stable/degrading trend detection"
affects:
  - 07-tps-kaizen-scripts-persistent-data (subsequent plans using same scripts dir)
  - any phase that reads kaizen incident/QC data for decision-making

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "awk gsub for global pattern counting in compact single-line JSON (no jq)"
    - "CLAUDE_PLUGIN_DATA → ANDON_STATE_DIR fallback env var resolution pattern"
    - "grep exit-1 suppression via awk instead of grep|wc pipeline to avoid set -e abort"

key-files:
  created:
    - skills/tps-kaizen/scripts/aggregate-incidents.sh
    - skills/tps-kaizen/scripts/quality-trend.sh
  modified: []

key-decisions:
  - "Use awk gsub for global pattern counting on compact JSON — grep -o|wc -l fails silently under set -euo pipefail when grep returns exit 1 with no matches"
  - "awk for JSON key extraction (not grep|sed chain) — single key extraction from compact single-line JSON requires matching from key to next quote boundary, which awk handles cleanly"
  - "macOS stat -f '%Sm' -t '%Y-%m-%d' for file mtime fallback — GNU ls --time-style is not available on macOS"

patterns-established:
  - "Bash script portability: bash 3.2+, POSIX tools only (awk/sed/sort/find/tr/wc), no jq/python"
  - "Script structure: shebang + set -euo pipefail + Apache 2.0 header + usage comment + --help flag"
  - "Data dir resolution: CLAUDE_PLUGIN_DATA first, then ANDON_STATE_DIR fallback, print resolved path to stderr"

requirements-completed: [SKILL-03, SKILL-05]

# Metrics
duration: 5min
completed: 2026-03-19
---

# Phase 07 Plan 01: TPS Kaizen Analysis Scripts Summary

**Two portable bash CLI tools for surfacing historical incident patterns and quality trends from kaizen persistent data stores, using only awk/sed/sort with no jq/python dependency.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-19T07:27:05Z
- **Completed:** 2026-03-19T07:32:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Created `aggregate-incidents.sh` — reads `analysis.json` from INC-* directories, groups incidents by `cause_id`, separates recurring patterns (2+ occurrences) from single occurrences, with period and count summary
- Created `quality-trend.sh` — reads `quality-self-assessment-*.json` files, outputs a time-series table (Date | Phase | Overall | Pass | Warn | Fail) and detects trend direction (improving/stable/degrading) by comparing last 3 assessments
- Both scripts resolve data directories via `CLAUDE_PLUGIN_DATA` with `ANDON_STATE_DIR` fallback, handle missing data gracefully (exit 0), and support `--help`

## Task Commits

Each task was committed atomically:

1. **Task 1: Create aggregate-incidents.sh** - `41e635e` (feat)
2. **Task 2: Create quality-trend.sh** - `31c74c1` (feat)

## Files Created/Modified

- `skills/tps-kaizen/scripts/aggregate-incidents.sh` - Incident aggregation and pattern clustering script
- `skills/tps-kaizen/scripts/quality-trend.sh` - Quality self-assessment trend timeline script

## Decisions Made

- Used `awk gsub` for global pattern counting rather than `grep -o | wc -l` — the grep pipeline propagates exit code 1 (no match) through the pipeline under `set -euo pipefail`, silently aborting the script when a status value has zero occurrences
- Used `awk` with string matching for JSON key extraction rather than chained `grep|sed` — awk can find and strip prefix/suffix within a single-line JSON record cleanly; the sed approach struggled with compact multi-key lines
- Used macOS `stat -f "%Sm" -t "%Y-%m-%d"` for file mtime fallback (with GNU `stat --format` as secondary fallback) — GNU `ls --time-style` is not available on macOS

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed JSON extraction via grep/sed chain producing garbage output on compact JSON**
- **Found during:** Task 1 (aggregate-incidents.sh)
- **Issue:** Initial `grep -m1 "key" | sed` chain matched the entire JSON line and failed to isolate the target value when JSON was compact single-line format
- **Fix:** Replaced with `awk` using `match()` to find the key pattern, then `sub()` to strip prefix and trailing quote
- **Files modified:** skills/tps-kaizen/scripts/aggregate-incidents.sh
- **Verification:** Test with 3 sample incidents confirmed CAUSE-001 shows 2 occurrences in recurring section, CAUSE-002 in single occurrences
- **Committed in:** 41e635e (Task 1 commit)

**2. [Rule 1 - Bug] Fixed grep exit-1 aborting script under set -euo pipefail in quality-trend.sh**
- **Found during:** Task 2 (quality-trend.sh)
- **Issue:** `grep -o "status":"warn" file | wc -l | tr -d ' ' || echo "0"` — when grep found no matches, it exited 1, causing `set -e` to abort the script silently mid-execution; additionally `|| echo "0"` also caused duplicate output (wc already printed 0)
- **Fix:** Replaced `grep|wc -l` pattern with `awk gsub` which returns the global substitution count and always exits 0
- **Files modified:** skills/tps-kaizen/scripts/quality-trend.sh
- **Verification:** Test with phase-1 (1 pass, 0 warn, 2 fail) confirmed correct counts; all 3 assessments shown with proper trend "improving"
- **Committed in:** 31c74c1 (Task 2 commit)

**3. [Rule 1 - Bug] Fixed macOS-incompatible date extraction fallback**
- **Found during:** Task 2 (quality-trend.sh)
- **Issue:** `ls -l --time-style=+%Y-%m-%d` is GNU-only; on macOS it silently produces unexpected output injecting empty or malformed rows into the report
- **Fix:** Replaced with `stat -f "%Sm" -t "%Y-%m-%d"` (macOS) with `stat --format="%y"` (GNU) as secondary fallback
- **Files modified:** skills/tps-kaizen/scripts/quality-trend.sh
- **Verification:** No spurious rows in output on macOS
- **Committed in:** 31c74c1 (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (all Rule 1 — bugs in initial implementation)
**Impact on plan:** All fixes necessary for correct output on compact single-line JSON and macOS portability. No scope creep.

## Issues Encountered

- `grep|wc -l` pattern for counting is fragile under `set -euo pipefail` when the pattern may have zero matches — this is a recurring bash scripting trap documented in project patterns.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both scripts ready for use by any user with kaizen incident/QC data in place
- Phase 07-02 (five-whys-validator and andon incident history) is already committed and may depend on or complement these scripts
- Requirement SKILL-03 (incident aggregation) and SKILL-05 (quality trend) are complete

---
*Phase: 07-tps-kaizen-scripts-persistent-data*
*Completed: 2026-03-19*
