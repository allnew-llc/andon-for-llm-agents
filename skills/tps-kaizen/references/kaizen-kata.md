# Improvement Kata (Kaizen Kata) — Continuous Improvement Guide

## Overview

Toyota Kata systematizes Toyota's improvement culture as **reproducible patterns (kata = form)**.
Proposed by Mike Rother in "Toyota Kata".

Two katas:
- **Improvement Kata**: Remove obstacles one by one toward a target
- **Coaching Kata**: Five questions to support Improvement Kata execution

---

## Improvement Kata 4 Steps

```
┌──────────────────────────────────────────┐
│           1. Direction / Challenge         │
│         Understand the ideal state         │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│          2. Current Condition              │
│        Measure where we are now            │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│          3. Target Condition               │
│      Set the next achievable goal          │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       4. Experiment Toward Target          │
│    Pick one obstacle, run small experiment │
│    → Observe result → Record learning      │
│    → Next experiment                       │
└──────────────────┬───────────────────────┘
                   ↓
            Target reached?
           ├── No → Repeat Step 4
           └── Yes → Set next target (Step 3)
```

---

## Step 1: Understand the Direction (Challenge)

### Purpose
Clarify the **big-picture direction** of improvement. This is a long-term vision,
not achievable in a single improvement cycle.

### Questions
- What is the **ideal state** for this area?
- Why does it matter? (customer value, quality, or efficiency impact)

### Template

```markdown
## Improvement Direction

**Target area**: [process / tool / product area]

**Ideal state**:
[Describe specifically. Not "better" but "how better"]

**Why it matters**:
- Customer impact: [quality / lead time / reliability]
- Team impact: [efficiency / workload / satisfaction]
- Business impact: [cost / speed / competitiveness]
```

---

## Step 2: Grasp Current Condition

### Purpose
Know the current state with **measurable metrics**.
Not guesses or feelings — data-based.

### Genchi Genbutsu (Go and See)

**Always check the real thing.** Not reports or memory — actual current state.

```bash
# Example: check current test coverage
find . -name "*Tests.swift" | wc -l
pytest --cov=src --cov-report=term-missing
```

### Template

```markdown
## Current Condition

**Survey date**: YYYY-MM-DD
**Method**: [commands run / files checked]

### Quantitative Metrics
| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| [metric 1] | [value] | [goal] | [delta] |
| [metric 2] | [value] | [goal] | [delta] |

### Process Observations
- [observations about current process]
- [bottlenecks or problem patterns]
- [what's working well]

### Recent Problem Patterns
| Date | Problem | Cause Category |
|------|---------|---------------|
| [date] | [problem] | [process / tool / knowledge / design] |
```

---

## Step 3: Set Next Target (Target Condition)

### Purpose
Set a **specific, achievable goal** for the next iteration.

### Rules

1. **Reachable**: Achievable in days to 2 weeks
2. **Measurable**: Objectively verifiable whether achieved
3. **Aligned**: Moves toward the direction from Step 1
4. **Slightly challenging**: Can't be achieved by continuing as-is (something must change)

### Template

```markdown
## Target Condition

**Deadline**: YYYY-MM-DD
**Target**:
[Specifically: what will be in what state when achieved]

**Achievement criteria**:
- [ ] [measurable condition 1]
- [ ] [measurable condition 2]
- [ ] [measurable condition 3]

**Gap from current state**:
[What needs to change to reach the target]
```

### Anti-patterns

- **Too big**: "100% test coverage for all modules" → break it down
- **Vague**: "Improve quality" → make it measurable
- **Too easy**: "Add one comment" → achievable without changing anything

---

## Step 4: Identify Obstacles and Experiment

### Purpose
Pick **one obstacle** blocking the target and run a **small experiment** to remove it.

### PDCA Cycle Mapping

```
Plan  → Pick obstacle, form hypothesis
Do    → Run experiment
Check → Observe result (as expected?)
Act   → Record learning, decide next experiment
```

### Template

```markdown
## Experiment Record

### Experiment #[number]

**Date**: YYYY-MM-DD
**Obstacle**: [specific obstacle blocking the target]

**Hypothesis**:
[If I make this change, X should become Y]
Rationale: [why I think so]

**Experiment steps**:
1. [specific step 1]
2. [specific step 2]
3. [specific step 3]

**Expected result**:
[what should be observable if the experiment succeeds]

---

**Actual result**:
[what actually happened — facts only]

**Hypothesis correct?**: [yes / no / partially]

**Learning**:
[what was learned from this experiment]

**Next step**:
- [ ] [what to do next]
```

### Experiment Rules

1. **One at a time**: Don't make multiple changes simultaneously (can't tell what worked)
2. **Small**: Results visible within a day
3. **Record**: Always record results and learning (input for next experiment)
4. **Failure is learning**: A wrong hypothesis is itself valuable information

---

## Coaching Kata — 5 Questions

Questions to check improvement progress (for yourself or teammates):

| # | Question | Purpose |
|---|----------|---------|
| 1 | **What is the target condition?** | Re-confirm the goal |
| 2 | **What is the actual current condition?** | Face reality |
| 3 | **What obstacles are preventing you from reaching the target?** | Clarify obstacles |
| 4 | **What is your next experiment? What do you expect?** | Decide next action |
| 5 | **What did you learn from the last experiment?** | Confirm learning |

### Usage

Ask these 5 questions at the start of a session or standup.
Detects when improvement progress has stalled.

---

## Improvement Log

### Format

```markdown
## Improvement Log: [target area]

### Cycle #1: [target summary]
- **Period**: YYYY-MM-DD to YYYY-MM-DD
- **Target**: [what was the goal]
- **Result**: [achieved / not achieved / partial]
- **Experiments**: [N runs]
- **Key learning**: [1-2 sentences]

### Cycle #2: [target summary]
...
```

### Standardizing Knowledge

Knowledge from improvement cycles is **applied to standard work**:

| Knowledge Type | Target |
|---------------|--------|
| Coding patterns | Templates / policy docs |
| Process improvement | Rules / pipeline config |
| Tool usage | Memory docs / skill files |
| Bug patterns | Tests / poka-yoke |

> **Without standards there can be no improvement. Without improvement there can be no standards.**
> Standards without improvement become stale. Improvement without standards has no baseline.
