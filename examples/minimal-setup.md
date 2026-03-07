# Minimal Setup (3 Files, 5 Minutes)

The absolute minimum to get ANDON line-stop working with Claude Code.

## What You Get

- Automatic failure detection on Bash command errors
- Incident reports with root cause classification
- Forward-progress blocking (git push, deploy) when ANDON is open
- Auto-generated prevention rules with rollback support

## Setup

### 1. Copy hook files

```bash
mkdir -p .claude/hooks

# Download or copy these 3 files:
# hooks/tps-kaizen-runtime.py  → .claude/hooks/tps-kaizen-runtime.py
# hooks/tps-andon-posttool-guard.sh → .claude/hooks/tps-andon-posttool-guard.sh
# hooks/tps-andon-pretool-guard.sh → .claude/hooks/tps-andon-pretool-guard.sh
# hooks/tps-andon-control.sh → .claude/hooks/tps-andon-control.sh

chmod +x .claude/hooks/*.sh
```

### 2. Create `.claude/settings.json`

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
        "hooks": [".claude/hooks/tps-andon-posttool-guard.sh"]
      }
    ]
  }
}
```

### 3. Add to CLAUDE.md (recommended)

Add this line to your project's `CLAUDE.md`:

```markdown
## ANDON / Kaizen

When a Bash command fails with non-zero exit, ANDON opens automatically.
While ANDON is open, forward-progress commands (git push, deploy) are blocked.
Fix the root cause, then close: `.claude/hooks/tps-andon-control.sh close "<reason>"`.
Use `kaizen:` prefix for commits that capture learning from the fix.
```

## Verify

```bash
python3 .claude/hooks/tps-kaizen-runtime.py status
# → ANDON: CLEAR
```

## Usage

Just start coding. When a command fails, ANDON handles the rest:

```
$ npm test  # fails
[TPS/ANDON] Anomaly detected — line stopped. incident=INC-20260305-123456-abc12345
Report: ~/.claude/state/kaizen/incidents/INC-20260305-123456-abc12345/report.md
```

Fix the issue, then:
```bash
.claude/hooks/tps-andon-control.sh close "fixed: missing test dependency"
```

## Next Steps

For the full experience (learning capture, Meta-ANDON, quality rules), see [INTEGRATION.md](../INTEGRATION.md).
