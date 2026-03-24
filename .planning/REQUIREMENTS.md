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

- [x] **LOOP-01**: Five Whys completion generates a Gotcha candidate YAML file in gotchas/candidates/
- [x] **LOOP-02**: Gotcha candidate includes auto-extracted pattern from the Five Whys root cause
- [x] **LOOP-03**: /tps-kaizen gotcha-review subcommand lists candidates and promotes approved ones to gotchas/
- [x] **LOOP-04**: Promoted Gotchas are immediately available for ANDON auto-surfacing (no restart required)

### Analysis & Metrics

- [x] **METRIC-01**: gotcha-stats.sh script reports Gotcha hit rates (how often each Gotcha matched an incident)
- [x] **METRIC-02**: gotcha-stats.sh identifies Gotchas with zero hits (potentially stale or too narrow pattern)
- [x] **METRIC-03**: gotcha-stats.sh shows prevention effectiveness (incidents where Gotcha was surfaced vs resolved faster)

### Skill Integration

- [x] **INTEG-01**: tps-kaizen SKILL.md updated with gotcha-review subcommand documentation
- [x] **INTEG-02**: tps-kaizen andon Step 0 updated to include Gotcha Registry check alongside incident history check

## v0.5.0 Requirements

Requirements for Vault — Local-First Secret Management milestone.

### Vault Core

- [x] **VAULT-01**: Local-first secret management — macOS Keychain as single source, vault.yaml metadata only (no values)
- [x] **VAULT-02**: 33 platform drivers (Cloudflare, Vercel, AWS, GCP, Azure, K8s, Docker, Asian clouds, etc.)
- [x] **VAULT-03**: Drift audit, sync status matrix, notification integrations (Slack, Teams, Datadog, PagerDuty)
- [x] **VAULT-04**: Version history with SHA-256 fingerprints, rollback support, run/export/import commands
- [x] **VAULT-05**: Environment inheritance (dev/stg/prd) with chain resolution
- [x] **VAULT-06**: Localhost-only web UI (stdlib, no secret values in browser)
- [x] **VAULT-07**: Security hardening (argv exposure fix, shell=True removal, gitignore check, pipe-based passing)

## Future Requirements

### v0.6.0 Candidates

- **COLLAB-01**: Gotcha sharing across teams via git-based registry sync
- **ML-01**: Pattern similarity scoring using embedding distance (beyond regex)
- **VISUAL-01**: Gotcha dependency graph visualization
- **VAULT-HOOK-01**: PostToolUse hook — detect 401/403/unauthorized and suggest `andon vault audit`
- **VAULT-HOOK-02**: PreToolUse hook — scan git diff for API key patterns before commit
- **VAULT-HOOK-03**: PreToolUse hook — run `andon vault audit` before deploy commands

## Out of Scope

| Feature | Reason |
|---------|--------|
| Web-based Gotcha editor | CLI-first philosophy |
| Real-time Gotcha push notifications | Batch analysis sufficient |
| Auto-promotion of candidates (no human review) | Safety — human approval required for pattern promotion |
| Breaking changes to existing hooks | Backward compat constraint |
| Windows/Linux Keychain | macOS only for now |
| Team secret sharing | Keychain is personal |
| Auto key rotation | Manual trigger only |

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
| LOOP-01 | Phase 13 | Complete |
| LOOP-02 | Phase 13 | Complete |
| LOOP-03 | Phase 13 | Complete |
| LOOP-04 | Phase 13 | Complete |
| METRIC-01 | Phase 14 | Complete |
| METRIC-02 | Phase 14 | Complete |
| METRIC-03 | Phase 14 | Complete |
| INTEG-01 | Phase 14 | Complete (2026-03-19) |
| INTEG-02 | Phase 14 | Complete (2026-03-19) |

| VAULT-01 | Phase 15 | Complete (2026-03-24) |
| VAULT-02 | Phase 15 | Complete (2026-03-24) |
| VAULT-03 | Phase 15 | Complete (2026-03-24) |
| VAULT-04 | Phase 15 | Complete (2026-03-24) |
| VAULT-05 | Phase 15 | Complete (2026-03-24) |
| VAULT-06 | Phase 15 | Complete (2026-03-24) |
| VAULT-07 | Phase 15 | Complete (2026-03-24) |

**Coverage:**
- v0.4.0 requirements: 17 total, 17 mapped, 0 unmapped ✓
- v0.5.0 requirements: 7 total, 7 mapped, 0 unmapped ✓

---
*Requirements defined: 2026-03-19*
*Last updated: 2026-03-24 — v0.5.0 vault requirements added, traceability mapped to phase 15*
