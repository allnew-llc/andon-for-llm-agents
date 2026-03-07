# Integration Guide

## Overview

This guide covers the full integration of ANDON for LLM Agents into your Claude Code project.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Claude Code Session                       │
│                                                              │
│  ┌──────────┐   PreToolUse    ┌───────────────────────┐    │
│  │  Agent    │ ──────────────→ │ tps-andon-pretool     │    │
│  │  (Bash)   │                 │ - quote validation     │    │
│  │           │                 │ - ANDON block check    │    │
│  │           │   PostToolUse   │                        │    │
│  │           │ ──────────────→ │ tps-andon-posttool    │    │
│  │           │                 │ → tps-kaizen-runtime   │    │
│  │           │                 │   - failure classify   │    │
│  │           │                 │   - incident create    │    │
│  │           │                 │   - auto-standardize   │    │
│  │           │                 │                        │    │
│  │           │   PostToolUse   │ kaizen-learning-capture│    │
│  │           │ ──────────────→ │ - fix commit detection │    │
│  └──────────┘                 └───────────────────────┘    │
│                                         │                    │
│                                         ▼                    │
│                            ┌─────────────────────┐          │
│                            │  ~/.claude/state/    │          │
│                            │  ├── andon-open.json │          │
│                            │  └── kaizen/         │          │
│                            │      ├── incidents/  │          │
│                            │      ├── registry    │          │
│                            │      └── history/    │          │
│                            └─────────────────────┘          │
└────────────────────────────────────────────────────────────┘
```

## Step-by-Step Setup

### 1. Copy Files

```bash
# From your project root
mkdir -p .claude/hooks .claude/rules .claude/commands

# Core hooks (required)
cp hooks/tps-kaizen-runtime.py .claude/hooks/
cp hooks/tps-andon-posttool-guard.sh .claude/hooks/
cp hooks/tps-andon-pretool-guard.sh .claude/hooks/
cp hooks/tps-andon-control.sh .claude/hooks/
chmod +x .claude/hooks/*.sh

# Learning capture hook (recommended)
cp hooks/kaizen-learning-capture.sh .claude/hooks/
chmod +x .claude/hooks/kaizen-learning-capture.sh

# Meta-ANDON guard (recommended for pipeline projects)
cp hooks/meta_andon_guard.py .claude/hooks/

# Rules (add to your CLAUDE.md or .claude/rules/)
cp rules/70-kaizen-learning.md .claude/rules/
cp rules/45-quality-driven-execution.md .claude/rules/

# Skills (optional but recommended)
mkdir -p .claude/commands
cp skills/tps-kaizen/tps-kaizen.md .claude/commands/
# Copy the full skill + references to a docs directory
cp -r skills/tps-kaizen docs/skills/tps-kaizen
```

### 2. Register Hooks

Add to your `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [".claude/hooks/tps-andon-pretool-guard.sh"]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          ".claude/hooks/tps-andon-posttool-guard.sh",
          ".claude/hooks/kaizen-learning-capture.sh"
        ]
      }
    ]
  }
}
```

### 3. Add Rules to CLAUDE.md

Option A: Reference the rule files

```markdown
# CLAUDE.md

## Rules
- `.claude/rules/70-kaizen-learning.md` — ANDON + Kaizen learning capture
- `.claude/rules/45-quality-driven-execution.md` — Quality-driven execution
```

Option B: Inline (if you don't use rule files)

Copy the content of `rules/70-kaizen-learning.md` directly into your `CLAUDE.md`.

### 4. Verify Installation

```bash
# Check hooks are executable
ls -la .claude/hooks/

# Test the runtime
python3 .claude/hooks/tps-kaizen-runtime.py status
# Should print: "ANDON: CLEAR"

# Test the control script
.claude/hooks/tps-andon-control.sh status
# Should print: "ANDON: CLEAR"
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANDON_WORKSPACE` | (auto-detect) | Override workspace root path |
| `ANDON_STATE_DIR` | `<workspace>/.claude/state` | Override state directory |
| `ANDON_CONFIDENCE_AUTO` | `0.70` | Threshold for auto-standardization |
| `ANDON_CONFIDENCE_MANUAL` | `0.70` | Threshold below which manual approval is required for close |
| `META_ANDON_FAILURE_THRESHOLD` | `3` | Consecutive failures to trigger Meta-ANDON |

### Customizing Failure Patterns

Edit `CLASSIFICATION_RULES` in `tps-kaizen-runtime.py`:

```python
CLASSIFICATION_RULES = [
    # (cause_id, label, confidence, regex_pattern)
    ("my_custom_error", "My custom error", 0.90, r"my specific pattern"),
    # ... keep existing rules ...
]
```

### Customizing Forward-Progress Blocks

Edit `block_patterns` in `tps-andon-pretool-guard.sh` to add/remove blocked commands:

```python
block_patterns = [
    r"\bgit\s+push\b",
    r"\bmy-deploy-command\b",  # Add your own
    # ...
]
```

---

## Usage Guide

### Normal Flow (Automatic)

1. You're coding with Claude Code
2. A Bash command fails (non-zero exit)
3. ANDON opens automatically — you see the incident report
4. Forward-progress commands are blocked
5. Fix the issue
6. Run Five Whys on the root cause
7. Close ANDON: `.claude/hooks/tps-andon-control.sh close "root cause: X; prevention: Y"`

### Manual ANDON

You can also open ANDON manually for problems the hook doesn't catch:

```
/tps-kaizen andon "deployment failed silently with exit 0"
```

### Checking Status

```bash
.claude/hooks/tps-andon-control.sh status
```

### Rolling Back Auto-Standardization

If the auto-generated standardization rule is wrong:

```bash
.claude/hooks/tps-andon-control.sh rollback INC-20260305-abc123
# or rollback the latest:
.claude/hooks/tps-andon-control.sh rollback latest
```

---

## Skill Setup (Optional)

The `/tps-kaizen` skill provides structured commands. To set it up:

1. Copy `skills/tps-kaizen/tps-kaizen.md` to `.claude/commands/tps-kaizen.md`
2. Update the file paths in the skill to point to your docs directory
3. Copy reference files to `docs/skills/tps-kaizen/references/`

Then use in Claude Code:
```
/tps-kaizen andon "tests are failing after dependency update"
/tps-kaizen five-whys "build fails on CI but passes locally"
/tps-kaizen kaizen "test coverage improvement"
/tps-kaizen audit
/tps-kaizen capture
```

---

## Integration with Existing Pipelines

### CI/CD Integration

The Meta-ANDON guard can be integrated with CI run tracking:

```python
from hooks.meta_andon_guard import evaluate_meta_andon

result = evaluate_meta_andon(
    artifacts_dir=Path("docs/pipeline"),
    consecutive_failures=3,
    failure_run_ids=["run-001", "run-002", "run-003"],
)

if result["blocked"]:
    print("Meta-ANDON: Blocked! Create required analysis artifacts first.")
    print(f"Missing: {result['missing_artifacts']}")
```

### Custom State Directory

If your project uses a different state directory:

```bash
export ANDON_STATE_DIR="/path/to/my/state"
```

---

## Troubleshooting

### ANDON won't close

**Missing artifacts**: Check that all required files exist:
```bash
ls ~/.claude/state/kaizen/incidents/INC-*/
# Should see: evidence.json, analysis.json, actions.json, report.md
```

**Low confidence**: If root cause confidence < 0.70, include `manual-approved:` in close reason:
```bash
.claude/hooks/tps-andon-control.sh close "manual-approved: verified root cause was X"
```

### Hooks not firing

1. Check `.claude/settings.json` has the hook configuration
2. Check hook files are executable: `chmod +x .claude/hooks/*.sh`
3. Check Python 3 is available: `python3 --version`

### State directory issues

The runtime auto-creates state directories. If you see permission errors:
```bash
mkdir -p ~/.claude/state/kaizen
```
