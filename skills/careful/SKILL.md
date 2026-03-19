---
name: careful
description: "Use when: destructive commands, dangerous operations, production safety, force push protection, database drop protection, careful mode, safe mode. Session-scoped on-demand hook that blocks rm -rf, force-push, DROP TABLE, and kubectl delete."
version: 1.0.0
---

# /careful — Destructive Command Guard via PreToolUse Hook

Physically blocks destructive Bash commands at the hook level using the same on-demand hook pattern as `/freeze`. The `careful-guard.sh` script is permanently registered in `~/.claude/settings.json` but does nothing unless activated. Activation creates a state file; deactivation deletes it. This is session-scoped safety — use it when working near production, running database migrations, or doing anything where a single wrong command causes irreversible damage.

Unlike instruction-only guards (telling Claude "be careful"), this enforcement happens at the PreToolUse hook level. The hook intercepts Bash tool calls before execution — Claude cannot bypass it through reasoning.

## When to Use This Skill

| Situation | Why Activate |
|-----------|-------------|
| Working near production systems | rm -rf or force push on wrong branch = outage |
| Refactoring with risky deletes | Large file/directory deletions during code cleanup |
| Database migration sessions | DROP TABLE accidents during schema changes |
| Kubernetes operations | kubectl delete on wrong namespace = data loss |
| Pair programming safety | Second layer of protection when multiple people share a session |

## Usage

```
/careful on        # activate destructive command blocking
/careful off       # deactivate
/careful status    # check current state
```

## Blocked Commands

The hook inspects the `command` field of every Bash tool call when careful mode is active:

| Pattern | What It Catches | What It Allows |
|---------|----------------|----------------|
| `rm -rf` / `rm -fr` | Recursive force delete (any flag combo with r+f) | `rm` without `-rf` |
| `git push --force` / `git push -f` | Force push | `git push` without force flag |
| `git reset --hard` | Destructive reset | `git reset --soft`, `git reset HEAD` |
| `DROP TABLE` / `DROP DATABASE` | SQL destructive ops (case-insensitive) | SELECT/INSERT/UPDATE |
| `kubectl delete` | Kubernetes resource deletion | `kubectl get`, `kubectl describe` |
| `docker system prune` | Docker-wide cleanup | `docker rm` single container |

The hook uses `grep -E` string matching on the full command string. It does NOT parse command AST — see Gotchas.

## Implementation

### On `/careful on`

```bash
STATE_FILE="$HOME/.claude/state/careful-state.json"
mkdir -p "$(dirname "$STATE_FILE")"
TMP_FILE=$(mktemp "${STATE_FILE}.tmp.XXXXXX")
cat > "$TMP_FILE" <<EOF
{
  "active": true,
  "activated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
mv "$TMP_FILE" "$STATE_FILE"
echo "Careful mode active: destructive commands will be blocked by PreToolUse hook"
```

### On `/careful off`

```bash
rm -f "$HOME/.claude/state/careful-state.json"
echo "Careful mode deactivated: all commands allowed"
```

### On `/careful status`

```bash
STATE_FILE="$HOME/.claude/state/careful-state.json"
if [ -f "$STATE_FILE" ]; then
  AT=$(jq -r '.activated_at // "(unknown)"' "$STATE_FILE" 2>/dev/null)
  echo "Careful mode ACTIVE (since $AT)"
else
  echo "Careful mode inactive"
fi
```

## On-Demand Hook Registration

`careful-guard.sh` must be registered in `~/.claude/settings.json` before the hook takes effect. This is a **one-time setup** that persists across all sessions.

Registration entry:

```json
{
  "matcher": "Bash",
  "hooks": [{ "type": "command", "command": "<path>/skills/careful/scripts/careful-guard.sh", "timeout": 5 }]
}
```

Note: The matcher is `"Bash"` — careful guards Bash command execution, unlike freeze which guards `"Edit|Write"`.

For detailed registration instructions, step-by-step setup, and verification script, see `references/hook-setup.md`.

## Gotchas

### Session Restart After Registration

Hook settings are loaded at session start and are not live-reloaded. After adding `careful-guard.sh` to `settings.json` for the first time, the session must be restarted before the hook takes effect. Once registered, state file changes (`/careful on/off`) take effect immediately — only the initial registration requires a restart.

### Pattern Matching Limitations

The hook uses `grep -E` string matching on the raw command text, not AST parsing. A command like `echo "rm -rf"` — where `rm -rf` is a string literal, not a command execution — will also be blocked. This is intentional: false positives (blocking a harmless echo) are vastly safer than false negatives (missing a real destructive command). If you need to print a destructive pattern as a string, run `/careful off` first, then `/careful on` after.

### Pipe and Subshell Detection

The hook checks the entire command string, including pipes and subshells. `echo foo | xargs rm -rf` will be caught because `rm -rf` appears in the string. However, commands built dynamically at runtime cannot be detected: `eval "$CMD"` where CMD contains `rm -rf` is invisible to the hook — it sees `eval "$CMD"`, not the expanded value. Runtime-constructed destructive commands are outside the protection scope.

### Careful vs Freeze Coexistence

Both careful and freeze hooks can be active simultaneously with no conflict. They guard different tools:
- freeze: `Edit` and `Write` tools (file modification operations)
- careful: `Bash` tool (shell command execution)

They use different state files (`careful-state.json` vs `freeze-state.json`) and are independently activated/deactivated. Running both simultaneously gives full coverage: careful blocks destructive shell commands, freeze locks the edit scope to a specific directory.

## Additional Resources

- **`references/hook-setup.md`** — Full hook registration JSON, verification script, and step-by-step first-time registration instructions
- **`scripts/careful-guard.sh`** — PreToolUse hook implementation
