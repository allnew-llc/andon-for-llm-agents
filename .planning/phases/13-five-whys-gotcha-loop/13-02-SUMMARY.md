---
phase: 13-five-whys-gotcha-loop
plan: "02"
subsystem: documentation
tags: [gotcha, five-whys, gotcha-review, skill, tps-kaizen]

requires:
  - phase: 13-01
    provides: hooks/gotcha_candidate.py with generate_candidate() API
provides:
  - "gotcha-review subcommand documented in skills/tps-kaizen/SKILL.md"
  - "Five Whys step 5 wiring generate_candidate() after prevention measures"
  - "five-whys Output Format post-completion note for candidate generation"
affects: [tps-kaizen, gotcha-registry, five-whys]

tech-stack:
  added: []
  patterns:
    - "Instruction-based subcommand: gotcha-review tells Claude to list/approve/skip/edit YAML files in gotchas/candidates/"
    - "Post-completion note pattern in Output Format sections wires generate_candidate() into Five Whys completion flow"

key-files:
  created: []
  modified:
    - skills/tps-kaizen/SKILL.md

key-decisions:
  - "gotcha-review is instruction-based (not a script): SKILL.md tells Claude what filesystem operations to do (mv, read YAML, display fields)"
  - "Immediate availability is explicitly documented: load_gotchas() reads from disk with no caching — promoted Gotchas are matchable in the same session"
  - "Candidate file name preserved during promotion: ID already embedded in YAML, no rename needed"
  - "ID conflict detection documented: load_gotchas() raises GotchaValidationError on duplicate IDs — user must edit before approval"

patterns-established:
  - "Usage table entry + dedicated subcommand section pattern: each new subcommand gets one-liner in Usage and a full ## Subcommand section"
  - "Post-step pattern in multi-step procedures: step N+1 captures learning from the preceding steps (Five Whys -> generate_candidate)"

requirements-completed: [LOOP-03, LOOP-04]

duration: 2min
completed: 2026-03-19
---

# Phase 13 Plan 02: Five Whys Gotcha Loop — SKILL.md Integration Summary

**gotcha-review subcommand (list/approve/skip/edit) and Five Whys step 5 wired into skills/tps-kaizen/SKILL.md v1.2.0, completing the Five Whys -> candidate -> live registry learning loop**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-19T14:57:01Z
- **Completed:** 2026-03-19T14:58:46Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Added `/tps-kaizen gotcha-review` to the Usage table in SKILL.md
- Added full `## Subcommand: gotcha-review` section with list/approve/skip/edit procedure, explaining `mv` from `gotchas/candidates/` to `gotchas/`, and documenting immediate availability (no caching in `load_gotchas()`)
- Added step 5 to andon Subcommand Step 4 (Investigate) wiring `generate_candidate()` after prevention measures are defined
- Added post-completion note to five-whys Output Format section prompting candidate generation and `gotcha-review`
- Bumped SKILL.md version from 1.1.0 to 1.2.0

## Task Commits

1. **Task 1: Add gotcha-review subcommand and Five Whys candidate integration to SKILL.md** - `15a1a94` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `skills/tps-kaizen/SKILL.md` - Four targeted changes: Usage table entry, gotcha-review section, andon step 5, five-whys post-completion note; version 1.1.0 -> 1.2.0

## Decisions Made

- gotcha-review is instruction-based (not a script): the section tells Claude which filesystem operations to perform rather than wrapping a Python function. This matches the existing pattern of other SKILL.md subcommands.
- Immediate availability is explicitly documented using exact `load_gotchas()` terminology from the interface contract, linking the human-readable instruction to the code contract.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 13 is complete. The Five Whys -> Gotcha learning loop is fully wired:
  - Plan 01: `generate_candidate()` in `hooks/gotcha_candidate.py` (LOOP-01, LOOP-02)
  - Plan 02: `gotcha-review` subcommand in SKILL.md + Five Whys step 5 (LOOP-03, LOOP-04)
- No blockers. Phase 14 (if any) can proceed.

---

## Self-Check

- [x] `skills/tps-kaizen/SKILL.md` modified with all 4 changes
- [x] `grep -c "gotcha-review" skills/tps-kaizen/SKILL.md` returns 4 (Usage table + section header + two cross-references)
- [x] `grep -c "generate_candidate" skills/tps-kaizen/SKILL.md` returns 4 (andon step 5 x2 + five-whys post-note x2)
- [x] `grep "version:" skills/tps-kaizen/SKILL.md` returns `version: 1.2.0`
- [x] `grep -c "gotchas/candidates/" skills/tps-kaizen/SKILL.md` returns 4
- [x] Commit `15a1a94` exists: `feat(13-02): add gotcha-review subcommand and Five Whys candidate integration to SKILL.md`

## Self-Check: PASSED

---
*Phase: 13-five-whys-gotcha-loop*
*Completed: 2026-03-19*
