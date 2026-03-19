---
name: freeze
description: On-demand directory lock — blocks Edit/Write outside a frozen directory via PreToolUse hook. Use when: protecting files, preventing accidental edits, locking directory scope, isolating changes to one directory.
---

# /freeze — Directory Lock via PreToolUse Hook

Physically blocks `Edit` and `Write` tool calls that target files **outside** a specified directory using a permanently-registered `PreToolUse` hook (`freeze-guard.sh`). Unlike instruction-only guards, this enforcement is at the hook level — it cannot be bypassed by Claude's reasoning.

The hook is registered once and then activated/deactivated via state file. This is the **on-demand hook pattern**: registration is permanent, activation is on-demand via state file toggle. When the state file is absent, the hook exits immediately with zero overhead.

## Usage

```
/freeze <dir>      # activate: only allow edits inside <dir>
/freeze .          # lock to current working directory
/freeze off        # deactivate the lock
/freeze status     # check current freeze state
```

## Behavior

When active:
- `Edit` or `Write` to a file **outside** the frozen directory → **physically denied** by PreToolUse hook with informative message
- `Edit` or `Write` to a file **inside** the frozen directory → allowed
- `Read`, `Grep`, `Glob`, `Bash` → always allowed (read-only operations are safe)
- Writes to `~/.claude/state/freeze-state.json` → always allowed (needed for `/freeze off`)
- Writes to `~/.claude/` → always allowed (self-management: skills, hooks)

## Implementation

### On `/freeze <dir>`

Run these steps using the Bash tool:

```bash
# 1. Resolve to absolute path (handles relative paths and symlinks)
FREEZE_DIR=$(python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "<dir>" 2>/dev/null || cd "<dir>" && pwd)

# 2. Verify directory exists
test -d "$FREEZE_DIR" || { echo "ERROR: directory does not exist: $FREEZE_DIR"; exit 1; }

# 3. Write state file atomically (tmp -> rename)
STATE_FILE="$HOME/.claude/state/freeze-state.json"
TMP_FILE=$(mktemp "${STATE_FILE}.tmp.XXXXXX")
cat > "$TMP_FILE" <<EOF
{
  "active": true,
  "directory": "$FREEZE_DIR",
  "activated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
mv "$TMP_FILE" "$STATE_FILE"

echo "Freeze active: edits outside $FREEZE_DIR will be blocked by PreToolUse hook"
```

After activating, confirm to the user:
> "Freeze active: edits outside `<resolved_path>` will be blocked by PreToolUse hook. Run `/freeze off` to deactivate."

### On `/freeze off`

```bash
rm -f "$HOME/.claude/state/freeze-state.json"
echo "Freeze released: all edits are now allowed"
```

Confirm to the user:
> "Freeze released: all edits are now allowed."

### On `/freeze status`

```bash
STATE_FILE="$HOME/.claude/state/freeze-state.json"
if [ -f "$STATE_FILE" ]; then
  ACTIVE=$(jq -r '.active // "false"' "$STATE_FILE" 2>/dev/null)
  DIR=$(jq -r '.directory // "(unknown)"' "$STATE_FILE" 2>/dev/null)
  AT=$(jq -r '.activated_at // "(unknown)"' "$STATE_FILE" 2>/dev/null)
  if [ "$ACTIVE" = "true" ]; then
    echo "Freeze ACTIVE: $DIR (since $AT)"
  else
    echo "Freeze inactive (state file exists but active=false)"
  fi
else
  echo "Freeze inactive: no state file"
fi
```

## State File

The hook reads `~/.claude/state/freeze-state.json` at every Edit/Write call:

```json
{
  "active": true,
  "directory": "/Users/masa/Development/my-project/src",
  "activated_at": "2026-03-19T10:00:00Z"
}
```

When the file does not exist, the guard exits immediately (zero overhead).

## On-Demand Hook Registration

The `freeze-guard.sh` hook must be registered in `~/.claude/settings.json` before freeze enforcement works. This is a **one-time setup** that persists across all sessions. Once registered, the hook is always present but does nothing when no state file exists — zero overhead when freeze is not active.

For step-by-step registration instructions and the exact JSON snippet, see `references/hook-setup.md`.

## Gotchas

### Session Restart After Registration

Hook settings are loaded at session start (not live-reloaded). After adding `freeze-guard.sh` to `settings.json` for the first time, restart the session for the hook to take effect. State file changes (`/freeze on/off`) take effect immediately without restart — only the initial registration requires a session restart.

### Symlink Resolution

Both the file path and the freeze directory are resolved with `os.path.realpath()` before comparison. Symlinks will not bypass the guard — both sides of the comparison are resolved to canonical paths before checking the directory boundary.

### State File Deletion Semantics

Use `rm -f` to deactivate. Setting `active: false` and leaving the file is not supported — the hook checks file existence, not the `active` field. Always delete the file to deactivate. This makes the inactive state zero-overhead: no file read, no JSON parse.

### Self-Management Allowed

The hook always allows writes to `~/.claude/` (hooks, skills, settings). This means you can update skill files or re-register the hook even while freeze is active. Self-management of Claude's own configuration is always permitted.

### Freeze Directory Boundary

Writes to the exact freeze directory path (not just files within it) are also allowed. The guard checks `startswith(freeze_dir)` so the directory itself is inside the boundary. This prevents the edge case where `/freeze /tmp/work` would block writes to `/tmp/work` itself.

## Additional Resources

When detailed setup information is needed, read these files:

- **`references/hook-setup.md`** — Full hook registration JSON snippet, setup verification script, and step-by-step first-time registration instructions
