# Roadmap: ANDON for LLM Agents

## Milestones

- ✅ **v0.1.0 Foundation** - Phases 1-3 (shipped 2026-03-10)
- ✅ **v0.2.0 Hardening** - Phases 4-5 (shipped 2026-03-10)
- ✅ **v0.3.0 Skill Quality & Ecosystem** - Phases 6-10 (shipped 2026-03-19)
- 🚧 **v0.4.0 Gotchas Engine** - Phases 11-14 (in progress)

## Phases

<details>
<summary>✅ v0.1.0 Foundation (Phases 1-3) - SHIPPED 2026-03-10</summary>

Phases 1-3 delivered the core ANDON safety framework: Jidoka lifecycle (open/close/rollback), Kaizen learning tools (Five Whys, improvement kata, 3M audit), Knowledge Packs, and the TPS Kaizen skill for Claude Code. Not GSD-tracked.

</details>

<details>
<summary>✅ v0.2.0 Hardening (Phases 4-5) - SHIPPED 2026-03-10</summary>

Phases 4-5 delivered production hardening: analysis paralysis guard, context quality monitor, self-check protocol, deviation rules hierarchy (L1-L4), and security hardening (flock, atomic writes, injection boundaries, path validation, secret redaction). GSD-integrated but not formally planned.

</details>

<details>
<summary>✅ v0.3.0 Skill Quality & Ecosystem (Phases 6-10) - SHIPPED 2026-03-19</summary>

Phases 6-10 delivered: tps-kaizen SKILL.md with trigger-focused description (14 keywords), 7 Gotchas, and related_skills; 3 analysis scripts (aggregate-incidents.sh, five-whys-validator.sh, quality-trend.sh); /qc-audit skill with trend analysis and gate-health correlation; 6 standalone skills upgraded to SKILL.md structure; 4 new skills (freee-analysis, standup, cleanup-artifacts, careful); on-demand hooks pattern (freeze + careful).

</details>

### 🚧 v0.4.0 Gotchas Engine (In Progress)

**Milestone Goal:** Evolve Gotchas from static text in SKILL.md into a structured data registry with automatic surfacing during ANDON, a Five Whys → Gotcha learning loop, and effectiveness metrics.

- [x] **Phase 11: Gotchas Registry** - YAML schema, seed data, registry loader, and Knowledge Pack extension point (completed 2026-03-19)
- [x] **Phase 12: ANDON Auto-Surfacing** - Hook integration, pattern matching, confidence scoring, and ranked results (completed 2026-03-19)
- [x] **Phase 13: Five Whys → Gotcha Loop** - Candidate generation, gotcha-review subcommand, and hot-reload promotion (completed 2026-03-19)
- [ ] **Phase 14: Analysis, Metrics & Skill Integration** - gotcha-stats.sh, tps-kaizen subcommand docs, and andon Step 0 update

## Phase Details

### Phase 11: Gotchas Registry
**Goal**: A structured Gotchas Registry exists that can be parsed, validated, and extended by Knowledge Packs — replacing the static text in SKILL.md with machine-readable YAML
**Depends on**: Nothing (first phase of this milestone)
**Requirements**: REG-01, REG-02, REG-03, REG-04
**Success Criteria** (what must be TRUE):
  1. Running the registry loader against gotchas/ produces a valid parsed list with all seed Gotchas and no schema errors
  2. gotchas/ directory contains at least 5 YAML files, each with id, name, pattern, severity, prevention, discovered, and source fields populated
  3. A Knowledge Pack directory (e.g., packs/financial/gotchas/) containing pack-specific YAML files is discovered and included by the loader without changes to core code
  4. Running the loader against a YAML file missing a required field produces a clear schema validation error, not a silent failure
**Plans:** 2/2 plans complete
Plans:
- [ ] 11-01-PLAN.md — Schema definition + registry loader module with TDD tests
- [ ] 11-02-PLAN.md — 7 seed Gotcha YAML files from tps-kaizen + pack-contributed example

### Phase 12: ANDON Auto-Surfacing
**Goal**: When ANDON opens, matching Gotchas are automatically surfaced with confidence scores so Claude can avoid repeating known failures
**Depends on**: Phase 11
**Requirements**: SURF-01, SURF-02, SURF-03, SURF-04
**Success Criteria** (what must be TRUE):
  1. Opening an ANDON incident with a known error pattern surfaces at least one matching Gotcha with prevention advice injected into additionalContext
  2. Match results include a confidence label (exact match, partial match, or category match) so the user can judge relevance
  3. When multiple Gotchas match, they are presented ranked by relevance score with the highest-confidence match first
  4. Opening an ANDON incident with no matching pattern produces no spurious Gotcha output (no false matches injected into context)
**Plans:** 1/1 plans complete
Plans:
- [ ] 12-01-PLAN.md — Gotcha surfacer module with TDD + ANDON hook integration

### Phase 13: Five Whys → Gotcha Loop
**Goal**: Completing a Five Whys analysis automatically produces a reviewable Gotcha candidate that can be promoted into the live registry without restarting any process
**Depends on**: Phase 11
**Requirements**: LOOP-01, LOOP-02, LOOP-03, LOOP-04
**Success Criteria** (what must be TRUE):
  1. After a Five Whys session completes, a candidate YAML file appears in gotchas/candidates/ with auto-extracted pattern and prevention derived from the root cause statement
  2. Running `/tps-kaizen gotcha-review` lists all files in gotchas/candidates/ with their key fields (id, pattern, severity) and prompts for approve or skip
  3. Approving a candidate in gotcha-review moves it from gotchas/candidates/ to gotchas/ without manual file operations
  4. A Gotcha promoted via gotcha-review is immediately matchable by the ANDON surfacing engine in the same session (no restart required)
**Plans**: 2 plans
Plans:
- [ ] 13-01-PLAN.md — Gotcha candidate generation module with TDD tests (LOOP-01, LOOP-02)
- [ ] 13-02-PLAN.md — SKILL.md gotcha-review subcommand + Five Whys integration (LOOP-03, LOOP-04)

### Phase 14: Analysis, Metrics & Skill Integration
**Goal**: Users can measure Gotcha hit rates and effectiveness, and the tps-kaizen skill surface all Gotcha operations (review, stats, andon check) clearly documented
**Depends on**: Phase 12, Phase 13
**Requirements**: METRIC-01, METRIC-02, METRIC-03, INTEG-01, INTEG-02
**Success Criteria** (what must be TRUE):
  1. Running gotcha-stats.sh outputs a hit-rate table showing each Gotcha ID, name, and how many times it matched an incident
  2. gotcha-stats.sh flags any Gotcha with zero hits and labels it as "potentially stale" in the output
  3. gotcha-stats.sh includes a prevention-effectiveness column showing whether incidents where a Gotcha was surfaced resolved differently than incidents without a match
  4. Running `/tps-kaizen` shows gotcha-review as a documented subcommand with usage description in SKILL.md
  5. The tps-kaizen andon Step 0 prompt includes a Gotcha Registry check alongside the existing incident history check
**Plans:** 2 plans
Plans:
- [ ] 14-01-PLAN.md — gotcha-stats.sh script with hit rates, staleness detection, and effectiveness metrics (METRIC-01, METRIC-02, METRIC-03)
- [ ] 14-02-PLAN.md — SKILL.md integration: verify gotcha-review docs, update Step 0 with Gotcha Registry check (INTEG-01, INTEG-02)

## Progress

**Execution Order:**
Phases 1-10 complete. Continuing: 11 → 12 → 13 → 14
Note: Phases 12 and 13 both depend on Phase 11 and can run in parallel. Phase 14 depends on both 12 and 13.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 6. tps-kaizen Core Quality | v0.3.0 | 1/1 | Complete | 2026-03-19 |
| 7. tps-kaizen Scripts & Persistent Data | v0.3.0 | 2/2 | Complete | 2026-03-19 |
| 8. QC Audit Skill | v0.3.0 | 2/2 | Complete | 2026-03-19 |
| 9. Standalone Skill Upgrades | v0.3.0 | 3/3 | Complete | 2026-03-19 |
| 10. New Skills & On-Demand Hooks | v0.3.0 | 2/2 | Complete | 2026-03-19 |
| 11. Gotchas Registry | v0.4.0 | 2/2 | Complete | 2026-03-19 |
| 12. ANDON Auto-Surfacing | v0.4.0 | 1/1 | Complete | 2026-03-19 |
| 13. Five Whys → Gotcha Loop | v0.4.0 | 2/2 | Complete | 2026-03-19 |
| 14. Analysis, Metrics & Skill Integration | v0.4.0 | 0/2 | Not started | - |
