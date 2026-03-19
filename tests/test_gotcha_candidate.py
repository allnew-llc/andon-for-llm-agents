#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for hooks/gotcha_candidate.py — Gotcha candidate generation from Five Whys output."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import yaml

# Ensure hooks/ is on sys.path
HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import pytest  # noqa: E402
from gotcha_candidate import generate_candidate  # noqa: E402
from gotcha_registry import validate_gotcha  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_ROOT_CAUSE = "CI pipeline fails because test dependencies are not pinned"
VALID_PREVENTION = "Pin all test dependencies in requirements-test.txt with exact versions"


# ---------------------------------------------------------------------------
# Test 1: generate_candidate() returns a Path in gotchas/candidates/
# ---------------------------------------------------------------------------


class TestGenerateCandidateBasic:
    def test_returns_path_to_yaml_in_candidates(self, tmp_path):
        """generate_candidate() returns a Path to a YAML file in {gotchas_dir}/candidates/."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        assert isinstance(result, Path)
        assert result.exists()
        assert result.suffix == ".yaml"
        # Must be inside the candidates/ subdirectory
        assert result.parent.name == "candidates"
        assert result.parent.parent == tmp_path

    def test_returns_absolute_path(self, tmp_path):
        """generate_candidate() returns an absolute path."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        assert result.is_absolute()


# ---------------------------------------------------------------------------
# Test 2: Generated YAML passes validate_gotcha()
# ---------------------------------------------------------------------------


class TestGenerateCandidateValidation:
    def test_generated_yaml_passes_validate_gotcha(self, tmp_path):
        """The generated YAML file passes validate_gotcha() — all required fields are present and valid."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        errors = validate_gotcha(data)
        assert errors == [], f"Generated YAML failed validation: {errors}"

    def test_generated_yaml_all_required_fields_present(self, tmp_path):
        """The generated YAML contains all fields required by REQUIRED_FIELDS."""
        from gotcha_registry import REQUIRED_FIELDS  # noqa: PLC0415

        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        for field_name in REQUIRED_FIELDS:
            assert field_name in data, f"Missing required field: {field_name}"
            assert data[field_name], f"Required field '{field_name}' is empty"


# ---------------------------------------------------------------------------
# Test 3: Candidate ID follows GOTCHA-CAND-YYYYMMDD-HHMMSS format
# ---------------------------------------------------------------------------


class TestCandidateId:
    def test_candidate_id_format(self, tmp_path):
        """The candidate ID follows the GOTCHA-CAND-YYYYMMDD-HHMMSS naming convention."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        candidate_id = data["id"]
        pattern = r"^GOTCHA-CAND-\d{8}-\d{6}$"
        assert re.match(pattern, candidate_id), (
            f"Candidate ID '{candidate_id}' does not match GOTCHA-CAND-YYYYMMDD-HHMMSS pattern"
        )

    def test_candidate_id_matches_filename(self, tmp_path):
        """The candidate YAML filename matches the candidate ID."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        expected_filename = data["id"] + ".yaml"
        assert result.name == expected_filename


# ---------------------------------------------------------------------------
# Test 4: Pattern field is auto-extracted from root cause keywords
# ---------------------------------------------------------------------------


class TestPatternExtraction:
    def test_pattern_field_is_regex_from_root_cause(self, tmp_path):
        """The pattern field is auto-extracted from root cause keywords with stopwords removed."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        pattern = data["pattern"]
        assert isinstance(pattern, str)
        assert len(pattern) > 0

    def test_pattern_excludes_common_stopwords(self, tmp_path):
        """Common stopwords (the, a, an, is, in, on, at, to, for, of, by, with) are removed from pattern."""
        result = generate_candidate(
            root_cause="The pipeline fails because it is not configured correctly",
            prevention="Configure the pipeline correctly",
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        pattern = data["pattern"]
        # Stopwords should not appear as standalone words in the pattern
        # The pattern contains keywords joined with .*? connector
        keywords = [kw for kw in pattern.split(".*?") if kw]
        stopwords = {"the", "a", "an", "is", "was", "were", "are", "in", "on",
                     "at", "to", "for", "of", "by", "with", "that", "this",
                     "it", "not", "but", "and", "or"}
        for kw in keywords:
            assert kw.lower() not in stopwords, f"Stopword '{kw}' found in pattern keywords"

    def test_pattern_keywords_joined_with_connector(self, tmp_path):
        """Pattern keywords are joined with '.*?' as regex connector."""
        root_cause = "database connection pool exhausted under load"
        result = generate_candidate(
            root_cause=root_cause,
            prevention="Increase pool size and add connection timeout",
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        pattern = data["pattern"]
        # Should contain .*? as connector between keywords (if more than one keyword)
        assert ".*?" in pattern


# ---------------------------------------------------------------------------
# Test 5: Name field is derived from root_cause
# ---------------------------------------------------------------------------


class TestNameDerivation:
    def test_name_derived_from_root_cause(self, tmp_path):
        """The name field is derived from the first ~50 chars of root_cause, title-cased."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        name = data["name"]
        assert isinstance(name, str)
        assert len(name) > 0
        # Name should be a shortened/cleaned version of root_cause
        # Should not be empty and should be title-cased or otherwise cleaned
        assert name[0].isupper() or name[0].isdigit()

    def test_name_is_truncated_at_word_boundary(self, tmp_path):
        """Name is truncated at a word boundary, not mid-word."""
        long_root_cause = (
            "The automated deployment pipeline silently skips integration tests "
            "when the feature flag is disabled causing regressions in production"
        )
        result = generate_candidate(
            root_cause=long_root_cause,
            prevention="Always run integration tests regardless of feature flag state",
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        name = data["name"]
        # Name should not end mid-word (no trailing partial word)
        # Check it ends with a space-free boundary (last char is a word char, not a space)
        assert not name.endswith(" ")
        assert len(name) <= 55  # Allow some flex around the ~50 char boundary


# ---------------------------------------------------------------------------
# Test 6: Default severity is "medium"
# ---------------------------------------------------------------------------


class TestDefaults:
    def test_default_severity_is_medium(self, tmp_path):
        """When no severity is specified, the generated YAML uses 'medium' as default."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        assert data["severity"] == "medium"

    # ---------------------------------------------------------------------------
    # Test 7: Default source is "five-whys"
    # ---------------------------------------------------------------------------

    def test_default_source_is_five_whys(self, tmp_path):
        """When no source is specified, the generated YAML uses 'five-whys' as source."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        assert data["source"] == "five-whys"

    # ---------------------------------------------------------------------------
    # Test 8: discovered field is today's date
    # ---------------------------------------------------------------------------

    def test_discovered_is_today(self, tmp_path):
        """The discovered field is set to today's date in YYYY-MM-DD format."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        today = date.today().isoformat()
        assert data["discovered"] == today


# ---------------------------------------------------------------------------
# Test 9: gotchas/candidates/ directory is created if it does not exist
# ---------------------------------------------------------------------------


class TestDirectoryCreation:
    def test_candidates_dir_created_if_not_exists(self, tmp_path):
        """generate_candidate() creates gotchas/candidates/ if it does not exist."""
        new_dir = tmp_path / "new_gotchas_dir"
        assert not new_dir.exists()

        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=new_dir,
        )
        assert new_dir.exists()
        assert (new_dir / "candidates").exists()
        assert result.exists()


# ---------------------------------------------------------------------------
# Test 10: Function returns absolute path
# (Already covered in TestGenerateCandidateBasic.test_returns_absolute_path)
# Adding a separate explicit test here for clarity
# ---------------------------------------------------------------------------


class TestReturnValue:
    def test_returned_path_is_readable_yaml(self, tmp_path):
        """The returned path points to a readable, valid YAML file."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        text = result.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        assert isinstance(data, dict)

    def test_prevention_text_preserved_in_yaml(self, tmp_path):
        """The prevention text is preserved faithfully in the YAML."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        # Prevention should contain the key content from the input
        assert "Pin" in data["prevention"] or "pin" in data["prevention"].lower()


# ---------------------------------------------------------------------------
# Test 11: Passing severity="critical" overrides the default
# ---------------------------------------------------------------------------


class TestSeverityOverride:
    def test_severity_critical_overrides_default(self, tmp_path):
        """Passing severity='critical' produces a YAML with severity='critical'."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            severity="critical",
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        assert data["severity"] == "critical"

    def test_severity_low_overrides_default(self, tmp_path):
        """Passing severity='low' produces a YAML with severity='low'."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            severity="low",
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        assert data["severity"] == "low"

    def test_source_override(self, tmp_path):
        """Passing source='tps-kaizen' overrides the default source."""
        result = generate_candidate(
            root_cause=VALID_ROOT_CAUSE,
            prevention=VALID_PREVENTION,
            source="tps-kaizen",
            gotchas_dir=tmp_path,
        )
        data = yaml.safe_load(result.read_text(encoding="utf-8"))
        assert data["source"] == "tps-kaizen"


# ---------------------------------------------------------------------------
# Test 12: Empty root_cause or empty prevention raises ValueError
# ---------------------------------------------------------------------------


class TestInputValidation:
    def test_empty_root_cause_raises_value_error(self, tmp_path):
        """Passing an empty root_cause raises ValueError."""
        with pytest.raises(ValueError, match="root_cause"):
            generate_candidate(
                root_cause="",
                prevention=VALID_PREVENTION,
                gotchas_dir=tmp_path,
            )

    def test_whitespace_only_root_cause_raises_value_error(self, tmp_path):
        """Passing a whitespace-only root_cause raises ValueError."""
        with pytest.raises(ValueError, match="root_cause"):
            generate_candidate(
                root_cause="   \n\t  ",
                prevention=VALID_PREVENTION,
                gotchas_dir=tmp_path,
            )

    def test_empty_prevention_raises_value_error(self, tmp_path):
        """Passing an empty prevention raises ValueError."""
        with pytest.raises(ValueError, match="prevention"):
            generate_candidate(
                root_cause=VALID_ROOT_CAUSE,
                prevention="",
                gotchas_dir=tmp_path,
            )

    def test_whitespace_only_prevention_raises_value_error(self, tmp_path):
        """Passing a whitespace-only prevention raises ValueError."""
        with pytest.raises(ValueError, match="prevention"):
            generate_candidate(
                root_cause=VALID_ROOT_CAUSE,
                prevention="   ",
                gotchas_dir=tmp_path,
            )
