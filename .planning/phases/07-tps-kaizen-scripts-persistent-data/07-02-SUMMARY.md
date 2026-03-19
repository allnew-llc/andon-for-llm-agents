---
phase: 07-tps-kaizen-scripts-persistent-data
plan: "02"
subsystem: tps-kaizen
tags: [validation, bash-script, skill-update, five-whys, incident-history]
dependency_graph:
  requires: []
  provides:
    - skills/tps-kaizen/scripts/five-whys-validator.sh
    - "SKILL.md andon Step 0: Check Incident History"
  affects:
    - skills/tps-kaizen/SKILL.md
tech_stack:
  added:
    - bash (POSIX-compatible validator script, bash 3.2+)
  patterns:
    - "Two-format detection (table vs expanded) with shared validation logic"
    - "Placeholder pattern matching for empty verification detection"
    - "Human error stop heuristic via keyword scan of final Why"
key_files:
  created:
    - skills/tps-kaizen/scripts/five-whys-validator.sh
  modified:
    - skills/tps-kaizen/SKILL.md
decisions:
  - "Used POSIX tools only (grep/sed/awk) for bash 3.2+ compatibility — no jq or python dependency"
  - "Human error stop check is a warning (not failure) — user decides if stopping early is justified"
  - "Version number stays at 1.1.0 — Step 0 is a documentation enhancement, not a new version"
  - "Step 0 inserted before Step 1 in andon cycle; existing steps 1-4 unchanged"
metrics:
  duration_minutes: 3
  completed_date: "2026-03-19"
  tasks_completed: 2
  files_changed: 2
---

# Phase 07 Plan 02: Five Whys Validator and Incident History Auto-Reference Summary

**One-liner**: Bash validator for Five Whys document completeness (depth + verification columns) plus andon workflow Step 0 that surfaces recurring incident patterns from persistent storage before starting analysis.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create five-whys-validator.sh | a2a9d9b | skills/tps-kaizen/scripts/five-whys-validator.sh |
| 2 | Update SKILL.md andon subcommand for incident history | 2e7cab9 | skills/tps-kaizen/SKILL.md |

## What Was Built

### Task 1: five-whys-validator.sh

An executable bash script (359 lines, POSIX-only) that validates Five Whys documents for mechanical completeness:

- **Input**: file path argument or stdin; `--help` prints usage and exits 0
- **Format detection**: Distinguishes table format (`| # | Why? | Verification |` rows) from expanded format (`### Why N:` sections with `**Verification**:` lines)
- **Depth check**: Counts causal levels; PASS if >= 5, FAIL if < 5
- **Verification check**: For each level, flags empty content, whitespace-only, or known placeholders (`[file/command checked]`, `TBD`, `TODO`, `N/A`, bracket-wrapped text)
- **Human error stop warning**: Scans final Why for phrases like "human error", "I made a mistake", "forgot to" — emits WARNING but does not fail (user judgment required)
- **Exit codes**: 0=PASS, 1=FAIL, 2=usage error

### Task 2: SKILL.md Step 0 insertion

Added `### Step 0: Check Incident History` before the existing Step 1 in the `andon` subcommand section:

- Instructs Claude to scan `${CLAUDE_PLUGIN_DATA}/kaizen/incidents/` (or `~/.claude/state/kaizen/incidents/` fallback) before beginning analysis
- Describes matching current error against `cause_id` and `category` fields in past `analysis.json` files
- Defines the output format for surfacing matches with confidence scores
- References `aggregate-incidents.sh` as a pattern summary tool
- Updated cycle description from "Jidoka 4-step cycle" to "Jidoka cycle (Step 0 + 4 steps)"
- Version stays at 1.1.0 (documentation enhancement within minor version)

## Verification Results

| Check | Result |
|-------|--------|
| Script exists and is executable | PASS |
| `--help` exits 0 | PASS |
| Complete table-format document → exit 0 | PASS |
| Incomplete document (depth < 5, empty verifications) → exit 1 | PASS |
| Complete expanded-format document → exit 0 | PASS |
| Human error stop warning triggered correctly | PASS |
| SKILL.md contains "Step 0: Check Incident History" | PASS (count: 1) |
| SKILL.md references CLAUDE_PLUGIN_DATA | PASS (count: 1) |
| All existing ## headers preserved (13 headers) | PASS |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

| Item | Status |
|------|--------|
| skills/tps-kaizen/scripts/five-whys-validator.sh | FOUND |
| .planning/phases/07-tps-kaizen-scripts-persistent-data/07-02-SUMMARY.md | FOUND |
| commit a2a9d9b (five-whys-validator.sh) | FOUND |
| commit 2e7cab9 (SKILL.md Step 0) | FOUND |
