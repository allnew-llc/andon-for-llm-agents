# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""kaizen_classify.py — Failure classification and domain routing.

Pattern-based failure classification with confidence scoring.
Integrates with Knowledge Pack domain classifiers for skill recommendations.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import re
from typing import Any

# ============================================================
# Built-in classification rules
# ============================================================
# (cause_id, label, confidence, regex_pattern)
# Add your own patterns by appending to this list.

CLASSIFICATION_RULES: list[tuple[str, str, float, str]] = [
    ("command_not_found", "Required command not installed", 0.94,
     r"(command not found|not recognized as an internal or external command)"),
    ("python_module_missing", "Python dependency missing", 0.88,
     r"(modulenotfounderror|no module named)"),
    ("node_module_missing", "Node dependency missing", 0.84,
     r"(cannot find module)"),
    ("permission_denied", "Permission denied", 0.82,
     r"(permission denied|eacces)"),
    ("path_missing", "File or path not found", 0.79,
     r"(no such file or directory|enoent)"),
    ("timeout", "Timeout or transient failure", 0.68,
     r"(timed out|timeout|etimedout)"),
    ("assertion_failure", "Test failure or assertion error", 0.62,
     r"(assertionerror|failed|failures)"),
]


def classify_failure(
    command: str,
    merged_output: str,
    *,
    init_packs: Any = None,
    pack_bundle: Any = None,
) -> dict[str, Any]:
    """Classify a command failure and generate prevention/standardization actions.

    Args:
        command: The failed command string.
        merged_output: Combined stdout/stderr output.
        init_packs: Callable to initialize packs (injected from runtime).
        pack_bundle: Pack bundle for skill recommendations.
    """
    text = f"{command}\n{merged_output}"
    lower = text.lower()

    cause_id = "unknown_failure"
    cause_label = "Unknown failure"
    confidence = 0.35
    matched_pattern = ""

    for cid, label, score, pattern in CLASSIFICATION_RULES:
        if re.search(pattern, lower, re.IGNORECASE):
            cause_id = cid
            cause_label = label
            confidence = score
            matched_pattern = pattern
            break

    details: dict[str, Any] = {}
    if cause_id == "command_not_found":
        m = re.search(r"([A-Za-z0-9._/-]+):\s*command not found", merged_output)
        if m:
            details["missing_command"] = m.group(1)
    elif cause_id == "python_module_missing":
        m = re.search(
            r"No module named ['\"]?([A-Za-z0-9._-]+)['\"]?",
            merged_output, re.IGNORECASE,
        )
        if m:
            details["missing_python_module"] = m.group(1)
    elif cause_id == "node_module_missing":
        m = re.search(
            r"Cannot find module ['\"]([^'\"]+)['\"]",
            merged_output, re.IGNORECASE,
        )
        if m:
            details["missing_node_module"] = m.group(1)
    elif cause_id == "path_missing":
        m = re.search(
            r"No such file or directory[: ]+['\"]?([^'\n\"]+)['\"]?",
            merged_output, re.IGNORECASE,
        )
        if m:
            details["missing_path"] = m.group(1)

    prevention_actions = _prevention_actions(cause_id, details)
    standardization_actions = _standardization_actions(cause_id, details)

    # Enrich with domain classification + skill recommendations from packs
    recommended_skills: dict[str, Any] = {}
    if init_packs is not None:
        init_packs()
    if pack_bundle is not None:
        try:
            from domain_classifier import recommend_skills as _recommend
            recommended_skills = _recommend(
                cause_id, command, merged_output,
                skill_map=pack_bundle.skill_map,
                extra_keywords=pack_bundle.extra_keywords,
            )
        except ImportError:
            pass

    return {
        "cause_id": cause_id,
        "cause_label": cause_label,
        "confidence": confidence,
        "matched_pattern": matched_pattern,
        "details": details,
        "prevention_actions": prevention_actions,
        "standardization_actions": standardization_actions,
        "recommended_skills": recommended_skills,
    }


def _prevention_actions(
    cause_id: str, details: dict[str, Any]
) -> list[dict[str, str]]:
    if cause_id == "command_not_found":
        missing = details.get("missing_command", "UNKNOWN_COMMAND")
        return [
            {"level": "L1", "action": f"Add existence check for `{missing}` before execution"},
            {"level": "L2", "action": "Add required command validation to CI preflight"},
            {"level": "L3", "action": "Document required commands in setup instructions"},
        ]
    if cause_id in {"python_module_missing", "node_module_missing"}:
        missing_dep = (
            details.get("missing_python_module")
            or details.get("missing_node_module", "UNKNOWN_DEP")
        )
        return [
            {"level": "L1", "action": f"Add dependency `{missing_dep}` existence check to startup"},
            {"level": "L2", "action": "Add dependency sync command to pipeline preflight"},
            {"level": "L3", "action": "Document dependency update procedure in runbook"},
        ]
    if cause_id == "path_missing":
        path_value = details.get("missing_path", "UNKNOWN_PATH")
        return [
            {"level": "L1", "action": f"Add existence check for required path `{path_value}`"},
            {"level": "L2", "action": "Add file existence checks to CI"},
            {"level": "L3", "action": "Add file placement rules to standards docs"},
        ]
    if cause_id == "permission_denied":
        return [
            {"level": "L1", "action": "Add execution permission check at startup"},
            {"level": "L2", "action": "Add explicit error on permission check failure"},
            {"level": "L3", "action": "Add permission rules to standards docs"},
        ]
    if cause_id == "timeout":
        return [
            {"level": "L1", "action": "Add explicit timeout/retry boundaries for external dependencies"},
            {"level": "L2", "action": "Separate transient vs permanent failure detection"},
            {"level": "L3", "action": "Standardize retry policy"},
        ]
    return [
        {"level": "L3", "action": "Pattern-match similar failures and add detection rules"},
        {"level": "L4", "action": "Record interim workaround in operations notes"},
    ]


def _standardization_actions(
    cause_id: str, details: dict[str, Any]
) -> list[dict[str, str]]:
    if cause_id == "command_not_found":
        return [{"type": "required_command", "value": details.get("missing_command", "UNKNOWN_COMMAND")}]
    if cause_id == "python_module_missing":
        return [{"type": "required_python_module", "value": details.get("missing_python_module", "UNKNOWN_DEP")}]
    if cause_id == "node_module_missing":
        return [{"type": "required_node_module", "value": details.get("missing_node_module", "UNKNOWN_DEP")}]
    if cause_id == "path_missing":
        return [{"type": "required_path", "value": details.get("missing_path", "UNKNOWN_PATH")}]
    if cause_id == "permission_denied":
        return [{"type": "permission_guard", "value": "execution_permissions"}]
    if cause_id == "timeout":
        return [{"type": "retry_policy", "value": "bounded_retry"}]
    return []
