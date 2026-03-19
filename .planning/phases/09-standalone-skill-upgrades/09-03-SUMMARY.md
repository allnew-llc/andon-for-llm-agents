---
phase: 09-standalone-skill-upgrades
plan: 03
subsystem: skill-documentation
tags: [apple-developer-docs, apple-review-guidelines, skill-upgrade, directory-structure, progressive-disclosure, ios-development, swiftui, swiftdata, storekit, healthkit, xctest, concurrency]

# Dependency graph
requires:
  - "06-tps-kaizen-core-quality (SKILL.md pattern established)"
provides:
  - "apple-developer-docs/ directory-based skill with 6 framework reference files"
  - "apple-review-guidelines/ directory-based skill with section details and rejection checklist"
affects: [ios-development, apple-developer-docs, apple-review-guidelines]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Progressive disclosure via references/ subdirectory for large skills (514-line and 233-line files)"
    - "Framework Index table pattern for multi-framework documentation"
    - "Trigger-focused description format: 'Use when: <specific triggers>'"

key-files:
  created:
    - ~/.claude/skills/apple-developer-docs/SKILL.md
    - ~/.claude/skills/apple-developer-docs/references/swiftui.md
    - ~/.claude/skills/apple-developer-docs/references/swiftdata.md
    - ~/.claude/skills/apple-developer-docs/references/storekit.md
    - ~/.claude/skills/apple-developer-docs/references/healthkit.md
    - ~/.claude/skills/apple-developer-docs/references/testing.md
    - ~/.claude/skills/apple-developer-docs/references/concurrency.md
    - ~/.claude/skills/apple-review-guidelines/SKILL.md
    - ~/.claude/skills/apple-review-guidelines/references/section-details.md
    - ~/.claude/skills/apple-review-guidelines/references/rejection-checklist.md
  modified: []

key-decisions:
  - "Framework Index table pattern for apple-developer-docs: each framework gets its own reference file, SKILL.md is lightweight entry point (~80 lines vs 514 lines)"
  - "Top 10 Rejection Causes table stays in apple-review-guidelines SKILL.md (highest-value quick-lookup content), full section details and checklist moved to references/"
  - "Quick Compliance Check condensed to 10 items in SKILL.md — complete checklist in references/rejection-checklist.md"
  - "Info.plist settings placed in references/concurrency.md alongside Swift 6 concurrency (both relate to app configuration and are commonly needed together)"

patterns-established:
  - "Framework Index table: | Framework | Use For | Reference | pointing to references/ files"
  - "SKILL.md retains highest-value quick lookups (property wrapper table, rejection ranking), full details in references/"

requirements-completed: [UPGRADE-05, UPGRADE-06]

# Metrics
duration: 8min
completed: 2026-03-19
---

# Phase 09 Plan 03: apple-developer-docs and apple-review-guidelines Skill Upgrades Summary

**514-line iOS API reference and 233-line review guidelines split into directory-based skills with per-framework progressive disclosure via references/ subdirectories**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-19T08:55:51Z
- **Completed:** 2026-03-19T09:04:25Z
- **Tasks:** 2
- **Files modified:** 10 created, 2 deleted

## Accomplishments
- apple-developer-docs/ created with lightweight SKILL.md (~80 lines) and 6 reference files covering SwiftUI, SwiftData, StoreKit 2, HealthKit, XCTest/Swift Testing, Swift 6 concurrency + Info.plist
- apple-review-guidelines/ created with SKILL.md containing rejection ranking table and 10-item quick checklist, plus 2 reference files for full section details and complete pre-submission checklist
- Both old flat files (514-line apple-developer-docs.md and 233-line apple-review-guidelines.md) deleted
- All original content preserved across SKILL.md + references/ files

## Task Commits

Tasks executed on files outside the git repository (~/.claude/skills/). Work documented in final metadata commit.

1. **Task 1: Upgrade apple-developer-docs.md to directory SKILL.md with per-framework references/** — external files only (feat)
2. **Task 2: Upgrade apple-review-guidelines.md to directory SKILL.md with references/** — external files only (feat)

**Plan metadata:** (see final commit hash)

## Files Created/Modified

### apple-developer-docs
- `~/.claude/skills/apple-developer-docs/SKILL.md` — Lightweight index (~80 lines): Framework Index table, Quick Reference property wrappers, WWDC sessions, external links
- `~/.claude/skills/apple-developer-docs/references/swiftui.md` — SwiftUI: basic structure, state management, NavigationStack, lists, sheets, accessibility
- `~/.claude/skills/apple-developer-docs/references/swiftdata.md` — SwiftData: model definition, important rules, best practices, HealthKit notes
- `~/.claude/skills/apple-developer-docs/references/storekit.md` — StoreKit 2: product types, purchase flow, SwiftUI views, best practices
- `~/.claude/skills/apple-developer-docs/references/healthkit.md` — HealthKit: setup, basic pattern, best practices
- `~/.claude/skills/apple-developer-docs/references/testing.md` — XCTest and Swift Testing: unit/UI tests, comparison table, best practices
- `~/.claude/skills/apple-developer-docs/references/concurrency.md` — Swift 6 concurrency errors + Info.plist required settings
- `~/.claude/skills/apple-developer-docs.md` — DELETED (514-line flat file)

### apple-review-guidelines
- `~/.claude/skills/apple-review-guidelines/SKILL.md` — Lightweight index (~90 lines): guideline structure, Top 10 rejection causes, 10-item quick compliance check, Additional Resources
- `~/.claude/skills/apple-review-guidelines/references/section-details.md` — Full section-by-section rules (Safety, Performance, Business, Design, Legal) and Apple Developer agreements table
- `~/.claude/skills/apple-review-guidelines/references/rejection-checklist.md` — Complete pre-submission checklist (7 categories, 24 items) and 4 common rejection patterns with fixes
- `~/.claude/skills/apple-review-guidelines.md` — DELETED (233-line flat file)

## Decisions Made
- Framework Index table pattern for apple-developer-docs: each framework gets its own reference file. SKILL.md stays at ~80 lines (down from 514) with the Quick Reference property wrapper table (most commonly needed)
- Top 10 Rejection Causes table stays in SKILL.md (highest-value quick-lookup). Full section details and complete checklist moved to references/ for progressive disclosure
- Info.plist settings placed alongside Swift 6 concurrency in references/concurrency.md — both relate to app configuration and are commonly needed together when setting up a new iOS app

## Deviations from Plan

None — plan executed exactly as written. All content from both original files preserved across SKILL.md + references/ files. Framework Index table and progressive disclosure pattern applied as specified.

## Issues Encountered

The skill files are located at `~/.claude/skills/` (outside the git repository). Per-task commits could not stage the skill files directly. Work is documented in this SUMMARY.md and the final metadata commit.

## Next Phase Readiness
- Both skills are now directory-based with progressive disclosure
- Phase 09 has 3 plans; this is plan 03 — all plans in the phase are now complete
- Ready for phase completion verification

---
*Phase: 09-standalone-skill-upgrades*
*Completed: 2026-03-19*
