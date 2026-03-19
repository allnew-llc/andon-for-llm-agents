#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for hooks/gotcha_surfacer.py — Gotcha pattern matching and auto-surfacing.

Covers:
  - Exact match (full pattern substring found in error text)
  - Partial match (significant word overlap)
  - Category match (tag or severity keyword match)
  - No match (unrelated error text)
  - Multiple matches ranked by score descending
  - format_surfaced_gotchas formatting
  - Empty registry (no crash)
  - surface_gotchas integration with real YAML files
"""

import sys
from pathlib import Path

# Ensure hooks/ is on sys.path
HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import pytest  # noqa: E402
from gotcha_surfacer import (  # noqa: E402
    ConfidenceLevel,
    MatchResult,
    format_surfaced_gotchas,
    match_gotchas,
    surface_gotchas,
)
from gotcha_registry import GotchaEntry  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_entry(
    gotcha_id: str = "GOTCHA-TEST",
    name: str = "Test Gotcha",
    pattern: str = "This is a test anti-pattern description",
    severity: str = "medium",
    prevention: str = "Do not do this anti-pattern in production code",
    tags: list[str] | None = None,
) -> GotchaEntry:
    return GotchaEntry(
        id=gotcha_id,
        name=name,
        pattern=pattern,
        severity=severity,
        prevention=prevention,
        discovered="2026-03-19",
        source="tps-kaizen",
        tags=tags or [],
    )


# ---------------------------------------------------------------------------
# Test 1: Exact match
# ---------------------------------------------------------------------------


def test_exact_match_returns_exact_confidence() -> None:
    """Error text containing the full pattern text verbatim → EXACT, score=1.0."""
    entry = make_entry(pattern="Agent stops and asks human for every minor decision")
    error_text = (
        "Detected: Agent stops and asks human for every minor decision "
        "which is causing pipeline delay"
    )
    results = match_gotchas(error_text, [entry])
    assert len(results) == 1
    assert results[0].confidence == ConfidenceLevel.EXACT
    assert results[0].score == 1.0
    assert results[0].gotcha is entry


# ---------------------------------------------------------------------------
# Test 2: Partial match
# ---------------------------------------------------------------------------


def test_partial_match_returns_partial_confidence() -> None:
    """Error text with 40%+ significant pattern words → PARTIAL, score in 0.5–0.8."""
    # Pattern has ~8 significant words: "five", "whys", "analysis", "terminates",
    # "human", "error", "process", "structural"
    pattern = (
        "Five Whys analysis terminates at human error instead of "
        "digging into the process or system gap that allowed the mistake"
    )
    entry = make_entry(pattern=pattern)
    # Include several significant words from the pattern
    error_text = "The five whys analysis stopped at human error without identifying structural root cause"
    results = match_gotchas(error_text, [entry])
    assert len(results) == 1
    assert results[0].confidence == ConfidenceLevel.PARTIAL
    assert 0.5 <= results[0].score <= 0.8


# ---------------------------------------------------------------------------
# Test 3: Category match — tag
# ---------------------------------------------------------------------------


def test_category_match_via_tag() -> None:
    """Error text containing a Gotcha tag word → CATEGORY, score ~0.3."""
    entry = make_entry(
        pattern="Completely unrelated pattern description about something else entirely",
        tags=["gate-gaming", "quality", "jidoka"],
    )
    error_text = "Detected gate-gaming behavior in the pipeline execution"
    results = match_gotchas(error_text, [entry])
    assert len(results) == 1
    assert results[0].confidence == ConfidenceLevel.CATEGORY
    assert 0.2 <= results[0].score <= 0.4


# ---------------------------------------------------------------------------
# Test 4: Category match — severity keyword
# ---------------------------------------------------------------------------


def test_category_match_via_severity_keyword() -> None:
    """Error text containing the severity level keyword → CATEGORY, score ~0.2."""
    entry = make_entry(
        pattern="Something completely different unrelated to the error at hand",
        severity="critical",
        tags=[],
    )
    error_text = "critical system failure detected in module initialization"
    results = match_gotchas(error_text, [entry])
    # Should match via 'critical' severity keyword
    assert len(results) == 1
    assert results[0].confidence == ConfidenceLevel.CATEGORY
    assert results[0].score == pytest.approx(0.2, abs=0.01)


# ---------------------------------------------------------------------------
# Test 5: No match
# ---------------------------------------------------------------------------


def test_no_match_returns_empty_list() -> None:
    """Error text with no connection to Gotcha → empty list."""
    entry = make_entry(
        pattern="Agent stops and asks human for every minor decision about code",
        tags=["five-whys", "root-cause"],
    )
    error_text = "Database connection timeout after 30 seconds on port 5432"
    results = match_gotchas(error_text, [entry])
    assert results == []


# ---------------------------------------------------------------------------
# Test 6: Multiple matches ranked by score descending
# ---------------------------------------------------------------------------


def test_multiple_matches_ranked_descending() -> None:
    """Three gotchas matching at different levels are returned sorted by score desc."""
    # Exact match entry
    exact_entry = make_entry(
        gotcha_id="GOTCHA-E",
        name="Exact Gotcha",
        pattern="gate gaming optimization artifact quality",
    )
    # Partial match entry — contains several words that also appear in error text
    partial_entry = make_entry(
        gotcha_id="GOTCHA-P",
        name="Partial Gotcha",
        pattern="agent optimization artifact reverse-engineers minimum conditions quality gate",
    )
    # Category match entry — only tag matches
    category_entry = make_entry(
        gotcha_id="GOTCHA-C",
        name="Category Gotcha",
        pattern="completely unrelated description about something different",
        tags=["gate-gaming"],
    )

    error_text = (
        "gate gaming optimization artifact quality detected in pipeline "
        "execution: gate-gaming behavior observed"
    )
    results = match_gotchas(error_text, [category_entry, partial_entry, exact_entry])

    # Should be sorted descending by score
    assert len(results) >= 2
    for i in range(len(results) - 1):
        assert results[i].score >= results[i + 1].score

    # Exact match must be first
    assert results[0].confidence == ConfidenceLevel.EXACT


# ---------------------------------------------------------------------------
# Test 7: format_surfaced_gotchas
# ---------------------------------------------------------------------------


def test_format_surfaced_gotchas_produces_readable_output() -> None:
    """format_surfaced_gotchas formats each match with ID, name, confidence, prevention."""
    entry = make_entry(
        gotcha_id="GOTCHA-001",
        name="Human Error Stop",
        prevention="Always ask why the process allowed the error.",
    )
    match = MatchResult(gotcha=entry, confidence=ConfidenceLevel.EXACT, score=1.0)
    output = format_surfaced_gotchas([match])
    assert "[GOTCHA_MATCH]" in output
    assert "GOTCHA-001" in output
    assert "Human Error Stop" in output
    assert "exact" in output.lower()
    assert "Always ask why the process allowed the error." in output


def test_format_surfaced_gotchas_empty_returns_empty_string() -> None:
    """format_surfaced_gotchas with empty list returns empty string."""
    assert format_surfaced_gotchas([]) == ""


# ---------------------------------------------------------------------------
# Test 8: Empty registry — no crash
# ---------------------------------------------------------------------------


def test_match_gotchas_with_empty_registry() -> None:
    """When no gotchas are loaded, match_gotchas returns empty list without crashing."""
    results = match_gotchas("some error text that would normally match things", [])
    assert results == []


# ---------------------------------------------------------------------------
# Test 9: surface_gotchas integration — real YAML files
# ---------------------------------------------------------------------------


def test_surface_gotchas_integration_with_real_yaml(tmp_path: Path) -> None:
    """surface_gotchas loads real gotchas from tmp_path and returns formatted string."""
    # Write a minimal YAML gotcha that will match our error text
    gotcha_yaml = tmp_path / "GOTCHA-INT-001.yaml"
    gotcha_yaml.write_text(
        "id: GOTCHA-INT-001\n"
        "name: Test Integration Gotcha\n"
        "pattern: agent reverse-engineers minimum gate conditions instead of producing quality artifacts\n"
        "severity: critical\n"
        "prevention: Focus on deliverable quality, not gate conditions.\n"
        "discovered: '2026-03-19'\n"
        "source: tps-kaizen\n"
        "tags:\n"
        "  - gate-gaming\n"
        "  - quality\n",
        encoding="utf-8",
    )
    # Error text that should match the pattern above
    error_text = (
        "agent reverse-engineers minimum gate conditions instead of producing quality artifacts"
    )
    result = surface_gotchas(error_text, tmp_path)
    assert result != "", "Expected a non-empty result for a matching error text"
    assert "GOTCHA-INT-001" in result
    assert "[GOTCHA_MATCH]" in result


def test_surface_gotchas_no_match_returns_empty_string(tmp_path: Path) -> None:
    """surface_gotchas returns empty string when no gotchas match error text."""
    gotcha_yaml = tmp_path / "GOTCHA-INT-002.yaml"
    gotcha_yaml.write_text(
        "id: GOTCHA-INT-002\n"
        "name: Unrelated Gotcha\n"
        "pattern: completely unique and unrelated anti-pattern never seen before\n"
        "severity: low\n"
        "prevention: Use this specific approach.\n"
        "discovered: '2026-03-19'\n"
        "source: tps-kaizen\n",
        encoding="utf-8",
    )
    error_text = "database connection refused on port 5432 after timeout"
    result = surface_gotchas(error_text, tmp_path)
    assert result == ""


def test_surface_gotchas_with_gate_gaming_gotcha_real_files() -> None:
    """Smoke: loads the real gotchas directory and matches gate gaming error text."""
    repo_root = Path(__file__).resolve().parent.parent
    gotchas_dir = repo_root / "gotchas"
    packs_dir = repo_root / "packs"

    if not gotchas_dir.is_dir():
        pytest.skip("Real gotchas directory not available")

    error_text = "Gate Gaming optimization for conditions detected in pipeline execution"
    result = surface_gotchas(
        error_text,
        gotchas_dir,
        packs_dir=packs_dir if packs_dir.is_dir() else None,
    )
    # The real GOTCHA-004 (Gate Gaming) should match
    assert result, f"Expected at least one match for gate gaming text, got: {result!r}"
    assert "GOTCHA_MATCH" in result
