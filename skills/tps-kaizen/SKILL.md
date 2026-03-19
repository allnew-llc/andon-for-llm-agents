---
name: TPS Kaizen
description: "Use when: error, test failure, build failure, incident, broken pipeline, stuck process, regression, anomaly, or any quality defect. Provides Jidoka (stop-and-fix) response, Five Whys root cause analysis, and Kaizen continuous improvement."
argument-hint: "<subcommand> [args] — andon, five-whys, kaizen, audit"
version: 1.2.0
---

# TPS Kaizen — Lean Manufacturing Improvement Skill

> "When an abnormality occurs, the machine stops automatically and no defective products are made" (Jidoka),
> and "each process produces only what is needed, when needed, flowing without stagnation" (Just-in-Time),
> delivering only good products to customers in a timely manner.

This skill applies the two pillars of TPS to software development,
providing procedures and frameworks for **autonomous improvement activities** when problems occur.

---

## When to Use This Skill

Invoke `/tps-kaizen` when you encounter:

| Trigger | Example | Subcommand |
|---------|---------|------------|
| Test failure | `pytest` returns non-zero, assertion errors | `andon` |
| Build error | Compilation failure, type errors, missing imports | `andon` |
| Runtime exception | Unhandled error in production or dev server | `andon` |
| Pipeline stuck | CI/CD hangs, deployment blocked, merge conflict loop | `andon` |
| Regression | Feature that worked before now fails | `andon` then `five-whys` |
| Incident | User-reported bug, data corruption, service outage | `andon` |
| Unexplained behavior | "It works on my machine", flaky tests | `five-whys` |
| Process inefficiency | Repeated manual work, slow feedback loops | `kaizen` or `audit` |
| Quality degradation | Increasing defect rate, declining test coverage | `audit` |

**Key signals in user messages**: "error", "failure", "broken", "stuck", "regression", "incident", "not working", "keeps failing", "can't figure out why"

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
/tps-kaizen gotcha-review          Review and promote Gotcha candidates
```

---

## Subcommand: `andon`

**Trigger**: When an anomaly occurs (test failure, build error, runtime exception, etc.)

Execute the Jidoka cycle (Step 0 + 4 steps):

### Step 0: Check Incident History

Before starting analysis, check for recurring patterns in past incidents.

1. **Scan persistent store**: Check `${CLAUDE_PLUGIN_DATA}/kaizen/incidents/` (if CLAUDE_PLUGIN_DATA is set) or `~/.claude/state/kaizen/incidents/` for past incident data
2. **Match current problem**: Compare the current error message, command, and failure category against `cause_id` and `category` fields in past `analysis.json` files
3. **Surface matches**: If matching incidents are found, report them:
   ```
   [History] Found N past incident(s) matching this pattern:
   - INC-YYYYMMDD-... : [root_cause_summary] (confidence: X.XX)
   - INC-YYYYMMDD-... : [root_cause_summary] (confidence: X.XX)
   Previous prevention measures: [from actions.json]
   ```
4. **Inform investigation**: Use past incident data to skip already-explored root causes and focus on what's new or what previous prevention measures failed to prevent

> **Tip**: Run `skills/tps-kaizen/scripts/aggregate-incidents.sh` to see a full pattern summary before starting.

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
5. **Generate Gotcha candidate**: After defining prevention measures, run gotcha candidate generation to capture the learning:
   ```python
   from gotcha_candidate import generate_candidate
   candidate_path = generate_candidate(
       root_cause="<root cause from Five Whys>",
       prevention="<prevention measures defined above>",
       tags=["<category from Five Whys>"]
   )
   ```
   Report the candidate path and suggest running `/tps-kaizen gotcha-review` to promote it.

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

> **After completion**: Run gotcha candidate generation to capture this learning as a reviewable Gotcha:
> ```python
> from gotcha_candidate import generate_candidate
> generate_candidate(root_cause="<root cause>", prevention="<prevention measures>")
> ```
> Then run `/tps-kaizen gotcha-review` to approve the candidate into the live registry.

> Detailed template and examples: `references/five-whys-template.md`

---

## Subcommand: `kaizen`

**Trigger**: Periodic improvement activities, or when problem trends are visible

Run structured improvement cycles using the "Improvement Kata" pattern.

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

## Subcommand: `gotcha-review`

**Trigger**: After Five Whys generates one or more Gotcha candidates, or periodically to check pending candidates

Review Gotcha candidates in `gotchas/candidates/` and promote approved ones to the live registry.

### Procedure

1. **List candidates**: Read all `*.yaml` files in `gotchas/candidates/`. For each, display:
   ```
   Candidate: {id}
     Pattern:  {pattern (first 80 chars)}
     Severity: {severity}
     Source:   {source}
   ```
   If no candidates exist, report "No Gotcha candidates pending review." and stop.

2. **Review each candidate**: For each candidate, ask the user:
   ```
   Approve this candidate? [approve / skip / edit]
   ```
   - **approve**: Move the YAML file from `gotchas/candidates/{file}` to `gotchas/{file}` using `mv`. The Gotcha is immediately available to `load_gotchas()` (no restart required because `load_gotchas()` reads from disk on each call).
   - **skip**: Leave the candidate in `gotchas/candidates/` for later review.
   - **edit**: Open the YAML content for inline editing (severity, pattern wording, tags), then re-ask approve/skip.

3. **Report results**: After reviewing all candidates, summarize:
   ```
   Gotcha Review Complete:
   - Approved: N (moved to gotchas/)
   - Skipped: N (remain in candidates/)
   - Total reviewed: N
   ```

### Notes

- Promoted Gotchas are immediately matchable by the ANDON surfacing engine in the same session because `load_gotchas()` reads from disk on every call with no caching.
- The candidate file name is preserved during promotion (the ID is already in the YAML).
- If a promoted Gotcha has an ID that conflicts with an existing Gotcha, `load_gotchas()` will raise `GotchaValidationError` on next load. Resolve by editing the candidate's `id` field before approval.

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

---

## Gotchas

### Human Error Stop

Five Whys analysis terminates at "human error" or "I made a mistake" instead of digging into the process/system gap that allowed the mistake. Always ask "Why did the process allow this error?" to reach a structural root cause. A root cause of "human error" means the investigation is incomplete — the system should be designed so that human error either cannot occur or is immediately caught.

### 4-Artifact Close Shortcut

Attempting to close ANDON without all 4 artifacts (evidence.json, analysis.json, actions.json, report.md). The close command will reject if any artifact is missing. Do not create placeholder/empty artifacts just to pass validation — each must contain genuine analysis. Thin artifacts that pass the close check but lack real content undermine the entire Jidoka cycle and leave the root cause unaddressed.

### Meta-ANDON Session Reset

Meta-ANDON failure counters reset at session boundaries. A pattern of 2 failures per session across multiple sessions will never trigger Meta-ANDON (requires 3 in one session). Long-running investigations should stay in one session or explicitly note the cross-session pattern. If continuity is broken, manually count cumulative failures and apply the Meta-ANDON protocol when the threshold is reached.

### Gate-Gaming

LLM agents optimize for Gate pass conditions (required_files, output_markers) instead of genuine quality. This produces thin artifacts that pass validation but fail in practice. Prevention: focus on deliverable quality criteria, not Gate conditions. See `rules/45-quality-driven-execution.md`. The symptom is artifacts that exist and contain the right keywords but provide no actionable insight.

### Confidence Threshold Bypass

ANDON close with root cause confidence below 0.70 is rejected unless the close reason includes `manual-approved:` prefix. Do not inflate confidence scores to bypass the threshold. If genuine confidence is low, get human verification and use `manual-approved: <verified reason>`. Inflated confidence that passes close validation leaves the team with false certainty and no real preventive measures.

### Andon Cord Fear

Team members hesitate to pull the Andon cord (report problems) because they fear blame or disruption. The TPS principle is: pulling the cord is always encouraged. The cost of stopping is always less than the cost of passing defects downstream. A culture where problems are hidden is more dangerous than any individual defect — it means the system cannot detect and respond to failures.

### Fix-and-Forget

Emergency fix restores normal operation, but Step 4 (Investigate) is skipped. The root cause remains, and the same failure recurs. Always complete the full 4-step Jidoka cycle. The emergency fix in Step 3 is explicitly not the end of the process — it is a temporary measure to restart the line while the real fix is developed through investigation and standard-work updates.

---

## Related Skills

| Skill | Path | When to Chain |
|-------|------|---------------|
| pipeline-debugging | `skills/pipeline-debugging/SKILL.md` | When ANDON is triggered by a pipeline failure — use pipeline-debugging for environment/config diagnosis before Five Whys for root cause |
| adversarial-review | `skills/adversarial-review/SKILL.md` | After kaizen improvements — use adversarial-review to stress-test the fix and verify it handles edge cases |
| qc-audit | `skills/qc-audit/SKILL.md` | After closing ANDON — use qc-audit to verify the fix improved overall quality metrics and did not regress other areas |

### Composition Patterns

**Incident Response Chain**: `andon` (stop + emergency fix) -> `five-whys` (root cause) -> `pipeline-debugging` (if infrastructure-related) -> `adversarial-review` (verify fix robustness)

**Quality Improvement Chain**: `audit` (identify waste) -> `kaizen` (plan improvement) -> `qc-audit` (measure impact)
