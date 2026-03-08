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

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from typing import Any

from kaizen_classify import classify_failure
from kaizen_core import (
    ANDON_FILE,
    CONFIDENCE_AUTOMATION_THRESHOLD,
    CONFIDENCE_MANUAL_REVIEW_THRESHOLD,
    HISTORY_DIR,
    INCIDENTS_DIR,
    KAIZEN_DIR,
    STANDARD_REGISTRY,
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
    apply_standardization,
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
            "low confidence root-cause estimation; "
            "human confirmation required before close"
        )
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
    andon_state = {
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
        "rollback_command": (
            f".claude/hooks/tps-andon-control.sh rollback {incident_id}"
        ),
    }
    write_json(ANDON_FILE, andon_state)

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

    incident_dir = INCIDENTS_DIR / incident_id
    backup = incident_dir / "rollback" / "standardization-registry.before.json"
    if not backup.exists():
        print(f"Rollback skipped: no rollback snapshot for {incident_id}")
        return 1

    before = load_json(backup)
    write_json(STANDARD_REGISTRY, before)
    md = KAIZEN_DIR / "STANDARDIZED_RULES.md"
    md.write_text(
        render_standard_registry_markdown(before), encoding="utf-8"
    )

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
        "# Pack 0 safety check"
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
