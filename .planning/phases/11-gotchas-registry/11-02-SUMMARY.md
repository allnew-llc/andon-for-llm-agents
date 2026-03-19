---
phase: 11-gotchas-registry
plan: "02"
subsystem: gotchas-engine
tags: [gotchas, yaml, registry, tps-kaizen, knowledge-packs, pci-dss]

requires:
  - phase: 11-01
    provides: gotcha_registry.py loader module with GotchaEntry dataclass and load_gotchas()

provides:
  - 7 seed Gotcha YAML files in gotchas/ extracted from tps-kaizen SKILL.md
  - 1 pack-contributed Gotcha YAML in packs/andon-pack-financial/gotchas/
  - End-to-end proof that registry schema, loader, and pack discovery work with real data

affects:
  - phase-12-auto-surfacing
  - phase-13-five-whys-loop

tech-stack:
  added: []
  patterns:
    - "Gotcha YAML files use POSIX-style block scalars (>) for multi-sentence prose fields"
    - "Pack-contributed Gotchas use pack name as source field (e.g., 'andon-pack-financial')"
    - "Severity conventions: critical for blocking/compliance failures, high for recurrence risk, medium for cultural/counter patterns"

key-files:
  created:
    - gotchas/GOTCHA-001-human-error-stop.yaml
    - gotchas/GOTCHA-002-four-artifact-close.yaml
    - gotchas/GOTCHA-003-meta-andon-session-reset.yaml
    - gotchas/GOTCHA-004-gate-gaming.yaml
    - gotchas/GOTCHA-005-confidence-threshold-bypass.yaml
    - gotchas/GOTCHA-006-andon-cord-fear.yaml
    - gotchas/GOTCHA-007-fix-and-forget.yaml
    - packs/andon-pack-financial/gotchas/GOTCHA-FIN-001-pci-cardholder-exposure.yaml
  modified: []

key-decisions:
  - "Severity assignments: GOTCHA-002 and GOTCHA-004 are critical (block ANDON close / undermine quality system); GOTCHA-001, GOTCHA-005, GOTCHA-007 are high (recurrence risk); GOTCHA-003 and GOTCHA-006 are medium (counter patterns)"
  - "Pack Gotcha source field set to pack name ('andon-pack-financial') not 'tps-kaizen', enabling source-based filtering in future phases"

patterns-established:
  - "Gotcha pattern field: 2-4 sentences describing the anti-pattern, including consequences"
  - "Gotcha prevention field: 2-3 sentences of actionable guidance, not just 'don't do X'"
  - "Pack Gotchas live in packs/{pack-name}/gotchas/ and require no core code changes to be discovered"

requirements-completed:
  - REG-02
  - REG-04

duration: 8min
completed: "2026-03-19"
---

# Phase 11 Plan 02: Gotchas Registry Seed Data Summary

**7 seed Gotcha YAMLs from tps-kaizen SKILL.md + 1 pack-contributed PCI-DSS Gotcha, proving the registry schema and pack discovery end-to-end with real data and all 19 tests passing**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-19T07:38:12Z
- **Completed:** 2026-03-19T07:46:00Z
- **Tasks:** 2
- **Files modified:** 8 (7 core gotchas + 1 pack gotcha)

## Accomplishments

- Created 7 seed Gotcha YAML files in gotchas/, one per anti-pattern from the tps-kaizen SKILL.md Gotchas section, with content restructured into the schema fields (not verbatim copies of SKILL.md prose)
- Created 1 pack-contributed Gotcha YAML in packs/andon-pack-financial/gotchas/, proving Knowledge Packs can extend the registry without any changes to hooks/gotcha_registry.py
- Validated that load_gotchas(Path('gotchas/')) returns 7 entries and load_gotchas(Path('gotchas/'), packs_dir=Path('packs/')) returns 8 entries — all 19 Phase 11 tests still pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Create 7 seed Gotcha YAML files** - `39690f7` (feat)
2. **Task 2: Create pack-contributed Gotcha example and validate full discovery** - `baf3a6e` (feat)

**Plan metadata:** *(this docs commit)*

## Files Created/Modified

- `gotchas/GOTCHA-001-human-error-stop.yaml` - Five Whys stopping at "human error" (severity: high)
- `gotchas/GOTCHA-002-four-artifact-close.yaml` - Placeholder artifacts to pass ANDON close (severity: critical)
- `gotchas/GOTCHA-003-meta-andon-session-reset.yaml` - Meta-ANDON counters reset across sessions (severity: medium)
- `gotchas/GOTCHA-004-gate-gaming.yaml` - Optimizing for gate conditions not quality (severity: critical)
- `gotchas/GOTCHA-005-confidence-threshold-bypass.yaml` - Inflating confidence scores (severity: high)
- `gotchas/GOTCHA-006-andon-cord-fear.yaml` - Hesitating to pull the Andon cord (severity: medium)
- `gotchas/GOTCHA-007-fix-and-forget.yaml` - Skipping Step 4 (Investigate) after emergency fix (severity: high)
- `packs/andon-pack-financial/gotchas/GOTCHA-FIN-001-pci-cardholder-exposure.yaml` - PCI cardholder data logged in plaintext (severity: critical)

## Decisions Made

- **Severity assignments:** GOTCHA-002 (4-artifact close) and GOTCHA-004 (gate-gaming) are `critical` because they directly undermine or block the Jidoka quality system itself. GOTCHA-001, GOTCHA-005, GOTCHA-007 are `high` because they cause structural root causes to go unaddressed and failures to recur. GOTCHA-003 and GOTCHA-006 are `medium` because they are cultural and counter patterns with lower immediate structural impact.
- **Pack source field:** Set to the pack name (`andon-pack-financial`) rather than `tps-kaizen` so that Phase 12 and Phase 13 can use `source` as a filter to surface domain-specific Gotchas in domain-specific contexts.

## Deviations from Plan

None - plan executed exactly as written. No changes to hooks/gotcha_registry.py were required; the existing pack discovery logic in Plan 01 handled GOTCHA-FIN-001 without modification.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 11 is now fully complete: schema + loader (Plan 01) + seed data (Plan 02)
- Phase 12 (auto-surfacing) and Phase 13 (Five Whys loop) can now start; both are independent of each other and can run in parallel per the v0.4.0 architectural decision
- The 8 Gotcha entries (7 core + 1 pack) provide sufficient variety to test surfacing and loop logic in Phase 12 and Phase 13

---
*Phase: 11-gotchas-registry*
*Completed: 2026-03-19*
