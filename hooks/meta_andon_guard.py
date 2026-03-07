#!/usr/bin/env python3
"""meta_andon_guard.py — Meta-ANDON: Detect repeated failure patterns

Detects when the agent is stuck in a whack-a-mole debugging loop by
tracking consecutive failures across runs.

This is a generic implementation. For pipeline-specific usage,
extend with your own project directory detection and run tracking.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

META_ANDON_FAILURE_THRESHOLD = int(
    os.environ.get("META_ANDON_FAILURE_THRESHOLD", "3")
)
META_ANDON_REQUIRED_ARTIFACTS = [
    "meta-andon-five-whys.md",
    "meta-andon-risk-table.md",
    "horizontal-sweep-report.md",
]
META_ANDON_STATE_SCHEMA_VERSION = "meta-andon-state.v1"

# Artifact content validation rules
META_ANDON_ARTIFACT_RULES: dict[str, dict[str, Any]] = {
    "meta-andon-five-whys.md": {
        "min_bytes": 80,
        "marker_groups": [
            ["why 1", "why 2", "why 3", "why 4", "why 5"],
        ],
    },
    "meta-andon-risk-table.md": {
        "min_bytes": 80,
        "marker_groups": [
            ["| phase |", "| risk", "| evidence", "| action"],
        ],
    },
    "horizontal-sweep-report.md": {
        "min_bytes": 80,
        "marker_groups": [
            ["| phase |", "| risk", "| evidence", "| action"],
        ],
    },
}


def _validate_meta_andon_state_schema(payload: dict[str, Any]) -> tuple[bool, str]:
    """Validate the meta-andon-state.json schema."""
    if not payload:
        return False, "meta-andon-state.json is missing or invalid JSON."

    if str(payload.get("schema_version", "")).strip() != META_ANDON_STATE_SCHEMA_VERSION:
        return False, f"schema_version must be '{META_ANDON_STATE_SCHEMA_VERSION}'."

    status = str(payload.get("status", "")).strip().lower()
    if status not in {"open", "closed"}:
        return False, "status must be 'open' or 'closed'."

    consecutive = payload.get("consecutive_failures")
    if not isinstance(consecutive, int) or consecutive < 0:
        return False, "consecutive_failures must be a non-negative integer."

    failure_runs = payload.get("failure_runs")
    if not isinstance(failure_runs, list) or any(
        not isinstance(item, str) for item in failure_runs
    ):
        return False, "failure_runs must be a string list."

    updated_at = str(payload.get("updated_at", "")).strip()
    if not updated_at:
        return False, "updated_at is required."

    return True, ""


def _validate_artifact_content(
    *, artifact_path: Path, rule: dict[str, Any]
) -> tuple[bool, str]:
    """Validate that a meta-andon artifact has real content."""
    min_bytes = int(rule.get("min_bytes", 1))
    try:
        size = artifact_path.stat().st_size
    except OSError:
        return False, "stat_error"
    if size < min_bytes:
        return False, f"too_small(<{min_bytes} bytes)"

    try:
        content = artifact_path.read_text(encoding="utf-8")
    except OSError:
        return False, "read_error"

    marker_groups = rule.get("marker_groups", [])
    if not marker_groups:
        return True, ""

    lowered = content.lower()
    for group in marker_groups:
        if all(str(marker).lower() in lowered for marker in group):
            return True, ""
    return False, "required_sections_missing"


def evaluate_meta_andon(
    *,
    artifacts_dir: Path,
    state_file: Path | None = None,
    consecutive_failures: int = 0,
    failure_run_ids: list[str] | None = None,
    threshold: int = META_ANDON_FAILURE_THRESHOLD,
) -> dict[str, Any]:
    """Evaluate whether Meta-ANDON should block further runs.

    Args:
        artifacts_dir: Directory where meta-andon artifacts should exist
        state_file: Path to meta-andon-state.json (optional)
        consecutive_failures: Number of consecutive failures detected
        failure_run_ids: IDs of the failing runs
        threshold: Number of consecutive failures to trigger Meta-ANDON

    Returns:
        dict with evaluation details including 'blocked' boolean
    """
    details: dict[str, Any] = {
        "artifacts_dir": str(artifacts_dir),
        "threshold": threshold,
        "consecutive_failures": consecutive_failures,
        "consecutive_failure_runs": failure_run_ids or [],
        "missing_artifacts": [],
        "invalid_artifacts": [],
        "state_schema_valid": True,
        "state_schema_error": "",
        "blocked": False,
    }

    # Check state file if provided
    if state_file and state_file.exists():
        try:
            state_payload = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            state_payload = {}

        valid, error = _validate_meta_andon_state_schema(state_payload)
        details["state_schema_valid"] = valid
        details["state_schema_error"] = error

        if valid:
            state_status = str(state_payload.get("status", "")).strip().lower()
            state_consecutive = int(state_payload.get("consecutive_failures", 0))
            consecutive_failures = max(consecutive_failures, state_consecutive)
            details["consecutive_failures"] = consecutive_failures

            if state_status == "open":
                # Meta-ANDON was previously triggered and not resolved
                pass

    # Check if threshold is met
    triggered = consecutive_failures >= threshold
    if not triggered:
        return details

    # Validate required artifacts
    missing: list[str] = []
    invalid: list[str] = []
    for artifact_name in META_ANDON_REQUIRED_ARTIFACTS:
        artifact = artifacts_dir / artifact_name
        if not artifact.exists():
            missing.append(artifact_name)
            continue
        rule = META_ANDON_ARTIFACT_RULES.get(artifact_name)
        if rule:
            valid, reason = _validate_artifact_content(
                artifact_path=artifact, rule=rule
            )
            if not valid:
                invalid.append(f"{artifact_name}:{reason}")

    details["missing_artifacts"] = missing
    details["invalid_artifacts"] = invalid
    details["blocked"] = bool(missing or invalid)
    return details
