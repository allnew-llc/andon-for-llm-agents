---
phase: 06-tps-kaizen-core-quality
plan: 01
subsystem: skill-documentation
tags: [tps-kaizen, skill-quality, documentation, jidoka]

# Dependency graph
requires: []
provides:
  - "tps-kaizen SKILL.md v1.1.0 with trigger-focused description containing error/failure/incident/broken/stuck/regression keywords"
  - "When to Use This Skill section with trigger table mapping 9 problem types to subcommands"
  - "Gotchas section documenting 7 named failure patterns with actionable prevention guidance"
  - "Related Skills section linking pipeline-debugging, adversarial-review, qc-audit with composition patterns"
affects:
  - "07-pipeline-debugging-skill (will add related skill linked from tps-kaizen)"
  - "08-adversarial-review-skill (will add related skill linked from tps-kaizen)"
  - "10-qc-audit-skill (will add related skill linked from tps-kaizen)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Trigger-focused SKILL.md description pattern: 'Use when: <keywords>' instead of abstract capability description"
    - "Gotchas section pattern: named failure patterns with structural root cause explanation"
    - "Related Skills table pattern: path + when-to-chain for skill composition"
    - "Composition Patterns section: named chains like 'Incident Response Chain' and 'Quality Improvement Chain'"

key-files:
  created: []
  modified:
    - "skills/tps-kaizen/SKILL.md"

key-decisions:
  - "Used 'Use when: ...' description format to maximize keyword matching for skill invocation (SKILL-01 requirement)"
  - "Added 7 Gotchas (5 required + 2 bonus: Andon Cord Fear, Fix-and-Forget) to document full failure pattern space"
  - "Added detailed explanatory paragraphs to each Gotcha beyond just the header, explaining the structural root cause"
  - "Placed When to Use section immediately after opening quote block, before Two Pillars, for first-reader discoverability"
  - "Forward-referenced skill paths for pipeline-debugging, adversarial-review, qc-audit as planned future skills"

patterns-established:
  - "Trigger-keyword pattern: SKILL.md descriptions use 'Use when: error, failure...' format for Claude Code invocation matching"
  - "Gotchas section format: ### heading + paragraph (not just bullet) for each named failure pattern"
  - "Related Skills table: columns are Skill | Path | When to Chain"
  - "Composition Patterns subsection: named chains with arrow notation showing skill sequencing"

requirements-completed: [SKILL-01, SKILL-02, SKILL-07]

# Metrics
duration: 2min
completed: 2026-03-19
---

# Phase 6 Plan 01: TPS Kaizen SKILL.md Core Quality Summary

**Trigger-focused description, 7-pattern Gotchas section, and Related Skills composition table added to tps-kaizen SKILL.md v1.1.0**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-03-19T06:43:29Z
- **Completed:** 2026-03-19T06:45:14Z
- **Tasks:** 1 of 1
- **Files modified:** 1

## Accomplishments

- Replaced abstract "Lean manufacturing (Jidoka + JIT) based anomaly detection..." description with trigger-focused keywords that Claude Code's skill invocation logic can match against user problem descriptions
- Added "When to Use This Skill" section with 9-row trigger table mapping test failures, build errors, regressions, incidents, unexplained behaviors, process inefficiencies, and quality degradation to specific subcommands
- Added "Gotchas" section documenting 7 named failure patterns: Human Error Stop, 4-Artifact Close Shortcut, Meta-ANDON Session Reset, Gate-Gaming, Confidence Threshold Bypass, Andon Cord Fear, Fix-and-Forget — each with structural root cause explanation
- Added "Related Skills" section linking pipeline-debugging, adversarial-review, and qc-audit with a composition patterns subsection defining Incident Response Chain and Quality Improvement Chain
- Bumped version from 1.0.0 to 1.1.0

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite SKILL.md with trigger-focused description, Gotchas, and related_skills** - `d09b876` (feat)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `skills/tps-kaizen/SKILL.md` - Added When to Use section, Gotchas section (7 patterns), Related Skills section with composition patterns; updated description and version

## Decisions Made

- Used "Use when: error, test failure, build failure, incident, broken pipeline, stuck process, regression..." format for the description field to maximize keyword hit rate in Claude Code's skill invocation matching (SKILL-01)
- Added 7 Gotchas (5 required + 2 bonus) because the codebase evidence showed Andon Cord Fear and Fix-and-Forget as equally important failure modes worth documenting
- Added explanatory paragraphs beyond the Gotcha headers (not just header + 1 sentence) to explain why each pattern is a problem at the structural level — avoids Gate-Gaming of "has 5+ named patterns" without real content
- Forward-referenced skill paths for pipeline-debugging, adversarial-review, qc-audit even though these skills are planned future deliverables — the path references establish the linking contract for when those skills are built

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- tps-kaizen SKILL.md v1.1.0 is complete with all three quality improvements (SKILL-01, SKILL-02, SKILL-07)
- Phase 7 (pipeline-debugging skill) and Phase 8 (adversarial-review skill) will need to create the forward-referenced skill paths that tps-kaizen now links to
- Phase 10 (qc-audit skill) likewise needs to fulfill the `skills/qc-audit/SKILL.md` path reference

---
*Phase: 06-tps-kaizen-core-quality*
*Completed: 2026-03-19*
