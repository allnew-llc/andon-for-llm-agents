---
phase: 10-new-skills-on-demand-hooks
plan: "01"
subsystem: skills
tags: [freee, accounting, mcp, standup, git, daily-summary, instruction-skill]
dependency_graph:
  requires: []
  provides:
    - skills/freee-analysis/SKILL.md
    - skills/standup/SKILL.md
    - skills/standup/scripts/standup.sh
  affects: []
tech_stack:
  added:
    - freee MCP tool orchestration pattern (instruction-only skill)
    - standup.sh POSIX bash script with BSD/GNU date portability
  patterns:
    - Instruction skill pattern (no scripts, orchestrates external MCP tools)
    - SKILL.md trigger table + Behavior steps + named Gotchas
    - Apache 2.0 header + set -euo pipefail + --help flag script pattern
key_files:
  created:
    - skills/freee-analysis/SKILL.md
    - skills/standup/SKILL.md
    - skills/standup/scripts/standup.sh
  modified: []
decisions:
  - "freee-analysis is an instruction-only skill: no scripts, no references/ subdirectory — all content fits in SKILL.md"
  - "standup.sh uses awk section-range pattern to extract STATE.md fields: '/^## Section$/{found=1;next} found && /^## /{exit} found{print}' — avoids the trap where the heading itself matches the stop pattern"
  - "standup.sh accepts 'week' shorthand and strips trailing 'h' suffix for convenience (48h = 48)"
  - "Shallow clone detection uses git rev-parse --is-shallow-repository with fallback to 'false' for older git versions"
metrics:
  duration_seconds: 258
  completed_date: "2026-03-19"
  tasks_completed: 2
  files_created: 3
---

# Phase 10 Plan 01: New Instruction Skills (freee-analysis, standup) Summary

Two new instruction-focused skills added to the andon skill ecosystem: freee-analysis orchestrates freee MCP tools for accounting data analysis, and standup aggregates git log plus GSD STATE.md into a formatted daily standup report via standup.sh.

---

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create freee-analysis SKILL.md | 043b8f0 | skills/freee-analysis/SKILL.md |
| 2 | Create standup SKILL.md and standup.sh | 1af11cf | skills/standup/SKILL.md, skills/standup/scripts/standup.sh |

---

## What Was Built

### freee-analysis (skills/freee-analysis/SKILL.md)

Instruction skill for fetching and analyzing freee accounting data via the `freee-mcp` MCP server. 176 lines.

Key sections:
- Trigger table: 6 scenarios (financial analysis, monthly close, expense audit, revenue tracking, tax prep, journal analysis)
- Behavior: 5-step MCP workflow — company context first, then targeted tool calls, analysis, and structured markdown output
- Available MCP Tools: 4 categories (account, journal/transaction, report, partner/tax) with `freee_*` tool name references
- Analysis Patterns: 4 common workflows (P&L comparison, expense breakdown, trial balance verification, revenue trend)
- 5 named Gotchas: Company ID Requirement, Fiscal Year Boundaries, Rate Limiting, Data Freshness, Read vs. Write Operations

### standup (skills/standup/SKILL.md + skills/standup/scripts/standup.sh)

SKILL.md: 75 lines. Instruction skill for daily standup summary generation. References `scripts/standup.sh` for data collection.

standup.sh: 157 lines. Bash script that:
- Accepts `<hours>`, `<hours>h`, or `week` (168h) argument
- Detects shallow clones and warns
- Computes `--since` with BSD/GNU date portability
- Extracts `Phase:`, `Plan:`, `Status:` from STATE.md via section-aware awk
- Extracts `Blockers/Concerns` section from STATE.md
- Finds first `[ ]` checkbox in ROADMAP.md as "Next Up"
- Handles edge cases: not-a-git-repo, no commits found, no STATE.md, no ROADMAP.md

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed awk range pattern for STATE.md section extraction**

- **Found during:** Task 2 — testing standup.sh output
- **Issue:** Initial awk range `/^## Current Position/,/^## /` stopped at the same line because the heading `## Current Position` itself matches the stop pattern `^## `. This produced empty output for Position/Plan/Status fields.
- **Fix:** Changed to explicit section-skip awk pattern: `'/^## Current Position$/{found=1;next} found && /^## /{exit} found{print}'` — skips the heading line, then prints until the next heading.
- **Files modified:** skills/standup/scripts/standup.sh
- **Commit:** 1af11cf (included in task commit — fix applied before committing)

---

## Verification Results

All checks passed:

```
ls skills/freee-analysis/SKILL.md skills/standup/SKILL.md skills/standup/scripts/standup.sh  → all 3 exist
head -3 skills/freee-analysis/SKILL.md  → name: freee-analysis
head -3 skills/standup/SKILL.md         → name: standup
bash -n skills/standup/scripts/standup.sh  → syntax valid
grep -c "###" skills/freee-analysis/SKILL.md  → 18 (≥ 3)
grep -c "###" skills/standup/SKILL.md         → 10 (≥ 3)
grep "freee_" skills/freee-analysis/SKILL.md  → 20 matches
grep "scripts/standup.sh" skills/standup/SKILL.md  → present
wc -l skills/freee-analysis/SKILL.md  → 176 (≥ 60)
wc -l skills/standup/SKILL.md        → 75 (≥ 50)
```

Live script test — standup.sh correctly extracted:
```
Phase: 6 of 10 (tps-kaizen Core Quality)
Plan: - of - in current phase
Status: Ready to plan
Blockers: None
```

---

## Self-Check: PASSED
