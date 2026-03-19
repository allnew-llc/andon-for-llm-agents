---
phase: 08-qc-audit-skill
plan: "02"
subsystem: qc-audit
tags: [bash, scripts, quality-trend, gate-health, data-collection, POSIX]
dependency_graph:
  requires: ["08-01"]
  provides: ["skills/qc-audit/scripts/trend.sh", "skills/qc-audit/scripts/gate-health.sh", "skills/qc-audit/scripts/collect-assessments.sh"]
  affects: ["skills/qc-audit/SKILL.md"]
tech_stack:
  added: []
  patterns: ["bash-3.2-portable", "awk-json-extraction", "POSIX-only-scripts", "macOS-stat-mtime"]
key_files:
  created:
    - skills/qc-audit/scripts/trend.sh
    - skills/qc-audit/scripts/gate-health.sh
    - skills/qc-audit/scripts/collect-assessments.sh
  modified: []
decisions:
  - "trend.sh is the qc-audit-owned canonical quality trend tool, distinct from tps-kaizen/scripts/quality-trend.sh, adding percentage rate summary and ASCII bar charts"
  - "gate-health.sh treats WARN as non-PASS for quality side — any non-PASS status maps to the WARN/FAIL quadrant to maintain strict quality-gate correlation semantics"
  - "collect-assessments.sh requires CLAUDE_PLUGIN_DATA (exits 1 if unset) — writing to central store is always intentional, unlike read-only scripts that gracefully fall back"
metrics:
  duration_minutes: 3
  completed_date: "2026-03-19"
  tasks_completed: 3
  files_created: 3
---

# Phase 08 Plan 02: QC Audit Scripts Summary

Three portable bash scripts providing quality trend analysis, gate-health correlation, and assessment aggregation for the /qc-audit skill central data store.

## What Was Built

### skills/qc-audit/scripts/trend.sh (307 lines)

Quality trend timeline report reading from `${CLAUDE_PLUGIN_DATA}/qc/` with `docs/pipeline/` fallback.

- Time-series table: Date | Phase | Overall | Pass | Warn | Fail counts
- Trend direction detection (improving/stable/degrading) based on last 3 assessments
- Aggregate rate summary: PASS/WARN/FAIL percentages across all criteria
- Per-phase ASCII bar charts using `#` (pass), `~` (warn), `!` (fail)
- Handles missing directory gracefully: prints "No quality assessment data found" and exits 0

### skills/qc-audit/scripts/gate-health.sh (297 lines)

Quality score vs gate pass rate correlation analysis with four-quadrant diagnosis.

- Joins quality self-assessments and gate results on `phase_id`
- Four-quadrant classification: Healthy / Gate Misaligned / Gate Too Lenient / Correctly Caught
- Correlation matrix (2x2: Quality PASS/WARN-FAIL x Gate PASS/FAIL)
- Health score: N/M phases healthy with percentage
- When no gate-result-*.json files exist: prints helpful tip and exits 0 (expected for most projects)

### skills/qc-audit/scripts/collect-assessments.sh (194 lines)

Aggregation script that copies `docs/pipeline/quality-self-assessment-*.json` from project directories into the central `${CLAUDE_PLUGIN_DATA}/qc/` store.

- Accepts zero or more PROJECT_DIR arguments (defaults to cwd)
- Requires CLAUDE_PLUGIN_DATA (exits 1 with clear error if unset)
- File mtime comparison: skips files already up-to-date in central store (macOS `stat -f '%m'` / GNU stat fallback)
- Per-file [collected]/[skipped] reporting with project-relative paths
- Summary line: "Collected N assessments from M project(s), skipped K"

## All Scripts Follow Phase 7 Portability Patterns

- Apache 2.0 license header (exact format from aggregate-incidents.sh)
- `set -euo pipefail`
- `usage()` function with `--help` / `-h` flag handling
- CLAUDE_PLUGIN_DATA env var resolution with fallback (or required + exit 1 for write operations)
- `extract_json_str()` helper using awk (no jq)
- `count_status()` helper using awk gsub (no grep|wc -l pipeline)
- macOS `stat -f '%Sm'` / `stat -f '%m'` with GNU stat fallback
- POSIX tools only: awk, sed, sort, find, cp

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | a44e715 | feat(08-02): create trend.sh quality trend timeline script |
| Task 2 | d2e98d8 | feat(08-02): create gate-health.sh quality-gate correlation analysis script |
| Task 3 | dcf82e9 | feat(08-02): create collect-assessments.sh aggregation script for central QC store |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

Files created:
- [x] skills/qc-audit/scripts/trend.sh exists and is executable
- [x] skills/qc-audit/scripts/gate-health.sh exists and is executable
- [x] skills/qc-audit/scripts/collect-assessments.sh exists and is executable

Line count minimums met:
- [x] trend.sh: 307 lines (>= 80)
- [x] gate-health.sh: 297 lines (>= 80)
- [x] collect-assessments.sh: 194 lines (>= 60)

Must-have truths verified:
- [x] trend.sh reads from ${CLAUDE_PLUGIN_DATA}/qc/ — confirmed via CLAUDE_PLUGIN_DATA env var resolution
- [x] gate-health.sh reads quality and gate data and shows correlation — four-quadrant diagnosis table implemented
- [x] collect-assessments.sh aggregates JSONs from project dirs to central store — copy with mtime-based duplicate detection
- [x] All scripts portable bash 3.2+ POSIX tools only — awk/sed/sort/find, no jq/python
- [x] All scripts support --help and handle missing data gracefully — exit 0 verified

Key links verified:
- [x] trend.sh contains CLAUDE_PLUGIN_DATA.*qc pattern
- [x] collect-assessments.sh contains CLAUDE_PLUGIN_DATA.*qc pattern
- [x] SKILL.md references scripts/trend.sh (pre-existing from Plan 08-01)

## Self-Check: PASSED
