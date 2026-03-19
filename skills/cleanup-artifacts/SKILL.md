---
name: cleanup-artifacts
description: "Use when: disk space, cleanup, build cache, derived data, old artifacts, orphaned outputs, pipeline artifacts, DerivedData, node_modules. Inventories and cleans pipeline artifacts, build caches, and orphaned outputs."
version: 1.0.0
---

# /cleanup-artifacts — Build Artifact and Cache Cleanup

Two-phase approach to safely reclaim disk space: always inventory first, clean only on explicit confirmation. This prevents accidental deletion of files that look like artifacts but are still needed.

## When to Use This Skill

| Situation | Trigger |
|-----------|---------|
| Low disk space warning | Running out of space on development machine |
| After pipeline runs | ios-app-factory output/ has accumulated many generated apps |
| Periodic maintenance | Monthly cleanup of DerivedData and build caches |
| Before archiving project | Reduce repository/backup size before archiving |

## Usage

```
/cleanup-artifacts                # Phase 1: inventory only (safe — no deletion)
/cleanup-artifacts clean          # Phase 1 inventory + Phase 2 cleanup (with confirmation)
/cleanup-artifacts clean --dry-run  # Preview what would be deleted without deleting
```

## Behavior

### Phase 1: Inventory (always runs first)

1. Run `scripts/cleanup-inventory.sh` to scan for artifacts at standard locations
2. Present results as a table:

   | Location | Type | Size | Last Modified | Recommendation |
   |----------|------|------|---------------|----------------|
   | ~/Library/Developer/Xcode/DerivedData/ | build-cache | 4.2G | 2026-03-15 | safe to delete |
   | ios-app-factory/output/ | pipeline-output | 890M | 2026-03-19 | review before delete |

3. Categories scanned:
   - **build caches** — Xcode DerivedData, .next/, .turbo/
   - **derived data** — simulator runtimes, device support files
   - **pipeline outputs** — ios-app-factory generated apps and reports
   - **node_modules** — JavaScript dependency trees (rebuilds with npm install)
   - **temporary files** — /tmp/claude-*, OS temp directories
4. Show total disk space recoverable before proceeding

### Phase 2: Cleanup (only on explicit `/cleanup-artifacts clean`)

1. Present the inventory table again with recommended deletions highlighted
2. **Always confirm with user before deleting anything** — ask "OK to delete these N items?" and wait for explicit yes
3. Execute `rm -rf` on confirmed targets only
4. Skip any item the user marks as "keep"
5. Report bytes reclaimed after cleanup

## Default Scan Locations

These locations are scanned by default. Override by setting environment variables or passing paths as arguments.

| Path | Type | Notes |
|------|------|-------|
| `~/Library/Developer/Xcode/DerivedData/` | build-cache | Xcode build intermediates |
| `ios-app-factory/output/` | pipeline-output | Generated app artifacts |
| `.planning/phases/*/` | planning-artifact | Only completed phases (has SUMMARY.md) |
| `**/node_modules/` | dependency | Rebuild with npm install |
| `**/build/` and `**/dist/` | build-output | Compiler output directories |
| `**/.next/` | build-cache | Next.js framework cache |
| `/tmp/claude-*` | temp | Claude temporary files |
| `${CLAUDE_PLUGIN_DATA}/` | plugin-data | **Inventory only — never auto-clean** |

## Gotchas

### Plugin Data is Sacred

Never auto-delete `${CLAUDE_PLUGIN_DATA}/` contents (kaizen incidents, qc assessments, state files). The plugin data directory contains audit trails and persistent state that cannot be reconstructed if deleted. The inventory script reports sizes for visibility, but cleanup of `${CLAUDE_PLUGIN_DATA}/` contents requires explicit per-directory approval naming the specific subdirectory — a blanket "clean everything" confirmation does not cover plugin data.

### DerivedData Rebuild Cost

Deleting DerivedData forces a full Xcode rebuild on the next build. For large projects (100k+ lines of Swift), this can take 10–30 minutes. Always warn the user of the expected rebuild time before confirming DerivedData cleanup. Check the project size with `du -sh ~/Library/Developer/Xcode/DerivedData/<ProjectName>/` and estimate based on ~1 minute per 10k source lines as a rough guide.

### Active Pipeline Guard

If any ios-app-factory pipeline is currently running, skip that output directory. Check for lock files: `ls ios-app-factory/output/.running 2>/dev/null` or look for a recent `pipeline.log` with an open timestamp. Deleting output files mid-pipeline causes silent corruption — the next pipeline phase will fail to find expected artifacts with no clear error message.

### Git-Tracked Files

Never delete files that are tracked by git. The inventory script checks `git ls-files --error-unmatch <path>` status and marks tracked files as "keep" in the Recommendation column. Even if a file is in a directory that looks like an artifact location (e.g., a committed `build/version.txt`), tracked files must be preserved.

## Additional Resources

- `scripts/cleanup-inventory.sh` — Scan script that reports artifact sizes and locations
