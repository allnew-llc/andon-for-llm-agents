---
phase: 10-new-skills-on-demand-hooks
plan: "02"
subsystem: skills
tags: [cleanup-artifacts, careful, on-demand-hook, PreToolUse, HOOK-01, HOOK-02, NEW-02]
dependency_graph:
  requires: []
  provides: [cleanup-artifacts-skill, careful-skill, HOOK-02]
  affects: [skills/cleanup-artifacts, skills/careful]
tech_stack:
  added: []
  patterns: [on-demand-hook-pattern, state-file-toggle, PreToolUse-hook, bash-grep-pattern-matching]
key_files:
  created:
    - skills/cleanup-artifacts/SKILL.md
    - skills/cleanup-artifacts/scripts/cleanup-inventory.sh
    - skills/careful/SKILL.md
    - skills/careful/scripts/careful-guard.sh
    - skills/careful/references/hook-setup.md
  modified: []
decisions:
  - "careful-guard.sh uses Bash matcher (not Edit|Write like freeze) — guards command execution not file writes"
  - "rm regex matches any r+f flag combo (rf, fr, rfi, Rrf) using alternation pattern for robustness"
  - "cleanup-artifacts uses two-phase model: inventory always runs first, cleanup requires explicit /cleanup-artifacts clean"
  - "HOOK-01 verified: freeze-guard.sh exists at ~/.claude/hooks/ and is registered in settings.json under PreToolUse"
  - "Plugin data (CLAUDE_PLUGIN_DATA) is inventory-only in cleanup-artifacts — never auto-cleaned, requires explicit per-directory approval"
metrics:
  duration_minutes: 4
  completed_date: "2026-03-19"
  tasks_completed: 2
  files_created: 5
---

# Phase 10 Plan 02: Cleanup-Artifacts and Careful Skills Summary

Created two new skills and verified HOOK-01: cleanup-artifacts skill (two-phase inventory/cleanup utility for build artifacts) and careful skill (on-demand PreToolUse hook blocking 6 destructive Bash command patterns), confirming the freeze on-demand hook pattern is operational.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create cleanup-artifacts SKILL.md and cleanup-inventory.sh | 2b8b09c | skills/cleanup-artifacts/SKILL.md, skills/cleanup-artifacts/scripts/cleanup-inventory.sh |
| 2 | Create careful SKILL.md with on-demand hook (HOOK-02) and verify HOOK-01 | ca3aeb1 | skills/careful/SKILL.md, skills/careful/scripts/careful-guard.sh, skills/careful/references/hook-setup.md |

## What Was Built

### cleanup-artifacts Skill

Two-phase artifact cleanup skill for managing disk space. Phase 1 (inventory) always runs first via `scripts/cleanup-inventory.sh`, presenting a size table of common artifact locations. Phase 2 (cleanup) only executes on explicit `/cleanup-artifacts clean` with user confirmation.

Key design decisions:
- Plugin data (`CLAUDE_PLUGIN_DATA`) is inventory-only — sizes shown but never auto-cleaned
- Active pipeline guard: skip output/ if ios-app-factory lock files present
- Git-tracked files always marked "keep" in inventory
- DerivedData rebuild cost warning before confirming cleanup

The inventory script covers: Xcode DerivedData, ios-app-factory/output/, completed .planning/phases/, node_modules/, build/dist/, .next/, /tmp/claude-*, and CLAUDE_PLUGIN_DATA. Uses POSIX tools only (find, du, stat, awk) with macOS-compatible `stat -f '%Sm'` for mtimes.

### careful Skill (HOOK-02)

On-demand PreToolUse hook that blocks 6 destructive Bash command patterns following the freeze hook pattern exactly. The hook is permanently registered in `~/.claude/settings.json` with `"matcher": "Bash"` and activates/deactivates via `~/.claude/state/careful-state.json`.

Blocked patterns:
1. `rm -rf` / `rm -fr` (any flag combo with r+f)
2. `git push --force` / `git push -f`
3. `git reset --hard`
4. `DROP TABLE` / `DROP DATABASE` (case-insensitive)
5. `kubectl delete`
6. `docker system prune`

The rm regex uses alternation to catch any flag ordering: `-rf`, `-fr`, `-rfi`, `-Rrf`, etc. All other patterns use `grep -E` on the full command string.

### HOOK-01 Verification

Confirmed before creating careful skill:
- `~/.claude/hooks/freeze-guard.sh` exists (91 lines, executable)
- Registered in `~/.claude/settings.json` under `PreToolUse` with `matcher: "Edit|Write"`
- On-demand pattern verified: state file absent = hook exits 0 immediately
- freeze SKILL.md is the reference implementation for the on-demand pattern

## Deviations from Plan

None — plan executed exactly as written.

## Requirements Satisfied

- **NEW-02**: cleanup-artifacts skill created with inventory phase and cleanup phase
- **HOOK-01**: freeze on-demand hook verified as operational (Phase 9 delivery confirmed)
- **HOOK-02**: careful on-demand hook implemented following freeze pattern exactly

## Self-Check

Files exist check:
- skills/cleanup-artifacts/SKILL.md — created (91 lines, >= 60 required)
- skills/cleanup-artifacts/scripts/cleanup-inventory.sh — created (190 lines, executable)
- skills/careful/SKILL.md — created (125 lines, >= 70 required)
- skills/careful/scripts/careful-guard.sh — created (122 lines, executable, syntax valid)
- skills/careful/references/hook-setup.md — created (101 lines, >= 30 required)

Commits verified:
- 2b8b09c: feat(10-02): create cleanup-artifacts skill with inventory script
- ca3aeb1: feat(10-02): create careful skill with on-demand destructive command hook (HOOK-02)

## Self-Check: PASSED
