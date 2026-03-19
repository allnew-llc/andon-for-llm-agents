# Requirements: ANDON for LLM Agents

**Defined:** 2026-03-19
**Core Value:** Stop defects from flowing downstream and learn from every failure

## v0.4.0 Requirements

Requirements for Gotchas Engine milestone. Each maps to roadmap phases.

### Gotchas Registry

- [x] **REG-01**: Gotchas Registry schema defined (YAML format with id, name, pattern, severity, prevention, discovered, source fields)
- [x] **REG-02**: gotchas/ directory exists in repo root with at least 5 seed Gotchas from existing tps-kaizen Gotchas section
- [x] **REG-03**: Registry loader (Python) can parse all YAML files in gotchas/ and validate schema
- [x] **REG-04**: Knowledge Packs can contribute pack-specific Gotchas via packs/{pack-name}/gotchas/ directory

### ANDON Auto-Surfacing

- [x] **SURF-01**: ANDON open hook auto-loads Gotchas Registry and matches current error against pattern fields
- [x] **SURF-02**: Matching Gotchas are injected into additionalContext with prevention advice when ANDON opens
- [x] **SURF-03**: Match results include confidence score (exact match, partial match, category match)
- [x] **SURF-04**: Multiple Gotcha matches are ranked by relevance and presented in order

### Five Whys → Gotcha Loop

- [ ] **LOOP-01**: Five Whys completion generates a Gotcha candidate YAML file in gotchas/candidates/
- [ ] **LOOP-02**: Gotcha candidate includes auto-extracted pattern from the Five Whys root cause
- [x] **LOOP-03**: /tps-kaizen gotcha-review subcommand lists candidates and promotes approved ones to gotchas/
- [x] **LOOP-04**: Promoted Gotchas are immediately available for ANDON auto-surfacing (no restart required)

### Analysis & Metrics

- [ ] **METRIC-01**: gotcha-stats.sh script reports Gotcha hit rates (how often each Gotcha matched an incident)
- [ ] **METRIC-02**: gotcha-stats.sh identifies Gotchas with zero hits (potentially stale or too narrow pattern)
- [ ] **METRIC-03**: gotcha-stats.sh shows prevention effectiveness (incidents where Gotcha was surfaced vs resolved faster)

### Skill Integration

- [ ] **INTEG-01**: tps-kaizen SKILL.md updated with gotcha-review subcommand documentation
- [ ] **INTEG-02**: tps-kaizen andon Step 0 updated to include Gotcha Registry check alongside incident history check

## Future Requirements

### v0.5.0 Candidates

- **COLLAB-01**: Gotcha sharing across teams via git-based registry sync
- **ML-01**: Pattern similarity scoring using embedding distance (beyond regex)
- **VISUAL-01**: Gotcha dependency graph visualization

## Out of Scope

| Feature | Reason |
|---------|--------|
| Web-based Gotcha editor | CLI-first philosophy |
| Real-time Gotcha push notifications | Batch analysis sufficient |
| Auto-promotion of candidates (no human review) | Safety — human approval required for pattern promotion |
| Breaking changes to existing hooks | Backward compat constraint |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REG-01 | Phase 11 | Complete |
| REG-02 | Phase 11 | Complete |
| REG-03 | Phase 11 | Complete |
| REG-04 | Phase 11 | Complete |
| SURF-01 | Phase 12 | Complete |
| SURF-02 | Phase 12 | Complete |
| SURF-03 | Phase 12 | Complete |
| SURF-04 | Phase 12 | Complete |
| LOOP-01 | Phase 13 | Pending |
| LOOP-02 | Phase 13 | Pending |
| LOOP-03 | Phase 13 | Complete |
| LOOP-04 | Phase 13 | Complete |
| METRIC-01 | Phase 14 | Pending |
| METRIC-02 | Phase 14 | Pending |
| METRIC-03 | Phase 14 | Pending |
| INTEG-01 | Phase 14 | Pending |
| INTEG-02 | Phase 14 | Pending |

**Coverage:**
- v0.4.0 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-19*
*Last updated: 2026-03-19 — traceability mapped to phases 11-14*
