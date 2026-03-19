# freeze-guard.sh Hook Registration

This file contains the detailed setup instructions for registering the `freeze-guard.sh` PreToolUse hook. This is a one-time setup — once registered, the hook persists across all sessions.

## Hook Registration JSON

Add the following entry to the `PreToolUse` array in `~/.claude/settings.json`:

```json
{
  "matcher": "Edit|Write",
  "hooks": [{ "type": "command", "command": "/Users/masa/.claude/hooks/freeze-guard.sh", "timeout": 5 }]
}
```

The full `hooks` section in `settings.json` should look like:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "/Users/masa/.claude/hooks/freeze-guard.sh", "timeout": 5 }]
      }
    ]
  }
}
```

## Checking Setup Status

Run this script to verify whether the hook is already registered:

```bash
python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
entries = [e for e in d.get('hooks', {}).get('PreToolUse', []) if 'Edit' in e.get('matcher', '')]
print('Hook registered:', len(entries) > 0)
if not entries:
    print('WARNING: freeze-guard.sh not registered. Run setup.')
"
```

## If Not Registered

1. Open `~/.claude/settings.json` in an editor
2. Add the entry to the `PreToolUse` array (create the `hooks` key if it doesn't exist):
   ```json
   {
     "matcher": "Edit|Write",
     "hooks": [{ "type": "command", "command": "/Users/masa/.claude/hooks/freeze-guard.sh", "timeout": 5 }]
   }
   ```
3. **Restart the Claude Code session** — hooks are loaded at session start and cached for the session duration.

After the session restart, `/freeze <dir>` will enforce at the hook level. State file changes (`/freeze on/off`) take effect immediately after that — no further restarts needed.

## How the On-Demand Pattern Works

The hook is registered permanently but does nothing unless a state file exists:

```
Registration (one-time):   ~/.claude/settings.json → freeze-guard.sh always runs on Edit/Write
Activation (on-demand):    /freeze <dir>  → creates ~/.claude/state/freeze-state.json
Deactivation (on-demand):  /freeze off    → deletes ~/.claude/state/freeze-state.json
```

When the state file does not exist, `freeze-guard.sh` exits 0 immediately. The overhead is a single `[ -f ... ]` check per Edit/Write call — negligible.
