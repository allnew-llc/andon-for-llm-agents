---
name: TPS Kaizen
description: Toyota Production System (Jidoka + JIT) based anomaly detection, root cause analysis, and continuous improvement skill
argument-hint: "<subcommand> [args] — andon, five-whys, kaizen, audit"
version: 1.0.0
---

# TPS Kaizen — Toyota Production System Improvement Skill

> "When an abnormality occurs, the machine stops automatically and no defective products are made" (Jidoka),
> and "each process produces only what is needed, when needed, flowing without stagnation" (Just-in-Time),
> delivering only good products to customers in a timely manner.

This skill applies the two pillars of TPS to software development,
providing procedures and frameworks for **autonomous improvement activities** when problems occur.

---

## Two Pillars

### Pillar 1: Jidoka (Autonomation) — Stop on Abnormality

When an abnormality is detected, **stop immediately** and don't pass defects downstream.
After stopping, **investigate root cause** and **embed prevention in standard work**.

```
Detect anomaly → Stop → Emergency fix → Root cause analysis → Prevention → Update standards
```

Software mapping:
| TPS Concept | Software Practice |
|-------------|-------------------|
| Anomaly detection | Test failure, build error, runtime exception, review rejection |
| Line stop | Pipeline halt, deploy abort, merge block |
| Andon | Error logs, alerts, dashboards, notifications |
| Poka-yoke | Type system, linter, pre-commit hook, compile-time checks |

### Pillar 2: Just-in-Time (JIT) — Produce Only What's Needed

Produce what's needed, when needed, in the amount needed.
Minimize inventory (work-in-progress) and shorten lead time.

```
Pull from downstream → One-piece flow → Maintain flow
```

Software mapping:
| TPS Concept | Software Practice |
|-------------|-------------------|
| Pull from downstream | Pull-based workflow (Kanban), don't build until needed |
| One-piece flow | Small PRs, single-purpose branches |
| Leveling (Heijunka) | Uniform batch sizes, WIP limits |
| 3M elimination | Muda(waste)=unused code, Mura(unevenness)=unstable process, Muri(overburden)=overload |

---

## Usage

```
/tps-kaizen andon <problem>       Execute Jidoka 4-step anomaly response
/tps-kaizen five-whys <problem>   Root cause analysis via Five Whys
/tps-kaizen kaizen <area>         Run improvement cycle via Improvement Kata
/tps-kaizen audit                 3M (Muda/Mura/Muri) waste audit
/tps-kaizen capture [learning]    Capture and standardize knowledge from fixes
```

---

## Subcommand: `andon`

**Trigger**: When an anomaly occurs (test failure, build error, runtime exception, etc.)

Execute the Jidoka 4-step cycle:

### Step 1: Detect — What happened

Record the **facts** accurately. Observations only, no speculation.

```markdown
## ANDON Report
- Timestamp: YYYY-MM-DD HH:MM
- Location: [file path / phase / tool name]
- Symptom: [observable facts only]
- Impact: [which downstream processes are blocked]
```

### Step 2: Stop — Don't pass defects downstream

1. **Don't commit** problematic changes (stash if uncommitted)
2. **Don't start** downstream pipeline steps
3. **Stop all** operations that could propagate the defect
4. Preserve related work branch state

> **Principle**: Stopping is always cheaper than passing incomplete artifacts downstream.

### Step 3: Emergency Fix — Restore normal state

The goal is **restarting the line**, not solving the root cause.

1. **Revert recent changes** (safest recovery)
2. If revert isn't possible, **minimal fix** to restore normal state
3. Record what was done (input for root cause analysis)

### Step 4: Investigate — Find root cause and prevent recurrence

**This is the most important step.** Don't stop at the emergency fix.

1. Run **`/tps-kaizen five-whys`** to identify root cause
2. Design **prevention measures** for the root cause
3. Embed prevention in **standard work** (rules, templates, CI config, etc.)
4. Add **automatic detection** (poka-yoke) for the same class of problems

> Detailed guide: `references/jidoka-response.md`

---

## Subcommand: `five-whys`

**Trigger**: Step 4 of `andon`, or when an unexplained problem occurs

Dig from surface symptoms to root cause using Five Whys analysis.

### Procedure

1. **Define the problem**: Fact-based, one sentence
2. **Why 1**: Why did this problem occur? (direct cause)
3. **Why 2**: Why did Why 1 occur?
4. **Why 3**: Why did Why 2 occur?
5. **Why 4**: Why did Why 3 occur?
6. **Why 5**: Why did Why 4 occur? (should reach root cause)

### Rules

- Each Why must be based on **verifiable facts** (no speculation)
- Don't stop at "human error" — dig into process/system issues
- Continue past 5 if needed; stop at 3 if root cause is found
- Branch the analysis if there are multiple causal paths

### Genchi Genbutsu (Go and See)

Analyze by **looking at actual code, logs, and config files**. Never rely on memory or assumption.

### Output Format

```markdown
## Five Whys Analysis

**Problem**: [one sentence]

| # | Why? | Verification |
|---|------|-------------|
| 1 | [direct cause] | [file/command checked] |
| 2 | [cause of 1] | [file/command checked] |
| 3 | [cause of 2] | [file/command checked] |
| 4 | [cause of 3] | [file/command checked] |
| 5 | [root cause] | [file/command checked] |

**Root cause**: [one sentence summary]

**Prevention measures**:
1. [specific action + implementation location]
2. [poka-yoke: automatic detection mechanism]
3. [standard work update location]
```

> Detailed template and examples: `references/five-whys-template.md`

---

## Subcommand: `kaizen`

**Trigger**: Periodic improvement activities, or when problem trends are visible

Run structured improvement cycles using Toyota Kata's "Improvement Kata".

### Improvement Kata 4 Steps

```
1. Understand the direction  — Clarify vision / ideal state
2. Grasp current condition   — Measure where we are now
3. Set next target           — Achievable next goal state
4. Experiment toward target  — Remove obstacles one at a time
```

> Detailed guide: `references/kaizen-kata.md`

---

## Subcommand: `audit`

**Trigger**: Periodic health check, or process review

Audit from the 3M (Muda/Mura/Muri) perspective.

### Muda (Waste) — 7 Types in Software

| # | Manufacturing Waste | Software Waste | Check Method |
|---|-------------------|----------------|-------------|
| 1 | Overproduction | Building unused features | Feature usage metrics |
| 2 | Waiting | Build wait, review wait, approval wait | Measure lead time |
| 3 | Transport | Unnecessary data transforms, over-abstraction | Trace data flow |
| 4 | Processing | Over-engineering, unnecessary optimization | YAGNI check |
| 5 | Inventory | Unmerged branches, unreleased code | `git branch -a` |
| 6 | Motion | Manual repetitive work, context switching | Analyze work logs |
| 7 | Defects | Bugs, rejections, rework | Measure defect rate |

### Mura (Unevenness)

| Target | Check |
|--------|-------|
| Process | Same type of work done differently each time? |
| Quality | Code quality / test coverage varies across modules? |
| Time | Same-type tasks take wildly different durations? |

### Muri (Overburden)

| Target | Check |
|--------|-------|
| People | Unrealistic deadlines, excessive parallel work? |
| Systems | Tools/processes used beyond design limits? |
| Code | Single class/function carrying too many responsibilities? |

---

## TPS Glossary

| Japanese | English | Meaning | Software Practice |
|----------|---------|---------|-------------------|
| Jidoka | Autonomation | Auto-stop on anomaly | CI/CD fail-fast |
| Just-in-Time | JIT | Produce when needed | Pull-based development |
| Andon | Andon | Visual anomaly signal | Alerts, dashboards |
| Kanban | Kanban | Pull signal | Task boards, WIP limits |
| Poka-yoke | Error-proofing | Prevent mistakes | Types, linters, pre-commit hooks |
| Kaizen | Continuous improvement | Always improve | Retrospectives, automation |
| Standard Work | Standard Work | Baseline for improvement | Rules files, templates |
| Mieruka | Visualization | Make problems visible | Logs, metrics, reports |
| Genchi Genbutsu | Go and see | See the actual thing | Check real code/logs |
| Heijunka | Leveling | Smooth production | Batch size adjustment |
| Muda | Waste | Non-value activities | Unused code, over-engineering |
| Mura | Unevenness | Variation | Inconsistent processes |
| Muri | Overburden | Overload | Unrealistic scope |

---

## Core Principles

1. **Genchi Genbutsu**: Don't guess — look at actual code, logs, and config
2. **Don't hide problems**: Pulling the Andon cord should be encouraged, not feared
3. **Blame the process, not the person**: Five Whys digs into system issues
4. **Small experiments**: Improvement is accumulated small experiments, not big bets
5. **Standards enable improvement**: Without standards, there's no baseline to improve from
