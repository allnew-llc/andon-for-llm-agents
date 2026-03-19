---
phase: 13-five-whys-gotcha-loop
plan: "01"
subsystem: gotcha-candidate
tags: [gotcha, five-whys, candidate-generation, tdd, python]
dependency_graph:
  requires: ["hooks/gotcha_registry.py"]
  provides: ["hooks/gotcha_candidate.py", "tests/test_gotcha_candidate.py"]
---

## What was done

Created `hooks/gotcha_candidate.py` (210 lines) — a Python module that transforms Five Whys root cause + prevention text into validated Gotcha candidate YAML files in `gotchas/candidates/`.

**Key features:**
- `generate_candidate(root_cause, prevention, ...)` → writes YAML to `gotchas/candidates/GOTCHA-CAND-{timestamp}.yaml`
- Auto-extracts pattern regex from root cause keywords (stopwords removed, joined with `.*?`)
- Name derived from root cause (truncated at word boundary)
- Self-validates via `validate_gotcha()` from `gotcha_registry.py`
- Severity/source overridable, defaults to medium/five-whys

**TDD:** 24 tests across 8 test classes, all passing.

## Commits

- `398027f`: test(13-01): add failing tests for gotcha candidate generation (RED)
- `119fd93`: feat(13-01): implement gotcha candidate generation module (GREEN)

## Requirements

- [x] LOOP-01: Five Whys completion generates candidate YAML in gotchas/candidates/
- [x] LOOP-02: Candidate includes auto-extracted pattern from root cause

## Self-Check: PASSED

- hooks/gotcha_candidate.py exists (210 lines)
- tests/test_gotcha_candidate.py exists (24 tests, all pass)
- ruff lint: clean
- Full suite: no regressions
