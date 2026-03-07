#!/bin/bash
# tps-andon-control.sh — ANDON control wrapper
#
# Usage:
#   ./.claude/hooks/tps-andon-control.sh status
#   ./.claude/hooks/tps-andon-control.sh close "reason"
#   ./.claude/hooks/tps-andon-control.sh rollback [incident_id|latest]
#
# Copyright 2026 AllNew LLC — Apache License 2.0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNTIME="$SCRIPT_DIR/tps-kaizen-runtime.py"
ACTION="${1:-status}"
ARG="${2:-}"

if [ ! -f "$RUNTIME" ]; then
  echo "Runtime not found: $RUNTIME" >&2
  exit 1
fi

case "$ACTION" in
  status)
    python3 "$RUNTIME" status
    ;;
  close)
    if [ -z "$ARG" ]; then
      ARG="manual"
    fi
    python3 "$RUNTIME" close "$ARG"
    ;;
  rollback)
    if [ -z "$ARG" ]; then
      ARG="latest"
    fi
    python3 "$RUNTIME" rollback "$ARG"
    ;;
  *)
    echo "Usage: $0 {status|close|rollback} [reason|incident_id]" >&2
    exit 2
    ;;
esac
