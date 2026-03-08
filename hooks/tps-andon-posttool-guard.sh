#!/bin/bash
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
# tps-andon-posttool-guard.sh — PostToolUse hook wrapper
#
# Delegates incident detection/analysis/report generation to runtime script.
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

INPUT_JSON="$INPUT_JSON" python3 "$RUNTIME" open-from-payload
