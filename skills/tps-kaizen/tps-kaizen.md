---
description: TPS (lean manufacturing) based anomaly response, root cause analysis, and continuous improvement
argument-hint: "<subcommand> — andon, five-whys, kaizen, audit, capture"
---

# TPS Kaizen

Improvement skill based on lean manufacturing principles (Jidoka + JIT).
Executes the cycle of problem detection, line stop, analysis, and recurrence prevention.

## Subcommands

| Command | Purpose |
|---------|---------|
| `andon <problem>` | Jidoka 4-step anomaly response (Detect → Stop → Fix → Investigate) |
| `five-whys <problem>` | Root cause analysis via Five Whys |
| `kaizen <area>` | Continuous improvement via Improvement Kata |
| `audit` | 3M (Muda/Mura/Muri) waste audit |
| `capture [learning]` | Capture and standardize knowledge from bug fixes |

## Execution

When this command is invoked, load the following skill files:

1. **Main skill**: `skills/tps-kaizen/SKILL.md`
2. **Reference files** (per subcommand):
   - `andon` → `references/jidoka-response.md`
   - `five-whys` → `references/five-whys-template.md`
   - `kaizen` → `references/kaizen-kata.md`
   - `audit` → SKILL.md `audit` section
   - `capture` → SKILL.md `capture` section + knowledge routing table

### Without arguments

Display the Usage section from SKILL.md and prompt subcommand selection.

### Subcommand behavior

#### `andon <problem>`

1. Load SKILL.md `andon` section and `references/jidoka-response.md`
2. Record the problem using the ANDON report template
3. Execute 4 steps: Detect → Stop → Fix → Investigate
4. Investigation step automatically invokes `five-whys`

#### `five-whys <problem>`

1. Load SKILL.md `five-whys` section and `references/five-whys-template.md`
2. Define the problem, verify with actual code/logs/config (Genchi Genbutsu)
3. Follow the Five Whys template to identify root cause
4. Propose prevention at levels L1 (poka-yoke) through L4 (alert)

#### `kaizen <area>`

1. Load SKILL.md `kaizen` section and `references/kaizen-kata.md`
2. Walk through Improvement Kata 4 steps interactively
3. Use Coaching Kata 5 questions to check progress

#### `audit`

1. Load SKILL.md `audit` section
2. Audit target from 3M perspectives (Muda/Mura/Muri)
3. Output audit report and identify top priority improvement
4. Optionally launch `kaizen` to start improvement cycle

#### `capture [learning]`

1. **Identify the learning**:
   - What was learned? (1-2 sentence summary)
   - Why did the problem occur? (root cause)
   - How to prevent recurrence? (L1 > L2 > L3 > L4)
2. **Route the knowledge**: Determine target (tests, docs, rules, templates)
3. **Apply to standards**: Record at determined location, use `kaizen:` commit prefix

## ANDON state control (hook integration)

- Status: `.claude/hooks/tps-andon-control.sh status`
- Close: `.claude/hooks/tps-andon-control.sh close "<reason>"`
- Rollback: `.claude/hooks/tps-andon-control.sh rollback <incident_id|latest>`

### Close gates

- `evidence.json`, `analysis.json`, `actions.json`, `report.md` must exist
- Low confidence (<0.70) requires `manual-approved:` in close reason
- PreToolUse blocks unmatched quotes and brittle inline JSON commands
