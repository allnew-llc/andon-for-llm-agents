#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for hooks/gotcha_registry.py — Gotcha Registry schema, loader, and pack discovery."""

import sys
from pathlib import Path

# Ensure hooks/ is on sys.path
HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import pytest  # noqa: E402
from gotcha_registry import (  # noqa: E402
    GotchaEntry,
    GotchaValidationError,
    load_gotchas,
    validate_gotcha,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_GOTCHA = {
    "id": "GOTCHA-001",
    "name": "Human Error Stop",
    "pattern": "Agent stops and asks human for every minor decision",
    "severity": "high",
    "prevention": "Set confidence threshold; only escalate when stuck after 3 auto-fix attempts",
    "discovered": "2026-03-19",
    "source": "tps-kaizen",
}

VALID_GOTCHA_2 = {
    "id": "GOTCHA-002",
    "name": "Silent Exception",
    "pattern": "Exception is swallowed without logging, causing invisible failures",
    "severity": "critical",
    "prevention": "Use logger.error with type(exc).__name__ and re-raise or return sentinel",
    "discovered": "2026-03-19",
    "source": "tps-kaizen",
}


def write_yaml(path: Path, content: str) -> None:
    """Write YAML content to a file."""
    path.write_text(content, encoding="utf-8")


def valid_yaml_content(data: dict) -> str:
    """Generate minimal YAML for a valid Gotcha dict."""
    return (
        f"id: {data['id']}\n"
        f"name: {data['name']}\n"
        f"pattern: {data['pattern']}\n"
        f"severity: {data['severity']}\n"
        f"prevention: {data['prevention']}\n"
        f"discovered: {data['discovered']}\n"
        f"source: {data['source']}\n"
    )


# ---------------------------------------------------------------------------
# Test: validate_gotcha()
# ---------------------------------------------------------------------------


class TestValidateGotcha:
    def test_valid_gotcha_returns_empty_list(self):
        """A valid Gotcha dict with all required fields returns no errors."""
        errors = validate_gotcha(VALID_GOTCHA)
        assert errors == []

    def test_missing_pattern_returns_error(self):
        """A dict missing 'pattern' returns an error mentioning the field name."""
        data = {k: v for k, v in VALID_GOTCHA.items() if k != "pattern"}
        errors = validate_gotcha(data)
        assert len(errors) >= 1
        assert any("pattern" in e for e in errors)

    def test_invalid_severity_returns_error(self):
        """A dict with severity not in (critical, high, medium, low) returns an error."""
        data = {**VALID_GOTCHA, "severity": "extreme"}
        errors = validate_gotcha(data)
        assert len(errors) >= 1
        assert any("severity" in e for e in errors)

    def test_multiple_missing_fields_returns_all_errors(self):
        """validate_gotcha() returns an error for each missing/invalid field, not just the first."""
        data = {}
        errors = validate_gotcha(data)
        required_fields = {"id", "name", "pattern", "severity", "prevention", "discovered", "source"}
        for field in required_fields:
            assert any(field in e for e in errors), f"No error reported for missing field: {field}"

    def test_empty_string_field_returns_error(self):
        """An empty string for a required field counts as missing."""
        data = {**VALID_GOTCHA, "name": ""}
        errors = validate_gotcha(data)
        assert any("name" in e for e in errors)

    def test_valid_all_severities(self):
        """All valid severity values are accepted without errors."""
        for severity in ("critical", "high", "medium", "low"):
            data = {**VALID_GOTCHA, "severity": severity}
            errors = validate_gotcha(data)
            assert errors == [], f"Unexpected errors for severity '{severity}': {errors}"

    def test_optional_fields_absent_no_errors(self):
        """Optional fields (tags, examples, references) do not cause errors when absent."""
        # VALID_GOTCHA has no optional fields — should return no errors
        errors = validate_gotcha(VALID_GOTCHA)
        assert errors == []

    def test_optional_fields_present_no_errors(self):
        """Optional fields are accepted when present."""
        data = {
            **VALID_GOTCHA,
            "tags": ["pipeline", "safety"],
            "examples": ["Agent asked user 47 times in one session"],
            "references": ["70-kaizen-learning.md"],
        }
        errors = validate_gotcha(data)
        assert errors == []


# ---------------------------------------------------------------------------
# Test: load_gotchas() — core directory
# ---------------------------------------------------------------------------


class TestLoadGotchasCore:
    def test_two_valid_files_returns_two_entries(self, tmp_path):
        """load_gotchas() with 2 valid .yaml files returns a list of 2 GotchaEntry objects."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()
        write_yaml(gotchas_dir / "001.yaml", valid_yaml_content(VALID_GOTCHA))
        write_yaml(gotchas_dir / "002.yaml", valid_yaml_content(VALID_GOTCHA_2))

        entries = load_gotchas(gotchas_dir)
        assert len(entries) == 2
        ids = {e.id for e in entries}
        assert "GOTCHA-001" in ids
        assert "GOTCHA-002" in ids

    def test_invalid_file_raises_validation_error(self, tmp_path):
        """load_gotchas() with 1 valid and 1 invalid .yaml raises GotchaValidationError."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()
        write_yaml(gotchas_dir / "001.yaml", valid_yaml_content(VALID_GOTCHA))
        # Missing required fields
        write_yaml(gotchas_dir / "bad.yaml", "id: GOTCHA-BAD\nname: Incomplete\n")

        with pytest.raises(GotchaValidationError) as exc_info:
            load_gotchas(gotchas_dir)
        # Error message should name the file
        assert "bad.yaml" in str(exc_info.value)

    def test_no_silent_failure_for_invalid(self, tmp_path):
        """Invalid YAML files produce GotchaValidationError — no silent skip."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()
        write_yaml(gotchas_dir / "bad.yaml", "id: X\n")  # Missing most fields

        with pytest.raises(GotchaValidationError):
            load_gotchas(gotchas_dir)

    def test_returns_gotcha_entry_instances(self, tmp_path):
        """load_gotchas() returns GotchaEntry dataclass instances."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()
        write_yaml(gotchas_dir / "001.yaml", valid_yaml_content(VALID_GOTCHA))

        entries = load_gotchas(gotchas_dir)
        assert len(entries) == 1
        entry = entries[0]
        assert isinstance(entry, GotchaEntry)
        assert entry.id == "GOTCHA-001"
        assert entry.severity == "high"

    def test_empty_directory_returns_empty_list(self, tmp_path):
        """load_gotchas() on an empty directory returns an empty list."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()
        entries = load_gotchas(gotchas_dir)
        assert entries == []

    def test_non_yaml_files_ignored(self, tmp_path):
        """load_gotchas() ignores non-.yaml files."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()
        write_yaml(gotchas_dir / "001.yaml", valid_yaml_content(VALID_GOTCHA))
        (gotchas_dir / "README.md").write_text("# README", encoding="utf-8")
        (gotchas_dir / "notes.txt").write_text("notes", encoding="utf-8")

        entries = load_gotchas(gotchas_dir)
        assert len(entries) == 1


# ---------------------------------------------------------------------------
# Test: load_gotchas() — pack discovery
# ---------------------------------------------------------------------------


class TestLoadGotchasPackDiscovery:
    def test_pack_gotchas_discovered(self, tmp_path):
        """load_gotchas() with packs_dir discovers .yaml files in packs/{name}/gotchas/."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()

        packs_dir = tmp_path / "packs"
        packs_dir.mkdir()
        pack_gotchas = packs_dir / "my-pack" / "gotchas"
        pack_gotchas.mkdir(parents=True)
        write_yaml(pack_gotchas / "002.yaml", valid_yaml_content(VALID_GOTCHA_2))

        entries = load_gotchas(gotchas_dir, packs_dir=packs_dir)
        ids = {e.id for e in entries}
        assert "GOTCHA-002" in ids

    def test_merged_core_and_pack_entries(self, tmp_path):
        """load_gotchas() returns entries from both gotchas/ and packs/*/gotchas/ merged."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()
        write_yaml(gotchas_dir / "001.yaml", valid_yaml_content(VALID_GOTCHA))

        packs_dir = tmp_path / "packs"
        packs_dir.mkdir()
        pack_gotchas = packs_dir / "my-pack" / "gotchas"
        pack_gotchas.mkdir(parents=True)
        write_yaml(pack_gotchas / "002.yaml", valid_yaml_content(VALID_GOTCHA_2))

        entries = load_gotchas(gotchas_dir, packs_dir=packs_dir)
        assert len(entries) == 2
        ids = {e.id for e in entries}
        assert "GOTCHA-001" in ids
        assert "GOTCHA-002" in ids

    def test_duplicate_id_across_core_and_pack_raises_error(self, tmp_path):
        """Duplicate Gotcha IDs across core and pack directories raise GotchaValidationError."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()
        write_yaml(gotchas_dir / "001.yaml", valid_yaml_content(VALID_GOTCHA))

        packs_dir = tmp_path / "packs"
        packs_dir.mkdir()
        pack_gotchas = packs_dir / "other-pack" / "gotchas"
        pack_gotchas.mkdir(parents=True)
        # Same ID as VALID_GOTCHA
        write_yaml(pack_gotchas / "dup.yaml", valid_yaml_content(VALID_GOTCHA))

        with pytest.raises(GotchaValidationError) as exc_info:
            load_gotchas(gotchas_dir, packs_dir=packs_dir)
        assert "GOTCHA-001" in str(exc_info.value)

    def test_pack_dir_without_gotchas_subdir_skipped(self, tmp_path):
        """Packs without a gotchas/ subdirectory are silently skipped."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()

        packs_dir = tmp_path / "packs"
        packs_dir.mkdir()
        # Pack dir with no gotchas/ subdir
        (packs_dir / "no-gotchas-pack").mkdir()

        entries = load_gotchas(gotchas_dir, packs_dir=packs_dir)
        assert entries == []

    def test_multiple_packs_all_discovered(self, tmp_path):
        """Gotchas from multiple packs are all discovered and merged."""
        gotchas_dir = tmp_path / "gotchas"
        gotchas_dir.mkdir()

        packs_dir = tmp_path / "packs"
        packs_dir.mkdir()

        pack_a_gotchas = packs_dir / "pack-a" / "gotchas"
        pack_a_gotchas.mkdir(parents=True)
        write_yaml(pack_a_gotchas / "001.yaml", valid_yaml_content(VALID_GOTCHA))

        pack_b_gotchas = packs_dir / "pack-b" / "gotchas"
        pack_b_gotchas.mkdir(parents=True)
        write_yaml(pack_b_gotchas / "002.yaml", valid_yaml_content(VALID_GOTCHA_2))

        entries = load_gotchas(gotchas_dir, packs_dir=packs_dir)
        assert len(entries) == 2
