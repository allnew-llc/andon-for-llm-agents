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
# quality-trend.sh - Quality self-assessment trend timeline
#
# Usage:
#   quality-trend.sh [--help]
#
# Environment variables:
#   CLAUDE_PLUGIN_DATA  If set, scans ${CLAUDE_PLUGIN_DATA}/qc/ for
#                       quality-self-assessment-*.json files.
#   (If CLAUDE_PLUGIN_DATA is not set, falls back to searching
#    docs/pipeline/quality-self-assessment-*.json in the current
#    working directory.)
#
# Description:
#   Reads quality self-assessment JSON files, extracts phase, timestamp,
#   overall status, and criterion counts, and prints a time-series table
#   with a trend summary (improving / stable / degrading).

set -euo pipefail

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
usage() {
    cat <<'EOF'
Usage: quality-trend.sh [--help]

Display a time-series trend report of quality self-assessments.

Environment variables:
  CLAUDE_PLUGIN_DATA   Scan ${CLAUDE_PLUGIN_DATA}/qc/ for assessment files.
                       If not set, falls back to docs/pipeline/ in the
                       current working directory.

Output:
  Prints a table of assessments sorted by date and a trend summary.
  Informational messages are printed to stderr.

Exit codes:
  0  Success (including the case where no data is found)
  1  Unexpected error
EOF
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    usage
    exit 0
fi

# ---------------------------------------------------------------------------
# Resolve data directory / file pattern
# ---------------------------------------------------------------------------
if [ -n "${CLAUDE_PLUGIN_DATA:-}" ]; then
    SEARCH_DIR="${CLAUDE_PLUGIN_DATA}/qc"
    echo "Data source: ${SEARCH_DIR}" >&2
    PATTERN="${SEARCH_DIR}/quality-self-assessment-*.json"
else
    SEARCH_DIR="$(pwd)/docs/pipeline"
    echo "Data source: ${SEARCH_DIR} (fallback; set CLAUDE_PLUGIN_DATA for central store)" >&2
    PATTERN="${SEARCH_DIR}/quality-self-assessment-*.json"
fi

# ---------------------------------------------------------------------------
# Collect assessment files
# ---------------------------------------------------------------------------
# Use find for safety (glob may not expand if dir missing)
if [ ! -d "${SEARCH_DIR}" ]; then
    echo "No quality assessment data found"
    exit 0
fi

assessment_files=""
file_count=0
while IFS= read -r f; do
    if [ -n "$f" ]; then
        assessment_files="${assessment_files}${f}"$'\n'
        file_count=$((file_count + 1))
    fi
done < <(find "${SEARCH_DIR}" -maxdepth 1 -name 'quality-self-assessment-*.json' -type f | sort)

if [ "$file_count" -eq 0 ]; then
    echo "No quality assessment data found"
    exit 0
fi

# ---------------------------------------------------------------------------
# Extract a string value for a simple flat JSON key (awk, no jq)
# Usage: extract_json_str <key> <file>
# ---------------------------------------------------------------------------
extract_json_str() {
    local key="$1"
    local file="$2"
    awk -v key="$key" '
    {
        pattern = "\"" key "\"[[:space:]]*:[[:space:]]*\"([^\"]*)\""
        if (match($0, pattern)) {
            s = substr($0, RSTART, RLENGTH)
            sub("^\"" key "\"[[:space:]]*:[[:space:]]*\"", "", s)
            sub("\"$", "", s)
            print s
            exit
        }
    }
    ' "$file"
}

# ---------------------------------------------------------------------------
# Count occurrences of a quoted string value in criteria array
# Counts all "status":"<val>" patterns within the file (global count).
# Usage: count_status <value> <file>
# Returns 0 if no matches. Uses gsub for global matching on compact JSON.
# ---------------------------------------------------------------------------
count_status() {
    local val="$1"
    local file="$2"
    # gsub replaces ALL occurrences and returns the count — works on
    # compact single-line JSON where multiple keys appear on one line.
    awk -v val="$val" '{
        n += gsub("\"status\"[[:space:]]*:[[:space:]]*\"" val "\"", "")
    } END { print n+0 }' "$file"
}

# ---------------------------------------------------------------------------
# Status to numeric rank for trend comparison (higher = better)
# ---------------------------------------------------------------------------
status_rank() {
    case "$1" in
        pass|PASS) echo "3" ;;
        warn|WARN) echo "2" ;;
        fail|FAIL) echo "1" ;;
        *)         echo "0" ;;
    esac
}

# ---------------------------------------------------------------------------
# Collect data rows: "timestamp|phase_id|overall|pass_count|warn_count|fail_count"
# ---------------------------------------------------------------------------
tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

rows_file="${tmp_dir}/rows.txt"
touch "$rows_file"

while IFS= read -r f; do
    [ -z "$f" ] && continue

    phase_id="$(extract_json_str "phase_id" "$f")"
    timestamp="$(extract_json_str "timestamp" "$f")"
    overall="$(extract_json_str "overall" "$f")"

    pass_count="$(count_status "pass" "$f")"
    warn_count="$(count_status "warn" "$f")"
    fail_count="$(count_status "fail" "$f")"

    # Derive date from timestamp or file mtime
    if [ -n "$timestamp" ]; then
        date_str="$(echo "$timestamp" | sed 's/T.*//' | sed 's/ .*//')"
    else
        # Try macOS stat first, then GNU stat, then fall back to "unknown"
        date_str="$(stat -f "%Sm" -t "%Y-%m-%d" "$f" 2>/dev/null \
                    || stat --format="%y" "$f" 2>/dev/null | sed 's/ .*//' \
                    || echo "unknown")"
    fi

    [ -z "$phase_id" ] && phase_id="$(basename "$f" .json | sed 's/quality-self-assessment-//')"
    [ -z "$overall" ] && overall="unknown"

    printf '%s|%s|%s|%s|%s|%s\n' \
        "$date_str" "$phase_id" "$(echo "$overall" | tr '[:lower:]' '[:upper:]')" \
        "$pass_count" "$warn_count" "$fail_count" \
        >> "$rows_file"

done <<< "$assessment_files"

# Sort rows by date (first field)
sorted_file="${tmp_dir}/sorted.txt"
sort "$rows_file" > "$sorted_file"

total_rows="$(wc -l < "$sorted_file" | tr -d ' ')"

# Status summary counts
total_pass=0
total_warn=0
total_fail=0

# ---------------------------------------------------------------------------
# Print report header
# ---------------------------------------------------------------------------
echo ""
echo "=== Quality Trend Report ==="
echo "Data source: ${SEARCH_DIR}"
echo "Assessments found: ${file_count}"
echo ""

# Table header
printf '%-10s | %-15s | %-7s | %4s | %4s | %4s\n' \
    "Date" "Phase" "Overall" "Pass" "Warn" "Fail"
printf '%s\n' "$(printf '%-10s-+-%-15s-+-%-7s-+-%4s-+-%4s-+-%4s' \
    "----------" "---------------" "-------" "----" "----" "----" \
    | sed 's/ /-/g')"

while IFS='|' read -r date_str phase_id overall pass_c warn_c fail_c; do
    [ -z "$date_str" ] && continue
    printf '%-10s | %-15s | %-7s | %4s | %4s | %4s\n' \
        "$date_str" "$phase_id" "$overall" "$pass_c" "$warn_c" "$fail_c"
    total_pass=$((total_pass + pass_c))
    total_warn=$((total_warn + warn_c))
    total_fail=$((total_fail + fail_c))
done < "$sorted_file"

echo ""

# Overall summary line
echo "Summary: ${total_pass} PASS, ${total_warn} WARN, ${total_fail} FAIL across ${file_count} assessments"

# ---------------------------------------------------------------------------
# Trend detection: compare last 3 assessments (earliest vs latest overall)
# ---------------------------------------------------------------------------
trend="stable"
if [ "$total_rows" -ge 2 ]; then
    # Get up to last 3 rows
    last3="$(tail -3 "$sorted_file")"
    earliest_overall="$(echo "$last3" | head -1 | awk -F'|' '{print $3}')"
    latest_overall="$(echo "$last3" | tail -1 | awk -F'|' '{print $3}')"

    earliest_rank="$(status_rank "$earliest_overall")"
    latest_rank="$(status_rank "$latest_overall")"

    if [ "$latest_rank" -gt "$earliest_rank" ]; then
        trend="improving"
    elif [ "$latest_rank" -lt "$earliest_rank" ]; then
        trend="degrading"
    else
        trend="stable"
    fi
fi

echo "Trend: ${trend} (based on last 3 assessments)"
echo ""
echo "=== End of Report ==="
