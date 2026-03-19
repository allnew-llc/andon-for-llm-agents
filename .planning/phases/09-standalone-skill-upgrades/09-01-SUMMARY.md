---
phase: 09-standalone-skill-upgrades
plan: 01
subsystem: skill-documentation
tags: [freeze, cherry-pick-prod, skill-upgrade, directory-structure, on-demand-hooks, progressive-disclosure]

# Dependency graph
requires:
  - "06-tps-kaizen-core-quality (SKILL.md pattern established)"
provides:
  - "freeze/SKILL.md with on-demand hook pattern, trigger-focused description, 5 named Gotchas"
  - "freeze/references/hook-setup.md with detailed hook registration instructions"
  - "cherry-pick-prod/SKILL.md with trigger-focused description, 5 named Gotchas with explanatory paragraphs"
  - "cherry-pick-prod/references/pr-template.md with PR template and extended body guidance"
affects:
  - "09-02-PLAN.md (same SKILL.md directory pattern applied to next batch)"
  - "09-03-PLAN.md (same pattern)"
  - "10-new-skills (on-demand hook pattern established by freeze/)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "SKILL.md directory structure pattern: flat .md → directory with SKILL.md + references/"
    - "On-demand hook pattern: permanent registration + state file toggle for zero-overhead activation"
    - "Gotchas pattern: named ### headings with explanatory paragraphs (not bullet points)"
    - "Progressive disclosure pattern: core content in SKILL.md, details in references/"
    - "Trigger-focused description: 'Use when: <keyword1>, <keyword2>...' for Claude invocation matching"

key-files:
  created:
    - "skills/freeze/SKILL.md"
    - "skills/freeze/references/hook-setup.md"
    - "skills/cherry-pick-prod/SKILL.md"
    - "skills/cherry-pick-prod/references/pr-template.md"
  modified: []

key-decisions:
  - "On-demand hook pattern: registration in settings.json is permanent, activation/deactivation via state file creates zero-overhead when inactive"
  - "Gotchas upgraded from bullet points to named ### patterns with explanatory paragraphs — explains WHY each failure mode occurs, not just that it exists"
  - "references/ files contain detail that first-time readers don't need but can find when required — progressive disclosure reduces cognitive load on SKILL.md"

# Metrics
metrics:
  duration_minutes: 5
  completed_date: "2026-03-19"
  tasks_completed: 2
  tasks_total: 2
  files_created: 4
  files_modified: 0
---

# Phase 9 Plan 01: Standalone Skill Upgrades (freeze + cherry-pick-prod) Summary

**One-liner:** Upgraded freeze and cherry-pick-prod from flat .md files to directory-based SKILL.md structure with trigger-focused descriptions, named Gotchas, and progressive disclosure via references/ subdirectories.

## Accomplishments

### Task 1: freeze/ SKILL.md

- Replaced `~/.claude/skills/freeze.md` with `freeze/SKILL.md` directory structure
- Added trigger-focused frontmatter description: "On-demand directory lock — blocks Edit/Write outside a frozen directory via PreToolUse hook. Use when: protecting files, preventing accidental edits, locking directory scope, isolating changes to one directory"
- Added section explaining the on-demand hook pattern: hook registered once in settings.json, activation/deactivation via state file toggle, zero overhead when state file absent
- Added Gotchas section with 5 named patterns using `### ` headings: Session Restart After Registration, Symlink Resolution, State File Deletion Semantics, Self-Management Allowed, Freeze Directory Boundary
- Extracted hook registration JSON snippet, setup verification script, and step-by-step first-time setup instructions to `references/hook-setup.md`
- Added Additional Resources section pointing to `references/hook-setup.md`
- Deleted old flat `freeze.md`

### Task 2: cherry-pick-prod/ SKILL.md

- Replaced `~/.claude/skills/cherry-pick-prod.md` with `cherry-pick-prod/SKILL.md` directory structure
- Added trigger-focused frontmatter description: "Safely cherry-pick commits to a release/prod branch using an isolated git worktree. Use when: hotfix, backport, cherry-pick, production fix, release branch patch, emergency deploy"
- Kept all 6 workflow steps intact (Preflight, Create Worktree, Cherry-Pick, Verify, Push & PR, Cleanup)
- Upgraded 5 bullet-point gotchas to named `### ` patterns with explanatory paragraphs documenting why each failure mode occurs: Stale Target Branch, Force Push Prohibition, Mid-Sequence Abort, Worktree Cleanup on Failure, Merge Commit Parents
- Extracted PR template and extended body guidance to `references/pr-template.md`
- Added Additional Resources section pointing to `references/pr-template.md`
- Deleted old flat `cherry-pick-prod.md`

## Decisions Made

1. **On-demand hook pattern framing**: Explicitly documented that freeze-guard.sh registration is permanent but activation is on-demand via state file. This pattern is the conceptual foundation for Phase 10's /careful skill.

2. **Gotchas as paragraphs not bullets**: Each Gotcha explains *why* the failure occurs (not just what), enabling readers to reason about edge cases rather than memorizing rules.

3. **Progressive disclosure**: Heavy operational details (hook JSON, PR template extended sections) extracted to references/ files. The SKILL.md reads quickly; details are available when needed.

4. **Skills tracked in project git**: Files created in both `~/.claude/skills/` (global availability) and `skills/` (project git tracking), consistent with the pattern from Phases 6-8.

## Deviations from Plan

None — plan executed exactly as written.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1: freeze/ SKILL.md | de75bb1 | feat(09-01): upgrade freeze.md to freeze/ SKILL.md with on-demand hook pattern |
| Task 2: cherry-pick-prod/ SKILL.md | 0d5d9ff | feat(09-01): upgrade cherry-pick-prod.md to cherry-pick-prod/ SKILL.md with Gotchas |

## Self-Check: PASSED

Files exist:
- skills/freeze/SKILL.md: FOUND
- skills/freeze/references/hook-setup.md: FOUND
- skills/cherry-pick-prod/SKILL.md: FOUND
- skills/cherry-pick-prod/references/pr-template.md: FOUND

Commits exist:
- de75bb1: FOUND
- 0d5d9ff: FOUND

All 7 plan verification criteria: PASSED
