# careful-guard.sh Hook Registration

This file contains the detailed setup instructions for registering the `careful-guard.sh` PreToolUse hook. This is a one-time setup — once registered, the hook persists across all sessions and activates/deactivates via state file with zero overhead when inactive.

## Hook Registration JSON

Add the following entry to the `PreToolUse` array in `~/.claude/settings.json`:

```json
{
  "matcher": "Bash",
  "hooks": [{ "type": "command", "command": "<absolute-path>/skills/careful/scripts/careful-guard.sh", "timeout": 5 }]
}
```

Replace `<absolute-path>` with the absolute path to the `andon-for-llm-agents` repository root. For example:

```json
{
  "matcher": "Bash",
  "hooks": [{ "type": "command", "command": "/Users/masa/.claude/skills/careful/scripts/careful-guard.sh", "timeout": 5 }]
}
```

Note: The matcher is `"Bash"`, not `"Edit|Write"` like the freeze hook. This hook guards Bash command execution, not file write operations.

### Full settings.json Example

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "/Users/masa/.claude/hooks/freeze-guard.sh", "timeout": 5 }]
      },
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "/Users/masa/.claude/skills/careful/scripts/careful-guard.sh", "timeout": 5 }]
      }
    ]
  }
}
```

## Checking Setup Status

Run this script to verify whether the hook is already registered:

```bash
python3 -c "
import json, os
settings_path = os.path.expanduser('~/.claude/settings.json')
d = json.load(open(settings_path))
entries = [e for e in d.get('hooks', {}).get('PreToolUse', []) if 'careful-guard' in str(e)]
print('careful-guard.sh registered:', len(entries) > 0)
if not entries:
    print('WARNING: careful-guard.sh not registered. Follow setup instructions.')
"
```

## If Not Registered

1. Open `~/.claude/settings.json` in an editor
2. Locate the `hooks.PreToolUse` array (create it if it does not exist)
3. Add the entry:
   ```json
   {
     "matcher": "Bash",
     "hooks": [{ "type": "command", "command": "<absolute-path-to-careful-guard.sh>", "timeout": 5 }]
   }
   ```
4. Save the file
5. **Restart the Claude Code session** — hooks are loaded at session start and cached for the session duration

After restarting, `/careful on` will activate destructive command blocking at the hook level.

## How the On-Demand Pattern Works

The hook is registered permanently but does nothing unless a state file exists:

```
Registration (one-time):   ~/.claude/settings.json → careful-guard.sh always runs on Bash calls
Activation (on-demand):    /careful on   → creates ~/.claude/state/careful-state.json
Deactivation (on-demand):  /careful off  → deletes ~/.claude/state/careful-state.json
```

When the state file does not exist, `careful-guard.sh` reads stdin and exits immediately with `{}`. The overhead is a single `[ -f ... ]` check per Bash tool call — negligible.

State file changes (`/careful on/off`) take effect immediately — no session restart needed after initial registration.

## Relationship to freeze Hook

Both `freeze-guard.sh` and `careful-guard.sh` follow the same on-demand hook pattern:

| Hook | Matcher | Guards | State File |
|------|---------|--------|-----------|
| `freeze-guard.sh` | `Edit\|Write` | File path scope (directory boundary) | `freeze-state.json` |
| `careful-guard.sh` | `Bash` | Command content (destructive patterns) | `careful-state.json` |

They can coexist in `settings.json` simultaneously with no conflict — independent matchers, independent state files, independent activation.
