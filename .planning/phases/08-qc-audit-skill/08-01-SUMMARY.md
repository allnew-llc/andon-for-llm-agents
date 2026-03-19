---
phase: 08-qc-audit-skill
plan: 01
subsystem: skills
tags: [qc-audit, quality, skill, self-assessment, gotchas, tps-kaizen]

# Dependency graph
requires:
  - phase: 07-tps-kaizen-scripts-persistent-data
    provides: tps-kaizen SKILL.md structure and pattern (trigger description, Gotchas, Related Skills) used as reference
provides:
  - skills/qc-audit/SKILL.md with trigger-focused description, 5-step self-assessment instructions, and Gotchas section
affects: [08-02-qc-audit-scripts, phase-09-standalone-skill-upgrades, any future skill needing qc-audit as Related Skill]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Trigger-focused SKILL.md description listing concrete keywords for Claude invocation"
    - "6-step quality self-assessment instructions referencing deliverable manifest quality_criteria (not gate conditions)"
    - "Named Gotchas with explanatory paragraphs documenting structural root causes"
    - "Composition Patterns table linking multiple skills in chains"

key-files:
  created:
    - skills/qc-audit/SKILL.md
  modified: []

key-decisions:
  - "Quality criteria loaded from deliverable manifest/PLAN.md must_haves, not derived from existing artifacts — prevents Criteria Drift gotcha"
  - "Five Gotchas named and documented with structural root causes: Score Inflation, Criteria Drift, Trend Blindness, Gate-Quality Conflation, Assessment-Only Syndrome"
  - "Self-assessment output saved to docs/pipeline/quality-self-assessment-{phase_id}.json matching rules/45-quality-driven-execution.md format"
  - "Related Skills section references tps-kaizen with 3 concrete composition chains (Quality Gate, Post-Incident, Continuous Improvement)"

patterns-established:
  - "Quality Self-Assessment Pattern: load criteria from source -> assess each criterion with specific evidence -> compute overall -> output table + JSON -> recommend actions"
  - "Pre-gate quality check: /qc-audit (no args) -> fix FAIL items -> /qc-audit (re-assess) -> gate submission"

requirements-completed: [QC-01, QC-02]

# Metrics
duration: 9min
completed: 2026-03-19
---

# Phase 08 Plan 01: QC Audit Skill Summary

**`/qc-audit` SKILL.md with trigger-focused description, 6-step quality self-assessment instructions referencing deliverable manifest quality_criteria, and 5 named Gotchas preventing score inflation and criteria drift**

## Performance

- **Duration:** 9 min
- **Started:** 2026-03-19T07:50:57Z
- **Completed:** 2026-03-19T08:00:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Created `skills/qc-audit/SKILL.md` (210 lines) following the tps-kaizen SKILL.md structural pattern established in Phase 6
- No-args subcommand provides 6-step quality self-assessment procedure that explicitly loads quality criteria from deliverable manifest (not gate conditions) — enforcing the principle from `rules/45-quality-driven-execution.md`
- Gotchas section documents 5 named failure patterns with explanatory paragraphs identifying structural root causes, not just bullet headers
- Related Skills section links to tps-kaizen with 3 composition patterns enabling multi-skill quality improvement chains

## Task Commits

Each task was committed atomically:

1. **Task 1: Create qc-audit SKILL.md with trigger description, Gotchas, and self-assessment instructions** - `8a1b667` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `skills/qc-audit/SKILL.md` — QC audit skill definition: YAML frontmatter with 9 trigger keywords, When to Use table (7 rows), no-args 6-step self-assessment, trend subcommand, gate-health subcommand, 5 Gotchas, Related Skills with composition patterns

## Decisions Made

- Quality criteria must be loaded from source (deliverable manifest, PLAN.md `must_haves`, ROADMAP.md success criteria) before examining any artifacts — never derive criteria from what already exists. This directly prevents the Criteria Drift gotcha.
- Five Gotchas named: Score Inflation, Criteria Drift, Trend Blindness, Gate-Quality Conflation, Assessment-Only Syndrome — each with an explanatory paragraph that names the structural root cause and a prevention mechanism
- Self-assessment JSON saved to `docs/pipeline/quality-self-assessment-{phase_id}.json` matching the format specified in `rules/45-quality-driven-execution.md`
- trend and gate-health subcommands documented with script references to Plan 08-02 deliverables, and interpretation guides covering all meaningful correlation patterns

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `skills/qc-audit/SKILL.md` is complete and discoverable by Claude when quality-related keywords appear
- Plan 08-02 can now proceed: `trend.sh`, `gate-health.sh`, and `collect-assessments.sh` scripts referenced in SKILL.md need to be created
- tps-kaizen SKILL.md already forward-references `skills/qc-audit/SKILL.md` in its Related Skills section (established in Phase 6) — the back-reference from qc-audit to tps-kaizen is now also in place

---
*Phase: 08-qc-audit-skill*
*Completed: 2026-03-19*
