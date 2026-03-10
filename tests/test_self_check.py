#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for ANDON close self-check validation (SCK-01 .. SCK-05).

Validates that close_incident rejects incomplete, empty, or malformed
artifacts — addressing the 'LLM Self-Report' problem where tool calls
are skipped but artifacts are reported as present.
"""

import importlib.util
import json
import sys
from pathlib import Path

# Ensure hooks/ is on sys.path
HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import pytest  # noqa: E402

# ---------------------------------------------------------------------------
# Importlib shim for hyphenated module name (tps-kaizen-runtime.py)
# ---------------------------------------------------------------------------
_spec = importlib.util.spec_from_file_location(
    "tps_kaizen_runtime",
    HOOKS_DIR / "tps-kaizen-runtime.py",
)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

_validate_artifact_size = _mod._validate_artifact_size
_validate_json_parse = _mod._validate_json_parse
_validate_report_headers = _mod._validate_report_headers
_validate_evidence_keys = _mod._validate_evidence_keys
validate_close_artifacts = _mod.validate_close_artifacts


# ============================================================
# Helpers
# ============================================================


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_valid_incident(incident_dir: Path) -> None:
    """Create a minimal valid set of incident artifacts."""
    evidence = {
        "incident_id": "INC-TEST",
        "command": "make build",
        "exit_code": 2,
        "output_snippet": "error: build failed",
    }
    analysis = {
        "cause_label": "build_failure",
        "confidence": 0.85,
    }
    actions = {
        "incident_id": "INC-TEST",
        "prevention_actions": [],
    }
    report = (
        "# Incident Report\n\n"
        "## Summary\n\nBuild failed.\n\n"
        "## Evidence\n\nSee evidence.json.\n"
    )

    _write(incident_dir / "evidence.json", json.dumps(evidence))
    _write(incident_dir / "analysis.json", json.dumps(analysis))
    _write(incident_dir / "actions.json", json.dumps(actions))
    _write(incident_dir / "report.md", report)


# ============================================================
# SCK-01: File size check
# ============================================================


class TestArtifactSize:
    def test_empty_file_rejected(self, tmp_path):
        p = tmp_path / "evidence.json"
        p.write_text("", encoding="utf-8")
        err = _validate_artifact_size(p)
        assert err is not None
        assert "empty or too small" in err
        assert "(0 bytes" in err

    def test_small_file_rejected(self, tmp_path):
        p = tmp_path / "analysis.json"
        p.write_text("{}", encoding="utf-8")  # 2 bytes
        err = _validate_artifact_size(p)
        assert err is not None
        assert "empty or too small" in err

    def test_minimum_size_passes(self, tmp_path):
        p = tmp_path / "actions.json"
        # 10 bytes exactly: {"a": "b"}
        content = '{"a": "b"}'
        assert len(content.encode("utf-8")) >= 10
        p.write_text(content, encoding="utf-8")
        err = _validate_artifact_size(p)
        assert err is None

    def test_nonexistent_file_returns_none(self, tmp_path):
        p = tmp_path / "missing.json"
        err = _validate_artifact_size(p)
        assert err is None


# ============================================================
# SCK-02: JSON parse check
# ============================================================


class TestJsonParse:
    def test_invalid_json_rejected(self, tmp_path):
        p = tmp_path / "evidence.json"
        p.write_text("{not valid json}", encoding="utf-8")
        err = _validate_json_parse(p)
        assert err is not None
        assert "invalid JSON" in err

    def test_truncated_json_rejected(self, tmp_path):
        p = tmp_path / "analysis.json"
        p.write_text('{"key": "value"', encoding="utf-8")
        err = _validate_json_parse(p)
        assert err is not None
        assert "invalid JSON" in err

    def test_valid_json_passes(self, tmp_path):
        p = tmp_path / "actions.json"
        p.write_text('{"key": "value"}', encoding="utf-8")
        err = _validate_json_parse(p)
        assert err is None

    def test_nonexistent_file_returns_none(self, tmp_path):
        p = tmp_path / "missing.json"
        err = _validate_json_parse(p)
        assert err is None


# ============================================================
# SCK-03: report.md header count
# ============================================================


class TestReportHeaders:
    def test_no_headers_rejected(self, tmp_path):
        p = tmp_path / "report.md"
        p.write_text("Just some text without any headers.\n", encoding="utf-8")
        err = _validate_report_headers(p)
        assert err is not None
        assert "missing required section headers" in err
        assert "found 0" in err

    def test_one_header_rejected(self, tmp_path):
        p = tmp_path / "report.md"
        p.write_text("# Title\n\n## Only one\n\nContent.\n", encoding="utf-8")
        err = _validate_report_headers(p)
        assert err is not None
        assert "found 1" in err

    def test_two_headers_pass(self, tmp_path):
        p = tmp_path / "report.md"
        p.write_text(
            "# Title\n\n## Summary\n\nText.\n\n## Evidence\n\nMore.\n",
            encoding="utf-8",
        )
        err = _validate_report_headers(p)
        assert err is None

    def test_many_headers_pass(self, tmp_path):
        p = tmp_path / "report.md"
        p.write_text(
            "# Title\n\n## A\n\n## B\n\n## C\n\n## D\n",
            encoding="utf-8",
        )
        err = _validate_report_headers(p)
        assert err is None

    def test_h1_not_counted_as_h2(self, tmp_path):
        p = tmp_path / "report.md"
        p.write_text("# Title\n\n# Another Title\n", encoding="utf-8")
        err = _validate_report_headers(p)
        assert err is not None
        assert "found 0" in err

    def test_nonexistent_file_returns_none(self, tmp_path):
        p = tmp_path / "report.md"
        err = _validate_report_headers(p)
        assert err is None


# ============================================================
# SCK-04: evidence.json required keys
# ============================================================


class TestEvidenceKeys:
    def test_missing_command_rejected(self, tmp_path):
        p = tmp_path / "evidence.json"
        data = {"exit_code": 1, "output_snippet": "error"}
        p.write_text(json.dumps(data), encoding="utf-8")
        err = _validate_evidence_keys(p)
        assert err is not None
        assert "'command'" in err

    def test_missing_exit_code_rejected(self, tmp_path):
        p = tmp_path / "evidence.json"
        data = {"command": "make", "output_snippet": "error"}
        p.write_text(json.dumps(data), encoding="utf-8")
        err = _validate_evidence_keys(p)
        assert err is not None
        assert "'exit_code'" in err

    def test_missing_output_snippet_rejected(self, tmp_path):
        p = tmp_path / "evidence.json"
        data = {"command": "make", "exit_code": 1}
        p.write_text(json.dumps(data), encoding="utf-8")
        err = _validate_evidence_keys(p)
        assert err is not None
        assert "'output_snippet'" in err

    def test_all_keys_present_passes(self, tmp_path):
        p = tmp_path / "evidence.json"
        data = {"command": "make", "exit_code": 1, "output_snippet": "err"}
        p.write_text(json.dumps(data), encoding="utf-8")
        err = _validate_evidence_keys(p)
        assert err is None

    def test_invalid_json_returns_none(self, tmp_path):
        """Invalid JSON is caught by _validate_json_parse, not here."""
        p = tmp_path / "evidence.json"
        p.write_text("{broken", encoding="utf-8")
        err = _validate_evidence_keys(p)
        assert err is None

    def test_nonexistent_file_returns_none(self, tmp_path):
        p = tmp_path / "evidence.json"
        err = _validate_evidence_keys(p)
        assert err is None


# ============================================================
# SCK-05: Integration — validate_close_artifacts
# ============================================================


class TestValidateCloseArtifacts:
    def test_valid_artifacts_pass(self, tmp_path):
        _make_valid_incident(tmp_path)
        errors = validate_close_artifacts(tmp_path)
        assert errors == []

    def test_empty_evidence_rejected(self, tmp_path):
        _make_valid_incident(tmp_path)
        # Overwrite evidence.json with empty file
        (tmp_path / "evidence.json").write_text("", encoding="utf-8")
        errors = validate_close_artifacts(tmp_path)
        assert len(errors) >= 1
        assert any("empty or too small" in e for e in errors)

    def test_invalid_json_analysis_rejected(self, tmp_path):
        _make_valid_incident(tmp_path)
        (tmp_path / "analysis.json").write_text("{not json}", encoding="utf-8")
        errors = validate_close_artifacts(tmp_path)
        assert any("invalid JSON" in e for e in errors)

    def test_report_no_headers_rejected(self, tmp_path):
        _make_valid_incident(tmp_path)
        (tmp_path / "report.md").write_text(
            "No headers here.\n", encoding="utf-8"
        )
        errors = validate_close_artifacts(tmp_path)
        assert any("missing required section headers" in e for e in errors)

    def test_evidence_missing_keys_rejected(self, tmp_path):
        _make_valid_incident(tmp_path)
        # Overwrite evidence with valid JSON but missing required keys
        (tmp_path / "evidence.json").write_text(
            json.dumps({"incident_id": "INC-TEST", "extra": "data_padding"}),
            encoding="utf-8",
        )
        errors = validate_close_artifacts(tmp_path)
        assert any("missing required key" in e for e in errors)

    def test_multiple_errors_collected(self, tmp_path):
        """When multiple artifacts are bad, all errors are reported."""
        _make_valid_incident(tmp_path)
        # Empty all JSON files
        (tmp_path / "evidence.json").write_text("", encoding="utf-8")
        (tmp_path / "analysis.json").write_text("", encoding="utf-8")
        (tmp_path / "actions.json").write_text("", encoding="utf-8")
        (tmp_path / "report.md").write_text("No headers.\n", encoding="utf-8")
        errors = validate_close_artifacts(tmp_path)
        # Should have at least: 3 size errors + report header error
        assert len(errors) >= 4
