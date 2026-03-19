#!/bin/bash
# careful-guard.sh — PreToolUse hook: block destructive Bash commands
#
# Copyright 2026 AllNew LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Always-on guard pattern: permanently registered in settings.json.
# When no state file exists (careful inactive), exits immediately with {}.
# When careful is active, blocks destructive Bash command patterns.
#
# State file: ~/.claude/state/careful-state.json
# Format: { "active": true, "activated_at": "ISO8601" }
#
# Blocked patterns:
#   rm -rf / rm -fr (recursive force delete)
#   git push --force / git push -f (force push)
#   git reset --hard (destructive reset)
#   DROP TABLE / DROP DATABASE (SQL, case-insensitive)
#   kubectl delete (Kubernetes resource deletion)
#   docker system prune (Docker cleanup)

set -euo pipefail

# --- Help ---

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<'EOF'
careful-guard.sh — PreToolUse hook: block destructive Bash commands

This script is registered as a PreToolUse hook in ~/.claude/settings.json.
It reads JSON from stdin and outputs {} (allow) or a deny response.

State file: ~/.claude/state/careful-state.json
  Present  → careful mode active, destructive commands blocked
  Absent   → careful mode inactive, all commands allowed (zero overhead)

Usage: Not called directly — invoked by Claude Code PreToolUse hook system.
EOF
  exit 0
fi

STATE_FILE="$HOME/.claude/state/careful-state.json"

# Read stdin once — PreToolUse hook provides JSON on stdin
INPUT=$(cat)

# Fast path: no state file = careful is inactive — allow everything
if [ ! -f "$STATE_FILE" ]; then
  echo "{}"
  exit 0
fi

# Only guard Bash tool
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null || echo "")
if [ "$TOOL_NAME" != "Bash" ]; then
  echo "{}"
  exit 0
fi

# Extract command from tool_input
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null || echo "")
if [ -z "$COMMAND" ]; then
  echo "{}"
  exit 0
fi

# Check for destructive patterns (case-insensitive where appropriate)
BLOCKED=""

# rm -rf: matches any flag combo containing both r and f (e.g., -rf, -fr, -rfi, -Rrf)
if echo "$COMMAND" | grep -qE 'rm[[:space:]].*-[a-zA-Z]*[rR][a-zA-Z]*[fF]|rm[[:space:]].*-[a-zA-Z]*[fF][a-zA-Z]*[rR]'; then
  BLOCKED="rm -rf (recursive force delete)"

# git push --force or git push -f
elif echo "$COMMAND" | grep -qE 'git[[:space:]]+push[[:space:]].*(--force|-f\b)'; then
  BLOCKED="git push --force (force push)"

# git reset --hard
elif echo "$COMMAND" | grep -qE 'git[[:space:]]+reset[[:space:]]+--hard'; then
  BLOCKED="git reset --hard (destructive reset)"

# DROP TABLE or DROP DATABASE (case-insensitive)
elif echo "$COMMAND" | grep -qiE 'DROP[[:space:]]+(TABLE|DATABASE)'; then
  BLOCKED="DROP TABLE/DATABASE (SQL destructive operation)"

# kubectl delete
elif echo "$COMMAND" | grep -qE 'kubectl[[:space:]]+delete'; then
  BLOCKED="kubectl delete (Kubernetes resource deletion)"

# docker system prune
elif echo "$COMMAND" | grep -qE 'docker[[:space:]]+system[[:space:]]+prune'; then
  BLOCKED="docker system prune (Docker cleanup)"
fi

if [ -n "$BLOCKED" ]; then
  jq -n \
    --arg blocked "$BLOCKED" \
    --arg cmd "$COMMAND" \
    '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: ("CAREFUL GUARD: Blocked \($blocked). Command: \($cmd). Run /careful off to disable protection.")
      }
    }'
  exit 0
fi

# Not a destructive command — allow
echo "{}"
exit 0
