# ANDON for LLM Agents

## What This Is

TPS (Toyota Production System) inspired safety and continuous improvement framework for LLM coding agents. Provides Claude Code hooks that detect anomalies, stop defect propagation, perform root cause analysis (Five Whys), and standardize learnings. Open source (Apache 2.0), published as `andon-for-llm-agents` on PyPI.

## Core Value

Stop defects from flowing downstream and learn from every failure — applied to LLM-assisted coding through Jidoka (autonomation) and Kaizen (continuous improvement).

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ **JIDOKA-01**: ANDON line stop on non-zero exit codes — v0.1.0
- ✓ **JIDOKA-02**: Forward-progress blocking (push, deploy, publish) during ANDON — v0.1.0
- ✓ **JIDOKA-03**: ANDON close with 4-artifact validation (evidence, analysis, actions, report) — v0.1.0
- ✓ **JIDOKA-04**: Confidence threshold (0.70) for close approval — v0.1.0
- ✓ **JIDOKA-05**: ANDON rollback support — v0.1.0
- ✓ **KAIZEN-01**: Five Whys root cause analysis framework — v0.1.0
- ✓ **KAIZEN-02**: Kaizen learning capture and routing — v0.1.0
- ✓ **KAIZEN-03**: Improvement Kata cycle (understand/grasp/target/experiment) — v0.1.0
- ✓ **KAIZEN-04**: 3M waste audit (Muda/Mura/Muri) — v0.1.0
- ✓ **GUARD-01**: Analysis paralysis detection (consecutive read-only tools) — v0.2.0
- ✓ **GUARD-02**: Context quality monitor (tool call count proxy) — v0.2.0
- ✓ **GUARD-03**: Self-check protocol (artifact size/parse/key validation) — v0.2.0
- ✓ **GUARD-04**: Deviation rules hierarchy (Level 1-4 action system) — v0.2.0
- ✓ **PACK-01**: Domain-specific knowledge packs (financial, GDPR, HIPAA, iOS, japan-legal) — v0.1.0
- ✓ **SEC-01**: Process-safe state files with flock — v0.2.0
- ✓ **SEC-02**: Prompt injection boundary markers — v0.2.0
- ✓ **SEC-03**: Path traversal validation — v0.2.0
- ✓ **SEC-04**: Secret redaction patterns — v0.2.0

- ✓ **SKILL-01**: tps-kaizen trigger-focused description (14 keywords) — v0.3.0
- ✓ **SKILL-02**: tps-kaizen Gotchas section (7 named failure patterns) — v0.3.0
- ✓ **SKILL-03**: aggregate-incidents.sh (incident pattern clustering) — v0.3.0
- ✓ **SKILL-04**: five-whys-validator.sh (depth/verification validation) — v0.3.0
- ✓ **SKILL-05**: quality-trend.sh (QC assessment trend timeline) — v0.3.0
- ✓ **SKILL-06**: andon Step 0 incident history auto-reference — v0.3.0
- ✓ **SKILL-07**: related_skills composability links — v0.3.0
- ✓ **QC-01~05**: /qc-audit skill with trend, gate-health, collect-assessments — v0.3.0
- ✓ **UPGRADE-01~06**: 6 standalone skills → SKILL.md structure — v0.3.0
- ✓ **NEW-01~03**: freee-analysis, cleanup-artifacts, standup skills — v0.3.0
- ✓ **HOOK-01~02**: On-demand hooks (freeze verified, careful created) — v0.3.0

- ✓ **REG-01~04**: Gotchas Registry (YAML schema, loader, 7+1 seed, pack extension) — v0.4.0
- ✓ **SURF-01~04**: ANDON auto-surfacing (3-tier confidence, hook integration) — v0.4.0
- ✓ **LOOP-01~04**: Five Whys → Gotcha loop (candidate gen, review, promotion) — v0.4.0
- ✓ **METRIC-01~03**: gotcha-stats.sh (hit rates, staleness, effectiveness) — v0.4.0
- ✓ **INTEG-01~02**: SKILL.md gotcha-review + Step 0 Registry check — v0.4.0

### Active

<!-- Current scope. Building toward these. -->

(Defining in next milestone)

### Out of Scope

- GUI dashboard — CLI-first, no web UI
- Non-Claude Code agents — Claude Code hooks only for now
- Real-time metrics collection — Batch analysis sufficient

## Context

- Published on GitHub: allnew-llc/andon-for-llm-agents
- Python 3.10+, single dependency (PyYAML)
- 7 skills in repo: tps-kaizen, qc-audit, freee-analysis, standup, cleanup-artifacts, careful (+ 6 upgraded user skills)
- 7 analysis scripts (bash, POSIX-only) + 3 Python modules (registry, surfacer, candidate)
- Gotchas Registry: 7 core + 1 pack YAML, auto-surfacing on ANDON open, Five Whys → candidate loop
- Integrated with AllNew LLC's ios-app-factory pipeline
- v0.3.0: Anthropic best practices, v0.4.0: Gotchas Engine (structured data + learning loop)

## Constraints

- **License**: Apache 2.0 — all additions must be compatible
- **Python**: >=3.10, minimal dependencies
- **Backward compat**: Existing hooks/packs must continue working
- **OSS**: All improvements must be suitable for public repository

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Shell hooks + Python guards | Claude Code hooks are shell-based, complex logic in Python | ✓ Good |
| Knowledge Packs for domain rules | Extensible without core changes | ✓ Good |
| Deviation rules hierarchy (L1-L4) | Different failures need different responses | ✓ Good |
| TPS terminology throughout | Consistent mental model, educational value | ✓ Good |
| Trigger-focused skill descriptions | Article: "description is for the model, not humans" | ✓ Good |
| POSIX-only bash scripts (no jq) | OSS portability — works on any machine | ✓ Good |
| On-demand hooks via state file toggle | Session-scoped activation without permanent overhead | ✓ Good |
| Progressive disclosure via references/ | Keep SKILL.md lightweight, detail on demand | ✓ Good |
| Gotchas as structured YAML (not markdown) | Machine-readable, pattern-matchable, pack-extensible | ✓ Good |
| 3-tier confidence (exact/partial/category) | Ranked matching avoids false positives | ✓ Good |
| Human approval for Gotcha promotion | Safety — no auto-promotion of candidate patterns | ✓ Good |
| Re-run matching in stats (not persisted) | Simpler architecture, no surfacing output schema dependency | ✓ Good |

---
*Last updated: 2026-03-19 after v0.4.0 milestone*
