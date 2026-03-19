---
phase: 11-gotchas-registry
plan: "01"
subsystem: gotchas-engine
tags: [registry, yaml-loader, schema-validation, pack-discovery, tdd]
dependency_graph:
  requires: []
  provides: [GotchaEntry, GotchaValidationError, load_gotchas, validate_gotcha]
  affects: [phase-12-auto-surfacing, phase-13-five-whys-loop]
tech_stack:
  added: []
  patterns: [dataclass-schema, multi-error-validation, glob-discovery, packs-pattern]
key_files:
  created:
    - hooks/gotcha_registry.py
    - tests/test_gotcha_registry.py
  modified: []
decisions:
  - "load_gotchas() raises on first invalid file (no silent skip) — fail-fast makes broken YAML easy to find"
  - "validate_gotcha() collects all errors before returning — callers get full error list not just the first"
  - "Duplicate ID detection uses dict(id -> source_path) — error message names both conflicting files"
  - "Optional fields (tags, examples, references) default to empty list — no None handling needed downstream"
metrics:
  duration: "2 minutes"
  completed: "2026-03-19"
  tasks_completed: 1
  files_created: 2
  files_modified: 0
---

# Phase 11 Plan 01: Gotcha Registry Schema and Loader Summary

Implemented `gotcha_registry.py` — the foundation of the Gotchas Engine v0.4.0 — with `GotchaEntry` dataclass, multi-error `validate_gotcha()`, and `load_gotchas()` with pack discovery via `packs/*/gotchas/` glob pattern.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (RED) | Write failing tests | 5ceaf48 | tests/test_gotcha_registry.py |
| 1 (GREEN) | Implement gotcha_registry module | 7308b4e | hooks/gotcha_registry.py |

## Implementation Details

### hooks/gotcha_registry.py (239 lines)

**GotchaEntry** — dataclass with 7 required fields (`id`, `name`, `pattern`, `severity`, `prevention`, `discovered`, `source`) and 3 optional fields (`tags`, `examples`, `references`) defaulting to empty lists.

**GotchaValidationError** — exception with `errors: list[str]` attribute for multi-error reporting. Message always includes the YAML file path.

**validate_gotcha(data: dict) -> list[str]** — pure function, collects all validation errors before returning. Checks: all 7 required fields present and non-empty, `severity` in valid set.

**load_gotchas(gotchas_dir, packs_dir=None) -> list[GotchaEntry]** — loads `*.yaml` from `gotchas_dir`, then discovers `packs/{name}/gotchas/*.yaml` when `packs_dir` is provided. Raises on first invalid file; raises on duplicate IDs across any source.

### tests/test_gotcha_registry.py (287 lines, 19 tests)

- `TestValidateGotcha` (8 tests): valid dict, missing fields, invalid severity, all-errors-collected, empty strings, all valid severities, optional fields absent/present
- `TestLoadGotchasCore` (6 tests): two valid files, invalid file raises, no-silent-failure, returns GotchaEntry, empty dir, non-yaml ignored
- `TestLoadGotchasPackDiscovery` (5 tests): pack discovery, merged core+pack, duplicate ID detection, pack without gotchas/ skipped, multiple packs

## Verification

```
python -m pytest tests/test_gotcha_registry.py -v   → 19 passed
ruff check hooks/gotcha_registry.py tests/test_gotcha_registry.py  → All checks passed
python -c "from gotcha_registry import ..."         → imports OK
python -m pytest tests/ -v                          → 165 passed (no regressions)
```

## Deviations from Plan

None — plan executed exactly as written.

## Decisions Made

1. **Fail-fast on first invalid file**: `load_gotchas()` raises `GotchaValidationError` immediately on the first bad YAML rather than collecting all file errors. This keeps the error surface small and makes the file path obvious in the message.

2. **Multi-error collect in `validate_gotcha()`**: Unlike the loader which fails fast per-file, `validate_gotcha()` collects all field-level errors within one dict before returning. Downstream callers get the full picture.

3. **Severity re-validation only when field is present**: The `validate_gotcha()` check for `severity` against valid values fires only when the field value is non-empty — avoiding duplicate "missing" + "invalid" error messages for the same field.

4. **`seen_ids` dict maps ID to source file path**: Enables precise duplicate error messages naming both the new file and the original source.

## Self-Check

```bash
[ -f "hooks/gotcha_registry.py" ] && echo "FOUND" || echo "MISSING"
[ -f "tests/test_gotcha_registry.py" ] && echo "FOUND" || echo "MISSING"
```

## Self-Check: PASSED

- hooks/gotcha_registry.py: FOUND
- tests/test_gotcha_registry.py: FOUND
- Commit 5ceaf48 (RED tests): FOUND
- Commit 7308b4e (GREEN implementation): FOUND
- 19 tests pass, 165 total suite tests pass
- ruff lint: clean
