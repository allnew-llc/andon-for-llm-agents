# Quality-Driven Execution (MUST)

## Purpose

In pipeline/phase execution, ensure that **high-quality deliverables are produced comprehensively,
and gates pass as a natural consequence** — NOT the other way around.

> "Quality is not inspected in, it is built into the process." — W. Edwards Deming
>
> Gates are the "last line of defense", not the "source of quality".
> The source of quality is the execution itself.

## Background (Why This Rule Exists)

LLMs are goal-function optimizers. When gate conditions (`required_files`, `output_markers`) are visible,
they **reverse-engineer the minimum output to pass the gate**. This is the same structure as
"teaching to the test" and causes:

- Deliverables that are barely-passing thin content
- Important items omitted because they're not in gate definitions
- "Existence checks" pass but content is useless for decision-making
- Downstream phases inherit thin deliverables, causing cascading quality degradation

---

## Principle 1: Purpose-First Execution (MUST)

When executing a phase, the first thing to reference is the **phase purpose and deliverable definitions** — NOT gate conditions.

### Thinking Order

```
1. What is the PURPOSE of this phase? (Why does this step exist?)
2. What deliverables at what quality are needed to achieve that purpose?
3. Create deliverables comprehensively
4. Self-assess quality against criteria; improve if below standard
5. Submit to gate as a result
```

### Prohibited Thinking Order

```
BAD: Read gate conditions → produce minimum to pass → next phase
BAD: Check required_files → create only those files
BAD: Check output_markers → include only those markers
```

---

## Principle 2: Deliverable Manifest (MUST)

Each phase should have a **deliverable definition with quality criteria** (Deliverable Manifest)
separate from gate conditions. Executors use the manifest, not the gate, as their driver.

### Structure Example

```yaml
phases:
  - id: "1a"
    purpose: "Validate market viability and feasibility of the app concept for Go/No-Go decision"

    deliverables:          # ← Executor references THIS to create deliverables
      - name: "Idea Validation Report"
        path: "docs/idea-validation.md"
        quality_criteria:
          - "3+ competitor apps analyzed by name"
          - "Target user persona is specific (age, occupation, pain points)"
          - "Differentiation derived from competitive analysis"
          - "At least 3 risks with mitigations listed"
          - "Monetization model justified with evidence"
        completeness_checklist:
          - "Quantitative market size evidence"
          - "Specific user pain point examples"
          - "Technical feasibility assessment"

    gates:                 # ← Gate is "minimum bar verification" only
      - type: tool_invocation
        checks:
          required_files: [...]
          required_output_markers: [...]
```

### Role Separation

| Element | Role | Executor Reference |
|---------|------|-------------------|
| `purpose` | Why this phase exists | Read FIRST |
| `deliverables` | What to create, at what quality | PRIMARY driver |
| `quality_criteria` | Quality bar for each deliverable | Used in self-assessment |
| `gates` | Mechanical minimum-bar check | Do NOT reference directly |

---

## Principle 3: Mandatory Quality Self-Assessment (MUST)

After creating deliverables and BEFORE gate submission, perform quality self-assessment.

### Flow

```
Create deliverables → [Quality Self-Assessment] → Improve if below bar → Submit to gate
                              ↑
                    Reference quality_criteria
                    Do NOT reference gate conditions
```

### Self-Assessment Output Format

```markdown
## Phase {id} Deliverable Quality Assessment

| Deliverable | Quality Criterion | Met? | Evidence |
|-------------|------------------|------|----------|
| Idea Validation Report | 3+ competitors analyzed by name | OK | Fitbit, MyFitnessPal, HealthMate analyzed |
| Same | Persona is specific | WARN | Age/occupation present but pain points lack depth |
| Same | Differentiation from analysis | OK | Derived from competitors' weak HealthKit integration |
| Same | 3+ risks listed | FAIL | Only 2 items. Tech risk missing |

→ Verdict: Not ready (2 items below bar). Improve before gate submission.
```

### Rules

- If any item is FAIL, **improve before gate submission** (MUST)
- WARN items: attempt improvement; if impossible for valid reasons, gate submission is allowed
- Save self-assessment to `docs/pipeline/quality-self-assessment-{phase_id}.json`
- **Skipping self-assessment is prohibited**. "Gate conditions are enough" is not acceptable

---

## Principle 4: Purpose-First Prompt Structure (MUST)

When an executor instructs the LLM to create deliverables, follow this structure:

### Correct: Quality-Driven Prompt

```
Phase {id}: {name}

[PURPOSE]
This phase exists to {purpose}.

[DELIVERABLES]
1. {deliverable.name} ({deliverable.path})
   - {quality_criteria[0]}
   - {quality_criteria[1]}
   - ...

[QUALITY BAR]
- {Qualitative: who reads this and what decision can they make?}
- {Completeness: what must not be missing?}
- {Honesty: include risks and constraints}

[DONE WHEN]
All deliverables created, quality self-assessment shows all items OK,
then submit to gate verification.
```

### Prohibited: Gate-Driven Prompt

```
Execute Phase {id}.
Gate conditions: required_files=[...], output_markers=[...]
```

Including gate conditions in the prompt is like "handing out the test questions before the exam" —
it drives gate-gaming behavior, not quality.

---

## Principle 5: Redefining Gate's Role

| Old Role | New Role |
|----------|----------|
| Phase "success criteria" | Phase "minimum bar check" |
| Target the executor aims for | Backstop the executor doesn't think about |
| Pass = success | Pass ≠ quality guarantee |
| Fail = fix and retry | Fail = signals fundamental quality problem |

**On gate failure:**
1. Making the minimum fix to pass the gate is **prohibited**
2. Trace back to the quality self-assessment to analyze why the deliverable was insufficient
3. Improve the deliverable quality itself — the gate passing is a natural consequence

---

## Future Extension: Blind Gate

The most effective gate-gaming prevention is hiding gate conditions from the executor entirely:

```
Executor knows:
  OK: purpose (why this phase exists)
  OK: deliverables (what to create at what quality)
  OK: quality_criteria (self-assessment checklist)
  NO: gates required_files / output_markers

Gate Checker knows:
  OK: gate conditions
  NO: how the executor created deliverables
```

Currently the implementation cost of this separation is high, so Principles 1-4 are used operationally.
Future work: implement information separation between executor and gate.

---

## Checklist (Phase Execution)

- [ ] Read the phase `purpose`?
- [ ] Listed all `deliverables` and understood quality criteria?
- [ ] NOT using gate conditions as the "target"?
- [ ] Created each deliverable with sufficient content per quality criteria?
- [ ] Performed quality self-assessment with all items OK?
- [ ] Improved any FAIL items before gate submission?
- [ ] On gate failure, improving deliverable quality (not just minimum gate fix)?

---

## Relationship to 70-kaizen-learning.md

- Repeated gate failures trigger **Meta-ANDON** from `70-kaizen-learning.md`
- Meta-ANDON's Desk Walk-Through is equivalent to performing **quality self-assessment** across all phases
- Following this rule significantly reduces Meta-ANDON trigger frequency
- This rule is "prevention"; Meta-ANDON is "detection and correction"
