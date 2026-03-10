#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for analysis paralysis detection (APD-01 through APD-04)."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Ensure hooks/ is on sys.path
HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    """Redirect STATE_DIR so tests use an isolated temp directory."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    monkeypatch.setenv("ANDON_STATE_DIR", str(state_dir))

    # Force reload of kaizen_core to pick up the new STATE_DIR
    if "kaizen_core" in sys.modules:
        del sys.modules["kaizen_core"]
    if "tps-kaizen-runtime" in sys.modules:
        del sys.modules["tps-kaizen-runtime"]

    # Re-import with fresh env
    import importlib
    import kaizen_core
    importlib.reload(kaizen_core)

    # Patch the module-level constants in the runtime module
    from kaizen_core import (
        ANALYSIS_COUNTER_FILE,
        ANDON_FILE,
        STATE_DIR,
    )

    yield {
        "state_dir": state_dir,
        "counter_file": ANALYSIS_COUNTER_FILE,
        "andon_file": ANDON_FILE,
    }


def _load_counter(counter_file: Path) -> dict:
    """Load the analysis counter state file."""
    if not counter_file.exists():
        return {}
    return json.loads(counter_file.read_text(encoding="utf-8"))


def _write_andon_open(andon_file: Path) -> None:
    """Create an ANDON open state file."""
    andon_file.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "status": "open",
        "incident_id": "INC-test-001",
        "opened_at": "2026-03-10T19:00:00+00:00",
    }
    fd = os.open(str(andon_file), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o640)
    try:
        os.write(fd, json.dumps(data).encode("utf-8"))
    finally:
        os.close(fd)


def _run_analysis_paralysis(tool_name: str, exit_code: int | None = None) -> str:
    """Call the analysis_paralysis function and capture stdout."""
    import importlib
    import kaizen_core
    importlib.reload(kaizen_core)

    # Need to re-import the runtime module to get fresh references
    if "tps_kaizen_runtime" in sys.modules:
        del sys.modules["tps_kaizen_runtime"]

    # Import the function directly from the module file
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "tps_kaizen_runtime",
        str(HOOKS_DIR / "tps-kaizen-runtime.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Capture stdout
    from io import StringIO
    captured = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        mod.analysis_paralysis(tool_name, exit_code)
    finally:
        sys.stdout = old_stdout
    return captured.getvalue()


# ============================================================
# APD-01: Counter increments on Read/Grep/Glob
# ============================================================


class TestReadIncrement:
    def test_read_increments_counter(self, isolated_state):
        """Read tool should increment the consecutive_reads counter."""
        output = _run_analysis_paralysis("Read")
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 1

    def test_grep_increments_counter(self, isolated_state):
        """Grep tool should increment the consecutive_reads counter."""
        _run_analysis_paralysis("Grep")
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 1

    def test_glob_increments_counter(self, isolated_state):
        """Glob tool should increment the consecutive_reads counter."""
        _run_analysis_paralysis("Glob")
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 1

    def test_multiple_reads_accumulate(self, isolated_state):
        """Multiple consecutive read calls should accumulate."""
        for _ in range(3):
            _run_analysis_paralysis("Read")
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 3

    def test_mixed_read_tools_accumulate(self, isolated_state):
        """Different read tools should all accumulate on the same counter."""
        _run_analysis_paralysis("Read")
        _run_analysis_paralysis("Grep")
        _run_analysis_paralysis("Glob")
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 3


# ============================================================
# APD-02: Counter resets on Edit/Write/Bash(exit 0)
# ============================================================


class TestWriteReset:
    def test_edit_resets_counter(self, isolated_state):
        """Edit tool should reset the consecutive_reads counter to 0."""
        for _ in range(3):
            _run_analysis_paralysis("Read")
        _run_analysis_paralysis("Edit")
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 0

    def test_write_resets_counter(self, isolated_state):
        """Write tool should reset the consecutive_reads counter to 0."""
        for _ in range(3):
            _run_analysis_paralysis("Grep")
        _run_analysis_paralysis("Write")
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 0

    def test_bash_exit_0_resets_counter(self, isolated_state):
        """Bash with exit code 0 should reset the counter."""
        for _ in range(3):
            _run_analysis_paralysis("Glob")
        _run_analysis_paralysis("Bash", exit_code=0)
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 0

    def test_bash_exit_nonzero_does_not_reset(self, isolated_state):
        """Bash with non-zero exit code should NOT reset the counter."""
        for _ in range(3):
            _run_analysis_paralysis("Read")
        _run_analysis_paralysis("Bash", exit_code=1)
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 3

    def test_bash_no_exit_code_does_not_reset(self, isolated_state):
        """Bash with no exit code should NOT reset the counter."""
        for _ in range(3):
            _run_analysis_paralysis("Read")
        _run_analysis_paralysis("Bash", exit_code=None)
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 3

    def test_edit_sets_last_write_at(self, isolated_state):
        """Edit should update last_write_at timestamp."""
        _run_analysis_paralysis("Edit")
        state = _load_counter(isolated_state["counter_file"])
        assert state["last_write_at"] != ""

    def test_unknown_tool_does_not_affect_counter(self, isolated_state):
        """Unknown tools (e.g., Skill) should not change the counter."""
        for _ in range(3):
            _run_analysis_paralysis("Read")
        _run_analysis_paralysis("Skill")
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 3


# ============================================================
# APD-03: Warning at normal threshold (5) and ANDON open threshold (3)
# ============================================================


class TestThresholdWarning:
    def test_no_warning_below_threshold(self, isolated_state):
        """No warning should be emitted below 5 consecutive reads."""
        for i in range(4):
            output = _run_analysis_paralysis("Read")
        # 4th call should not trigger warning
        assert "[ANDON] Analysis paralysis" not in output

    def test_warning_at_threshold_5(self, isolated_state):
        """Warning should be emitted at exactly 5 consecutive reads."""
        for i in range(4):
            _run_analysis_paralysis("Read")
        output = _run_analysis_paralysis("Read")  # 5th
        assert "[ANDON] Analysis paralysis detected" in output
        assert "5 consecutive" in output

    def test_warning_above_threshold(self, isolated_state):
        """Warning should continue to be emitted above threshold."""
        for i in range(6):
            _run_analysis_paralysis("Read")
        output = _run_analysis_paralysis("Read")  # 7th
        assert "[ANDON] Analysis paralysis detected" in output
        assert "7 consecutive" in output

    def test_andon_open_threshold_3(self, isolated_state):
        """When ANDON is open, threshold should be 3."""
        _write_andon_open(isolated_state["andon_file"])
        for i in range(2):
            _run_analysis_paralysis("Read")
        output = _run_analysis_paralysis("Read")  # 3rd
        assert "[ANDON] Analysis paralysis detected" in output
        assert "3 consecutive" in output

    def test_andon_open_no_warning_below_3(self, isolated_state):
        """When ANDON is open, no warning below 3 reads."""
        _write_andon_open(isolated_state["andon_file"])
        output = _run_analysis_paralysis("Read")  # 1st
        assert "[ANDON] Analysis paralysis" not in output
        output = _run_analysis_paralysis("Read")  # 2nd
        assert "[ANDON] Analysis paralysis" not in output

    def test_warning_resets_after_write(self, isolated_state):
        """After a write, counter resets and warning stops."""
        for _ in range(5):
            _run_analysis_paralysis("Read")
        output = _run_analysis_paralysis("Read")  # 6th — warning
        assert "[ANDON] Analysis paralysis detected" in output

        _run_analysis_paralysis("Edit")  # reset
        output = _run_analysis_paralysis("Read")  # 1st after reset
        assert "[ANDON] Analysis paralysis" not in output


# ============================================================
# APD-04: Counter persistence to JSON file
# ============================================================


class TestPersistence:
    def test_counter_file_created(self, isolated_state):
        """State file should be created on first call."""
        assert not isolated_state["counter_file"].exists()
        _run_analysis_paralysis("Read")
        assert isolated_state["counter_file"].exists()

    def test_counter_persisted_across_calls(self, isolated_state):
        """Counter should be persisted and read back across calls."""
        _run_analysis_paralysis("Read")
        _run_analysis_paralysis("Read")

        # Read the file directly to verify persistence
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 2

    def test_state_file_structure(self, isolated_state):
        """State file should have the expected keys."""
        _run_analysis_paralysis("Read")
        state = _load_counter(isolated_state["counter_file"])
        assert "consecutive_reads" in state
        assert "last_write_at" in state
        assert "session_id" in state

    def test_missing_state_file_handled_gracefully(self, isolated_state):
        """If state file is missing, it should be created with defaults."""
        # Ensure the file doesn't exist
        if isolated_state["counter_file"].exists():
            isolated_state["counter_file"].unlink()

        # Should not raise
        output = _run_analysis_paralysis("Read")
        state = _load_counter(isolated_state["counter_file"])
        assert state["consecutive_reads"] == 1

    def test_corrupt_state_file_handled_gracefully(self, isolated_state):
        """If state file is corrupt, it should be recreated."""
        counter_file = isolated_state["counter_file"]
        counter_file.parent.mkdir(parents=True, exist_ok=True)
        counter_file.write_text("not valid json", encoding="utf-8")

        # Should not raise — load_json returns {} for corrupt files
        output = _run_analysis_paralysis("Read")
        state = _load_counter(counter_file)
        assert state["consecutive_reads"] == 1

    def test_file_permissions(self, isolated_state):
        """State file should have 0o640 permissions."""
        _run_analysis_paralysis("Read")
        counter_file = isolated_state["counter_file"]
        mode = counter_file.stat().st_mode & 0o777
        assert mode == 0o640, f"Expected 0o640, got {oct(mode)}"
