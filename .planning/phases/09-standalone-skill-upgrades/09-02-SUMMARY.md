---
phase: 09-standalone-skill-upgrades
plan: 02
subsystem: skills
tags: [skill-upgrade, yaml-frontmatter, trigger-description, ios-app-factory, blog-critic, progressive-disclosure]

# Dependency graph
requires: []
provides:
  - "~/.claude/skills/ios-app-factory-operator/ directory with SKILL.md (YAML frontmatter, trigger-focused description, English section headers)"
  - "~/.claude/skills/blog-reader-critic/ directory with SKILL.md (YAML frontmatter, Gotchas section, Additional Resources)"
  - "~/.claude/skills/blog-reader-critic/references/audit-protocol.md (5-test audit protocol for progressive disclosure)"
affects: [ios-app-factory, blog-writing, technical-writing-review]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "SKILL.md with YAML frontmatter for skill invocation matching"
    - "Trigger table (Trigger | Action) for structured When-to-Use sections"
    - "Gotchas section with named patterns for failure mode documentation"
    - "references/ subdirectory for progressive disclosure of supplementary content"

key-files:
  created:
    - "~/.claude/skills/ios-app-factory-operator/SKILL.md"
    - "~/.claude/skills/blog-reader-critic/SKILL.md"
    - "~/.claude/skills/blog-reader-critic/references/audit-protocol.md"
  modified: []

key-decisions:
  - "ios-app-factory-operator is compact (59 lines source) — no references/ subdirectory needed; existing external .codex/skills/ links are sufficient"
  - "blog-reader-critic Critical Evaluation Criteria tables (INSTANT KILL, YELLOW FLAGS, WHAT MAKES YOU KEEP READING) retained in SKILL.md — these are the core value of the skill and must load on every invocation"
  - "Audit Protocol (5 named tests) extracted to references/audit-protocol.md — supplementary depth not needed for every invocation"
  - "Three named Gotchas added to blog-reader-critic: Persona Drift, Confirmation Bias, Kindness Creep — documenting the ways the hostile-reviewer persona breaks down"
  - "ios-app-factory-operator section headers translated from Japanese to English for consistency with SKILL.md pattern established in Phase 6"

patterns-established:
  - "Compact skill pattern: no references/ when skill fits in ~60 lines and external docs are sufficient"
  - "Persona skill pattern: keep identity + evaluation criteria in SKILL.md, extract audit protocols to references/"

requirements-completed: [UPGRADE-03, UPGRADE-04]

# Metrics
duration: 4min
completed: 2026-03-19
---

# Phase 09 Plan 02: Standalone Skill Upgrades (ios-app-factory-operator + blog-reader-critic) Summary

**Two personal operator skills upgraded to directory-based SKILL.md structure with YAML frontmatter trigger descriptions, enabling Claude Code skill invocation matching at the right moment**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-19T08:55:59Z
- **Completed:** 2026-03-19T09:00:04Z
- **Tasks:** 2 completed
- **Files modified:** 5 (3 created, 2 deleted)

## Accomplishments

- ios-app-factory-operator upgraded from flat .md to directory SKILL.md with YAML frontmatter and trigger-focused description covering 6 invocation keywords
- 使うタイミング Japanese bullet list converted to English trigger table (Trigger | Action) matching Phase 6 pattern
- blog-reader-critic upgraded to directory SKILL.md with 3 named Gotchas (Persona Drift, Confirmation Bias, Kindness Creep) and references/ progressive disclosure
- Audit Protocol (5 named tests: SO WHAT?, PROVE IT, I ALREADY KNEW THAT, WOULD I SHARE THIS?, HACKER NEWS COMMENT) extracted to references/audit-protocol.md
- Both old flat .md files deleted

## Task Commits

Each task was committed atomically:

1. **Task 1: Upgrade ios-app-factory-operator.md to directory SKILL.md** - `a3bf042` (feat)
2. **Task 2: Upgrade blog-reader-critic.md to directory SKILL.md with references/** - included in final docs commit (feat)

**Plan metadata:** (this SUMMARY commit)

## Files Created/Modified

- `~/.claude/skills/ios-app-factory-operator/SKILL.md` - YAML frontmatter + trigger table + English headers, 5 sections
- `~/.claude/skills/blog-reader-critic/SKILL.md` - YAML frontmatter + persona + criteria tables + Gotchas + Additional Resources
- `~/.claude/skills/blog-reader-critic/references/audit-protocol.md` - 5-test audit protocol for systematic section-by-section evaluation
- `~/.claude/skills/ios-app-factory-operator.md` — DELETED (replaced by directory)
- `~/.claude/skills/blog-reader-critic.md` — DELETED (replaced by directory)

## Decisions Made

- ios-app-factory-operator does NOT get a references/ subdirectory — the skill is compact and the external .codex/skills/ references are sufficient. Creating an empty references/ for form's sake would add noise.
- blog-reader-critic criteria tables (INSTANT KILL, YELLOW FLAGS, WHAT MAKES YOU KEEP READING) stay in SKILL.md, not references/ — these tables are the core value of the skill and every invocation needs them loaded.
- Three named Gotchas added to blog-reader-critic that weren't in the original: Persona Drift, Confirmation Bias, Kindness Creep. These document the three ways the hostile-reviewer persona typically degrades during use.
- Japanese section headers in ios-app-factory-operator translated to English for consistency with the SKILL.md pattern established in Phase 6 (content meaning preserved identically).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Two more personal skills remain in Phase 09: Plan 03 covers the remaining upgrades
- The SKILL.md pattern (YAML frontmatter + trigger table + Gotchas + references/) is now fully established across ios-app-factory-operator, blog-reader-critic, freeze, cherry-pick-prod, tps-kaizen, and qc-audit

---
*Phase: 09-standalone-skill-upgrades*
*Completed: 2026-03-19*
