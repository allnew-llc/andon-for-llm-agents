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
# collect-assessments.sh - Aggregate quality-self-assessment JSONs into central store
#
# Usage:
#   collect-assessments.sh [PROJECT_DIR ...] [--help]
#
# Environment variables:
#   CLAUDE_PLUGIN_DATA  MUST be set. Target store: ${CLAUDE_PLUGIN_DATA}/qc/
#
# Description:
#   Searches each PROJECT_DIR for docs/pipeline/quality-self-assessment-*.json
#   files and copies them to the central ${CLAUDE_PLUGIN_DATA}/qc/ store.
#   Skips files that are already up-to-date (same or newer version in store).
#   If no PROJECT_DIR arguments are provided, scans the current directory.
#   Requires CLAUDE_PLUGIN_DATA to be set (exits 1 if not).

set -euo pipefail

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
usage() {
    cat <<'EOF'
Usage: collect-assessments.sh [PROJECT_DIR ...] [--help]

Aggregate quality-self-assessment JSON files from project directories into the
central ${CLAUDE_PLUGIN_DATA}/qc/ store.

Arguments:
  PROJECT_DIR ...  One or more project root directories to scan.
                   If omitted, scans the current working directory.

Environment variables:
  CLAUDE_PLUGIN_DATA  REQUIRED. Target central store: ${CLAUDE_PLUGIN_DATA}/qc/
                      This script WRITES to the central store and requires
                      CLAUDE_PLUGIN_DATA to be set explicitly.

Behavior:
  - Scans each PROJECT_DIR for docs/pipeline/quality-self-assessment-*.json
  - Copies each file to ${CLAUDE_PLUGIN_DATA}/qc/ preserving the filename
  - Skips files that are already up-to-date (source is not newer than destination)
  - Reports [collected] or [skipped] per file, summary at the end

Exit codes:
  0  Success
  1  CLAUDE_PLUGIN_DATA is not set
EOF
}

# Handle --help before checking env vars
for arg in "$@"; do
    if [ "$arg" = "--help" ] || [ "$arg" = "-h" ]; then
        usage
        exit 0
    fi
done

# ---------------------------------------------------------------------------
# Require CLAUDE_PLUGIN_DATA
# ---------------------------------------------------------------------------
if [ -z "${CLAUDE_PLUGIN_DATA:-}" ]; then
    echo "Error: CLAUDE_PLUGIN_DATA must be set for collection." >&2
    echo "This script aggregates project-local assessments into the central store." >&2
    echo "Example: export CLAUDE_PLUGIN_DATA=~/.claude/skill-data" >&2
    exit 1
fi

TARGET_DIR="${CLAUDE_PLUGIN_DATA}/qc"

# ---------------------------------------------------------------------------
# Resolve project directories
# ---------------------------------------------------------------------------
if [ "$#" -eq 0 ]; then
    project_dirs="$(pwd)"
else
    project_dirs=""
    for d in "$@"; do
        project_dirs="${project_dirs}${d}"$'\n'
    done
fi

# ---------------------------------------------------------------------------
# Ensure target store exists
# ---------------------------------------------------------------------------
mkdir -p "${TARGET_DIR}"

# ---------------------------------------------------------------------------
# File mtime helper: returns epoch seconds
# Tries macOS stat -f '%m' first, then GNU stat --format='%Y'
# ---------------------------------------------------------------------------
file_mtime_epoch() {
    local f="$1"
    stat -f '%m' "$f" 2>/dev/null \
        || stat --format='%Y' "$f" 2>/dev/null \
        || echo "0"
}

# ---------------------------------------------------------------------------
# Main collection loop
# ---------------------------------------------------------------------------
echo ""
echo "=== Collecting Quality Assessments ==="
echo "Target store: ${TARGET_DIR}"

total_collected=0
total_skipped=0
project_count=0

while IFS= read -r proj_dir; do
    [ -z "$proj_dir" ] && continue

    echo ""
    echo "Scanning: ${proj_dir}"

    # Check project directory exists
    if [ ! -d "$proj_dir" ]; then
        echo "  [warn] Directory not found: ${proj_dir} — skipping"
        continue
    fi

    project_count=$((project_count + 1))
    proj_collected=0
    proj_skipped=0
    pipeline_dir="${proj_dir}/docs/pipeline"

    # Find assessment files in this project
    if [ ! -d "${pipeline_dir}" ]; then
        echo "  (0 assessments found — no docs/pipeline/ directory)"
        continue
    fi

    found_any=0
    while IFS= read -r src_file; do
        [ -z "$src_file" ] && continue
        found_any=1

        filename="$(basename "$src_file")"
        dest_file="${TARGET_DIR}/${filename}"

        # Check if destination exists and is up-to-date
        if [ -f "$dest_file" ]; then
            src_epoch="$(file_mtime_epoch "$src_file")"
            dest_epoch="$(file_mtime_epoch "$dest_file")"

            if [ "$src_epoch" -le "$dest_epoch" ]; then
                # Source is not newer than destination — skip
                printf '  [skipped]   %s (already up-to-date)\n' \
                    "$(echo "$src_file" | sed "s|${proj_dir}/||")"
                proj_skipped=$((proj_skipped + 1))
                total_skipped=$((total_skipped + 1))
                continue
            fi
        fi

        # Copy file to central store
        cp "$src_file" "$dest_file"
        printf '  [collected] %s\n' \
            "$(echo "$src_file" | sed "s|${proj_dir}/||")"
        proj_collected=$((proj_collected + 1))
        total_collected=$((total_collected + 1))

    done < <(find "${pipeline_dir}" -maxdepth 1 \
                  -name 'quality-self-assessment-*.json' -type f | sort)

    if [ "$found_any" -eq 0 ]; then
        echo "  (0 assessments found)"
    fi

done <<< "$project_dirs"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
if [ "$project_count" -eq 0 ]; then
    echo "Summary: No valid project directories scanned"
else
    echo "Summary: Collected ${total_collected} assessments from ${project_count} project(s), skipped ${total_skipped}"
fi
echo "=== Done ==="
