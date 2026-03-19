#!/usr/bin/env bash
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
# gotcha-stats.sh - Report Gotcha hit rates, stale detection, and prevention effectiveness
#
# Usage:
#   gotcha-stats.sh [--help]
#
# Environment variables:
#   CLAUDE_PLUGIN_DATA  If set, uses ${CLAUDE_PLUGIN_DATA}/kaizen/incidents/
#                       as the incidents data directory.
#   ANDON_STATE_DIR     If CLAUDE_PLUGIN_DATA is not set, uses
#                       ${ANDON_STATE_DIR}/kaizen/incidents/ (default:
#                       ~/.claude/state/kaizen/incidents/).
#   GOTCHA_DIR          Path to the Gotcha YAML registry directory.
#                       Default: repo root /gotchas/ detected via git, or
#                       script-relative ../../../../gotchas/
#
# Description:
#   Reads Gotcha YAML files from GOTCHA_DIR and incident data from the
#   incidents directory. For each Gotcha, counts how many incidents matched
#   its pattern (using the same 40%+ keyword threshold as gotcha_surfacer.py).
#   Flags Gotchas with zero hits as potentially stale. Computes average
#   resolution time for incidents with vs. without Gotcha matches to produce
#   a prevention effectiveness heuristic.
#
# Output:
#   Prints a structured report to stdout. Informational messages go to stderr.
#
# Exit codes:
#   0  Success (including when no data is found)
#   1  Unexpected error

set -euo pipefail

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
usage() {
    cat <<'EOF'
Usage: gotcha-stats.sh [--help]

Report Gotcha hit rates, stale detection, and prevention effectiveness.

Environment variables:
  CLAUDE_PLUGIN_DATA   Use ${CLAUDE_PLUGIN_DATA}/kaizen/incidents/ as incidents dir.
  ANDON_STATE_DIR      Fallback state root (default: ~/.claude/state).
                       Incidents dir: ${ANDON_STATE_DIR}/kaizen/incidents/
  GOTCHA_DIR           Path to Gotcha YAML registry directory.
                       Default: auto-detected via git rev-parse or script-relative path.

Output:
  === Gotcha Effectiveness Report ===
  Hit Rate Table: per-Gotcha match counts across all incidents
  Stale Gotchas: those with zero hits (potentially outdated)
  Prevention Effectiveness: avg resolution time with vs. without Gotcha match

  Note: Effectiveness comparison is heuristic (correlation, not causation).

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
# Resolve incidents directory
# ---------------------------------------------------------------------------
if [ -n "${CLAUDE_PLUGIN_DATA:-}" ]; then
    INCIDENTS_DIR="${CLAUDE_PLUGIN_DATA}/kaizen/incidents"
    HISTORY_DIR="${CLAUDE_PLUGIN_DATA}/kaizen/history"
else
    STATE_DIR="${ANDON_STATE_DIR:-${HOME}/.claude/state}"
    INCIDENTS_DIR="${STATE_DIR}/kaizen/incidents"
    HISTORY_DIR="${STATE_DIR}/kaizen/history"
fi

# ---------------------------------------------------------------------------
# Resolve Gotcha registry directory
# ---------------------------------------------------------------------------
if [ -n "${GOTCHA_DIR:-}" ]; then
    GOTCHAS_DIR="${GOTCHA_DIR}"
else
    # Try git repo root first
    repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
    if [ -n "$repo_root" ] && [ -d "${repo_root}/gotchas" ]; then
        GOTCHAS_DIR="${repo_root}/gotchas"
    else
        # Fallback: script-relative path (skills/tps-kaizen/scripts/ -> ../../../../gotchas)
        script_dir="$(cd "$(dirname "$0")" && pwd)"
        GOTCHAS_DIR="${script_dir}/../../../../gotchas"
    fi
fi

echo "Incidents source: ${INCIDENTS_DIR}" >&2
echo "Gotcha registry:  ${GOTCHAS_DIR}" >&2

# ---------------------------------------------------------------------------
# Check Gotcha registry
# ---------------------------------------------------------------------------
if [ ! -d "${GOTCHAS_DIR}" ]; then
    echo "No Gotcha registry found at ${GOTCHAS_DIR}"
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
# Extract a YAML scalar value for a given key.
# Handles:
#   key: "value"    (quoted)
#   key: value      (unquoted)
#   key: >          (block scalar — reads continuation lines until next key)
# Usage: extract_yaml_value <key> <file>
# For block scalars, joins continuation lines with a space.
# ---------------------------------------------------------------------------
extract_yaml_value() {
    local key="$1"
    local file="$2"
    if [ ! -f "$file" ]; then
        printf ''
        return
    fi
    awk -v key="$key" '
    BEGIN { found=0; block=0; val="" }
    {
        # Match "key: >" (block scalar indicator)
        if (!found && $0 ~ "^" key ":[ \t]*>[ \t]*$") {
            found=1; block=1; next
        }
        # Match "key: value" or "key: \"value\""
        if (!found && $0 ~ "^" key ":[ \t]") {
            found=1; block=0
            # Extract value part after "key: "
            sub("^" key ":[ \t]*", "")
            # Strip surrounding quotes if present
            gsub(/^"/, ""); gsub(/"$/, "")
            val=$0
            next
        }
        # If in block scalar mode, accumulate indented continuation lines
        if (found && block) {
            # A non-indented line that is not blank means end of block
            if ($0 ~ /^[^ \t]/ && $0 !~ /^$/) {
                found=0; block=0
                exit
            }
            # Skip blank lines
            if ($0 ~ /^[ \t]*$/) { next }
            # Trim leading whitespace and append
            line=$0
            sub(/^[ \t]+/, "", line)
            if (val == "") { val=line } else { val=val " " line }
            next
        }
        # If non-block, we already captured val in the match line; stop
        if (found && !block) { exit }
    }
    END { print val }
    ' "$file"
}

# ---------------------------------------------------------------------------
# Stopwords (mirrors gotcha_surfacer.py _STOPWORDS + common extras)
# ---------------------------------------------------------------------------
# We store as a single string with spaces for awk matching.
STOPWORDS=" a an and are as at be been but by do does for from had has have he her him his how if in into is it its no not of on or our out per so some than that the their them then there they this those to too up us was we were what when where which who will with you your "

# ---------------------------------------------------------------------------
# Convert ISO8601 timestamp to epoch seconds (cross-platform: BSD & GNU date)
# Strips trailing Z or timezone offset.
# Usage: iso_to_epoch <timestamp_string>
# Returns empty string on failure.
# ---------------------------------------------------------------------------
iso_to_epoch() {
    local ts="$1"
    if [ -z "$ts" ]; then
        printf ''
        return
    fi
    # Strip trailing Z or +HH:MM / -HH:MM
    local clean_ts
    clean_ts="$(echo "$ts" | sed 's/Z$//' | sed 's/[+-][0-9][0-9]:[0-9][0-9]$//')"

    local epoch
    # Try GNU date first
    epoch="$(date -d "${clean_ts}" '+%s' 2>/dev/null || true)"
    if [ -z "$epoch" ]; then
        # Try BSD date (macOS)
        epoch="$(date -j -f '%Y-%m-%dT%H:%M:%S' "${clean_ts}" '+%s' 2>/dev/null || true)"
    fi
    printf '%s' "$epoch"
}

# ---------------------------------------------------------------------------
# Extract significant keywords from pattern text (mirrors Python surfacer logic)
# Words >= 3 chars, not in stopwords list, lowercased alphanumeric/underscore/hyphen
# Usage: significant_words <text>
# Prints one word per line.
# ---------------------------------------------------------------------------
significant_words() {
    local text="$1"
    # Lowercase, extract word tokens (alphanum, underscore, hyphen)
    echo "$text" | tr '[:upper:]' '[:lower:]' | \
    awk -v stopwords="${STOPWORDS}" '
    {
        n = split($0, words, /[^a-z0-9_-]+/)
        for (i=1; i<=n; i++) {
            w = words[i]
            if (length(w) < 3) continue
            # Check if stopword
            if (index(stopwords, " " w " ") > 0) continue
            print w
        }
    }
    '
}

# ---------------------------------------------------------------------------
# Check if incident output_snippet matches a Gotcha pattern
# Uses 40%+ keyword threshold (PARTIAL match, same as surfacer)
# Also checks EXACT match (full pattern as substring of snippet)
# Usage: incident_matches_gotcha <snippet_lower> <pattern_text>
# Returns: "exact", "partial", or ""
# ---------------------------------------------------------------------------
incident_matches_gotcha() {
    local snippet_lower="$1"
    local pattern="$2"

    # EXACT: full normalised pattern appears as substring of snippet
    local pattern_norm
    pattern_norm="$(echo "$pattern" | tr '[:upper:]' '[:lower:]' | tr -s ' \t\n' ' ' | sed 's/^ //;s/ $//')"
    local snippet_norm
    snippet_norm="$(echo "$snippet_lower" | tr -s ' \t\n' ' ' | sed 's/^ //;s/ $//')"
    if [ -n "$pattern_norm" ] && echo "$snippet_norm" | grep -qF "$pattern_norm" 2>/dev/null; then
        echo "exact"
        return
    fi

    # PARTIAL: 40%+ of significant pattern keywords appear in snippet
    local total=0 matched=0
    while IFS= read -r word; do
        [ -z "$word" ] && continue
        total=$((total + 1))
        if echo "$snippet_lower" | grep -qw "$word" 2>/dev/null; then
            matched=$((matched + 1))
        fi
    done < <(significant_words "$pattern")

    if [ "$total" -gt 0 ]; then
        # Check if matched/total >= 0.40 using integer arithmetic (multiply by 100)
        local ratio_pct=$(( matched * 100 / total ))
        if [ "$ratio_pct" -ge 40 ]; then
            echo "partial"
            return
        fi
    fi

    echo ""
}

# ---------------------------------------------------------------------------
# Load Gotcha registry into parallel arrays
# ---------------------------------------------------------------------------
tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

gotcha_count=0
gotcha_ids_file="${tmp_dir}/gotcha_ids.txt"
gotcha_names_file="${tmp_dir}/gotcha_names.txt"
gotcha_patterns_file="${tmp_dir}/gotcha_patterns.txt"  # one pattern per line (TAB-encoded newlines)
gotcha_discovered_file="${tmp_dir}/gotcha_discovered.txt"

touch "$gotcha_ids_file" "$gotcha_names_file" "$gotcha_patterns_file" "$gotcha_discovered_file"

while IFS= read -r yaml_file; do
    [ -z "$yaml_file" ] && continue
    gid="$(extract_yaml_value "id" "$yaml_file")"
    gname="$(extract_yaml_value "name" "$yaml_file")"
    gpattern="$(extract_yaml_value "pattern" "$yaml_file")"
    gdiscovered="$(extract_yaml_value "discovered" "$yaml_file")"

    if [ -z "$gid" ]; then
        echo "Warning: skipping ${yaml_file} — no id field" >&2
        continue
    fi

    gotcha_count=$((gotcha_count + 1))
    printf '%s\n' "$gid" >> "$gotcha_ids_file"
    printf '%s\n' "$gname" >> "$gotcha_names_file"
    # Store pattern with internal newlines replaced by spaces (already done by extract_yaml_value)
    printf '%s\n' "$gpattern" >> "$gotcha_patterns_file"
    printf '%s\n' "$gdiscovered" >> "$gotcha_discovered_file"

done < <(find "${GOTCHAS_DIR}" -maxdepth 1 -name '*.yaml' | sort)

if [ "$gotcha_count" -eq 0 ]; then
    echo "No Gotcha YAML files found in ${GOTCHAS_DIR}"
    exit 0
fi

# ---------------------------------------------------------------------------
# Check incidents directory
# ---------------------------------------------------------------------------
if [ ! -d "${INCIDENTS_DIR}" ]; then
    echo ""
    echo "=== Gotcha Effectiveness Report ==="
    echo "Data source: ${INCIDENTS_DIR}"
    echo "Registry: ${GOTCHAS_DIR}"
    echo "Total Gotchas: ${gotcha_count}"
    echo "Total incidents scanned: 0"
    echo ""
    echo "No incident data found in ${INCIDENTS_DIR}"
    echo ""
    # Print stale table — all Gotchas are stale with no incidents
    echo "--- Hit Rate Table ---"
    printf '%-14s | %-30s | %4s | %s\n' "ID" "Name" "Hits" "Effectiveness"
    idx=1
    while IFS= read -r gid; do
        gname="$(sed -n "${idx}p" "$gotcha_names_file")"
        printf '%-14s | %-30s | %4d | ** POTENTIALLY STALE **\n' "$gid" "$gname" 0
        idx=$((idx + 1))
    done < "$gotcha_ids_file"
    echo ""
    echo "--- Stale Gotchas (zero hits) ---"
    idx=1
    while IFS= read -r gid; do
        gname="$(sed -n "${idx}p" "$gotcha_names_file")"
        gdiscovered="$(sed -n "${idx}p" "$gotcha_discovered_file")"
        echo "${gid}: ${gname} (discovered: ${gdiscovered})"
        echo "  Consider: broadening pattern or archiving if no longer relevant"
        idx=$((idx + 1))
    done < "$gotcha_ids_file"
    echo ""
    echo "--- Prevention Effectiveness Summary ---"
    echo "Incidents with Gotcha match: 0 (avg resolution: N/A)"
    echo "Incidents without Gotcha match: 0 (avg resolution: N/A)"
    echo "Delta: no data"
    echo "Note: Correlation only. Gotcha surfacing may help but is not the sole factor."
    echo ""
    echo "=== End of Report ==="
    exit 0
fi

# Collect incident directories
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
# Load incident data: snippet, opened_at, closed_at (from history)
# ---------------------------------------------------------------------------
# Files to store per-incident data:
inc_snippets_file="${tmp_dir}/inc_snippets.txt"    # incident_id|snippet_lower
inc_opened_file="${tmp_dir}/inc_opened.txt"         # incident_id|epoch
inc_closed_file="${tmp_dir}/inc_closed.txt"         # incident_id|epoch
touch "$inc_snippets_file" "$inc_opened_file" "$inc_closed_file"

min_date=""
max_date=""

while IFS= read -r inc_dir; do
    [ -z "$inc_dir" ] && continue

    evidence_file="${inc_dir}/evidence.json"
    inc_id="$(basename "$inc_dir")"

    # Extract snippet and opened_at
    snippet="$(extract_json_value "output_snippet" "$evidence_file")"
    opened_at="$(extract_json_value "opened_at" "$evidence_file")"

    # Also try to get incident_id from file (may differ from dir name)
    file_inc_id="$(extract_json_value "incident_id" "$evidence_file")"
    [ -n "$file_inc_id" ] && inc_id="$file_inc_id"

    snippet_lower="$(echo "$snippet" | tr '[:upper:]' '[:lower:]')"
    printf '%s|%s\n' "$inc_id" "$snippet_lower" >> "$inc_snippets_file"

    opened_epoch="$(iso_to_epoch "$opened_at")"
    printf '%s|%s\n' "$inc_id" "$opened_epoch" >> "$inc_opened_file"

    # Track date range from opened_at
    if [ -n "$opened_at" ]; then
        date_str="$(echo "$opened_at" | sed 's/T.*//')"
        if [ -z "$min_date" ] || [ "$date_str" \< "$min_date" ]; then
            min_date="$date_str"
        fi
        if [ -z "$max_date" ] || [ "$date_str" \> "$max_date" ]; then
            max_date="$date_str"
        fi
    fi

done <<< "$incident_dirs"

# Scan history directory for closed ANDON records
if [ -d "${HISTORY_DIR}" ]; then
    while IFS= read -r hist_file; do
        [ -z "$hist_file" ] && continue

        # Extract nested andon.incident_id using awk (compact JSON: "incident_id":"INC-...")
        hist_inc_id="$(awk '
        {
            pattern = "\"incident_id\"[[:space:]]*:[[:space:]]*\"([^\"]*)\""
            if (match($0, pattern)) {
                s = substr($0, RSTART, RLENGTH)
                sub("^\"incident_id\"[[:space:]]*:[[:space:]]*\"", "", s)
                sub("\"$", "", s)
                print s
                exit
            }
        }
        ' "$hist_file")"

        closed_at="$(extract_json_value "closed_at" "$hist_file")"

        if [ -n "$hist_inc_id" ] && [ -n "$closed_at" ]; then
            closed_epoch="$(iso_to_epoch "$closed_at")"
            printf '%s|%s\n' "$hist_inc_id" "$closed_epoch" >> "$inc_closed_file"
        fi

    done < <(find "${HISTORY_DIR}" -maxdepth 1 -name 'andon-closed-*.json' | sort)
fi

# ---------------------------------------------------------------------------
# Compute hit rates: for each Gotcha, scan all incidents
# ---------------------------------------------------------------------------
# Output file: gotcha_id|hits|hit_inc_ids (pipe-separated IDs)
gotcha_hits_file="${tmp_dir}/gotcha_hits.txt"
touch "$gotcha_hits_file"

# Track which incidents matched at least one Gotcha
matched_incidents_file="${tmp_dir}/matched_incidents.txt"
touch "$matched_incidents_file"

# Read all snippets into memory (one line per incident: inc_id|snippet)
# Process each Gotcha against all incidents
idx=0
while IFS= read -r gid; do
    idx=$((idx + 1))
    gpattern="$(sed -n "${idx}p" "$gotcha_patterns_file")"
    hits=0
    hit_inc_ids=""

    while IFS='|' read -r inc_id snippet_lower; do
        [ -z "$inc_id" ] && continue
        match_type="$(incident_matches_gotcha "$snippet_lower" "$gpattern")"
        if [ -n "$match_type" ]; then
            hits=$((hits + 1))
            hit_inc_ids="${hit_inc_ids}${inc_id},"
            # Record this incident as matched (for effectiveness)
            echo "$inc_id" >> "$matched_incidents_file"
        fi
    done < "$inc_snippets_file"

    printf '%s|%d|%s\n' "$gid" "$hits" "$hit_inc_ids" >> "$gotcha_hits_file"

done < "$gotcha_ids_file"

# Deduplicate matched incidents
matched_incidents_dedup="${tmp_dir}/matched_incidents_dedup.txt"
if [ -s "$matched_incidents_file" ]; then
    sort -u "$matched_incidents_file" > "$matched_incidents_dedup"
else
    touch "$matched_incidents_dedup"
fi

# ---------------------------------------------------------------------------
# Compute prevention effectiveness (METRIC-03)
# ---------------------------------------------------------------------------
# For each incident: check if it's in matched_incidents_dedup
# Calculate resolution time if both opened and closed epochs are known

with_match_total_secs=0
with_match_count=0
without_match_total_secs=0
without_match_count=0

while IFS= read -r inc_dir; do
    [ -z "$inc_dir" ] && continue

    evidence_file="${inc_dir}/evidence.json"
    inc_id_dir="$(basename "$inc_dir")"
    file_inc_id="$(extract_json_value "incident_id" "$evidence_file")"
    inc_id="${file_inc_id:-$inc_id_dir}"

    opened_epoch="$(grep -m1 "^${inc_id}|" "$inc_opened_file" 2>/dev/null | cut -d'|' -f2 || true)"
    closed_epoch="$(grep -m1 "^${inc_id}|" "$inc_closed_file" 2>/dev/null | cut -d'|' -f2 || true)"

    # Check if this incident matched any Gotcha
    if grep -qx "$inc_id" "$matched_incidents_dedup" 2>/dev/null; then
        is_matched=1
    else
        is_matched=0
    fi

    # Compute resolution time if both timestamps available
    if [ -n "$opened_epoch" ] && [ -n "$closed_epoch" ] && \
       [ "$opened_epoch" -gt 0 ] 2>/dev/null && [ "$closed_epoch" -gt 0 ] 2>/dev/null; then
        res_secs=$((closed_epoch - opened_epoch))
        if [ "$res_secs" -ge 0 ]; then
            if [ "$is_matched" -eq 1 ]; then
                with_match_total_secs=$((with_match_total_secs + res_secs))
                with_match_count=$((with_match_count + 1))
            else
                without_match_total_secs=$((without_match_total_secs + res_secs))
                without_match_count=$((without_match_count + 1))
            fi
        fi
    fi

done <<< "$incident_dirs"

# Helper: format seconds as human-readable duration
format_duration() {
    local secs="$1"
    if [ -z "$secs" ] || [ "$secs" -eq 0 ] 2>/dev/null; then
        echo "0min"
        return
    fi
    local mins=$(( secs / 60 ))
    local remaining=$(( secs % 60 ))
    if [ "$mins" -ge 60 ]; then
        local hours=$(( mins / 60 ))
        local rem_mins=$(( mins % 60 ))
        echo "${hours}h${rem_mins}min"
    elif [ "$mins" -gt 0 ]; then
        echo "${mins}min${remaining}s"
    else
        echo "${secs}s"
    fi
}

# ---------------------------------------------------------------------------
# Print the report
# ---------------------------------------------------------------------------
period="${min_date:-?} to ${max_date:-?}"
total_matched_incs="$(wc -l < "$matched_incidents_dedup" | tr -d ' ')"
total_unmatched_incs=$(( incident_count - total_matched_incs ))

echo ""
echo "=== Gotcha Effectiveness Report ==="
echo "Data source: ${INCIDENTS_DIR}"
echo "Registry: ${GOTCHAS_DIR}"
echo "Total Gotchas: ${gotcha_count}"
echo "Total incidents scanned: ${incident_count}"
echo "Period: ${period}"

# --- Hit Rate Table ---
echo ""
echo "--- Hit Rate Table ---"
printf '%-14s | %-30s | %4s | %s\n' "ID" "Name" "Hits" "Effectiveness"

idx=0
stale_ids_file="${tmp_dir}/stale_ids.txt"
touch "$stale_ids_file"

while IFS='|' read -r gid hits hit_inc_ids; do
    idx=$((idx + 1))
    gname="$(sed -n "${idx}p" "$gotcha_names_file")"

    if [ "$hits" -eq 0 ]; then
        printf '%-14s | %-30s | %4d | ** POTENTIALLY STALE **\n' \
            "$gid" "$gname" "$hits"
        echo "$gid" >> "$stale_ids_file"
        continue
    fi

    # Compute per-Gotcha avg resolution for matched incidents
    g_with_total=0
    g_with_count=0

    # hit_inc_ids is a comma-separated list
    IFS=',' read -ra hids <<< "$hit_inc_ids"
    for hid in "${hids[@]}"; do
        [ -z "$hid" ] && continue
        o_ep="$(grep -m1 "^${hid}|" "$inc_opened_file" 2>/dev/null | cut -d'|' -f2 || true)"
        c_ep="$(grep -m1 "^${hid}|" "$inc_closed_file" 2>/dev/null | cut -d'|' -f2 || true)"
        if [ -n "$o_ep" ] && [ -n "$c_ep" ] && \
           [ "$o_ep" -gt 0 ] 2>/dev/null && [ "$c_ep" -gt 0 ] 2>/dev/null; then
            g_secs=$((c_ep - o_ep))
            if [ "$g_secs" -ge 0 ]; then
                g_with_total=$((g_with_total + g_secs))
                g_with_count=$((g_with_count + 1))
            fi
        fi
    done

    if [ "$g_with_count" -gt 0 ]; then
        g_avg_secs=$((g_with_total / g_with_count))
        g_avg_fmt="$(format_duration "$g_avg_secs")"
        eff_str="avg ${g_avg_fmt} resolution (${g_with_count} closed)"
    else
        eff_str="no closed incidents for timing"
    fi

    printf '%-14s | %-30s | %4d | %s\n' "$gid" "$gname" "$hits" "$eff_str"

done < "$gotcha_hits_file"

# --- Stale Gotchas ---
echo ""
echo "--- Stale Gotchas (zero hits) ---"

stale_count=0
if [ -s "$stale_ids_file" ]; then
    while IFS= read -r sgid; do
        [ -z "$sgid" ] && continue
        stale_count=$((stale_count + 1))
        # Find index in gotcha_ids_file
        sidx=0
        while IFS= read -r gid_cmp; do
            sidx=$((sidx + 1))
            if [ "$gid_cmp" = "$sgid" ]; then
                sname="$(sed -n "${sidx}p" "$gotcha_names_file")"
                sdiscovered="$(sed -n "${sidx}p" "$gotcha_discovered_file")"
                echo "${sgid}: ${sname} (discovered: ${sdiscovered})"
                echo "  Consider: broadening pattern or archiving if no longer relevant"
                break
            fi
        done < "$gotcha_ids_file"
    done < "$stale_ids_file"
else
    echo "  (none — all Gotchas matched at least one incident)"
fi

# --- Prevention Effectiveness Summary ---
echo ""
echo "--- Prevention Effectiveness Summary ---"

total_matched_str="${total_matched_incs}"
total_unmatched_str="${total_unmatched_incs}"

if [ "$with_match_count" -gt 0 ]; then
    with_avg_secs=$((with_match_total_secs / with_match_count))
    with_avg_fmt="$(format_duration "$with_avg_secs")"
    with_avg_str="${with_avg_fmt}"
else
    with_avg_str="N/A (no closed incidents)"
    with_avg_secs=0
fi

if [ "$without_match_count" -gt 0 ]; then
    without_avg_secs=$((without_match_total_secs / without_match_count))
    without_avg_fmt="$(format_duration "$without_avg_secs")"
    without_avg_str="${without_avg_fmt}"
else
    without_avg_str="N/A (no closed incidents)"
    without_avg_secs=0
fi

echo "Incidents with Gotcha match: ${total_matched_str} (avg resolution: ${with_avg_str})"
echo "Incidents without Gotcha match: ${total_unmatched_str} (avg resolution: ${without_avg_str})"

# Delta calculation
if [ "$with_match_count" -gt 0 ] && [ "$without_match_count" -gt 0 ]; then
    delta_secs=$(( without_avg_secs - with_avg_secs ))
    if [ "$delta_secs" -gt 0 ]; then
        # Gotcha-matched incidents resolved faster
        pct=$(( delta_secs * 100 / without_avg_secs ))
        echo "Delta: Gotcha-matched incidents resolved ~${pct}% faster"
    elif [ "$delta_secs" -lt 0 ]; then
        # Gotcha-matched incidents resolved slower (possibly harder problems)
        abs_delta=$(( -delta_secs ))
        pct=$(( abs_delta * 100 / without_avg_secs ))
        echo "Delta: Gotcha-matched incidents resolved ~${pct}% slower (may reflect harder problem types)"
    else
        echo "Delta: No difference in resolution time"
    fi
else
    echo "Delta: insufficient data for comparison"
fi

echo "Note: Correlation only. Gotcha surfacing may help but is not the sole factor."
echo ""
echo "=== End of Report ==="
