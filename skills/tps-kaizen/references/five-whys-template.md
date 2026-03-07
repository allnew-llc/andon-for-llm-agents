# Five Whys Analysis — Detailed Template and Guide

## Overview

Five Whys is a root cause analysis technique systematized by Taiichi Ohno (father of TPS).
From surface symptoms, repeat "Why?" to reach the **true cause**.

> "By asking 'Why?' five times, the root cause of a problem becomes clear." — Taiichi Ohno

---

## Procedure

### Preparation

1. **Define the problem in one sentence** — eliminate ambiguity, state facts
2. **Gather related data** — logs, code, config files, commit history
3. **Verify with Genchi Genbutsu** — look at actual files, not memory or assumptions

### Analysis

For each Why:
1. **Form a hypothesis** — "Could X be the cause?"
2. **Verify** — check actual code / logs / config
3. **Record facts** — document verification results
4. **Proceed to next Why** — "Then why did THAT happen?"

### Completion Criteria

- Reached a **process or system-level cause**
- Further "Why?" only produces "human made a mistake" with no deeper answer
- Reached an **actionable cause** (don't stop at causes you can't fix)

---

## Template

```markdown
# Five Whys Analysis Report

## Problem Definition

**Date**: YYYY-MM-DD
**Problem**: [objective fact in one sentence — include subject, predicate, specifics]
**Impact**: [what is blocked, who is affected]

## Analysis

### Why 1: Why did [problem] happen?

**Hypothesis**: [possible direct cause]
**Verification**:
```
[command run / file path checked]
[output]
```
**Conclusion**: [fact based on verification]

---

### Why 2: Why did [Why 1 conclusion] happen?

**Hypothesis**: [possible cause]
**Verification**:
```
[command run / file path checked]
[output]
```
**Conclusion**: [fact based on verification]

---

### Why 3: Why did [Why 2 conclusion] happen?

**Hypothesis**: [possible cause]
**Verification**:
```
[command run / file path checked]
[output]
```
**Conclusion**: [fact based on verification]

---

### Why 4: Why did [Why 3 conclusion] happen?

**Hypothesis**: [possible cause]
**Verification**:
```
[command run / file path checked]
[output]
```
**Conclusion**: [fact based on verification]

---

### Why 5: Why did [Why 4 conclusion] happen?

**Hypothesis**: [possible cause]
**Verification**:
```
[command run / file path checked]
[output]
```
**Conclusion**: [fact based on verification]

---

## Root Cause

**Root cause**: [1-2 sentence summary]
**Category**: [process defect / tool gap / knowledge gap / design flaw / spec omission]

## Prevention Measures

| # | Measure | Level | Implementation Location | Deadline |
|---|---------|-------|------------------------|----------|
| 1 | [measure] | L1-poka-yoke / L2-auto-detect / L3-standardize / L4-alert | [file path] | [date] |
| 2 | [measure] | [level] | [file path] | [date] |

## Horizontal Sweep

Could the same problem occur elsewhere?
- [ ] Check other modules for the same pattern
- [ ] Check other pipeline phases for the same risk
- [ ] Check templates/config for the same defect
```

---

## Branching Analysis

When the cause isn't singular, branch the causal chain:

```
Problem: Build failed
├── Why 1a: Dependency library not found
│   └── Why 2a: Package.resolved is stale
│       └── Why 3a: CI doesn't run package resolve
│           └── Root cause A: CI config missing package resolution step
│
└── Why 1b: Compile error
    └── Why 2b: API had breaking change
        └── Why 3b: Dependency version wasn't pinned
            └── Root cause B: No version pinning policy
```

---

## Common Mistakes

### 1. Stopping at "human error"

```
BAD: Why 3: Developer forgot to write tests → done
GOOD: Why 3: Developer forgot to write tests
      Why 4: No process to verify test existence
      Why 5: CI doesn't have test coverage check
```

### 2. Not verifying hypotheses

```
BAD: Why 2: Probably the config was wrong
GOOD: Why 2: project.yml TARGETED_DEVICE_FAMILY was "1,2" (confirmed: line 47)
```

### 3. Stopping at unfixable causes

```
BAD: Root cause: Apple's API docs are confusing → no action
GOOD: Root cause: No standard procedure for verifying Apple API behavior → action: add checklist
```

### 4. Fixating on exactly 5

- If you reach root cause at 3, stop at 3
- If 5 isn't enough, continue to 7 or 10
- The criterion is reaching a **fixable system issue**, not hitting a number
