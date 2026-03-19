#!/usr/bin/env bash
# Copyright 2024 AllNew LLC
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
# standup.sh - Collect git activity and GSD task state for daily standup
#
# Usage:
#   standup.sh [--help] [<hours>|week]
#
# Arguments:
#   <hours>   Number of hours to look back (default: 24). Must be a positive integer.
#             Suffix 'h' is accepted and stripped (e.g., "48h" = 48 hours).
#   week      Shorthand for 168 hours (7 days).
#
# Output:
#   Prints structured sections to stdout:
#     === GIT ACTIVITY (last Nh) ===
#     === TASK STATE ===
#     === NEXT UP ===

set -euo pipefail

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
usage() {
    cat <<'EOF'
Usage: standup.sh [--help] [<hours>|week]

Collect git activity and GSD task state into a structured standup summary.

Arguments:
  <hours>   Hours to look back (default: 24). Suffix 'h' accepted (e.g. 48h).
  week      Look back 7 days (168 hours).

Output sections:
  === GIT ACTIVITY (last Nh) ===    Recent commits via git log
  === TASK STATE ===                 Current position from .planning/STATE.md
  === NEXT UP ===                    Next incomplete item from .planning/ROADMAP.md

Environment:
  No environment variables required. All data comes from the git repo and
  optional .planning/ directory in the repo root or parent directories.

Examples:
  standup.sh             # Last 24 hours
  standup.sh 48h         # Last 48 hours
  standup.sh week        # Last 7 days
EOF
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
HOURS=24

if [ "${1-}" = "--help" ] || [ "${1-}" = "-h" ]; then
    usage
    exit 0
fi

if [ $# -gt 0 ]; then
    ARG="$1"
    if [ "$ARG" = "week" ]; then
        HOURS=168
    else
        # Strip trailing 'h' if present, then validate as integer
        STRIPPED="${ARG%h}"
        case "$STRIPPED" in
            ''|*[!0-9]*)
                printf 'Error: argument must be a positive integer or "week" (got: %s)\n' "$ARG" >&2
                usage >&2
                exit 1
                ;;
            *)
                HOURS="$STRIPPED"
                ;;
        esac
        if [ "$HOURS" -le 0 ] 2>/dev/null; then
            printf 'Error: hours must be greater than 0 (got: %s)\n' "$HOURS" >&2
            exit 1
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Verify we are in a git repository
# ---------------------------------------------------------------------------
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    printf 'Error: not a git repository. Run standup.sh from inside a git repo.\n' >&2
    exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"

# ---------------------------------------------------------------------------
# Shallow clone detection
# ---------------------------------------------------------------------------
IS_SHALLOW="false"
if git rev-parse --is-shallow-repository >/dev/null 2>&1; then
    SHALLOW_RESULT="$(git rev-parse --is-shallow-repository 2>/dev/null || echo false)"
    if [ "$SHALLOW_RESULT" = "true" ]; then
        IS_SHALLOW="true"
    fi
fi

# ---------------------------------------------------------------------------
# Compute --since value for git log
# ---------------------------------------------------------------------------
# Use ISO 8601 offset format for portability (bash 3.2+ on macOS/Linux)
if date --version >/dev/null 2>&1; then
    # GNU date
    SINCE="$(date -d "${HOURS} hours ago" --iso-8601=seconds)"
else
    # BSD date (macOS)
    SINCE="$(date -v -"${HOURS}H" '+%Y-%m-%dT%H:%M:%S%z')"
fi

# ---------------------------------------------------------------------------
# GIT ACTIVITY section
# ---------------------------------------------------------------------------
printf '=== GIT ACTIVITY (last %sh) ===\n' "$HOURS"

if [ "$IS_SHALLOW" = "true" ]; then
    printf '[WARNING: shallow clone detected — history may be incomplete. Run: git fetch --unshallow]\n'
fi

COMMIT_OUTPUT="$(git log --oneline --since="$SINCE" --no-merges 2>/dev/null || true)"

if [ -z "$COMMIT_OUTPUT" ]; then
    printf '(no commits found in the last %s hours)\n' "$HOURS"
    printf 'Note: commits may be on a different branch or in another repository.\n'
else
    printf '%s\n' "$COMMIT_OUTPUT"
fi

printf '\n'

# ---------------------------------------------------------------------------
# Locate .planning/ directory (repo root or parent)
# ---------------------------------------------------------------------------
find_planning_dir() {
    local dir="$REPO_ROOT"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.planning" ]; then
            printf '%s/.planning' "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

PLANNING_DIR=""
if find_planning_dir >/dev/null 2>&1; then
    PLANNING_DIR="$(find_planning_dir)"
fi

# ---------------------------------------------------------------------------
# TASK STATE section
# ---------------------------------------------------------------------------
printf '=== TASK STATE ===\n'

STATE_FILE=""
if [ -n "$PLANNING_DIR" ] && [ -f "$PLANNING_DIR/STATE.md" ]; then
    STATE_FILE="$PLANNING_DIR/STATE.md"
fi

if [ -z "$STATE_FILE" ]; then
    printf 'Position: (no .planning/STATE.md found — project may not use GSD)\n'
    printf 'Blockers: unknown\n'
else
    # Extract Current Position line
    # The range must skip the heading line itself, then stop at the next ## heading
    POSITION="$(awk '/^## Current Position$/{found=1;next} found && /^## /{exit} found{print}' "$STATE_FILE" | grep -m1 '^Phase:' || true)"
    PLAN_LINE="$(awk '/^## Current Position$/{found=1;next} found && /^## /{exit} found{print}' "$STATE_FILE" | grep -m1 '^Plan:' || true)"
    STATUS_LINE="$(awk '/^## Current Position$/{found=1;next} found && /^## /{exit} found{print}' "$STATE_FILE" | grep -m1 '^Status:' || true)"

    if [ -n "$POSITION" ]; then
        printf '%s\n' "$POSITION"
    else
        printf 'Position: (not found in STATE.md)\n'
    fi

    if [ -n "$PLAN_LINE" ]; then
        printf '%s\n' "$PLAN_LINE"
    fi

    if [ -n "$STATUS_LINE" ]; then
        printf '%s\n' "$STATUS_LINE"
    fi

    # Extract Blockers section
    BLOCKERS="$(awk '/^### Blockers\/Concerns$/{found=1;next} found && /^### /{exit} found{print}' "$STATE_FILE" | grep -v '^$' | head -5 || true)"
    if [ -z "$BLOCKERS" ] || printf '%s' "$BLOCKERS" | grep -q '^None'; then
        printf 'Blockers: None\n'
    else
        printf 'Blockers:\n'
        printf '%s\n' "$BLOCKERS" | while IFS= read -r line; do
            printf '  %s\n' "$line"
        done
    fi
fi

printf '\n'

# ---------------------------------------------------------------------------
# NEXT UP section
# ---------------------------------------------------------------------------
printf '=== NEXT UP ===\n'

ROADMAP_FILE=""
if [ -n "$PLANNING_DIR" ] && [ -f "$PLANNING_DIR/ROADMAP.md" ]; then
    ROADMAP_FILE="$PLANNING_DIR/ROADMAP.md"
fi

if [ -z "$ROADMAP_FILE" ]; then
    printf '(no .planning/ROADMAP.md found)\n'
else
    # Find the first incomplete phase: look for lines with [ ] (unchecked checkbox)
    NEXT_PHASE="$(grep -m1 '\[ \]' "$ROADMAP_FILE" 2>/dev/null || true)"
    if [ -n "$NEXT_PHASE" ]; then
        printf '%s\n' "$NEXT_PHASE" | sed 's/^[[:space:]]*//'
    else
        # Fall back: show last phase line (all may be complete)
        LAST_PHASE="$(grep -E '^\|.*Phase' "$ROADMAP_FILE" 2>/dev/null | tail -1 || true)"
        if [ -n "$LAST_PHASE" ]; then
            printf '(all phases complete — last: %s)\n' "$LAST_PHASE"
        else
            printf '(no incomplete phases found in ROADMAP.md)\n'
        fi
    fi
fi
