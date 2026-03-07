# Kaizen Learning Capture (MUST)

## Purpose

Automatically capture and standardize knowledge gained from bug fixes and problem resolution,
preventing recurrence and building organizational knowledge.

> "Without standards there can be no improvement. Without improvement there can be no standards." — Improvement Kata

## Trigger (MUST)

Execute the **knowledge capture process** after completing a fix when any of the following apply:

1. **Bug fix**: A fix that required root cause investigation
2. **Workaround discovery**: Found a way to work around an API/framework limitation
3. **Configuration trap**: Discovered a "gotcha" in build settings, CSS specs, API behavior, etc.
4. **Process improvement**: Found and fixed an inefficiency or gap in the workflow

## Session Enforcement Guard (Jidoka)

- When a Bash command exits with a non-zero code, the PostToolUse hook opens an ANDON incident and treats it as a line stop
- On anomaly detection, the KAIZEN runtime automatically:
  1. Issues an incident ID
  2. Collects evidence (failed command, exit code, output snippet, git context)
  3. Estimates root cause (with confidence score)
  4. Generates prevention actions and standardization rules
  5. Outputs a report (`~/.claude/state/kaizen/incidents/<incident>/report.md`)
- While ANDON is open, the PreToolUse hook blocks forward-progress commands (`git push`, normal `git commit`, deploy commands)
- Investigation, fix, and verification commands remain allowed (only "shipping defects downstream" is blocked)
- **Human-involved trial limit (MUST)**:
  - Max 2 consecutive attempts for operations requiring user action (login, manual input, re-auth, manual verification)
  - After 2 consecutive failures, treat as line stop — do not attempt a 3rd time
  - To resume: present `root cause hypothesis`, `verification result`, `prevention plan`, and `new approach` — get agreement before proceeding
- Close ANDON in this order:
  1. Run `/tps-kaizen andon <problem>`
  2. Run `/tps-kaizen five-whys <problem>`
  3. Apply prevention measures to standards (review auto-generated suggestions)
  4. `<workspace-root>/.claude/hooks/tps-andon-control.sh close "<reason>"`
- `close` is rejected if artifacts (evidence/analysis/actions/report) are incomplete
- If root cause confidence is low (<0.70), close is only allowed with `manual-approved:` in the reason string
- Exception: `kaizen:` prefixed `git commit` is allowed during ANDON (for capturing learning)
- Rollback: `<workspace-root>/.claude/hooks/tps-andon-control.sh rollback <incident_id|latest>`

## Meta-ANDON (Pattern Detection) (MUST)

Individual Five Whys tracks "the root cause of a specific problem". But **repeated failure patterns**
(failing at a different point each time) require a higher-level guard.
Meta-ANDON addresses "the problem behind the problems".

> Lesson: LLMs are good at "solving the problem in front of them" but won't step back to see
> patterns in their own behavior unless explicitly instructed. Without explicit rules to stop them,
> they enter an endless whack-a-mole loop.

### Trigger Conditions (any one activates)

1. **3 consecutive full-run failures** (even at different phases — count is "same-purpose runs in the same session")
2. **2+ ANDON opens in one session at different phases/locations**
3. **Fix→run→different failure cycle repeated twice** (fix A→run→Phase X fails→fix B→run→Phase Y fails = 2 cycles)

### Required Actions (MUST)

When Meta-ANDON triggers, **immediately ban further "just try it" runs** and do the following first:

**Step 1: Pattern Analysis (Pattern Five Whys)**

Normal Five Whys asks "why did this problem happen?" Pattern Five Whys asks:

- "Why does it keep failing at different points?"
- "What structural cause is common to all these failures?" (e.g., schema mismatch, unverified environment assumptions, gate/implementation gap)
- "Where are similar landmines we haven't stepped on yet?"

**Step 2: Desk Walk-Through (All Remaining Phases)**

For ALL untested phases/steps, verify at code level:

| Check | Method |
|-------|--------|
| Input artifacts match previous phase output? | Compare output schema ↔ next phase input paths/keys |
| Gate conditions are satisfiable by generated artifacts? | Check required_files / output_markers in code |
| External dependencies (APIs, build tools, signing) handled? | Check subprocess / API calls in executor code |
| Previous fixes don't have side effects on later phases? | grep impact radius of modified code |

Present results in table format:

```
| Phase | Risk? | Evidence | Action |
|-------|-------|----------|--------|
| 2a    | None  | —        | —      |
| 2b    | Yes   | Signing flag contradicts gate | Add compile-only exception to gate |
| 3     | TBD   | No test path for xcodebuild | Add xcodeproj support |
| ...   | ...   | ...      | ...    |
```

**Step 3: Batch Fix Proposal**

- List ALL discovered issues from the desk walk-through before fixing any
- Fix all at once, not one-by-one
- Present fix plan to user, get agreement, then implement → test → re-run

### Prohibited Actions

- Running "let's just try the next one and see" after Meta-ANDON triggers is **prohibited**
- Returning to the fix-one→run→fail-different loop is **prohibited** (until full analysis is complete)
- Ignoring Meta-ANDON because "this time the cause is different" is **prohibited** (different causes IS the pattern)

### Release Conditions

Re-run is allowed only when ALL of the following are met:

1. Pattern Five Whys analysis presented to user
2. Desk Walk-Through results for all phases presented to user
3. Batch fixes completed and related tests passing
4. User explicitly approves re-run

---

## Specification Boundary Guard (MUST)

To prevent recurrence, **the meaning of user-specified requirements/constraints must not be changed unilaterally by the implementation**.

### Rules

1. **Requirement meaning immutability**:
   - e.g., changing `source=xai required` to `any external LLM is OK` is prohibited without explicit approval
2. **Separate proposal from implementation**:
   - If you judge a spec change is needed, first present a proposal with rationale, impact, and alternatives — implement only after approval
3. **No shortcut spec relaxation**:
   - Never implement requirement relaxation first "to make it pass faster"
4. **Immediate correction on violation**:
   - If requirement drift is detected, stop work, revert the diff, and state facts and prevention measures

---

## Horizontal Sweep on Fixes (MUST)

After a bug fix or gate failure fix, perform a **horizontal sweep** BEFORE re-running.

> Lesson: Same as backporting fixes across derived projects.
> If you fix one place without checking others, you'll step on the same landmine next door.

### Procedure

After fix, BEFORE re-run:

1. **Check other phases for same pattern**: Search code for the same structural issue (schema mismatch, path assumptions, env dependency, gate conditions)
2. **Verify input/output alignment**: Does the fixed phase's output align with the next phase's gate/input?
3. **Reverse-lookup gate conditions**: Are added/changed artifacts reflected in related gate checks?

### Output Format

```
| Phase | Same risk? | Evidence | Action |
|-------|-----------|----------|--------|
| 1a    | No        | —        | —      |
| 1b    | Yes       | Same schema branching as quick_actions | Fixed |
| 2a    | TBD       | output_markers unverified | Desk check pending |
| ...   | ...       | ...      | ...    |
```

### No Skip Allowed

- Re-running without horizontal sweep is prohibited
- "This fix is local, no sweep needed" is prohibited (you can't know it's local without checking)
- If the sweep result is "no impact on any phase", a one-line report suffices (no busywork)

---

## Command Writing Best Practices (Error Prevention)

- Use heredocs for commands with 2+ quote types, or JSON/regex in a long one-liner
- Add lightweight validation before execution (`bash -n`, `jq -e .`, `python3 -m py_compile`)
- PreToolUse hook pre-rejects:
  - Obvious unmatched quotes
  - Fragile long inline JSON + multi-escape patterns

```bash
cat <<'SH' >/tmp/run.sh
set -euo pipefail
# commands...
SH
bash -n /tmp/run.sh && bash /tmp/run.sh
```

## Knowledge Routing Table

| Knowledge Type | Target | Example |
|---------------|--------|---------|
| Coding pattern | Template / policy docs | DI pattern, mock techniques |
| Process improvement | Rules files / pipeline config | Workflow additions/fixes |
| Tool/API trap | Memory docs | CSS specs, API version quirks |
| Bug pattern | Tests / poka-yoke (helper functions) | `assertGradientBackground()` |
| Config trap | Templates / rules | `PRODUCT_MODULE_NAME` collision |

## Capture Process (3 Steps)

**Step 1: Identify the Learning**
- What was learned? (1-2 sentence summary)
- Why did the problem occur? (root cause)
- How to prevent recurrence? (prevention measure)

**Step 2: Route the Knowledge**
- Use the routing table above to determine where knowledge should be recorded
- If multiple destinations apply, prioritize highest impact
- Prevention level priority: L1 (compile-time) > L2 (auto-detect) > L3 (standardize) > L4 (alert)

**Step 3: Apply to Standards**
- Record knowledge at the determined destination
- Merge with existing similar knowledge if applicable
- Use `kaizen:` prefix in commit messages

### Notes

- Knowledge capture MUST be completed in the **same session** as the fix (don't defer)
- Even "trivial fixes" warrant capture if the root cause is in design or process
- `/tps-kaizen capture` command provides a structured template
