# Milestones

## v0.4.0 — Gotchas Engine (Shipped 2026-03-19)

**Goal:** Gotchas を静的テキストから構造化データ + 自動サーフェシングエンジンに進化させ、学習ループを閉じる

**Stats:** 4 phases (11-14), 7 plans, 39 files changed, +5,801 lines, 784 LOC in Python modules, 727 LOC in gotcha-stats.sh

**Delivered:**
- Gotchas Registry: YAML schema + loader (validate/discover/pack-extend), 7 core + 1 pack seed Gotchas
- ANDON Auto-Surfacing: 3-tier confidence matching (exact/partial/category), hook integration, prevention advice injection
- Five Whys → Gotcha Loop: candidate generation from root cause, gotcha-review subcommand, immediate promotion
- gotcha-stats.sh: hit rates, zero-hit staleness flags, prevention effectiveness metrics
- SKILL.md v1.2.0: Step 0 Gotcha Registry check, gotcha-review documented

**Phases:** 11-14 (GSD-tracked, fully planned and verified)

---

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
