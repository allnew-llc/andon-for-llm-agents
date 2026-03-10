#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for context_monitor.py — proxy-based context degradation detection."""

import json
import os
import sys
from pathlib import Path

# Ensure hooks/ is on sys.path
HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import pytest  # noqa: E402

# We need to set ANDON_STATE_DIR before importing context_monitor
# so that kaizen_core.STATE_DIR (and thus ANDON_FILE) points to our
# temp directory during tests.


@pytest.fixture()
def state_dir(tmp_path, monkeypatch):
    """Create a temporary state directory and configure kaizen_core to use it."""
    sd = tmp_path / "state"
    sd.mkdir()
    monkeypatch.setenv("ANDON_STATE_DIR", str(sd))

    # Force kaizen_core to re-evaluate its module-level paths
    # by reloading it.  This ensures ANDON_FILE points to our temp dir.
    import importlib
    import kaizen_core

    importlib.reload(kaizen_core)

    # Also reload context_monitor so it picks up the reloaded kaizen_core
    import context_monitor

    importlib.reload(context_monitor)

    yield sd

    # Restore after test
    importlib.reload(kaizen_core)
    importlib.reload(context_monitor)


@pytest.fixture()
def ctx(state_dir):
    """Return a freshly-reloaded context_monitor module bound to state_dir."""
    import context_monitor

    return context_monitor


# ============================================================
# Counter increment
# ============================================================


class TestCounterIncrement:
    def test_first_call_creates_state(self, state_dir, ctx):
        result = ctx.increment_and_check(state_dir)
        assert result["call_count"] == 1
        assert result["level"] == "PEAK"
        assert result["warning"] is None

    def test_counter_increments(self, state_dir, ctx):
        for i in range(5):
            result = ctx.increment_and_check(state_dir)
        assert result["call_count"] == 5
        assert result["level"] == "PEAK"

    def test_state_persists_to_file(self, state_dir, ctx):
        ctx.increment_and_check(state_dir)
        ctx.increment_and_check(state_dir)
        state = ctx.get_state(state_dir)
        assert state["tool_call_count"] == 2
        assert state["quality_level"] == "PEAK"
        assert "session_id" in state


# ============================================================
# Level transitions
# ============================================================


class TestLevelTransitions:
    def _advance_to(self, state_dir, ctx, count):
        """Advance the counter to exactly `count` calls."""
        result = None
        for _ in range(count):
            result = ctx.increment_and_check(state_dir)
        assert result is not None
        return result

    def test_peak_to_good_at_30(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 30)
        assert result["level"] == "GOOD"
        assert result["call_count"] == 30
        # GOOD level does not produce a warning
        assert result["warning"] is None

    def test_good_to_degrading_at_60(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 60)
        assert result["level"] == "DEGRADING"
        assert result["call_count"] == 60
        assert result["warning"] is not None
        assert "High tool call count" in result["warning"]
        assert "60" in result["warning"]

    def test_degrading_to_poor_at_100(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 100)
        assert result["level"] == "POOR"
        assert result["call_count"] == 100
        assert result["warning"] is not None
        assert "Very high tool call count" in result["warning"]
        assert "100" in result["warning"]

    def test_still_peak_at_29(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 29)
        assert result["level"] == "PEAK"

    def test_still_good_at_59(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 59)
        assert result["level"] == "GOOD"

    def test_still_degrading_at_99(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 99)
        assert result["level"] == "DEGRADING"

    def test_poor_stays_poor_at_150(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 150)
        assert result["level"] == "POOR"


# ============================================================
# Warning generation at 60 and 100 calls
# ============================================================


class TestWarningGeneration:
    def _advance_to(self, state_dir, ctx, count):
        result = None
        for _ in range(count):
            result = ctx.increment_and_check(state_dir)
        assert result is not None
        return result

    def test_degrading_warning_message(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 60)
        assert result["warning"] is not None
        assert "[ANDON/Context]" in result["warning"]
        assert "Agent sessions" in result["warning"]

    def test_poor_warning_message(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 100)
        assert result["warning"] is not None
        assert "[ANDON/Context]" in result["warning"]
        assert "fresh session" in result["warning"]

    def test_no_warning_at_peak(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 10)
        assert result["warning"] is None

    def test_no_warning_at_good(self, state_dir, ctx):
        result = self._advance_to(state_dir, ctx, 45)
        assert result["warning"] is None


# ============================================================
# ANDON-open additional warning
# ============================================================


class TestAndonOpenWarning:
    def _create_andon_open(self, state_dir, ctx):
        """Create an open ANDON state file."""
        import kaizen_core

        andon_file = kaizen_core.ANDON_FILE
        andon_file.parent.mkdir(parents=True, exist_ok=True)
        kaizen_core.write_json(andon_file, {
            "status": "open",
            "incident_id": "INC-test-001",
            "opened_at": "2026-03-10T00:00:00+00:00",
        })

    def _advance_to(self, state_dir, ctx, count):
        result = None
        for _ in range(count):
            result = ctx.increment_and_check(state_dir)
        assert result is not None
        return result

    def test_andon_open_poor_produces_extra_warning(self, state_dir, ctx):
        self._create_andon_open(state_dir, ctx)
        result = self._advance_to(state_dir, ctx, 100)
        assert result["andon_warning"] is not None
        assert "Five Whys" in result["andon_warning"]
        assert "fresh session" in result["andon_warning"]

    def test_no_andon_warning_when_andon_closed(self, state_dir, ctx):
        # No ANDON file => andon is closed
        result = self._advance_to(state_dir, ctx, 100)
        assert result["andon_warning"] is None

    def test_no_andon_warning_at_degrading(self, state_dir, ctx):
        self._create_andon_open(state_dir, ctx)
        result = self._advance_to(state_dir, ctx, 60)
        # ANDON warning only triggers at POOR level
        assert result["andon_warning"] is None


# ============================================================
# Warn-once behavior (no duplicate warnings)
# ============================================================


class TestWarnOnce:
    def _advance_to(self, state_dir, ctx, count):
        result = None
        for _ in range(count):
            result = ctx.increment_and_check(state_dir)
        assert result is not None
        return result

    def test_degrading_warns_only_on_transition(self, state_dir, ctx):
        # Advance to 60 => transition to DEGRADING => warning
        result_60 = self._advance_to(state_dir, ctx, 60)
        assert result_60["warning"] is not None

        # Call 61 => still DEGRADING, no transition => no warning
        result_61 = ctx.increment_and_check(state_dir)
        assert result_61["warning"] is None
        assert result_61["level"] == "DEGRADING"

    def test_poor_warns_only_on_transition(self, state_dir, ctx):
        # Advance to 100 => POOR transition => warning
        result_100 = self._advance_to(state_dir, ctx, 100)
        assert result_100["warning"] is not None

        # Call 101 => still POOR, no transition => no warning
        result_101 = ctx.increment_and_check(state_dir)
        assert result_101["warning"] is None
        assert result_101["level"] == "POOR"

    def test_andon_poor_warns_only_once(self, state_dir, ctx):
        import kaizen_core

        andon_file = kaizen_core.ANDON_FILE
        andon_file.parent.mkdir(parents=True, exist_ok=True)
        kaizen_core.write_json(andon_file, {
            "status": "open",
            "incident_id": "INC-test-002",
            "opened_at": "2026-03-10T00:00:00+00:00",
        })

        # Advance to 100 => POOR + ANDON open => both warnings
        result_100 = self._advance_to(state_dir, ctx, 100)
        assert result_100["warning"] is not None
        assert result_100["andon_warning"] is not None

        # Call 101 => POOR but no transition, ANDON_POOR already warned
        result_101 = ctx.increment_and_check(state_dir)
        assert result_101["warning"] is None
        assert result_101["andon_warning"] is None

    def test_both_degrading_and_poor_warn_in_sequence(self, state_dir, ctx):
        """Verify that both DEGRADING (at 60) and POOR (at 100) trigger."""
        result_60 = self._advance_to(state_dir, ctx, 60)
        assert result_60["warning"] is not None
        assert "High tool call count" in result_60["warning"]

        # No more warnings between 61-99
        for _ in range(39):
            r = ctx.increment_and_check(state_dir)
            assert r["warning"] is None

        # Call 100 => POOR transition => new warning
        result_100 = ctx.increment_and_check(state_dir)
        assert result_100["warning"] is not None
        assert "Very high tool call count" in result_100["warning"]


# ============================================================
# Session reset
# ============================================================


class TestSessionReset:
    def test_reset_clears_counter(self, state_dir, ctx):
        # Accumulate some calls
        for _ in range(50):
            ctx.increment_and_check(state_dir)

        state_before = ctx.get_state(state_dir)
        assert state_before["tool_call_count"] == 50
        old_session = state_before["session_id"]

        # Reset
        ctx.reset_session(state_dir)

        state_after = ctx.get_state(state_dir)
        assert state_after["tool_call_count"] == 0
        assert state_after["quality_level"] == "PEAK"
        assert state_after["warnings_issued"] == []
        assert state_after["session_id"] != old_session

    def test_after_reset_warnings_fire_again(self, state_dir, ctx):
        # Advance to DEGRADING
        for _ in range(60):
            ctx.increment_and_check(state_dir)

        # Reset
        ctx.reset_session(state_dir)

        # Advance to DEGRADING again => should warn again
        result = None
        for _ in range(60):
            result = ctx.increment_and_check(state_dir)
        assert result is not None
        assert result["warning"] is not None
        assert "High tool call count" in result["warning"]


# ============================================================
# Edge cases
# ============================================================


class TestEdgeCases:
    def test_corrupted_state_file_recovers(self, state_dir, ctx):
        """If the state file is corrupt JSON, increment_and_check should recover."""
        sf = state_dir / "andon-context-monitor.json"
        sf.write_text("not valid json", encoding="utf-8")

        result = ctx.increment_and_check(state_dir)
        assert result["call_count"] == 1
        assert result["level"] == "PEAK"

    def test_missing_state_file_initializes(self, state_dir, ctx):
        """First call with no state file should initialize cleanly."""
        result = ctx.increment_and_check(state_dir)
        assert result["call_count"] == 1
        assert result["level"] == "PEAK"
        assert result["warning"] is None
        assert result["andon_warning"] is None

    def test_level_for_count_boundary_values(self, ctx):
        """Test _level_for_count at exact boundaries."""
        assert ctx._level_for_count(0) == "PEAK"
        assert ctx._level_for_count(29) == "PEAK"
        assert ctx._level_for_count(30) == "GOOD"
        assert ctx._level_for_count(59) == "GOOD"
        assert ctx._level_for_count(60) == "DEGRADING"
        assert ctx._level_for_count(99) == "DEGRADING"
        assert ctx._level_for_count(100) == "POOR"
        assert ctx._level_for_count(999) == "POOR"
