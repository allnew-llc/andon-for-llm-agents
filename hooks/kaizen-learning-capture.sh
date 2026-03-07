#!/bin/bash
# kaizen-learning-capture.sh — PostToolUse hook for automated knowledge capture
#
# Triggered after every Bash tool use. Detects git commit commands with
# fix/bug-related keywords and injects a prompt reminding the agent to
# capture the learning.
#
# Hook type: PostToolUse (Bash matcher)
# Output: JSON with optional PostToolUse additionalContext
#
# Copyright 2026 AllNew LLC — Apache License 2.0

set -euo pipefail

INPUT=$(cat)

TOOL_INPUT=$(printf '%s\n' "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")

# Only process git commit commands
if ! printf '%s\n' "$TOOL_INPUT" | grep -q "git commit"; then
  echo "{}"
  exit 0
fi

COMMIT_MSG="$TOOL_INPUT"

HAS_FIX_KEYWORD=false
for keyword in "fix" "bug" "hotfix" "patch" "workaround" "kaizen"; do
  if printf '%s\n' "$COMMIT_MSG" | grep -qi "$keyword"; then
    HAS_FIX_KEYWORD=true
    break
  fi
done

if [ "$HAS_FIX_KEYWORD" = true ]; then
  cat <<'HOOK_JSON'
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "[Kaizen Learning Capture] This commit may contain knowledge from a bug fix or problem resolution. Per the Kaizen Learning Capture rule, please verify: (1) What was learned? (2) Where should the knowledge be routed? (tests/poka-yoke, docs, rules, templates) (3) Has the standard been updated? — Use `/tps-kaizen capture` for a structured template."
  }
}
HOOK_JSON
else
  echo "{}"
fi
