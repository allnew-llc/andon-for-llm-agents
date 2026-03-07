# Jidoka (Autonomation) — Detailed Anomaly Response Guide

## Overview

Jidoka originates from Sakichi Toyoda's automatic loom invention.
When a thread breaks, the machine **stops automatically** — producing zero defective goods.
This principle is applied to software development.

---

## 4-Step Cycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐
│ 1. Detect │ →  │ 2. Stop  │ →  │ 3. Fix   │ →  │ 4. Investigate│
└──────────┘    └──────────┘    └──────────┘    └──────────────┘
     ↑                                                │
     └──────── Update standard work ← Prevention ─────┘
```

---

## Step 1: Detect

### Purpose
Record the problem **as objective fact**.

### Checklist

- [ ] Described what happened (symptoms) objectively?
- [ ] When did it occur? (timestamp)
- [ ] Where did it occur? (file, line number, phase, tool)
- [ ] Reproduction steps clear?
- [ ] Full error message / log saved?

### Template

```markdown
## ANDON Report

- **Timestamp**: YYYY-MM-DD HH:MM
- **Detection method**: [test failure / build error / runtime exception / rejection / manual]
- **Location**: [file:line / phase / tool name]
- **Symptom**: [objective facts only — no speculation]
- **Error message**:
  ```
  [paste complete error message]
  ```
- **Reproduction steps**:
  1. [step 1]
  2. [step 2]
  3. [result]
- **Impact**: [which downstream processes are blocked]
- **Related files**: [list of changed/related files]
```

### Anti-patterns

- **Writing speculation as fact**: "Probably caused by X" → NO. Investigate in Step 4
- **Truncating error messages**: "Build failed" → NO. Paste the full message
- **Underestimating impact**: "Not a big deal" → NO. List all blocked downstream processes

---

## Step 2: Stop

### Purpose
**Never pass defects downstream.**

### Stop Actions in Software

| Situation | Stop Action |
|-----------|------------|
| Tests failing | Don't merge. Block branch until CI is fixed |
| Build error | Don't start downstream pipeline steps |
| Review rejection | Don't resubmit same build. Investigate first |
| Runtime crash | Halt release. Hotfix branch |
| Pipeline anomaly | Don't start processing other items |

### Principle

> **Cost of passing incomplete artifacts downstream >> Cost of temporary stop**

- Don't `--no-verify` past failing tests
- Don't proceed with "I'll fix it later"
- Don't context-switch to other work and forget about it

### State Preservation

```bash
# Safely save current changes
git stash push -m "andon: [brief problem description]"

# Or record with a WIP commit
git add -A && git commit -m "WIP: andon stop — [brief problem description]"
```

---

## Step 3: Emergency Fix

### Purpose
**Restore normal state.** This is NOT the root cause fix.

### Priority (safest first)

1. **Revert the recent change** (safest)
   ```bash
   git revert HEAD
   ```

2. **Revert only the problematic change**
   ```bash
   git revert <commit-hash>
   ```

3. **Minimal fix** (only when revert is impossible)
   - Keep changes minimal
   - Don't add new features
   - Don't refactor

### Record

```markdown
## Emergency Fix Record

- **Method**: [revert / minimal fix / other]
- **Changes**: [what was done specifically]
- **Normal state confirmed**: [tests pass? build succeeds?]
- **Residual risk**: [side effects or unresolved issues from the fix]
```

---

## Step 4: Investigate

### Purpose
**Find root cause** and **embed prevention in standard work**.

> **This is the most important step.**
> If you stop at the emergency fix, the same problem will absolutely recur.

### Procedure

1. **Run Five Whys**: `/tps-kaizen five-whys <problem>`
2. **Identify root cause**: Process/system-level cause
3. **Design prevention**:
   - **Poka-yoke**: Make the same mistake physically impossible
   - **Auto-detection**: CI / test / lint catch it automatically
   - **Standard work update**: Update rules, templates, checklists
4. **Implement prevention measures**
5. **Verify effectiveness**

### Prevention Levels

| Level | Type | Reliability | Example |
|-------|------|-------------|---------|
| 1 | Poka-yoke (make it impossible) | Highest | Compile error, type constraint |
| 2 | Auto-detect | High | Add test, CI check |
| 3 | Standardize procedure | Medium | Update rules, checklist |
| 4 | Alert / reminder | Low | Comment, README note |

> **Always aim for Level 1-2.** Levels 3-4 depend on human attention and degrade over time.

---

## Visualization (Mieruka) — Making Problems Visible

Jidoka assumes problems are **visible**. If they aren't visible, they can't be detected.

### What to Visualize

| Target | How |
|--------|-----|
| Build state | CI/CD dashboard |
| Test results | Test reports (with coverage) |
| Pipeline progress | Activity logs, handoff files |
| Quality metrics | Code metrics, defect rates |
| Improvement progress | Experiment records from Kaizen Kata |

### Anti-patterns

- Logs are output but **nobody looks at them**
- Errors are caught and **silently swallowed** (silent failure)
- Problems exist only in **someone's memory**
- "I'll look at it later" and then **don't**
