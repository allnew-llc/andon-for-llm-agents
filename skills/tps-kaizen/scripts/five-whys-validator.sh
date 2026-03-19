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
# Usage:
#   five-whys-validator.sh [FILE]
#   five-whys-validator.sh --help
#   cat analysis.md | five-whys-validator.sh
#
# Validates a Five Whys document for:
#   - Depth >= 5 causal levels
#   - Verification column/field filled (non-empty, non-placeholder)
#
# Supports two formats:
#   1. Table format:   | # | Why? | Verification |
#   2. Expanded format: ### Why N: ... + **Verification**: ...
#
# Exit codes:
#   0 = PASS
#   1 = FAIL (document incomplete)
#   2 = Usage error (no input provided)

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REQUIRED_DEPTH=5
PLACEHOLDER_PATTERN='^\[.*\]$\|^TBD$\|^TODO$\|^N/A$\|^\s*$'

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------
usage() {
    cat <<'USAGE'
Usage: five-whys-validator.sh [FILE]
       five-whys-validator.sh --help
       cat analysis.md | five-whys-validator.sh

Validates a Five Whys document for completeness.

Supported formats:
  Table format:     | # | Why? | Verification | rows
  Expanded format:  ### Why N: ... with **Verification**: lines

Exit codes:
  0  PASS — document is complete
  1  FAIL — document is incomplete (< 5 levels or empty verifications)
  2  Usage error — no input provided

Options:
  --help   Print this help and exit 0
USAGE
}

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
if [ $# -gt 0 ] && [ "$1" = "--help" ]; then
    usage
    exit 0
fi

INPUT_SOURCE="stdin"
CONTENT=""

if [ $# -gt 0 ]; then
    FILE="$1"
    INPUT_SOURCE="$FILE"
    if [ ! -f "$FILE" ]; then
        echo "Error: File not found: $FILE" >&2
        exit 2
    fi
    CONTENT=$(cat "$FILE")
else
    # Check if stdin has data
    if [ -t 0 ]; then
        echo "Error: No input provided. Provide a file path or pipe content via stdin." >&2
        usage >&2
        exit 2
    fi
    CONTENT=$(cat)
fi

# ---------------------------------------------------------------------------
# Detect format
# ---------------------------------------------------------------------------
# Table format: lines matching | digit | ... | ... |
TABLE_ROWS=$(echo "$CONTENT" | grep -E '^\|[[:space:]]*[0-9]+[[:space:]]*\|' || true)

# Expanded format: headings matching ### Why N
EXPANDED_SECTIONS=$(echo "$CONTENT" | grep -iE '^###[[:space:]]+Why[[:space:]]+[0-9]' || true)

if [ -n "$TABLE_ROWS" ]; then
    FORMAT="table"
elif [ -n "$EXPANDED_SECTIONS" ]; then
    FORMAT="expanded"
else
    FORMAT="unknown"
fi

# ---------------------------------------------------------------------------
# Helper: check if a string is a placeholder or empty
# is_placeholder <text>  → returns 0 if placeholder/empty, 1 if real content
# ---------------------------------------------------------------------------
is_placeholder() {
    local text
    text=$(echo "$1" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')  # trim whitespace
    if [ -z "$text" ]; then
        return 0
    fi
    # Check known placeholder patterns
    case "$text" in
        "[file/command checked]"|"[command/file checked]"|"[verification]"|"[verify]")
            return 0 ;;
        TBD|TODO|"N/A"|"n/a"|"-"|"—"|"...")
            return 0 ;;
    esac
    # Bracket-wrapped placeholder: [anything]
    if echo "$text" | grep -qE '^\[.+\]$'; then
        return 0
    fi
    return 1
}

# ---------------------------------------------------------------------------
# Validate TABLE format
# ---------------------------------------------------------------------------
validate_table() {
    local rows="$1"
    local depth=0
    local filled=0
    local level_results=""

    while IFS= read -r row; do
        # Extract columns by splitting on |
        # Row format: | N | why text | verification text |
        # Strip leading/trailing |
        local stripped
        stripped=$(echo "$row" | sed 's/^[[:space:]]*|//;s/|[[:space:]]*$//')

        # Split on | to get fields
        local col1 col2 col3
        col1=$(echo "$stripped" | awk -F'|' '{print $1}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        col2=$(echo "$stripped" | awk -F'|' '{print $2}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        col3=$(echo "$stripped" | awk -F'|' '{print $3}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

        # col1 must be a number
        if ! echo "$col1" | grep -qE '^[0-9]+$'; then
            continue
        fi

        depth=$((depth + 1))
        local level_num="$col1"

        if is_placeholder "$col3"; then
            level_results="${level_results}  Level ${level_num}: FAIL (empty verification)\n"
        else
            filled=$((filled + 1))
            level_results="${level_results}  Level ${level_num}: PASS\n"
        fi
    done <<< "$rows"

    echo "$depth $filled $level_results"
}

# ---------------------------------------------------------------------------
# Validate EXPANDED format
# ---------------------------------------------------------------------------
validate_expanded() {
    local content="$1"
    local depth=0
    local filled=0
    local level_results=""
    local current_level=""
    local in_section=0
    local section_has_verification=0
    local verification_content=""

    while IFS= read -r line; do
        # Check for new ### Why N section
        if echo "$line" | grep -qiE '^###[[:space:]]+Why[[:space:]]+[0-9]'; then
            # Save previous section result if any
            if [ -n "$current_level" ]; then
                if [ "$section_has_verification" -eq 1 ] && ! is_placeholder "$verification_content"; then
                    filled=$((filled + 1))
                    level_results="${level_results}  Level ${current_level}: PASS\n"
                else
                    level_results="${level_results}  Level ${current_level}: FAIL (empty verification)\n"
                fi
            fi

            # Start new section
            current_level=$(echo "$line" | grep -oiE 'Why[[:space:]]+[0-9]+' | grep -oE '[0-9]+')
            depth=$((depth + 1))
            in_section=1
            section_has_verification=0
            verification_content=""
            continue
        fi

        # Within a section, look for **Verification**: line
        if [ "$in_section" -eq 1 ]; then
            if echo "$line" | grep -qiE '^\*\*Verification\*\*:'; then
                section_has_verification=1
                # Content may be on same line after the colon
                verification_content=$(echo "$line" | sed 's/^\*\*[Vv]erification\*\*:[[:space:]]*//')
            elif [ "$section_has_verification" -eq 1 ] && [ -z "$verification_content" ]; then
                # Content might be on the next non-empty line
                local trimmed
                trimmed=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                if [ -n "$trimmed" ]; then
                    verification_content="$trimmed"
                fi
            fi
        fi
    done <<< "$content"

    # Save last section
    if [ -n "$current_level" ]; then
        if [ "$section_has_verification" -eq 1 ] && ! is_placeholder "$verification_content"; then
            filled=$((filled + 1))
            level_results="${level_results}  Level ${current_level}: PASS\n"
        else
            level_results="${level_results}  Level ${current_level}: FAIL (empty verification)\n"
        fi
    fi

    echo "$depth $filled $level_results"
}

# ---------------------------------------------------------------------------
# Check for human error stop (last Why)
# ---------------------------------------------------------------------------
check_human_error_stop() {
    local content="$1"
    local last_why=""
    local format="$2"
    local warning=""

    if [ "$format" = "table" ]; then
        # Get the last numbered row's why column
        last_why=$(echo "$content" | grep -E '^\|[[:space:]]*[0-9]+[[:space:]]*\|' | tail -1 | awk -F'|' '{print $3}')
    else
        # Get the last ### Why N section text
        last_why=$(echo "$content" | awk '/^###[[:space:]]+[Ww]hy[[:space:]]+[0-9]/{buf=""} {buf=buf"\n"$0} END{print buf}')
    fi

    if echo "$last_why" | grep -qiE 'human error|i made a mistake|forgot to|did.t remember|didn.t notice'; then
        warning="WARNING: Final cause may be stopping at human error — consider digging into process/system issues (see Gotchas: Human Error Stop)"
    fi

    echo "$warning"
}

# ---------------------------------------------------------------------------
# Run validation
# ---------------------------------------------------------------------------
DEPTH=0
FILLED=0
LEVEL_RESULTS=""

if [ "$FORMAT" = "table" ]; then
    # Parse table rows
    RAW=$(validate_table "$TABLE_ROWS")
    DEPTH=$(echo "$RAW" | awk '{print $1}')
    FILLED=$(echo "$RAW" | awk '{print $2}')
    # Level results are the remainder (everything after the first two words)
    LEVEL_RESULTS=$(echo "$RAW" | cut -d' ' -f3-)
elif [ "$FORMAT" = "expanded" ]; then
    RAW=$(validate_expanded "$CONTENT")
    DEPTH=$(echo "$RAW" | awk '{print $1}')
    FILLED=$(echo "$RAW" | awk '{print $2}')
    LEVEL_RESULTS=$(echo "$RAW" | cut -d' ' -f3-)
else
    # Unknown format — we can't find any Five Whys structure
    DEPTH=0
    FILLED=0
    LEVEL_RESULTS="  (No recognized Five Whys structure found in document)\n"
fi

# Depth check
if [ "$DEPTH" -ge "$REQUIRED_DEPTH" ]; then
    DEPTH_STATUS="PASS"
else
    DEPTH_STATUS="FAIL"
fi

# Verification check
if [ "$DEPTH" -gt 0 ] && [ "$FILLED" -eq "$DEPTH" ]; then
    VERIF_STATUS="PASS"
else
    VERIF_STATUS="FAIL"
fi

# Human error stop check
HUMAN_ERROR_WARNING=$(check_human_error_stop "$CONTENT" "$FORMAT")

# Overall result
FAIL_REASONS=""
if [ "$DEPTH_STATUS" = "FAIL" ]; then
    FAIL_REASONS="${FAIL_REASONS}depth < ${REQUIRED_DEPTH} (found ${DEPTH}); "
fi
if [ "$VERIF_STATUS" = "FAIL" ]; then
    FAIL_REASONS="${FAIL_REASONS}${FILLED}/${DEPTH} verifications filled; "
fi

if [ -z "$FAIL_REASONS" ]; then
    OVERALL="PASS"
    EXIT_CODE=0
else
    OVERALL="FAIL"
    EXIT_CODE=1
fi

# ---------------------------------------------------------------------------
# Output report
# ---------------------------------------------------------------------------
echo "=== Five Whys Validation Report ==="
echo "File: ${INPUT_SOURCE}"
echo ""
echo "Depth Check:"
echo "  Levels found: ${DEPTH}"
echo "  Required: ${REQUIRED_DEPTH}"
echo "  Status: ${DEPTH_STATUS}"
echo ""
echo "Verification Check:"
if [ -n "$LEVEL_RESULTS" ]; then
    printf "%b" "$LEVEL_RESULTS"
fi
echo "  Filled: ${FILLED}/${DEPTH}"
echo "  Status: ${VERIF_STATUS}"
echo ""
echo "Warnings:"
if [ -n "$HUMAN_ERROR_WARNING" ]; then
    echo "  - ${HUMAN_ERROR_WARNING}"
else
    echo "  (none)"
fi
echo ""
echo "Overall: ${OVERALL}"
if [ "$OVERALL" = "FAIL" ]; then
    echo "Reason: ${FAIL_REASONS%%; }"
fi
echo ""
echo "=== End of Report ==="

exit $EXIT_CODE
