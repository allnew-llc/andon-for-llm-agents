# Requirements: ANDON for LLM Agents

**Defined:** 2026-03-19
**Core Value:** Stop defects from flowing downstream and learn from every failure

## v0.3.0 Requirements

Requirements for skill quality and ecosystem milestone. Each maps to roadmap phases.

### TPS-Kaizen Skill Improvement

- [x] **SKILL-01**: tps-kaizen SKILL.md description is trigger-focused (lists when to call: error, failure, incident, broken, stuck, regression)
- [x] **SKILL-02**: tps-kaizen has Gotchas section with 5+ documented failure patterns (human error stop, 4-artifact close, Meta-ANDON session reset, Gate-Gaming, confidence threshold)
- [ ] **SKILL-03**: tps-kaizen has scripts/ directory with aggregate-incidents.sh (past incident aggregation and pattern analysis)
- [x] **SKILL-04**: tps-kaizen has scripts/five-whys-validator.sh (completeness check: 5 levels reached, verification column filled)
- [ ] **SKILL-05**: tps-kaizen has scripts/quality-trend.sh (quality self-assessment trend over time)
- [x] **SKILL-06**: tps-kaizen andon subcommand auto-references past incident history from ${CLAUDE_PLUGIN_DATA}/kaizen/ and detects recurring patterns
- [x] **SKILL-07**: tps-kaizen SKILL.md includes related_skills section linking to pipeline-debugging, adversarial-review, qc-audit

### QC Audit Skill

- [ ] **QC-01**: /qc-audit skill exists with SKILL.md, trigger-focused description, and Gotchas
- [ ] **QC-02**: /qc-audit (no args) executes quality self-assessment for the current phase using quality_criteria from deliverable manifest
- [ ] **QC-03**: /qc-audit trend reads ${CLAUDE_PLUGIN_DATA}/qc/ history and displays trend of FAIL/WARN/OK rates over time
- [ ] **QC-04**: /qc-audit gate-health analyzes correlation between quality scores and Gate pass rates
- [ ] **QC-05**: /qc-audit has scripts/collect-assessments.sh that aggregates quality-self-assessment JSON files from project dirs into central store

### Standalone Skill Upgrades

- [ ] **UPGRADE-01**: freeze.md upgraded to freeze/ SKILL.md structure with on-demand hooks (dynamic hook registration on skill activation)
- [ ] **UPGRADE-02**: cherry-pick-prod.md upgraded to cherry-pick-prod/ SKILL.md structure with Gotchas and references/
- [ ] **UPGRADE-03**: ios-app-factory-operator.md upgraded to SKILL.md structure with trigger-focused description
- [ ] **UPGRADE-04**: blog-reader-critic.md upgraded to SKILL.md structure with trigger-focused description
- [ ] **UPGRADE-05**: apple-developer-docs.md upgraded to SKILL.md structure with progressive disclosure (references/)
- [ ] **UPGRADE-06**: apple-review-guidelines.md upgraded to SKILL.md structure with progressive disclosure (references/)

### New Skill Categories

- [ ] **NEW-01**: /freee-analysis skill exists — fetches freee accounting data via MCP and performs analysis/visualization
- [ ] **NEW-02**: /cleanup-artifacts skill exists — inventories and cleans pipeline artifacts, build caches, and orphaned outputs
- [ ] **NEW-03**: /standup skill exists — aggregates git log + task state into daily summary format

### On-Demand Hooks

- [ ] **HOOK-01**: freeze skill registers on-demand PreToolUse hook that blocks Edit/Write outside frozen directory (only active when /freeze is invoked)
- [ ] **HOOK-02**: /careful skill exists with on-demand hook blocking rm -rf, force-push, DROP TABLE, kubectl delete (session-scoped activation)

## Future Requirements

### v0.4.0 Candidates

- **MEASURE-01**: Skill triggering accuracy dashboard (expected vs actual invocations)
- **MEASURE-02**: Cross-session learning analytics (pattern recurrence detection over weeks)
- **COMPOSE-01**: Skill dependency graph visualization
- **PACK-02**: Additional knowledge packs (kubernetes, terraform, AWS CDK)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Plugin marketplace publishing | Separate workflow, not part of skill quality |
| Non-Claude Code agent support | Current focus is Claude Code hooks only |
| Web-based skill editor | CLI-first philosophy |
| Automated skill generation from code | Too speculative for v0.3.0 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SKILL-01 | Phase 6 | Complete |
| SKILL-02 | Phase 6 | Complete |
| SKILL-07 | Phase 6 | Complete |
| SKILL-03 | Phase 7 | Pending |
| SKILL-04 | Phase 7 | Complete |
| SKILL-05 | Phase 7 | Pending |
| SKILL-06 | Phase 7 | Complete |
| QC-01 | Phase 8 | Pending |
| QC-02 | Phase 8 | Pending |
| QC-03 | Phase 8 | Pending |
| QC-04 | Phase 8 | Pending |
| QC-05 | Phase 8 | Pending |
| UPGRADE-01 | Phase 9 | Pending |
| UPGRADE-02 | Phase 9 | Pending |
| UPGRADE-03 | Phase 9 | Pending |
| UPGRADE-04 | Phase 9 | Pending |
| UPGRADE-05 | Phase 9 | Pending |
| UPGRADE-06 | Phase 9 | Pending |
| NEW-01 | Phase 10 | Pending |
| NEW-02 | Phase 10 | Pending |
| NEW-03 | Phase 10 | Pending |
| HOOK-01 | Phase 10 | Pending |
| HOOK-02 | Phase 10 | Pending |

**Coverage:**
- v0.3.0 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0

---
*Requirements defined: 2026-03-19*
*Last updated: 2026-03-19 after roadmap creation (phases 6-10 assigned)*
