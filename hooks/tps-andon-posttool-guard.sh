#!/bin/bash
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
# tps-andon-posttool-guard.sh — PostToolUse hook wrapper
#
# Delegates incident detection/analysis/report generation to runtime script.
# Also runs analysis paralysis detection for all tool invocations.
#
# Copyright 2026 AllNew LLC — Apache License 2.0

set -euo pipefail

INPUT_JSON="$(cat)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNTIME="$SCRIPT_DIR/tps-kaizen-runtime.py"

if [ ! -f "$RUNTIME" ]; then
  echo "{}"
  exit 0
fi

# --- 1. Existing ANDON open-from-payload ---
ANDON_OUTPUT=$(INPUT_JSON="$INPUT_JSON" python3 "$RUNTIME" open-from-payload)

# --- 2. Analysis paralysis detection ---
# Extract tool_name and exit_code from the payload JSON
TOOL_NAME=$(echo "$INPUT_JSON" | python3 -c "
import sys, json
try:
    p = json.load(sys.stdin)
    print(p.get('tool_name', ''))
except (json.JSONDecodeError, ValueError, KeyError):
    print('')
" 2>/dev/null || echo "")

EXIT_CODE=$(echo "$INPUT_JSON" | python3 -c "
import sys, json
def find_exit_code(obj):
    if isinstance(obj, dict):
        for k in ('exit_code', 'exitCode', 'status_code', 'statusCode', 'code', 'returncode'):
            v = obj.get(k)
            if isinstance(v, int):
                return v
        for v in obj.values():
            r = find_exit_code(v)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for item in obj:
            r = find_exit_code(item)
            if r is not None:
                return r
    return None
try:
    p = json.load(sys.stdin)
    ec = find_exit_code(p)
    print(ec if ec is not None else '')
except (json.JSONDecodeError, ValueError, KeyError):
    print('')
" 2>/dev/null || echo "")

AP_OUTPUT=""
if [ -n "$TOOL_NAME" ]; then
  AP_ARGS=("$TOOL_NAME")
  if [ -n "$EXIT_CODE" ]; then
    AP_ARGS+=("$EXIT_CODE")
  fi
  AP_OUTPUT=$(python3 "$RUNTIME" analysis-paralysis "${AP_ARGS[@]}" 2>/dev/null || echo "{}")
fi

# --- 3. Context quality check ---
CTX_OUTPUT=$(python3 "$RUNTIME" context-check 2>/dev/null || echo "{}")

# --- 4. Merge outputs ---
# Collect all non-empty outputs and merge additionalContext values.
# If ANDON produced output with block/decision, it takes priority for those fields.
python3 -c "
import sys, json

outputs = []
for arg in sys.argv[1:]:
    arg = arg.strip()
    if arg and arg != '{}':
        try:
            outputs.append(json.loads(arg))
        except (json.JSONDecodeError, ValueError, KeyError):
            pass

if not outputs:
    print('{}')
    raise SystemExit(0)

# Start with the first output that has a decision (block), or the first output
merged = {}
for o in outputs:
    if 'decision' in o:
        merged = dict(o)
        break
if not merged:
    merged = dict(outputs[0])

# Collect all additionalContext strings
contexts = []
for o in outputs:
    ctx = o.get('hookSpecificOutput', {}).get('additionalContext', '')
    if ctx and ctx not in contexts:
        contexts.append(ctx)

if contexts:
    hso = merged.setdefault('hookSpecificOutput', {})
    hso['additionalContext'] = ' '.join(contexts)
    if 'hookEventName' not in hso:
        hso['hookEventName'] = 'PostToolUse'

print(json.dumps(merged, ensure_ascii=False))
" "$ANDON_OUTPUT" "$AP_OUTPUT" "$CTX_OUTPUT"
