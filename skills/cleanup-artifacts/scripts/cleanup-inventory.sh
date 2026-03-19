#!/bin/bash
# cleanup-inventory.sh — Scan common artifact locations and report sizes
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
# Usage: cleanup-inventory.sh [--help] [BASE_DIR]
#
# Scans common artifact locations relative to BASE_DIR (default: current directory)
# and the user's home directory. Reports sizes in a tab-separated format.
#
# Output format:
#   Location  Type  Size  Last_Modified
#
# Exit codes:
#   0  Always exits 0 — missing directories are skipped gracefully

set -euo pipefail

# --- Help ---

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<'EOF'
cleanup-inventory.sh — Scan artifact locations and report sizes

Usage: cleanup-inventory.sh [BASE_DIR]

  BASE_DIR   Base project directory (default: current working directory)

Output:
  Tab-separated inventory of found artifact locations with size and type.
  Missing directories are skipped silently.

Environment:
  CLAUDE_PLUGIN_DATA   If set, includes plugin data directory in inventory.
EOF
  exit 0
fi

BASE_DIR="${1:-$(pwd)}"
BASE_DIR="${BASE_DIR%/}"

# --- Utility functions ---

# Get directory size using du -sh (macOS compatible)
get_size() {
  local dir="$1"
  du -sh "$dir" 2>/dev/null | awk '{print $1}' || echo "?"
}

# Get last modified date using stat (macOS: stat -f '%Sm' -t '%Y-%m-%d')
get_mtime() {
  local dir="$1"
  stat -f '%Sm' -t '%Y-%m-%d' "$dir" 2>/dev/null || echo "unknown"
}

# Count items in directory
count_items() {
  local dir="$1"
  find "$dir" -maxdepth 1 -mindepth 1 2>/dev/null | wc -l | tr -d ' '
}

# Print one inventory row
print_row() {
  local path="$1"
  local type="$2"
  local size="$3"
  local mtime="$4"
  local count="$5"
  printf "%-55s  %-18s  %-8s  %-12s  %s items\n" "$path" "$type" "$size" "$mtime" "$count"
}

# --- Main scan ---

FOUND=0
TOTAL_BYTES=0

echo "=== ARTIFACT INVENTORY ==="
printf "%-55s  %-18s  %-8s  %-12s  %s\n" "Location" "Type" "Size" "Last_Modified" "Items"
printf -- "%.0s-" {1..110}; echo

# 1. Xcode DerivedData
DERIVED_DATA="$HOME/Library/Developer/Xcode/DerivedData"
if [ -d "$DERIVED_DATA" ]; then
  SIZE=$(get_size "$DERIVED_DATA")
  MTIME=$(get_mtime "$DERIVED_DATA")
  COUNT=$(count_items "$DERIVED_DATA")
  print_row "$DERIVED_DATA" "build-cache" "$SIZE" "$MTIME" "$COUNT"
  FOUND=$((FOUND + 1))
else
  echo "# SKIP: $DERIVED_DATA (not found)" >&2
fi

# 2. ios-app-factory/output/
OUTPUT_DIR="$BASE_DIR/ios-app-factory/output"
if [ -d "$OUTPUT_DIR" ]; then
  SIZE=$(get_size "$OUTPUT_DIR")
  MTIME=$(get_mtime "$OUTPUT_DIR")
  COUNT=$(count_items "$OUTPUT_DIR")
  print_row "$OUTPUT_DIR" "pipeline-output" "$SIZE" "$MTIME" "$COUNT"
  FOUND=$((FOUND + 1))
else
  echo "# SKIP: $OUTPUT_DIR (not found)" >&2
fi

# 3. .planning/phases/ — only completed phases (has SUMMARY.md)
PHASES_DIR="$BASE_DIR/.planning/phases"
if [ -d "$PHASES_DIR" ]; then
  COMPLETED_PHASES=0
  for phase_dir in "$PHASES_DIR"/*/; do
    if [ -d "$phase_dir" ] && ls "$phase_dir"*SUMMARY.md 2>/dev/null | grep -q .; then
      SIZE=$(get_size "$phase_dir")
      MTIME=$(get_mtime "$phase_dir")
      COUNT=$(count_items "$phase_dir")
      phase_name=$(basename "$phase_dir")
      print_row ".planning/phases/$phase_name" "planning-artifact" "$SIZE" "$MTIME" "$COUNT"
      COMPLETED_PHASES=$((COMPLETED_PHASES + 1))
      FOUND=$((FOUND + 1))
    fi
  done
  if [ "$COMPLETED_PHASES" -eq 0 ]; then
    echo "# SKIP: $PHASES_DIR (no completed phases found)" >&2
  fi
fi

# 4. node_modules directories (scan up to 3 levels deep)
while IFS= read -r -d '' nm_dir; do
  SIZE=$(get_size "$nm_dir")
  MTIME=$(get_mtime "$nm_dir")
  COUNT=$(count_items "$nm_dir")
  print_row "$nm_dir" "dependency" "$SIZE" "$MTIME" "$COUNT"
  FOUND=$((FOUND + 1))
done < <(find "$BASE_DIR" -maxdepth 3 -name "node_modules" -type d -print0 2>/dev/null)

# 5. build/ and dist/ directories (scan up to 3 levels deep)
while IFS= read -r -d '' build_dir; do
  SIZE=$(get_size "$build_dir")
  MTIME=$(get_mtime "$build_dir")
  COUNT=$(count_items "$build_dir")
  DIR_TYPE=$(basename "$build_dir")
  print_row "$build_dir" "build-output ($DIR_TYPE)" "$SIZE" "$MTIME" "$COUNT"
  FOUND=$((FOUND + 1))
done < <(find "$BASE_DIR" -maxdepth 3 \( -name "build" -o -name "dist" \) -type d -print0 2>/dev/null)

# 6. .next/ directories (Next.js cache)
while IFS= read -r -d '' next_dir; do
  SIZE=$(get_size "$next_dir")
  MTIME=$(get_mtime "$next_dir")
  COUNT=$(count_items "$next_dir")
  print_row "$next_dir" "build-cache (.next)" "$SIZE" "$MTIME" "$COUNT"
  FOUND=$((FOUND + 1))
done < <(find "$BASE_DIR" -maxdepth 3 -name ".next" -type d -print0 2>/dev/null)

# 7. /tmp/claude-* files
CLAUDE_TMP=$(find /tmp -maxdepth 1 -name "claude-*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$CLAUDE_TMP" -gt 0 ]; then
  # Treat all claude-* tmp entries as one group
  TOTAL_TMP_SIZE=$(du -sh /tmp/claude-* 2>/dev/null | awk '{sum+=$1} END{print sum"K"}' || echo "?")
  # Get most recent mtime
  LAST_TMP=$(find /tmp -maxdepth 1 -name "claude-*" 2>/dev/null | xargs stat -f '%Sm' -t '%Y-%m-%d' 2>/dev/null | sort -r | head -1 || echo "unknown")
  print_row "/tmp/claude-*" "temp" "$TOTAL_TMP_SIZE" "$LAST_TMP" "$CLAUDE_TMP"
  FOUND=$((FOUND + 1))
fi

# 8. CLAUDE_PLUGIN_DATA (inventory only — never auto-clean)
if [ -n "${CLAUDE_PLUGIN_DATA:-}" ] && [ -d "$CLAUDE_PLUGIN_DATA" ]; then
  SIZE=$(get_size "$CLAUDE_PLUGIN_DATA")
  MTIME=$(get_mtime "$CLAUDE_PLUGIN_DATA")
  COUNT=$(count_items "$CLAUDE_PLUGIN_DATA")
  print_row "$CLAUDE_PLUGIN_DATA" "plugin-data [KEEP]" "$SIZE" "$MTIME" "$COUNT"
  FOUND=$((FOUND + 1))
fi

# --- Summary ---
printf -- "%.0s-" {1..110}; echo
echo "=== TOTAL: $FOUND locations scanned ==="
echo ""
echo "Run /cleanup-artifacts clean to proceed with selective cleanup."
echo "Run /cleanup-artifacts clean --dry-run to preview deletions."
