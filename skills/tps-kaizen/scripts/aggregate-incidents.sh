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
# aggregate-incidents.sh - Aggregate and cluster past incidents by pattern
#
# Usage:
#   aggregate-incidents.sh [--help]
#
# Environment variables:
#   CLAUDE_PLUGIN_DATA  If set, uses ${CLAUDE_PLUGIN_DATA}/kaizen/incidents/
#                       as the data directory.
#   ANDON_STATE_DIR     If CLAUDE_PLUGIN_DATA is not set, uses
#                       ${ANDON_STATE_DIR}/kaizen/incidents/ (default:
#                       ~/.claude/state/kaizen/incidents/).
#
# Description:
#   Reads incident analysis.json files from the incidents directory,
#   groups them by cause_id, and prints a summary of recurring patterns
#   and single occurrences.

set -euo pipefail

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
usage() {
    cat <<'EOF'
Usage: aggregate-incidents.sh [--help]

Aggregate and cluster past incidents by pattern.

Environment variables:
  CLAUDE_PLUGIN_DATA   Use ${CLAUDE_PLUGIN_DATA}/kaizen/incidents/ as data dir.
  ANDON_STATE_DIR      Fallback state root (default: ~/.claude/state).
                       Data dir: ${ANDON_STATE_DIR}/kaizen/incidents/

Output:
  Prints a grouped summary of past incidents with pattern counts to stdout.
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
# Resolve data directory
# ---------------------------------------------------------------------------
if [ -n "${CLAUDE_PLUGIN_DATA:-}" ]; then
    INCIDENTS_DIR="${CLAUDE_PLUGIN_DATA}/kaizen/incidents"
else
    STATE_DIR="${ANDON_STATE_DIR:-${HOME}/.claude/state}"
    INCIDENTS_DIR="${STATE_DIR}/kaizen/incidents"
fi

echo "Data source: ${INCIDENTS_DIR}" >&2

# ---------------------------------------------------------------------------
# Handle missing / empty directory
# ---------------------------------------------------------------------------
if [ ! -d "${INCIDENTS_DIR}" ]; then
    echo "No incident data found in ${INCIDENTS_DIR}"
    exit 0
fi

# Collect incident directories (INC-* pattern)
incident_dirs=""
incident_count=0
while IFS= read -r d; do
    if [ -n "$d" ]; then
        incident_dirs="${incident_dirs}${d}"$'\n'
        incident_count=$((incident_count + 1))
    fi
done < <(find "${INCIDENTS_DIR}" -maxdepth 1 -mindepth 1 -type d -name 'INC-*' | sort)

if [ "$incident_count" -eq 0 ]; then
    echo "No incident data found in ${INCIDENTS_DIR}"
    exit 0
fi

# ---------------------------------------------------------------------------
# Extract a value for a simple flat JSON key (awk, no jq)
# Handles compact single-line JSON and multiline JSON.
# Usage: extract_json_value <key> <file>
# Returns the unquoted string value or empty string if not found.
# ---------------------------------------------------------------------------
extract_json_value() {
    local key="$1"
    local file="$2"
    if [ ! -f "$file" ]; then
        printf ''
        return
    fi
    # Use awk to find "key":"value" or "key": "value" patterns.
    # Works on compact single-line JSON: matches the key, captures the
    # string value that follows, and stops at the closing quote.
    awk -v key="$key" '
    {
        # Look for the key followed by optional whitespace, colon,
        # optional whitespace, and a quoted string value.
        pattern = "\"" key "\"[[:space:]]*:[[:space:]]*\"([^\"]*)\""
        if (match($0, pattern)) {
            # Extract the captured group manually (awk does not support
            # capture groups portably, so we trim the prefix/suffix).
            s = substr($0, RSTART, RLENGTH)
            # Remove leading: "key": "
            sub("^\"" key "\"[[:space:]]*:[[:space:]]*\"", "", s)
            # Remove trailing quote
            sub("\"$", "", s)
            print s
            exit
        }
    }
    ' "$file"
}

# ---------------------------------------------------------------------------
# Collect data from each incident
# ---------------------------------------------------------------------------
# We build two flat files in /tmp for aggregation:
#   cause_data: cause_id TAB date TAB category TAB summary
tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

cause_data="${tmp_dir}/cause_data.txt"
touch "$cause_data"

min_date=""
max_date=""

while IFS= read -r inc_dir; do
    [ -z "$inc_dir" ] && continue

    analysis_file="${inc_dir}/analysis.json"
    evidence_file="${inc_dir}/evidence.json"

    cause_id="$(extract_json_value "cause_id" "$analysis_file")"
    category="$(extract_json_value "category" "$analysis_file")"
    root_cause="$(extract_json_value "root_cause_summary" "$analysis_file")"
    opened_at="$(extract_json_value "opened_at" "$evidence_file")"

    # Derive date from opened_at or fall back to directory name
    if [ -n "$opened_at" ]; then
        date_str="$(echo "$opened_at" | sed 's/T.*//' | sed 's/ .*//')"
    else
        # INC-YYYYMMDD-HHMMSS-hash → extract date portion
        dir_name="$(basename "$inc_dir")"
        raw_date="$(echo "$dir_name" | sed 's/INC-\([0-9]\{8\}\)-.*/\1/')"
        if echo "$raw_date" | grep -qE '^[0-9]{8}$'; then
            date_str="$(echo "$raw_date" | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3/')"
        else
            date_str="unknown"
        fi
    fi

    [ -z "$cause_id" ] && cause_id="unknown"
    [ -z "$category" ] && category="unknown"
    [ -z "$root_cause" ] && root_cause="(no summary)"

    # Track date range
    if [ "$date_str" != "unknown" ]; then
        if [ -z "$min_date" ] || [ "$date_str" \< "$min_date" ]; then
            min_date="$date_str"
        fi
        if [ -z "$max_date" ] || [ "$date_str" \> "$max_date" ]; then
            max_date="$date_str"
        fi
    fi

    # Escape TAB in values just in case; use pipe as delimiter
    printf '%s|%s|%s|%s\n' "$cause_id" "$date_str" "$category" "$root_cause" \
        >> "$cause_data"

done <<< "$incident_dirs"

# ---------------------------------------------------------------------------
# Aggregate by cause_id
# ---------------------------------------------------------------------------
# Get unique cause_ids
unique_causes="${tmp_dir}/unique_causes.txt"
awk -F'|' '{print $1}' "$cause_data" | sort -u > "$unique_causes"

unique_count="$(wc -l < "$unique_causes" | tr -d ' ')"
period="${min_date:-?} to ${max_date:-?}"

# ---------------------------------------------------------------------------
# Print report
# ---------------------------------------------------------------------------
echo ""
echo "=== Incident Pattern Summary ==="
echo "Data source: ${INCIDENTS_DIR}"
echo "Total incidents: ${incident_count}"
echo "Unique patterns: ${unique_count}"
echo "Period: ${period}"

# Separate recurring vs single
recurring_output="${tmp_dir}/recurring.txt"
single_output="${tmp_dir}/single.txt"
touch "$recurring_output" "$single_output"

while IFS= read -r cid; do
    [ -z "$cid" ] && continue

    # All rows for this cause_id
    rows="$(grep -F "${cid}|" "$cause_data" || true)"
    count="$(echo "$rows" | grep -c '.' || true)"

    # Most recent date
    last_date="$(echo "$rows" | awk -F'|' '{print $2}' | sort -r | head -1)"
    # Category (first occurrence)
    cat_val="$(echo "$rows" | awk -F'|' 'NR==1{print $3}')"
    # Root cause (most recent)
    summary="$(echo "$rows" | awk -F'|' '{print $2"|"$4}' | sort -r | head -1 | awk -F'|' '{print $2}')"

    if [ "$count" -ge 2 ]; then
        {
            printf '\n  [%s] (%d occurrences)\n' "$cid" "$count"
            printf '  Category: %s\n' "$cat_val"
            printf '  Last seen: %s\n' "$last_date"
            printf '  Root cause: %s\n' "$summary"
        } >> "$recurring_output"
    else
        date_val="$(echo "$rows" | awk -F'|' 'NR==1{print $2}')"
        {
            printf '\n  [%s]\n' "$cid"
            printf '  Category: %s\n' "$cat_val"
            printf '  Date: %s\n' "$date_val"
            printf '  Root cause: %s\n' "$summary"
        } >> "$single_output"
    fi

done < "$unique_causes"

echo ""
echo "--- Recurring Patterns (2+ occurrences) ---"
if [ -s "$recurring_output" ]; then
    cat "$recurring_output"
else
    echo ""
    echo "  (none)"
fi

echo ""
echo "--- Single Occurrences ---"
if [ -s "$single_output" ]; then
    cat "$single_output"
else
    echo ""
    echo "  (none)"
fi

echo ""
echo "=== End of Summary ==="
