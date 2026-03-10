# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""kaizen_incident.py — Standardization registry and incident report generation.

Manages the persistent standardization registry (auto-generated prevention
rules) and generates human-readable incident reports.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import datetime
import hashlib
import os
from pathlib import Path
from typing import Any

from kaizen_core import (
    CONFIDENCE_MANUAL_REVIEW_THRESHOLD,
    KAIZEN_DIR,
    STANDARD_REGISTRY,
    load_json,
    now_utc,
    write_json,
)

def _write_text_secure(path: Path, content: str) -> None:
    """Write text to a file with explicit 0o640 permissions."""
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o640)
    try:
        os.write(fd, content.encode("utf-8"))
    finally:
        os.close(fd)


# === Incident ID ===

def incident_id_from(command: str, at: str) -> str:
    digest = hashlib.sha256(
        f"{at}:{command}".encode("utf-8", errors="ignore")
    ).hexdigest()[:8]
    t = datetime.datetime.fromisoformat(at.replace("Z", "+00:00"))
    return f"INC-{t.strftime('%Y%m%d-%H%M%S')}-{digest}"


# === Standardization Registry ===

def load_standard_registry() -> dict[str, Any]:
    data = load_json(STANDARD_REGISTRY)
    if not data:
        return {"version": 1, "rules": []}
    if not isinstance(data.get("rules"), list):
        data["rules"] = []
    return data


def render_standard_registry_markdown(registry: dict[str, Any]) -> str:
    lines = [
        "# KAIZEN Standardized Rules",
        "",
        f"- updated_at: {now_utc()}",
        "",
        "| type | value | source_incident | active |",
        "|------|-------|-----------------|--------|",
    ]
    for rule in registry.get("rules", []):
        lines.append(
            f"| {rule.get('type','')} | {rule.get('value','')} "
            f"| {rule.get('source_incident','')} | {rule.get('active', True)} |"
        )
    return "\n".join(lines) + "\n"


def apply_standardization(
    incident_id: str, actions: list[dict[str, str]], incident_dir: Path
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "applied": False,
        "applied_count": 0,
        "rollback_ready": False,
        "backup_file": "",
    }
    if not actions:
        return result

    registry = load_standard_registry()
    backup_dir = incident_dir / "rollback"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backup_dir / "standardization-registry.before.json"
    write_json(backup_file, registry)

    existing = {
        (str(rule.get("type", "")), str(rule.get("value", "")))
        for rule in registry.get("rules", [])
        if isinstance(rule, dict) and rule.get("active", True)
    }

    added = 0
    for action in actions:
        rtype = str(action.get("type", "")).strip()
        value = str(action.get("value", "")).strip()
        if not rtype or not value:
            continue
        key = (rtype, value)
        if key in existing:
            continue
        registry["rules"].append(
            {
                "type": rtype,
                "value": value,
                "source_incident": incident_id,
                "created_at": now_utc(),
                "active": True,
            }
        )
        existing.add(key)
        added += 1

    write_json(STANDARD_REGISTRY, registry)
    standard_md = KAIZEN_DIR / "STANDARDIZED_RULES.md"
    _write_text_secure(
        standard_md, render_standard_registry_markdown(registry)
    )

    result["applied"] = added > 0
    result["applied_count"] = added
    result["rollback_ready"] = True
    result["backup_file"] = str(backup_file)
    return result


# === Incident Report ===

def enrich_analysis_for_level(
    analysis: dict[str, Any],
    actions_data: dict[str, Any],
) -> None:
    """Add level-specific fields to analysis and actions in-place.

    Level 1-2: No additional fields (existing behavior).
    Level 3:   Adds ``proposed_fix`` to analysis.
    Level 4:   Adds ``requires_approval: true`` to analysis.
    """
    action_level = int(analysis.get("action_level", 2))
    if action_level == 3:
        cause_id = analysis.get("cause_id", "unknown_failure")
        standardization = analysis.get("standardization_actions", [])
        proposed = (
            standardization[0].get("value", "review required")
            if standardization
            else "review required"
        )
        analysis["proposed_fix"] = (
            f"Proposed fix for {cause_id}: {proposed}"
        )
    elif action_level == 4:
        analysis["requires_approval"] = True


def write_incident_report(
    incident_id: str,
    incident_dir: Path,
    evidence: dict[str, Any],
    analysis: dict[str, Any],
    actions: dict[str, Any],
    standardization_result: dict[str, Any],
) -> Path:
    report_path = incident_dir / "report.md"
    lines: list[str] = []
    lines.append(f"# KAIZEN Incident Report: {incident_id}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- opened_at: {evidence.get('opened_at', '')}")
    lines.append(f"- command: `{evidence.get('command', '')}`")
    lines.append(f"- exit_code: `{evidence.get('exit_code', '')}`")
    lines.append(
        f"- root_cause: `{analysis.get('cause_label', '')}` "
        f"({analysis.get('confidence', 0):.2f})"
    )
    lines.append("")

    lines.append("## Evidence")
    lines.append(f"- workspace: `{evidence.get('workspace', '')}`")
    git_ctx = evidence.get("git", {})
    if isinstance(git_ctx, dict):
        lines.append(f"- branch: `{git_ctx.get('branch', '')}`")
        lines.append(f"- head: `{git_ctx.get('head', '')}`")
    snippet = str(evidence.get("output_snippet", "")).strip()
    if snippet:
        lines.append("")
        lines.append("```text")
        lines.append(snippet)
        lines.append("```")
        lines.append("")

    lines.append("## Recurrence Prevention")
    for item in analysis.get("prevention_actions", []):
        level = item.get("level", "")
        action = item.get("action", "")
        lines.append(f"- {level}: {action}")
    if not analysis.get("prevention_actions"):
        lines.append("- No automatic prevention actions generated")
    lines.append("")

    rec = analysis.get("recommended_skills", {})
    if rec and (rec.get("primary") or rec.get("secondary")):
        lines.append("## Recommended Knowledge Skills")
        lines.append(f"- domain: `{rec.get('domain', '')}`")
        for skill in rec.get("primary", []):
            lines.append(
                f"- **[primary]** `{skill.get('ref', '')}`: "
                f"{skill.get('description', '')}"
            )
        for skill in rec.get("secondary", []):
            lines.append(
                f"- [secondary] `{skill.get('ref', '')}`: "
                f"{skill.get('description', '')}"
            )
        lines.append("")

    lines.append("## Standardization")
    lines.append(
        f"- auto_applied: `{standardization_result.get('applied', False)}`"
    )
    lines.append(
        f"- applied_count: `{standardization_result.get('applied_count', 0)}`"
    )
    lines.append(
        f"- rollback_ready: `{standardization_result.get('rollback_ready', False)}`"
    )
    backup_file = standardization_result.get("backup_file", "")
    if backup_file:
        lines.append(f"- rollback_backup: `{backup_file}`")
    for item in analysis.get("standardization_actions", []):
        lines.append(
            f"- rule: `{item.get('type','')}` = `{item.get('value','')}`"
        )
    if not analysis.get("standardization_actions"):
        lines.append("- no standardization rules were generated")
    lines.append("")

    confidence = float(analysis.get("confidence", 0.0))
    lines.append("## Review Gate")
    if confidence < CONFIDENCE_MANUAL_REVIEW_THRESHOLD:
        lines.append(
            "- confidence below threshold; manual review required before close "
            '(use close reason including "manual-approved").'
        )
    else:
        lines.append("- confidence threshold met for auto-standardization.")
    lines.append("")

    lines.append("## Operations")
    lines.append(
        "- close: `.claude/hooks/tps-andon-control.sh close \"<reason>\"`"
    )
    lines.append(
        f"- rollback: `.claude/hooks/tps-andon-control.sh rollback {incident_id}`"
    )
    lines.append("")

    _write_text_secure(report_path, "\n".join(lines))
    return report_path


def update_final_report_on_close(
    incident_id: str, incident_dir: Path, reason: str
) -> Path:
    report = incident_dir / "report.md"
    final = incident_dir / "final-report.md"
    base = (
        report.read_text(encoding="utf-8")
        if report.exists()
        else f"# KAIZEN Incident Report: {incident_id}\n"
    )
    lines = [
        base, "", "## Close Summary",
        f"- closed_at: {now_utc()}", f"- close_reason: {reason}", "",
    ]
    _write_text_secure(final, "\n".join(lines))
    return final
