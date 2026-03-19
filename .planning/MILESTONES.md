# Milestones

## v0.3.0 — Skill Quality & Ecosystem (Shipped 2026-03-19)

**Goal:** Anthropic ベストプラクティスに基づくスキル品質向上と Claude 環境エコシステム拡充

**Stats:** 5 phases (6-10), 10 plans, 16 feat commits, 50 files changed, +8,143 lines, 4,464 LOC in skills/

**Delivered:**
- tps-kaizen SKILL.md upgraded: trigger-focused description (14 keywords), 7 Gotchas, related_skills, Step 0 incident history
- 3 analysis scripts: aggregate-incidents.sh, five-whys-validator.sh, quality-trend.sh
- /qc-audit skill: quality self-assessment, trend analysis, gate-health correlation + 3 scripts
- 6 standalone skills upgraded to SKILL.md structure with progressive disclosure
- 4 new skills: freee-analysis, standup, cleanup-artifacts, careful
- On-demand hooks pattern: freeze (HOOK-01 verified) + careful (HOOK-02)

**Phases:** 6-10 (GSD-tracked, fully planned and verified)

---

## v0.1.0 — Foundation (Shipped 2026-03-10)

**Goal:** Core ANDON safety framework with TPS principles

**Delivered:**
- Jidoka: ANDON open/close/rollback lifecycle
- Kaizen: Five Whys, learning capture, improvement kata, 3M audit
- Knowledge Packs: financial, GDPR, HIPAA, iOS, japan-legal
- TPS Kaizen skill for Claude Code
- CLI entry point (`andon`)

**Phases:** 1-3 (initial development, not GSD-tracked)

## v0.2.0 — Hardening (Shipped 2026-03-10)

**Goal:** Production hardening with advanced guards and security

**Delivered:**
- Analysis paralysis guard
- Context quality monitor
- Self-check protocol enhancement
- Deviation rules hierarchy (L1-L4)
- Security hardening (flock, atomic writes, injection boundaries, path validation, secret redaction)
- Legal accuracy fixes (compliance → reference patterns)

**Phases:** 4-5 (GSD-integrated, not formally tracked)

---
*Last phase number: 5*
