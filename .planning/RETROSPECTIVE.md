# Retrospective

## Milestone: v0.4.0 — Gotchas Engine

**Shipped:** 2026-03-19
**Phases:** 4 (11-14) | **Plans:** 7 | **Duration:** Single session (continuation from v0.3.0)

### What Was Built
- Gotchas Registry: YAML schema + Python loader with pack discovery (239 lines, 19 tests)
- ANDON auto-surfacing: 3-tier confidence matching engine (335 lines, 12 tests) integrated into runtime hook
- Five Whys → Gotcha candidate loop: auto-generation from root cause (210 lines, 24 tests) + gotcha-review subcommand
- gotcha-stats.sh: hit rates, staleness detection, prevention effectiveness (727 lines)
- tps-kaizen SKILL.md v1.2.0: Step 0 Registry check + gotcha-review documented

### What Worked
- **TDD for Python modules**: All 3 modules (registry, surfacer, candidate) built TDD-first — caught deviation issues early
- **Phase 12+13 parallel execution**: Independent features executed simultaneously, no merge conflicts
- **Consistent script patterns**: gotcha-stats.sh reused the same awk/POSIX patterns from v0.3.0 scripts
- **Article-driven → engine-driven**: v0.3.0 laid the static Gotchas foundation, v0.4.0 naturally built on top

### What Was Inefficient
- **13-01 agent truncation**: One executor agent stopped mid-task (GREEN committed but no SUMMARY). Required manual recovery.
- **REQUIREMENTS.md tracking lag**: LOOP-01/02 not marked Complete by executor — caught by verifier, fixed manually
- **gotcha-stats.sh is large** (727 lines): The keyword-overlap matching reimplemented in bash is verbose compared to Python. Future consideration: share matching logic.

### Patterns Established
- **Gotcha lifecycle**: YAML → Registry → Surfacing → Candidate → Review → Promotion → Stats
- **TDD for hook modules**: RED/GREEN/REFACTOR with explicit test behavior specs
- **Graceful import failure**: Surfacer import wrapped in try/except so ANDON never blocked by missing module
- **Re-run matching**: Stats script re-computes matches rather than reading persisted surfacing data — simpler architecture

### Key Lessons
- Structured data (YAML) with a loader is fundamentally better than markdown text for machine consumption
- The learning loop (incident → Five Whys → Gotcha → prevention) is the core value proposition of the Gotchas Engine
- Human approval for promotion is the right safety constraint — auto-promotion would risk noisy/incorrect patterns

### Cost Observations
- Model mix: sonnet for all subagents, opus for orchestration (same as v0.3.0)
- Sessions: 1 continuous session (spanning both v0.3.0 and v0.4.0)
- Notable: 9 phases (5 + 4) planned and executed in a single conversation

---

## Milestone: v0.3.0 — Skill Quality & Ecosystem

**Shipped:** 2026-03-19
**Phases:** 5 (6-10) | **Plans:** 10 | **Duration:** Single session

### What Was Built
- tps-kaizen SKILL.md upgraded with trigger description, 7 Gotchas, related_skills, 3 analysis scripts, Step 0 incident history
- /qc-audit skill with self-assessment workflow, trend/gate-health/collect scripts
- 6 standalone skills upgraded to SKILL.md directory structure with progressive disclosure
- 4 new skills (freee-analysis, standup, cleanup-artifacts, careful)
- On-demand hooks pattern established (freeze verified, careful created)

### What Worked
- **Parallel execution in waves**: Phases 8+9 could overlap; plans within waves ran parallel — significant time savings
- **Pattern establishment early**: Phase 6 set the SKILL.md pattern, all subsequent phases followed it naturally
- **POSIX-only scripts**: No dependency issues, all scripts passed bash -n and --help on first try
- **Article-driven requirements**: Clear source of truth made requirements definition fast
- **GSD workflow**: Plan→verify→execute→verify cycle caught issues before they compounded

### What Was Inefficient
- **Phase 8 ROADMAP marked "In Progress"**: The roadmap analyzer showed Phase 8 as incomplete even though all plans had summaries — likely a race condition from parallel executor updates
- **Summary extraction failed**: `summary-extract --fields one_liner` returned None for all summaries — SUMMARY.md frontmatter may not have the expected `one_liner` field

### Patterns Established
- **Trigger-focused descriptions**: "Use when: error, failure, incident..." pattern for all skills
- **Gotchas section**: Named failure patterns with structural explanations
- **Progressive disclosure**: SKILL.md index + references/ for large content
- **On-demand hooks**: State file toggle (activate/deactivate), permanent registration, zero overhead when inactive
- **Script portability**: bash 3.2+, POSIX tools only, awk for JSON extraction instead of jq

### Key Lessons
- Description field optimization has the highest ROI for skill triggering accuracy
- Scripts give Claude composable tools — better than instructions alone
- On-demand hooks solve the "too strict globally, needed sometimes" problem elegantly

### Cost Observations
- Model mix: 100% sonnet for subagents (researcher, planner, checker, executor, verifier), opus for orchestration
- Sessions: 1 continuous session
- Notable: 5 phases planned and executed in a single conversation

---

## Cross-Milestone Trends

| Metric | v0.1.0 | v0.2.0 | v0.3.0 | v0.4.0 |
|--------|--------|--------|--------|--------|
| Phases | 3 | 2 | 5 | 4 |
| Plans | — | — | 10 | 7 |
| GSD-tracked | No | Partial | Full | Full |
| Verification | — | — | All passed | All passed |
| TDD | — | — | No | Yes (3 modules) |
| Python LOC | — | — | 0 | 784 |
