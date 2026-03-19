# Roadmap: ANDON for LLM Agents

## Milestones

- ✅ **v0.1.0 Foundation** - Phases 1-3 (shipped 2026-03-10)
- ✅ **v0.2.0 Hardening** - Phases 4-5 (shipped 2026-03-10)
- 🚧 **v0.3.0 Skill Quality & Ecosystem** - Phases 6-10 (in progress)

## Phases

<details>
<summary>✅ v0.1.0 Foundation (Phases 1-3) - SHIPPED 2026-03-10</summary>

Phases 1-3 delivered the core ANDON safety framework: Jidoka lifecycle (open/close/rollback), Kaizen learning tools (Five Whys, improvement kata, 3M audit), Knowledge Packs, and the TPS Kaizen skill for Claude Code. Not GSD-tracked.

</details>

<details>
<summary>✅ v0.2.0 Hardening (Phases 4-5) - SHIPPED 2026-03-10</summary>

Phases 4-5 delivered production hardening: analysis paralysis guard, context quality monitor, self-check protocol, deviation rules hierarchy (L1-L4), and security hardening (flock, atomic writes, injection boundaries, path validation, secret redaction). GSD-integrated but not formally planned.

</details>

### 🚧 v0.3.0 Skill Quality & Ecosystem (In Progress)

**Milestone Goal:** Elevate tps-kaizen skill quality to Anthropic best practices, add /qc-audit skill, migrate standalone .md skills to SKILL.md structure, and introduce new skill categories plus on-demand hooks.

- [x] **Phase 6: tps-kaizen Core Quality** - Trigger-focused description, documented gotchas, and related_skills composability (completed 2026-03-19)
- [ ] **Phase 7: tps-kaizen Scripts & Persistent Data** - scripts/ directory with analysis tools and persistent incident history
- [ ] **Phase 8: QC Audit Skill** - New /qc-audit skill with quality assessment, trend analysis, and gate correlation
- [ ] **Phase 9: Standalone Skill Upgrades** - Migrate 6 existing .md skills to SKILL.md structure with progressive disclosure
- [ ] **Phase 10: New Skills & On-Demand Hooks** - Three new skill categories and session-scoped on-demand hook pattern

## Phase Details

### Phase 6: tps-kaizen Core Quality
**Goal**: Users invoking Claude Code skills can find and use tps-kaizen correctly because its description, failure modes, and composition links are explicitly documented
**Depends on**: Nothing (first phase of this milestone)
**Requirements**: SKILL-01, SKILL-02, SKILL-07
**Success Criteria** (what must be TRUE):
  1. tps-kaizen SKILL.md description lists concrete trigger keywords (error, failure, incident, broken, stuck, regression) so Claude invokes it at the right moment
  2. A user reading tps-kaizen for the first time finds a Gotchas section with 5+ named failure patterns (human error stop, 4-artifact close, Meta-ANDON session reset, Gate-Gaming, confidence threshold)
  3. tps-kaizen SKILL.md contains a related_skills section with direct links to pipeline-debugging, adversarial-review, and qc-audit
**Plans**: 1 plan
Plans:
- [ ] 06-01-PLAN.md — Rewrite SKILL.md with trigger-focused description, Gotchas, and related_skills

### Phase 7: tps-kaizen Scripts & Persistent Data
**Goal**: Users can run tps-kaizen subcommands that analyze historical incident data and detect recurring failure patterns using persistent storage
**Depends on**: Phase 6
**Requirements**: SKILL-03, SKILL-04, SKILL-05, SKILL-06
**Success Criteria** (what must be TRUE):
  1. Running aggregate-incidents.sh from tps-kaizen/scripts/ produces a summary of past incidents and pattern clusters from ${CLAUDE_PLUGIN_DATA}/kaizen/
  2. Running five-whys-validator.sh reports whether a Five Whys document has reached 5 causal levels and filled the verification column
  3. Running quality-trend.sh outputs a time-series view of quality self-assessment results
  4. The tps-kaizen andon subcommand automatically surfaces past incidents matching the current problem pattern from the persistent kaizen store
**Plans**: TBD

### Phase 8: QC Audit Skill
**Goal**: Users can actively trigger quality self-assessments, view historical quality trends, and understand the correlation between quality scores and gate pass rates
**Depends on**: Phase 7
**Requirements**: QC-01, QC-02, QC-03, QC-04, QC-05
**Success Criteria** (what must be TRUE):
  1. /qc-audit skill exists with a SKILL.md that has a trigger-focused description and a Gotchas section
  2. Running /qc-audit with no arguments executes a quality self-assessment for the current phase using quality_criteria from the deliverable manifest and produces a pass/warn/fail result
  3. Running /qc-audit trend displays a trend chart of FAIL/WARN/OK rates over time from ${CLAUDE_PLUGIN_DATA}/qc/ history
  4. Running /qc-audit gate-health shows a correlation analysis between quality scores and Gate pass rates for recent phases
  5. Running scripts/collect-assessments.sh aggregates quality-self-assessment JSON files from multiple project directories into the central ${CLAUDE_PLUGIN_DATA}/qc/ store
**Plans**: TBD

### Phase 9: Standalone Skill Upgrades
**Goal**: Six existing single-file skills are promoted to SKILL.md directory structure with trigger-focused descriptions, Gotchas sections, and progressive disclosure via references/
**Depends on**: Phase 6
**Requirements**: UPGRADE-01, UPGRADE-02, UPGRADE-03, UPGRADE-04, UPGRADE-05, UPGRADE-06
**Success Criteria** (what must be TRUE):
  1. freeze/ SKILL.md exists with on-demand hook registration pattern (dynamic hook activated only when /freeze is invoked), replacing the flat freeze.md
  2. cherry-pick-prod/ SKILL.md exists with a Gotchas section and a references/ subdirectory for supplementary material
  3. ios-app-factory-operator/ SKILL.md exists with a trigger-focused description that tells Claude when to invoke the skill
  4. blog-reader-critic/ SKILL.md and apple-developer-docs/ SKILL.md and apple-review-guidelines/ SKILL.md each have trigger-focused descriptions and progressive disclosure via references/
**Plans**: TBD

### Phase 10: New Skills & On-Demand Hooks
**Goal**: Three new skill categories are available for use, and the on-demand hook pattern is established with a second example beyond freeze
**Depends on**: Phase 9
**Requirements**: NEW-01, NEW-02, NEW-03, HOOK-01, HOOK-02
**Success Criteria** (what must be TRUE):
  1. /freee-analysis skill exists and can fetch freee accounting data via MCP and produce an analysis or visualization output
  2. /cleanup-artifacts skill exists and inventories pipeline artifacts, build caches, and orphaned outputs, then executes cleanup on request
  3. /standup skill exists and aggregates git log plus task state into a daily summary in a standard format
  4. /careful skill exists with a session-scoped on-demand hook that blocks rm -rf, force-push, DROP TABLE, and kubectl delete for the duration of the session
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 6 → 7 → 8 → 9 → 10
Note: Phase 9 depends on Phase 6 (not 8), so phases 8 and 9 can proceed in parallel after phases 6 and 7 complete.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 6. tps-kaizen Core Quality | 1/1 | Complete   | 2026-03-19 | - |
| 7. tps-kaizen Scripts & Persistent Data | v0.3.0 | 0/? | Not started | - |
| 8. QC Audit Skill | v0.3.0 | 0/? | Not started | - |
| 9. Standalone Skill Upgrades | v0.3.0 | 0/? | Not started | - |
| 10. New Skills & On-Demand Hooks | v0.3.0 | 0/? | Not started | - |
