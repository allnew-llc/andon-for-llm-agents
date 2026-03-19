#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""tps-kaizen-runtime.py — ANDON Runtime Engine for LLM Agent Hooks

CLI dispatcher and command orchestration. Core logic is split into:
  kaizen_core.py      — configuration, JSON I/O, text sanitization
  kaizen_payload.py   — payload extraction, git context
  kaizen_classify.py  — failure classification rules
  kaizen_incident.py  — standardization registry, incident reports

Commands:
  open-from-payload   detect failure and open/update incident automatically
  status              print current ANDON status
  close <reason>      close ANDON when required artifacts are present
  rollback [id]       restore auto-standardization state for an incident
  check-output-safety check text against Pack 0
  analysis-paralysis  detect consecutive reads without code changes
  context-check       increment tool call counter and warn on degradation

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import datetime
import fcntl
import json
import os
import sys
from pathlib import Path
from typing import Any

from kaizen_classify import classify_failure, get_action_level
from kaizen_core import (
    ANALYSIS_COUNTER_FILE,
    ANDON_FILE,
    CONFIDENCE_AUTOMATION_THRESHOLD,
    CONFIDENCE_MANUAL_REVIEW_THRESHOLD,
    HISTORY_DIR,
    INCIDENTS_DIR,
    KAIZEN_DIR,
    STANDARD_REGISTRY,
    STATE_DIR,
    WORKSPACE,
    append_json_event,
    ensure_dirs,
    load_json,
    now_utc,
    print_empty,
    print_hook_context,
    redact_secrets,
    safe_snippet,
    write_json,
)
from kaizen_incident import (
    _write_text_secure,
    apply_standardization,
    enrich_analysis_for_level,
    incident_id_from,
    render_standard_registry_markdown,
    update_final_report_on_close,
    write_incident_report,
)
from kaizen_payload import (
    collect_git_context,
    collect_text_blobs,
    derive_exit_code,
    get_command,
    get_payload_from_env,
    get_workdir,
    is_readonly_failure,
    is_tolerant_command,
)

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
        from pack_loader import PackBundle, PackLoader

        _safety_guard = OutputSafetyGuard()

        packs_dir = Path(__file__).parent.parent / "packs"
        loader = PackLoader(pack0_available=True)
        if packs_dir.is_dir():
            _pack_bundle = loader.load_all(packs_dir)
            if _pack_bundle.safety_extensions:
                _safety_guard.merge_pack_extensions(
                    _pack_bundle.safety_extensions
                )
        else:
            _pack_bundle = PackBundle.empty()
    except ImportError:
        _safety_guard = None
        _pack_bundle = None


# === Gotcha Surfacer (lazy-loaded) ===
_surfacer_loaded = False


def _init_surfacer() -> None:
    """Lazy-load the Gotcha surfacer. Failure is non-fatal — ANDON must not block."""
    global _surfacer_loaded
    if _surfacer_loaded:
        return
    try:
        from gotcha_surfacer import surface_gotchas as _sf  # noqa: F811

        globals()["_surface_gotchas"] = _sf
    except ImportError:
        globals()["_surface_gotchas"] = None
    _surfacer_loaded = True


# === Self-Check Validation (SCK-01 .. SCK-05) ===


_MIN_JSON_SIZE = 10  # bytes
_MIN_REPORT_HEADERS = 2
_EVIDENCE_REQUIRED_KEYS = ("command", "exit_code", "output_snippet")


def _validate_artifact_size(path: Path) -> str | None:
    """SCK-01: Reject JSON artifacts that are empty or too small."""
    if not path.exists():
        return None  # existence check handled separately
    size = path.stat().st_size
    if size < _MIN_JSON_SIZE:
        return (
            f"[ANDON] Close rejected: {path.name} is empty or too small "
            f"({size} bytes, minimum {_MIN_JSON_SIZE})"
        )
    return None


def _validate_json_parse(path: Path) -> str | None:
    """SCK-02: Reject artifacts that contain invalid JSON."""
    if not path.exists():
        return None
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        return f"[ANDON] Close rejected: {path.name} contains invalid JSON"
    return None


def _validate_report_headers(path: Path) -> str | None:
    """SCK-03: report.md must contain at least 2 '## ' section headers."""
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    header_count = sum(
        1 for line in text.splitlines() if line.startswith("## ")
    )
    if header_count < _MIN_REPORT_HEADERS:
        return (
            f"[ANDON] Close rejected: report.md missing required section "
            f"headers (found {header_count}, minimum {_MIN_REPORT_HEADERS})"
        )
    return None


def _validate_evidence_keys(path: Path) -> str | None:
    """SCK-04: evidence.json must contain required top-level keys."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        return None  # parse error caught by _validate_json_parse
    if not isinstance(data, dict):
        return (
            f"[ANDON] Close rejected: {path.name} contains invalid JSON"
        )
    for key in _EVIDENCE_REQUIRED_KEYS:
        if key not in data:
            return (
                f"[ANDON] Close rejected: evidence.json missing "
                f"required key '{key}'"
            )
    return None


def validate_close_artifacts(incident_dir: Path) -> list[str]:
    """Run all self-check validations. Returns list of error messages."""
    errors: list[str] = []

    json_artifacts = [
        incident_dir / "evidence.json",
        incident_dir / "analysis.json",
        incident_dir / "actions.json",
    ]

    # SCK-01: file size
    for path in json_artifacts:
        err = _validate_artifact_size(path)
        if err:
            errors.append(err)

    # SCK-02: JSON parse
    for path in json_artifacts:
        err = _validate_json_parse(path)
        if err:
            errors.append(err)

    # SCK-03: report.md headers
    err = _validate_report_headers(incident_dir / "report.md")
    if err:
        errors.append(err)

    # SCK-04: evidence.json required keys
    err = _validate_evidence_keys(incident_dir / "evidence.json")
    if err:
        errors.append(err)

    return errors


# === Commands ===


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

    merged_output = redact_secrets(
        safe_snippet("\n".join(collect_text_blobs(payload)))
    )
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

    _init_packs()
    analysis = classify_failure(
        command, merged_output,
        init_packs=_init_packs,
        pack_bundle=_pack_bundle,
    )
    analysis["updated_at"] = now_utc()
    action_level = int(analysis.get("action_level", 2))

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

    actions_data: dict[str, Any] = {
        "incident_id": incident_id,
        "auto_generated_at": now_utc(),
        "prevention_actions": analysis.get("prevention_actions", []),
        "standardization_actions": analysis.get("standardization_actions", []),
        "standardization_result": standardization_result,
        "manual_review_required": confidence < CONFIDENCE_MANUAL_REVIEW_THRESHOLD,
        "action_level": action_level,
    }
    if actions_data["manual_review_required"]:
        actions_data["manual_review_note"] = (
            "low confidence root-cause estimation; "
            "human confirmation required before close"
        )

    # Enrich analysis and actions with level-specific fields
    enrich_analysis_for_level(analysis, actions_data)

    write_json(incident_dir / "analysis.json", analysis)
    write_json(incident_dir / "actions.json", actions_data)

    report_path = write_incident_report(
        incident_id, incident_dir, evidence, analysis,
        actions_data, standardization_result,
    )

    # Redact secrets from the raw payload before persisting
    write_json(
        incident_dir / "payload-latest.json",
        json.loads(
            redact_secrets(json.dumps(payload, ensure_ascii=False, default=str))
        ),
    )

    # --- Level-based response ---
    # Level 1: Auto-fix only, log event but don't open ANDON
    if action_level == 1:
        # Log the incident artifacts but don't set ANDON state to open
        print_empty()
        return 0

    # Level 2-4: Open ANDON (existing + new behavior)
    andon_state: dict[str, Any] = {
        "status": "open",
        "incident_id": incident_id,
        "opened_at": (
            andon.get("opened_at", opened_at) if is_existing_open else opened_at
        ),
        "updated_at": now_utc(),
        "command": redact_secrets(command),
        "exit_code": exit_code,
        "report_path": str(report_path),
        "incident_dir": str(incident_dir),
        "action_level": action_level,
        "rollback_command": (
            f".claude/hooks/tps-andon-control.sh rollback {incident_id}"
        ),
    }
    write_json(ANDON_FILE, andon_state)

    # --- Gotcha auto-surfacing ---
    _init_surfacer()
    gotcha_context = ""
    sf = globals().get("_surface_gotchas")
    if sf is not None:
        gotchas_dir = WORKSPACE / "gotchas"
        packs_dir_path = WORKSPACE / "packs"
        gotcha_context = sf(
            merged_output,
            gotchas_dir,
            packs_dir=packs_dir_path if packs_dir_path.is_dir() else None,
        )

    cause_id = analysis.get("cause_id", "unknown_failure")

    if action_level == 4:
        # Level 4: Block + require user approval
        message = (
            f"[ANDON/Level-4] {cause_id} requires human approval "
            f"before proceeding. incident={incident_id} "
            f"Report: {report_path} "
            "Use '.claude/hooks/tps-andon-control.sh close' after review."
        )
        if gotcha_context:
            message += f" {gotcha_context}"
        print_hook_context(message, block=True)
        return 0

    if action_level == 3:
        # Level 3: ANDON open + inject proposed fix
        proposed_fix = analysis.get("proposed_fix", "review required")
        message = (
            f"[ANDON/Level-3] Proposed fix for {cause_id}: "
            f"{proposed_fix}. "
            f"incident={incident_id} "
            f"Report: {report_path} "
            "Review and apply or report if insufficient."
        )
        if gotcha_context:
            message += f" {gotcha_context}"
        print_hook_context(message, block=True)
        return 0

    # Level 2: Existing behavior (ANDON open + auto-standardize)
    if confidence < CONFIDENCE_MANUAL_REVIEW_THRESHOLD:
        message = (
            f"[TPS/ANDON] Anomaly detected — line stopped. "
            f"incident={incident_id} "
            f"(root cause confidence {confidence:.2f} — manual review required). "
            f"Report: {report_path} "
            "Run `/tps-kaizen andon <problem>` then "
            "`/tps-kaizen five-whys <problem>`, "
            "then `.claude/hooks/tps-andon-control.sh close "
            '"manual-approved: <reason>"`.'
        )
    else:
        message = (
            f"[TPS/ANDON] Anomaly detected — line stopped. "
            f"incident={incident_id} "
            f"(root cause confidence {confidence:.2f}). "
            f"Auto-standardization: "
            f"{standardization_result.get('applied', False)} "
            f"Report: {report_path} "
            'After fix: `.claude/hooks/tps-andon-control.sh close "<reason>"`.'
        )
    if gotcha_context:
        message += f" {gotcha_context}"

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
    incident_dir = (INCIDENTS_DIR / incident_id).resolve()
    if not str(incident_dir).startswith(str(INCIDENTS_DIR.resolve())):
        print("Invalid incident ID: path traversal detected")
        return 1
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

    # SCK-01..SCK-04: Self-check validation of artifact contents
    self_check_errors = validate_close_artifacts(incident_dir)
    if self_check_errors:
        for err in self_check_errors:
            print(err)
        return 1

    analysis = load_json(incident_dir / "analysis.json")
    confidence = float(analysis.get("confidence", 0.0))
    if (
        confidence < CONFIDENCE_MANUAL_REVIEW_THRESHOLD
        and "manual-approved" not in reason.lower()
    ):
        print(
            "ANDON close blocked: low-confidence incident requires "
            "manual-approved marker in close reason"
        )
        print(
            'Example: .claude/hooks/tps-andon-control.sh close '
            '"manual-approved: verified root cause"'
        )
        return 1

    final_report = update_final_report_on_close(
        incident_id, incident_dir, reason
    )
    archive_file = HISTORY_DIR / (
        "andon-closed-"
        f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        ".json"
    )
    archive_payload = {
        "andon": andon,
        "closed_at": now_utc(),
        "close_reason": reason,
        "final_report": str(final_report),
    }
    write_json(archive_file, archive_payload)
    ANDON_FILE.unlink(missing_ok=True)

    print(f"ANDON closed: {reason}")
    print(f"Incident: {incident_id}")
    print(f"Final report: {final_report}")
    print(f"Archive: {archive_file}")
    print(
        f"Rollback: .claude/hooks/tps-andon-control.sh rollback {incident_id}"
    )
    return 0


def find_incident_for_rollback(target: str) -> str | None:
    if target and target != "latest":
        return target
    andon = load_json(ANDON_FILE)
    if andon and andon.get("status") == "open" and andon.get("incident_id"):
        return str(andon["incident_id"])

    candidates = sorted(
        INCIDENTS_DIR.glob("INC-*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
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

    incident_dir = (INCIDENTS_DIR / incident_id).resolve()
    if not str(incident_dir).startswith(str(INCIDENTS_DIR.resolve())):
        print("Invalid incident ID: path traversal detected")
        return 1
    backup = incident_dir / "rollback" / "standardization-registry.before.json"
    if not backup.exists():
        print(f"Rollback skipped: no rollback snapshot for {incident_id}")
        return 1

    before = load_json(backup)
    write_json(STANDARD_REGISTRY, before)
    md = KAIZEN_DIR / "STANDARDIZED_RULES.md"
    _write_text_secure(md, render_standard_registry_markdown(before))

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
    """Check text against Pack 0 Output Safety Guard."""
    _init_packs()
    if _safety_guard is None:
        print(
            "Pack 0 (Output Safety Guard) not available — "
            "PyYAML may be missing"
        )
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


# === Analysis Paralysis Detection ===

# Tools that count as "read" operations (no code changes)
_READ_TOOLS = frozenset({"Read", "Grep", "Glob"})
# Tools that count as "write" operations (code changes)
_WRITE_TOOLS = frozenset({"Edit", "Write"})

# Thresholds
_NORMAL_THRESHOLD = 5
_ANDON_OPEN_THRESHOLD = 3


def analysis_paralysis(tool_name: str, exit_code: int | None) -> int:
    """Detect analysis paralysis: too many consecutive reads without writes.

    Increments a counter for Read/Grep/Glob calls, resets on
    Edit/Write/Bash(exit 0). When the counter exceeds the threshold,
    returns a warning message via hook context.

    Args:
        tool_name: The name of the tool that was just invoked.
        exit_code: The exit code of the tool (relevant for Bash).

    Returns:
        0 on success.
    """
    ensure_dirs()

    path = ANALYSIS_COUNTER_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o640)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)

        raw = os.read(fd, 1_000_000)
        state: dict[str, Any] = {}
        if raw:
            try:
                state = json.loads(raw.decode("utf-8"))
            except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                state = {}

        if not state:
            state = {
                "consecutive_reads": 0,
                "last_write_at": "",
                "session_id": "",
            }

        # Determine whether this tool call is a read or write
        if tool_name in _READ_TOOLS:
            state["consecutive_reads"] = state.get("consecutive_reads", 0) + 1
        elif tool_name in _WRITE_TOOLS:
            state["consecutive_reads"] = 0
            state["last_write_at"] = now_utc()
        elif tool_name == "Bash":
            if exit_code is not None and exit_code == 0:
                state["consecutive_reads"] = 0
                state["last_write_at"] = now_utc()
            # Bash with non-zero exit does not reset (failed command)
        else:
            # Other tools (e.g., Skill, ToolSearch) — no effect
            pass

        os.lseek(fd, 0, os.SEEK_SET)
        os.ftruncate(fd, 0)
        os.write(fd, json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8"))

        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)

    consecutive = state.get("consecutive_reads", 0)

    # Determine threshold: lower when ANDON is already open
    andon = load_json(ANDON_FILE)
    andon_is_open = bool(
        andon and andon.get("status") == "open"
    )
    threshold = _ANDON_OPEN_THRESHOLD if andon_is_open else _NORMAL_THRESHOLD

    if consecutive >= threshold:
        message = (
            f"[ANDON] Analysis paralysis detected: {consecutive} consecutive "
            f"read operations without any code changes. "
            f"Write code or report a blocker."
        )
        print_hook_context(message, block=False)
        return 0

    print_empty()
    return 0


# === Context Quality Monitor ===


def context_check() -> int:
    """Increment tool call counter and warn on context degradation."""
    ensure_dirs()
    from context_monitor import increment_and_check

    result = increment_and_check(STATE_DIR)

    warning = result.get("warning")
    andon_warning = result.get("andon_warning")

    if warning or andon_warning:
        parts = [p for p in (warning, andon_warning) if p]
        message = " ".join(parts)
        print_hook_context(message, block=False)
        return 0

    print_empty()
    return 0


# === CLI ===


def usage() -> int:
    print(
        "Usage:\n"
        "  tps-kaizen-runtime.py open-from-payload   "
        "# read payload JSON from INPUT_JSON env\n"
        "  tps-kaizen-runtime.py status\n"
        "  tps-kaizen-runtime.py close <reason>\n"
        "  tps-kaizen-runtime.py rollback [incident_id|latest]\n"
        "  tps-kaizen-runtime.py check-output-safety <text>  "
        "# Pack 0 safety check\n"
        "  tps-kaizen-runtime.py analysis-paralysis <tool_name> [exit_code]  "
        "# analysis paralysis guard\n"
        "  tps-kaizen-runtime.py context-check  "
        "# context quality monitor"
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
    if cmd == "analysis-paralysis":
        if len(sys.argv) < 3:
            print("analysis-paralysis requires <tool_name>", file=sys.stderr)
            return usage()
        ap_tool = sys.argv[2]
        ap_exit: int | None = None
        if len(sys.argv) >= 4:
            try:
                ap_exit = int(sys.argv[3])
            except ValueError:
                ap_exit = None
        return analysis_paralysis(ap_tool, ap_exit)
    if cmd == "context-check":
        return context_check()
    return usage()


if __name__ == "__main__":
    sys.exit(main())
