#!/usr/bin/env python3
"""tps-kaizen-runtime.py — ANDON Runtime Engine for LLM Agent Hooks

Runtime engine for TPS/ANDON hooks:
- open-from-payload: detect failure and open/update incident automatically
- status: print current ANDON status
- close: close ANDON only when required artifacts are present
- rollback: restore auto-standardization state for an incident

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

# === Pack 0 + Domain Classifier + Pack Loader ===
# Lazy-imported to avoid hard failures if PyYAML is not installed
_pack_bundle = None  # type: ignore
_safety_guard = None  # type: ignore


def _init_packs() -> None:
    """Load Pack 0 (Output Safety Guard), domain classifier, and packs."""
    global _pack_bundle, _safety_guard
    if _safety_guard is not None:
        return
    try:
        from output_safety_guard import OutputSafetyGuard
        from pack_loader import PackLoader, PackBundle

        _safety_guard = OutputSafetyGuard()

        packs_dir = Path(__file__).parent / "packs"
        loader = PackLoader(pack0_available=True)
        if packs_dir.is_dir():
            _pack_bundle = loader.load_all(packs_dir)
            if _pack_bundle.safety_extensions:
                _safety_guard.merge_pack_extensions(_pack_bundle.safety_extensions)
        else:
            _pack_bundle = PackBundle.empty()
    except ImportError:
        _safety_guard = None
        _pack_bundle = None


# === Configuration ===
# Override WORKSPACE by setting ANDON_WORKSPACE environment variable
WORKSPACE = Path(os.environ.get("ANDON_WORKSPACE", "")).resolve() if os.environ.get("ANDON_WORKSPACE") else Path(__file__).resolve().parents[2]
STATE_DIR = Path(os.environ.get("ANDON_STATE_DIR", "")).resolve() if os.environ.get("ANDON_STATE_DIR") else WORKSPACE / ".claude" / "state"
KAIZEN_DIR = STATE_DIR / "kaizen"
INCIDENTS_DIR = KAIZEN_DIR / "incidents"
HISTORY_DIR = STATE_DIR / "history"
ANDON_FILE = STATE_DIR / "andon-open.json"
STANDARD_REGISTRY = KAIZEN_DIR / "standardization-registry.json"

# Confidence thresholds
CONFIDENCE_AUTOMATION_THRESHOLD = float(os.environ.get("ANDON_CONFIDENCE_AUTO", "0.70"))
CONFIDENCE_MANUAL_REVIEW_THRESHOLD = float(os.environ.get("ANDON_CONFIDENCE_MANUAL", "0.70"))


def now_utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def ensure_dirs() -> None:
    INCIDENTS_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    KAIZEN_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    # Use explicit file mode (owner rw, group r, no other) to avoid
    # umask-dependent world-readable permissions on incident data.
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o640)
    try:
        os.write(fd, content.encode("utf-8"))
    finally:
        os.close(fd)


def append_json_event(path: Path, data: dict[str, Any]) -> None:
    existing: dict[str, Any] = load_json(path)
    events: list[dict[str, Any]] = []
    if isinstance(existing.get("events"), list):
        events = existing["events"]
    events.append(data)
    write_json(path, {"events": events})


def print_hook_context(message: str, block: bool) -> None:
    payload: dict[str, Any] = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        }
    }
    if block:
        payload["decision"] = "block"
        payload["reason"] = message
    print(json.dumps(payload, ensure_ascii=False))


def print_empty() -> None:
    print("{}")


def get_payload_from_env() -> dict[str, Any]:
    raw = os.environ.get("INPUT_JSON", "")
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
        return {}
    except Exception:
        return {}


def get_command(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command.strip()
    return ""


def get_workdir(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        workdir = tool_input.get("workdir")
        if isinstance(workdir, str) and workdir.strip():
            return workdir.strip()
    return str(WORKSPACE)


def find_exit_code(obj: Any) -> int | None:
    if isinstance(obj, dict):
        for key in ("exit_code", "exitCode", "status_code", "statusCode", "code", "returncode"):
            value = obj.get(key)
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.lstrip("-").isdigit():
                return int(value)
        for value in obj.values():
            child = find_exit_code(value)
            if child is not None:
                return child
    elif isinstance(obj, list):
        for item in obj:
            child = find_exit_code(item)
            if child is not None:
                return child
    return None


def collect_text_blobs(payload: dict[str, Any]) -> list[str]:
    blobs: list[str] = []
    for key in ("tool_response", "tool_output", "output", "stdout", "stderr"):
        value = payload.get(key)
        if isinstance(value, str):
            blobs.append(value)
        elif isinstance(value, dict):
            for nested in ("stdout", "stderr", "output", "text", "message"):
                nested_value = value.get(nested)
                if isinstance(nested_value, str):
                    blobs.append(nested_value)
    return blobs


def derive_exit_code(payload: dict[str, Any]) -> int | None:
    code = find_exit_code(payload)
    if code is not None:
        return code
    merged = "\n".join(collect_text_blobs(payload))
    match = re.search(
        r"(?:exit(?:ed)?\s+with\s+code|exit[_ ]code)\s*[:=]?\s*(-?\d+)",
        merged,
        re.IGNORECASE,
    )
    if match:
        try:
            return int(match.group(1))
        except Exception:
            return None
    return None


def is_tolerant_command(command: str) -> bool:
    lower = command.lower()
    return "|| true" in lower or "||true" in lower


def is_readonly_failure(command: str) -> bool:
    readonly = {
        "ls", "cat", "sed", "head", "tail", "find", "rg", "grep",
        "pwd", "echo", "date", "which", "whoami", "wc", "sort",
        "cut", "awk", "tr", "jq", "stat", "uname",
    }
    try:
        argv = shlex.split(command, posix=True)
    except Exception:
        argv = command.split()
    first = os.path.basename(argv[0]) if argv else ""
    return first in readonly


def safe_snippet(text: str, limit: int = 2400) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


# Secret redaction patterns — applied before any output is persisted
_SECRET_PATTERNS: list[re.Pattern[str]] = [
    # Bearer / Authorization headers
    re.compile(r"(Bearer\s+)[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(r"(Authorization:\s*(?:Bearer|Basic|Token)\s+)[^\s'\"]+", re.IGNORECASE),
    # Common API key prefixes (OpenAI, Anthropic, Google, Stripe, AWS, GitHub)
    re.compile(r"(sk-(?:proj-|live-|test-)?)[A-Za-z0-9]{8,}"),
    re.compile(r"(sk-ant-)[A-Za-z0-9\-]{8,}"),
    re.compile(r"(AIza)[A-Za-z0-9\-_]{30,}"),
    re.compile(r"(sk_(?:live|test)_)[A-Za-z0-9]{8,}"),
    re.compile(r"(AKIA)[A-Z0-9]{12,}"),
    re.compile(r"(ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9]{30,}"),
    re.compile(r"(xai-)[A-Za-z0-9]{20,}"),
    # Generic export KEY=value in shell output
    re.compile(
        r"((?:API_KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|AUTH)[\w]*\s*=\s*)[^\s'\"]+",
        re.IGNORECASE,
    ),
    # Key-value in JSON-like output (captures closing quote to preserve valid JSON)
    re.compile(
        r'("(?:api_?key|secret|token|password|credential|auth)[^"]*"\s*:\s*")[^"]{8,}(")',
        re.IGNORECASE,
    ),
]


def redact_secrets(text: str) -> str:
    """Mask potential secrets/tokens in text before persisting to incident files."""
    result = text
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub(
            lambda m: m.group(1) + "<REDACTED>" + (m.group(2) if m.lastindex and m.lastindex >= 2 else ""),
            result,
        )
    return result


def run_git(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=6,
            check=False,
        )
    except Exception:
        return ""
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    if out:
        return out
    return err


def collect_git_context(cwd: Path) -> dict[str, str]:
    repo = WORKSPACE if (WORKSPACE / ".git").exists() else cwd
    return {
        "repo": str(repo),
        "branch": run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo),
        "head": run_git(["rev-parse", "--short", "HEAD"], repo),
        "status": run_git(["status", "--short"], repo),
    }


# ============================================================
# Failure Classification
# ============================================================
# Built-in rules. Add your own patterns by appending to this list
# or loading from a JSON config file.

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


def classify_failure(command: str, merged_output: str) -> dict[str, Any]:
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
        m = re.search(r"No module named ['\"]?([A-Za-z0-9._-]+)['\"]?", merged_output, re.IGNORECASE)
        if m:
            details["missing_python_module"] = m.group(1)
    elif cause_id == "node_module_missing":
        m = re.search(r"Cannot find module ['\"]([^'\"]+)['\"]", merged_output, re.IGNORECASE)
        if m:
            details["missing_node_module"] = m.group(1)
    elif cause_id == "path_missing":
        m = re.search(r"No such file or directory[: ]+['\"]?([^'\n\"]+)['\"]?", merged_output, re.IGNORECASE)
        if m:
            details["missing_path"] = m.group(1)

    prevention_actions: list[dict[str, str]] = []
    standardization_actions: list[dict[str, str]] = []

    if cause_id == "command_not_found":
        missing = details.get("missing_command", "UNKNOWN_COMMAND")
        prevention_actions = [
            {"level": "L1", "action": f"Add existence check for `{missing}` before execution"},
            {"level": "L2", "action": "Add required command validation to CI preflight"},
            {"level": "L3", "action": "Document required commands in setup instructions"},
        ]
        standardization_actions = [{"type": "required_command", "value": missing}]
    elif cause_id in {"python_module_missing", "node_module_missing"}:
        missing_dep = details.get("missing_python_module") or details.get("missing_node_module", "UNKNOWN_DEP")
        prevention_actions = [
            {"level": "L1", "action": f"Add dependency `{missing_dep}` existence check to startup"},
            {"level": "L2", "action": "Add dependency sync command to pipeline preflight"},
            {"level": "L3", "action": "Document dependency update procedure in runbook"},
        ]
        dtype = "required_python_module" if cause_id == "python_module_missing" else "required_node_module"
        standardization_actions = [{"type": dtype, "value": missing_dep}]
    elif cause_id == "path_missing":
        path_value = details.get("missing_path", "UNKNOWN_PATH")
        prevention_actions = [
            {"level": "L1", "action": f"Add existence check for required path `{path_value}`"},
            {"level": "L2", "action": "Add file existence checks to CI"},
            {"level": "L3", "action": "Add file placement rules to standards docs"},
        ]
        standardization_actions = [{"type": "required_path", "value": path_value}]
    elif cause_id == "permission_denied":
        prevention_actions = [
            {"level": "L1", "action": "Add execution permission check at startup"},
            {"level": "L2", "action": "Add explicit error on permission check failure"},
            {"level": "L3", "action": "Add permission rules to standards docs"},
        ]
        standardization_actions = [{"type": "permission_guard", "value": "execution_permissions"}]
    elif cause_id == "timeout":
        prevention_actions = [
            {"level": "L1", "action": "Add explicit timeout/retry boundaries for external dependencies"},
            {"level": "L2", "action": "Separate transient vs permanent failure detection"},
            {"level": "L3", "action": "Standardize retry policy"},
        ]
        standardization_actions = [{"type": "retry_policy", "value": "bounded_retry"}]
    else:
        prevention_actions = [
            {"level": "L3", "action": "Pattern-match similar failures and add detection rules"},
            {"level": "L4", "action": "Record interim workaround in operations notes"},
        ]

    # Enrich with domain classification + skill recommendations from packs
    recommended_skills: dict[str, Any] = {}
    _init_packs()
    if _pack_bundle is not None:
        try:
            from domain_classifier import recommend_skills as _recommend
            recommended_skills = _recommend(
                cause_id, command, merged_output,
                skill_map=_pack_bundle.skill_map,
                extra_keywords=_pack_bundle.extra_keywords,
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


def incident_id_from(command: str, at: str) -> str:
    digest = hashlib.sha256(f"{at}:{command}".encode("utf-8", errors="ignore")).hexdigest()[:8]
    t = datetime.datetime.fromisoformat(at.replace("Z", "+00:00"))
    return f"INC-{t.strftime('%Y%m%d-%H%M%S')}-{digest}"


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
    standard_md.write_text(render_standard_registry_markdown(registry), encoding="utf-8")

    result["applied"] = added > 0
    result["applied_count"] = added
    result["rollback_ready"] = True
    result["backup_file"] = str(backup_file)
    return result


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
    lines.append(f"- root_cause: `{analysis.get('cause_label', '')}` ({analysis.get('confidence', 0):.2f})")
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
            lines.append(f"- **[primary]** `{skill.get('ref', '')}`: {skill.get('description', '')}")
        for skill in rec.get("secondary", []):
            lines.append(f"- [secondary] `{skill.get('ref', '')}`: {skill.get('description', '')}")
        lines.append("")

    lines.append("## Standardization")
    lines.append(f"- auto_applied: `{standardization_result.get('applied', False)}`")
    lines.append(f"- applied_count: `{standardization_result.get('applied_count', 0)}`")
    lines.append(f"- rollback_ready: `{standardization_result.get('rollback_ready', False)}`")
    backup_file = standardization_result.get("backup_file", "")
    if backup_file:
        lines.append(f"- rollback_backup: `{backup_file}`")
    for item in analysis.get("standardization_actions", []):
        lines.append(f"- rule: `{item.get('type','')}` = `{item.get('value','')}`")
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
    lines.append("- close: `.claude/hooks/tps-andon-control.sh close \"<reason>\"`")
    lines.append(f"- rollback: `.claude/hooks/tps-andon-control.sh rollback {incident_id}`")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
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
    lines = [base, "", "## Close Summary", f"- closed_at: {now_utc()}", f"- close_reason: {reason}", ""]
    final.write_text("\n".join(lines), encoding="utf-8")
    return final


def open_from_payload() -> int:
    ensure_dirs()
    payload = get_payload_from_env()
    if not payload:
        print_empty()
        return 0

    tool_name = payload.get("tool_name")
    if isinstance(tool_name, str) and tool_name and tool_name != "Bash":
        print_empty()
        return 0

    command = get_command(payload)
    if not command:
        print_empty()
        return 0
    if is_tolerant_command(command):
        print_empty()
        return 0

    exit_code = derive_exit_code(payload)
    if exit_code is None or exit_code == 0:
        print_empty()
        return 0
    if is_readonly_failure(command):
        print_empty()
        return 0

    andon = load_json(ANDON_FILE)
    is_existing_open = bool(
        andon and andon.get("status") == "open" and andon.get("incident_id")
    )

    opened_at = now_utc()
    incident_id = (
        andon.get("incident_id", "")
        if is_existing_open
        else incident_id_from(command, opened_at)
    )
    incident_dir = INCIDENTS_DIR / incident_id
    incident_dir.mkdir(parents=True, exist_ok=True)

    merged_output = redact_secrets(safe_snippet("\n".join(collect_text_blobs(payload))))
    workdir = Path(get_workdir(payload))
    git_ctx = collect_git_context(workdir)

    event_record = {
        "at": now_utc(),
        "command": redact_secrets(command),
        "exit_code": exit_code,
        "output_snippet": merged_output,
    }
    append_json_event(incident_dir / "events.json", event_record)

    evidence = load_json(incident_dir / "evidence.json")
    failures = evidence.get("failures")
    if not isinstance(failures, list):
        failures = []
    failures.append(event_record)
    evidence = {
        "incident_id": incident_id,
        "opened_at": evidence.get("opened_at", opened_at),
        "last_updated_at": now_utc(),
        "workspace": str(workdir),
        "command": redact_secrets(command),
        "exit_code": exit_code,
        "output_snippet": merged_output,
        "git": git_ctx,
        "failures": failures,
    }
    write_json(incident_dir / "evidence.json", evidence)

    analysis = classify_failure(command, merged_output)
    analysis["updated_at"] = now_utc()
    write_json(incident_dir / "analysis.json", analysis)

    standardization_result: dict[str, Any] = {
        "applied": False,
        "applied_count": 0,
        "rollback_ready": False,
        "backup_file": "",
    }
    confidence = float(analysis.get("confidence", 0.0))
    if not is_existing_open and confidence >= CONFIDENCE_AUTOMATION_THRESHOLD:
        standardization_result = apply_standardization(
            incident_id,
            analysis.get("standardization_actions", []),
            incident_dir,
        )

    actions_data = {
        "incident_id": incident_id,
        "auto_generated_at": now_utc(),
        "prevention_actions": analysis.get("prevention_actions", []),
        "standardization_actions": analysis.get("standardization_actions", []),
        "standardization_result": standardization_result,
        "manual_review_required": confidence < CONFIDENCE_MANUAL_REVIEW_THRESHOLD,
    }
    if actions_data["manual_review_required"]:
        actions_data["manual_review_note"] = (
            "low confidence root-cause estimation; human confirmation required before close"
        )
    write_json(incident_dir / "actions.json", actions_data)

    report_path = write_incident_report(
        incident_id, incident_dir, evidence, analysis, actions_data, standardization_result,
    )

    # Redact secrets from the raw payload before persisting
    write_json(
        incident_dir / "payload-latest.json",
        json.loads(redact_secrets(json.dumps(payload, ensure_ascii=False, default=str))),
    )
    andon_state = {
        "status": "open",
        "incident_id": incident_id,
        "opened_at": andon.get("opened_at", opened_at) if is_existing_open else opened_at,
        "updated_at": now_utc(),
        "command": redact_secrets(command),
        "exit_code": exit_code,
        "report_path": str(report_path),
        "incident_dir": str(incident_dir),
        "rollback_command": f".claude/hooks/tps-andon-control.sh rollback {incident_id}",
    }
    write_json(ANDON_FILE, andon_state)

    if confidence < CONFIDENCE_MANUAL_REVIEW_THRESHOLD:
        message = (
            f"[TPS/ANDON] Anomaly detected — line stopped. incident={incident_id} "
            f"(root cause confidence {confidence:.2f} — manual review required). "
            f"Report: {report_path} "
            "Run `/tps-kaizen andon <problem>` then `/tps-kaizen five-whys <problem>`, "
            'then `.claude/hooks/tps-andon-control.sh close "manual-approved: <reason>"`.'
        )
    else:
        message = (
            f"[TPS/ANDON] Anomaly detected — line stopped. incident={incident_id} "
            f"(root cause confidence {confidence:.2f}). "
            f"Auto-standardization: {standardization_result.get('applied', False)} "
            f"Report: {report_path} "
            'After fix: `.claude/hooks/tps-andon-control.sh close "<reason>"`.'
        )

    print_hook_context(message, block=True)
    return 0


def status() -> int:
    ensure_dirs()
    andon = load_json(ANDON_FILE)
    if andon and andon.get("status") == "open":
        print("ANDON: OPEN")
        print(json.dumps(andon, ensure_ascii=False, indent=2))
        return 0
    print("ANDON: CLEAR")
    return 0


def close_incident(reason: str) -> int:
    ensure_dirs()
    andon = load_json(ANDON_FILE)
    if not andon or andon.get("status") != "open":
        print("ANDON already clear")
        return 0

    incident_id = str(andon.get("incident_id", "")).strip()
    if not incident_id:
        print("ANDON close blocked: incident_id missing")
        return 1
    incident_dir = INCIDENTS_DIR / incident_id
    required = [
        incident_dir / "evidence.json",
        incident_dir / "analysis.json",
        incident_dir / "actions.json",
        incident_dir / "report.md",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("ANDON close blocked: required artifacts are missing")
        for item in missing:
            print(f"- {item}")
        return 1

    analysis = load_json(incident_dir / "analysis.json")
    confidence = float(analysis.get("confidence", 0.0))
    if confidence < CONFIDENCE_MANUAL_REVIEW_THRESHOLD and "manual-approved" not in reason.lower():
        print(
            "ANDON close blocked: low-confidence incident requires manual-approved marker in close reason"
        )
        print('Example: .claude/hooks/tps-andon-control.sh close "manual-approved: verified root cause"')
        return 1

    final_report = update_final_report_on_close(incident_id, incident_dir, reason)
    archive_file = HISTORY_DIR / (
        f"andon-closed-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    archive_payload = {
        "andon": andon,
        "closed_at": now_utc(),
        "close_reason": reason,
        "final_report": str(final_report),
    }
    write_json(archive_file, archive_payload)
    try:
        ANDON_FILE.unlink()
    except FileNotFoundError:
        pass

    print(f"ANDON closed: {reason}")
    print(f"Incident: {incident_id}")
    print(f"Final report: {final_report}")
    print(f"Archive: {archive_file}")
    print(f"Rollback: .claude/hooks/tps-andon-control.sh rollback {incident_id}")
    return 0


def find_incident_for_rollback(target: str) -> str | None:
    if target and target != "latest":
        return target
    andon = load_json(ANDON_FILE)
    if andon and andon.get("status") == "open" and andon.get("incident_id"):
        return str(andon["incident_id"])

    candidates = sorted(
        INCIDENTS_DIR.glob("INC-*"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if candidates:
        return candidates[0].name
    return None


def rollback_incident(target: str) -> int:
    ensure_dirs()
    incident_id = find_incident_for_rollback(target)
    if not incident_id:
        print("Rollback skipped: no incident found")
        return 1

    incident_dir = INCIDENTS_DIR / incident_id
    backup = incident_dir / "rollback" / "standardization-registry.before.json"
    if not backup.exists():
        print(f"Rollback skipped: no rollback snapshot for {incident_id}")
        return 1

    before = load_json(backup)
    write_json(STANDARD_REGISTRY, before)
    md = KAIZEN_DIR / "STANDARDIZED_RULES.md"
    md.write_text(render_standard_registry_markdown(before), encoding="utf-8")

    rollback_meta = {
        "incident_id": incident_id,
        "rolled_back_at": now_utc(),
        "restored_from": str(backup),
    }
    write_json(incident_dir / "rollback-executed.json", rollback_meta)
    print(f"Rollback completed for {incident_id}")
    print(f"Restored: {backup}")
    return 0


def check_output_safety(text: str) -> int:
    """Check text against Pack 0 Output Safety Guard. Returns 0 if safe, 1 if triggered."""
    _init_packs()
    if _safety_guard is None:
        print("Pack 0 (Output Safety Guard) not available — PyYAML may be missing")
        return 2
    result = _safety_guard.check(text)
    if not result.triggered:
        print(json.dumps({"safe": True}, ensure_ascii=False))
        return 0
    output = {
        "safe": False,
        "level": result.level.value if result.level else "",
        "category": result.category.value if result.category else "",
        "reason": result.reason,
    }
    if result.disclaimer:
        output["disclaimer"] = result.disclaimer
    if result.professional_referral:
        output["professional_referral"] = result.professional_referral
    if result.helpline:
        output["helpline"] = result.helpline
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1


def usage() -> int:
    print(
        "Usage:\n"
        "  tps-kaizen-runtime.py open-from-payload   # read payload JSON from INPUT_JSON env\n"
        "  tps-kaizen-runtime.py status\n"
        "  tps-kaizen-runtime.py close <reason>\n"
        "  tps-kaizen-runtime.py rollback [incident_id|latest]\n"
        "  tps-kaizen-runtime.py check-output-safety <text>  # Pack 0 safety check"
    )
    return 2


def main() -> int:
    if len(sys.argv) < 2:
        return usage()
    cmd = sys.argv[1]
    if cmd == "open-from-payload":
        return open_from_payload()
    if cmd == "status":
        return status()
    if cmd == "close":
        reason = sys.argv[2] if len(sys.argv) >= 3 else "manual"
        return close_incident(reason)
    if cmd == "rollback":
        target = sys.argv[2] if len(sys.argv) >= 3 else "latest"
        return rollback_incident(target)
    if cmd == "check-output-safety":
        text = sys.argv[2] if len(sys.argv) >= 3 else sys.stdin.read()
        return check_output_safety(text)
    return usage()


if __name__ == "__main__":
    sys.exit(main())
