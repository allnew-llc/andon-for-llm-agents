---
name: QC Audit
description: "Use when: quality assessment, quality audit, gate preparation, quality score, defect trend, quality degradation, pass rate, deliverable review, pre-gate check, or quality self-evaluation. Provides quality self-assessment, historical trend analysis, and gate-health correlation."
argument-hint: "[subcommand] — (none), trend, gate-health"
version: 1.0.0
---

# QC Audit — Quality Self-Assessment Skill

> "Quality is built into the process, not inspected into the product." — W. Edwards Deming
>
> Gate conditions verify the minimum threshold. Quality criteria define what the deliverable must actually be.
> Run `/qc-audit` before every gate submission — not after.

---

## When to Use This Skill

Invoke `/qc-audit` when you encounter:

| Trigger | Example | Subcommand |
|---------|---------|------------|
| Pre-gate quality check | Before submitting phase artifacts to gate | (no args) |
| Quality self-assessment | Evaluating deliverable quality against criteria | (no args) |
| Quality degradation | Increasing failure rate, declining pass rates | trend |
| Post-incident quality check | After closing ANDON, verify quality restored | (no args) |
| Trend analysis | Reviewing quality trajectory over multiple phases | trend |
| Gate failure investigation | Understanding why gates keep failing | gate-health |
| Process improvement planning | Data for kaizen improvement cycles | gate-health |

**Key signals in user messages**: "quality", "assessment", "audit", "gate score", "pass rate", "trend", "defect rate", "deliverable quality"

---

## Usage

```
/qc-audit                  Execute quality self-assessment for current phase
/qc-audit trend            Display quality trend over time (FAIL/WARN/OK rates)
/qc-audit gate-health      Show correlation between quality scores and gate pass rates
```

---

## Subcommand: (no arguments)

**Trigger**: Before gate submission, after ANDON close, or any time deliverable quality needs verification.

Execute a quality self-assessment for the current phase using `quality_criteria` from the deliverable manifest (see `rules/45-quality-driven-execution.md`). Do NOT derive criteria from the gate conditions — criteria come from the deliverable manifest or phase success criteria.

### Step 1: Identify Current Phase

1. Determine the current phase from project context: check `ROADMAP.md`, `STATE.md`, or user-provided context
2. Note the phase ID (e.g., `1a`, `2b`, `08-01`) — this is used in the output filename
3. Locate the phase's deliverable manifest or success criteria section

### Step 2: Load Quality Criteria

1. Read the deliverable manifest for the current phase
   - For ios-app-factory projects: check the pipeline config's `deliverables[].quality_criteria` fields
   - For GSD-tracked projects: check the phase's `must_haves.truths` and `artifacts` in the PLAN.md
   - Otherwise: use the phase's success criteria from `ROADMAP.md`
2. For each deliverable, extract all `quality_criteria` items explicitly
3. If no explicit manifest exists, derive criteria from observable phase goals — never derive criteria from what already exists in the artifacts

### Step 3: Assess Each Criterion

1. For each quality criterion, examine the actual deliverable artifact on disk
2. Assign a status:
   - `pass`: Criterion is clearly met with specific, verifiable evidence (file examined, content confirmed)
   - `warn`: Criterion is partially met, or evidence is thin (exists but lacks depth, present but sparse)
   - `fail`: Criterion is not met, artifact is missing, or content is empty/placeholder
3. Record evidence with specifics: file path, line count, what was found, why this status was assigned

### Step 4: Compute Overall Status

- `pass`: All individual criteria are `pass`
- `warn`: No criteria are `fail`, but at least one is `warn`
- `fail`: At least one criterion is `fail`

### Step 5: Output Results

Display a summary table:

```
| Criterion                      | Status | Evidence                                      |
|-------------------------------|--------|-----------------------------------------------|
| Gotchas section has 5+ items  | pass   | skills/qc-audit/SKILL.md: 5 named patterns   |
| Related Skills links tps-kaizen| pass   | Line 180: tps-kaizen linked with composition  |
| File >= 150 lines              | pass   | wc -l = 210 lines                             |
```

Show overall result:

```
Overall: PASS / WARN / FAIL
```

Save the result to `docs/pipeline/quality-self-assessment-{phase_id}.json`:

```json
{
  "phase_id": "<current_phase>",
  "timestamp": "<ISO8601>",
  "overall": "pass|warn|fail",
  "criteria": [
    { "name": "<criterion>", "status": "pass|warn|fail", "evidence": "<what was checked and found>" }
  ]
}
```

### Step 6: Recommend Actions

- If `fail`: List specific fixes needed before gate submission. Do NOT submit to gate with FAIL items — fix first (see `rules/45-quality-driven-execution.md`)
- If `warn`: List improvements to strengthen the deliverable. Document the reason if deferring improvement
- If `pass`: Note readiness for gate submission and any optional improvements that would add value

---

## Subcommand: `trend`

**Trigger**: When reviewing quality trajectory over multiple phases, after closing ANDON, or after a kaizen improvement cycle.

**Purpose**: Display a historical quality trend from aggregated self-assessment data, showing how FAIL/WARN/OK rates have changed over time.

**Action**: Run `skills/qc-audit/scripts/trend.sh` (created in Plan 08-02). The script reads from:
- `${CLAUDE_PLUGIN_DATA}/qc/` (if `CLAUDE_PLUGIN_DATA` is set)
- `docs/pipeline/quality-self-assessment-*.json` in the current project

**Interpretation guide**:

| Trend | Meaning | Recommended Action |
|-------|---------|-------------------|
| improving | Quality increasing — PASS rate rising | Continue current practices; document what's working |
| stable | No significant change — consistent quality level | Monitor; look for incremental improvements |
| degrading | Quality decreasing — WARN/FAIL rate rising | Investigate root causes; run `/tps-kaizen audit` |

**Tip**: Run after closing ANDON or completing a kaizen cycle to measure whether the improvement had the intended quality impact.

---

## Subcommand: `gate-health`

**Trigger**: When gates keep failing despite apparent work completion, or when planning a quality improvement cycle.

**Purpose**: Analyze the correlation between quality self-assessment scores (pass/warn/fail) and gate pass/fail rates for recent phases. Reveals misalignment between quality definitions and gate conditions.

**Action**: Run `skills/qc-audit/scripts/gate-health.sh` (created in Plan 08-02). The script reads from:
- `${CLAUDE_PLUGIN_DATA}/qc/` for quality self-assessment history
- Gate result logs from the pipeline (if available)

**Interpretation guide**:

| Pattern | Meaning | Recommended Action |
|---------|---------|-------------------|
| High quality score + Gate passes | Healthy alignment | No action needed |
| High quality score + Gate fails | Gate conditions misaligned with quality criteria — gate is checking things not in quality criteria | Review and update gate conditions to match quality intent |
| Low quality score + Gate passes | Gate conditions too lenient — gate passes thin artifacts | Tighten gate conditions; improve quality criteria coverage |
| Low quality score + Gate fails | Expected correlation — fix quality first | Run `/qc-audit` no-args, fix FAIL items, resubmit |

---

## Gotchas

### Score Inflation

Agent inflates `pass` or `warn` assessments to avoid fixing deliverables before gate submission. The symptom is an evidence column filled with vague justifications ("looks good", "seems complete", "appears to be present") instead of specific file paths, line counts, or measurable attributes. This passes the assessment but leaves defects undetected until they cause downstream failures.

Prevention: Evidence must cite specific, verifiable facts — file path examined, what content was found, why that content satisfies the criterion. "Looks good" is never acceptable evidence. If you cannot name the specific file and what it contains, the criterion is `warn` at best.

### Criteria Drift

Quality criteria are modified or reinterpreted to match what the existing deliverable already contains, rather than improving the deliverable to match the original criteria. The assessment bends the ruler to fit the measurement. This is the quality audit equivalent of Gate-Gaming — producing a passing score without producing a quality artifact.

Prevention: Load quality criteria from the source (deliverable manifest, PLAN.md `must_haves`, or ROADMAP.md success criteria) before examining any deliverable artifacts. Never derive criteria from what already exists. The criteria define the standard; the artifact must reach the standard, not the reverse.

### Trend Blindness

Running `/qc-audit` only for the current phase before gate submission, without checking whether quality is improving or degrading over time. A single PASS result in isolation hides a degrading quality trajectory — each phase may be passing individually while the overall system quality is declining due to accumulating `warn` items and thin evidence.

Prevention: Run `/qc-audit trend` periodically (at least every 3-5 phases, or after every ANDON close and kaizen cycle), not only before gate submission. A phase PASS combined with a degrading trend requires investigation of the trend, not celebration of the individual result.

### Gate-Quality Conflation

Treating gate pass as equivalent to quality pass. Gates check minimum conditions: file exists, required markers are present, expected output was produced. Quality assessment checks whether the deliverable is genuinely useful — whether a human or downstream agent can use it effectively to make decisions or take action. A deliverable can satisfy every gate condition and still be low quality.

Prevention: Always run `/qc-audit` assessment before gate submission, not after gate pass. Gate pass confirms minimum correctness; quality assessment confirms genuine usefulness. The order matters: assess quality → fix failures → submit to gate → gate pass confirms readiness.

### Assessment-Only Syndrome

Running `/qc-audit` and generating the self-assessment JSON, but not acting on `warn` or `fail` results. The assessment becomes a checkbox exercise — it produces output, it creates a file, but it changes nothing. The FAIL items remain unfixed. The WARN items remain thin. The next gate submission uses the same low-quality artifacts.

Prevention: FAIL items MUST be fixed before gate submission — this is not optional. WARN items should be addressed unless there is a specific, documented reason to defer (not just "it's close enough"). The assessment is only useful if the results drive action. If you are running assessments without fixing what they find, stop running assessments and fix the process instead.

---

## Related Skills

| Skill | Path | When to Chain |
|-------|------|---------------|
| tps-kaizen | `skills/tps-kaizen/SKILL.md` | After ANDON close — run `/qc-audit` (no args) to verify quality is restored before resuming work |
| tps-kaizen audit | `skills/tps-kaizen/SKILL.md` | Before `/qc-audit trend` — use 3M audit (`/tps-kaizen audit`) to identify waste patterns affecting quality, then run trend to see if elimination improved scores |

### Composition Patterns

**Quality Gate Chain**: `/qc-audit` (self-assess) -> fix FAIL items -> `/qc-audit` (re-assess) -> gate submission

**Post-Incident Chain**: `/tps-kaizen andon` (stop and fix) -> `/tps-kaizen five-whys` (root cause) -> `/qc-audit` (verify quality restored)

**Continuous Improvement Chain**: `/qc-audit trend` (identify trajectory) -> `/tps-kaizen kaizen` (plan improvement) -> `/qc-audit gate-health` (measure impact)
