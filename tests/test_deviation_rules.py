#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for deviation rules hierarchy (DEV-01 .. DEV-05).

Validates action level assignment, level-aware behavior in classify/incident/
runtime, pack override support, and backward compatibility.
"""

import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Ensure hooks/ is on sys.path
HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import pytest  # noqa: E402

from kaizen_classify import (  # noqa: E402
    ACTION_LEVELS,
    CLASSIFICATION_RULES,
    CLASSIFICATION_TO_LEVEL,
    classify_failure,
    get_action_level,
)
from kaizen_incident import enrich_analysis_for_level  # noqa: E402

# ---------------------------------------------------------------------------
# Importlib shim for hyphenated module name (tps-kaizen-runtime.py)
# ---------------------------------------------------------------------------
_spec = importlib.util.spec_from_file_location(
    "tps_kaizen_runtime",
    HOOKS_DIR / "tps-kaizen-runtime.py",
)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

open_from_payload = _mod.open_from_payload


# ============================================================
# DEV-01: Default action levels for each classification
# ============================================================


class TestDefaultActionLevels:
    """Each built-in classification has a correct default level."""

    def test_level_1_classifications(self):
        for cls in ACTION_LEVELS["auto_fix"]:
            assert CLASSIFICATION_TO_LEVEL[cls] == 1, f"{cls} should be level 1"

    def test_level_2_classifications(self):
        for cls in ACTION_LEVELS["auto_fix_log"]:
            assert CLASSIFICATION_TO_LEVEL[cls] == 2, f"{cls} should be level 2"

    def test_level_3_classifications(self):
        for cls in ACTION_LEVELS["pause_propose"]:
            assert CLASSIFICATION_TO_LEVEL[cls] == 3, f"{cls} should be level 3"

    def test_all_classification_rules_have_levels(self):
        """Every cause_id in CLASSIFICATION_RULES has an entry in the level map."""
        for cause_id, _label, _score, _pattern in CLASSIFICATION_RULES:
            level = get_action_level(cause_id)
            assert 1 <= level <= 4, (
                f"{cause_id} level {level} out of range"
            )

    def test_command_not_found_is_level_1(self):
        assert get_action_level("command_not_found") == 1

    def test_python_module_missing_is_level_1(self):
        assert get_action_level("python_module_missing") == 1

    def test_node_module_missing_is_level_1(self):
        assert get_action_level("node_module_missing") == 1

    def test_permission_denied_is_level_2(self):
        assert get_action_level("permission_denied") == 2

    def test_path_missing_is_level_2(self):
        assert get_action_level("path_missing") == 2

    def test_timeout_is_level_3(self):
        assert get_action_level("timeout") == 3

    def test_assertion_failure_is_level_3(self):
        assert get_action_level("assertion_failure") == 3

    def test_unknown_classification_defaults_to_level_2(self):
        assert get_action_level("some_unknown_thing") == 2
        assert get_action_level("") == 2
        assert get_action_level("totally_new_error") == 2


# ============================================================
# DEV-02: classify_failure() returns action_level
# ============================================================


class TestClassifyFailureActionLevel:
    """classify_failure() includes action_level in return dict."""

    def test_action_level_present_in_result(self):
        result = classify_failure("foo: command not found", "foo: command not found")
        assert "action_level" in result

    def test_command_not_found_returns_level_1(self):
        result = classify_failure("foo", "foo: command not found")
        assert result["action_level"] == 1
        assert result["cause_id"] == "command_not_found"

    def test_permission_denied_returns_level_2(self):
        result = classify_failure("cat /root/x", "permission denied")
        assert result["action_level"] == 2
        assert result["cause_id"] == "permission_denied"

    def test_timeout_returns_level_3(self):
        result = classify_failure("curl http://x", "timed out")
        assert result["action_level"] == 3
        assert result["cause_id"] == "timeout"

    def test_unknown_failure_returns_level_2(self):
        result = classify_failure("wat", "something weird happened")
        assert result["action_level"] == 2
        assert result["cause_id"] == "unknown_failure"

    def test_pack_overrides_applied(self):
        """Pack overrides change the action_level in classify_failure."""
        overrides = {"command_not_found": 4}
        result = classify_failure(
            "foo", "foo: command not found",
            pack_overrides=overrides,
        )
        assert result["action_level"] == 4
        assert result["cause_id"] == "command_not_found"

    def test_backward_compatibility_no_extra_args(self):
        """Existing callers without pack_overrides still work."""
        result = classify_failure("pip install x", "ModuleNotFoundError: No module named 'x'")
        assert result["cause_id"] == "python_module_missing"
        assert result["action_level"] == 1
        # All original keys still present
        for key in (
            "cause_id", "cause_label", "confidence", "matched_pattern",
            "details", "prevention_actions", "standardization_actions",
            "recommended_skills",
        ):
            assert key in result, f"Missing key: {key}"


# ============================================================
# DEV-03: Pack override support via get_action_level
# ============================================================


class TestPackOverrides:
    """Pack overrides escalate or de-escalate classifications."""

    def test_override_escalates(self):
        # command_not_found normally level 1, override to 3
        assert get_action_level("command_not_found", {"command_not_found": 3}) == 3

    def test_override_deescalates(self):
        # timeout normally level 3, override to 1
        assert get_action_level("timeout", {"timeout": 1}) == 1

    def test_override_to_level_4(self):
        assert get_action_level("path_missing", {"path_missing": 4}) == 4

    def test_override_clamped_to_valid_range(self):
        # Out-of-range values are clamped to 1-4
        assert get_action_level("timeout", {"timeout": 0}) == 1
        assert get_action_level("timeout", {"timeout": 99}) == 4

    def test_override_for_unknown_classification(self):
        assert get_action_level("custom_error", {"custom_error": 4}) == 4

    def test_override_does_not_affect_other_classifications(self):
        overrides = {"timeout": 1}
        assert get_action_level("timeout", overrides) == 1
        # Other classifications unaffected
        assert get_action_level("command_not_found", overrides) == 1
        assert get_action_level("permission_denied", overrides) == 2

    def test_none_overrides_ignored(self):
        assert get_action_level("timeout", None) == 3

    def test_empty_overrides_ignored(self):
        assert get_action_level("timeout", {}) == 3


# ============================================================
# DEV-04: enrich_analysis_for_level
# ============================================================


class TestEnrichAnalysisForLevel:
    """Level-aware enrichment of analysis and actions dicts."""

    def test_level_1_no_enrichment(self):
        analysis = {"action_level": 1, "cause_id": "command_not_found"}
        actions = {}
        enrich_analysis_for_level(analysis, actions)
        assert "proposed_fix" not in analysis
        assert "requires_approval" not in analysis

    def test_level_2_no_enrichment(self):
        analysis = {"action_level": 2, "cause_id": "permission_denied"}
        actions = {}
        enrich_analysis_for_level(analysis, actions)
        assert "proposed_fix" not in analysis
        assert "requires_approval" not in analysis

    def test_level_3_adds_proposed_fix(self):
        analysis = {
            "action_level": 3,
            "cause_id": "timeout",
            "standardization_actions": [
                {"type": "retry_policy", "value": "bounded_retry"},
            ],
        }
        actions = {}
        enrich_analysis_for_level(analysis, actions)
        assert "proposed_fix" in analysis
        assert "timeout" in analysis["proposed_fix"]
        assert "bounded_retry" in analysis["proposed_fix"]
        assert "requires_approval" not in analysis

    def test_level_3_no_standardization_actions(self):
        analysis = {
            "action_level": 3,
            "cause_id": "timeout",
            "standardization_actions": [],
        }
        actions = {}
        enrich_analysis_for_level(analysis, actions)
        assert "proposed_fix" in analysis
        assert "review required" in analysis["proposed_fix"]

    def test_level_4_adds_requires_approval(self):
        analysis = {"action_level": 4, "cause_id": "critical_failure"}
        actions = {}
        enrich_analysis_for_level(analysis, actions)
        assert analysis.get("requires_approval") is True
        assert "proposed_fix" not in analysis

    def test_missing_action_level_defaults_to_2(self):
        analysis = {"cause_id": "something"}
        actions = {}
        enrich_analysis_for_level(analysis, actions)
        assert "proposed_fix" not in analysis
        assert "requires_approval" not in analysis


# ============================================================
# DEV-05: Level-based runtime behavior (open_from_payload)
# ============================================================


def _make_payload(command: str, output: str, exit_code: int = 1) -> dict:
    """Build a minimal PostToolUse payload.

    Uses top-level ``stdout`` so that ``collect_text_blobs`` picks it up,
    and ``tool_result`` dict with ``exitCode`` so ``derive_exit_code`` finds it.
    """
    return {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "tool_result": {"exitCode": exit_code},
        "stdout": output,
        "stderr": "",
    }


class TestLevel1NoAndonOpen:
    """Level 1: Auto-fix only, no ANDON open."""

    def test_level_1_does_not_write_andon_file(self, tmp_path, monkeypatch):
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        monkeypatch.setattr(_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(_mod, "ANDON_FILE", state_dir / "andon-open.json")
        monkeypatch.setattr(_mod, "KAIZEN_DIR", state_dir / "kaizen")
        monkeypatch.setattr(_mod, "INCIDENTS_DIR", state_dir / "kaizen" / "incidents")
        monkeypatch.setattr(_mod, "HISTORY_DIR", state_dir / "history")
        monkeypatch.setattr(_mod, "STANDARD_REGISTRY", state_dir / "kaizen" / "standardization-registry.json")

        # Also patch kaizen_core paths so ensure_dirs works
        import kaizen_core
        monkeypatch.setattr(kaizen_core, "STATE_DIR", state_dir)
        monkeypatch.setattr(kaizen_core, "ANDON_FILE", state_dir / "andon-open.json")
        monkeypatch.setattr(kaizen_core, "KAIZEN_DIR", state_dir / "kaizen")
        monkeypatch.setattr(kaizen_core, "INCIDENTS_DIR", state_dir / "kaizen" / "incidents")
        monkeypatch.setattr(kaizen_core, "HISTORY_DIR", state_dir / "history")

        payload = _make_payload("foo", "foo: command not found")
        monkeypatch.setenv("INPUT_JSON", json.dumps(payload))

        captured = []
        monkeypatch.setattr(_mod, "print_empty", lambda: captured.append("empty"))
        monkeypatch.setattr(
            _mod, "print_hook_context",
            lambda msg, block: captured.append(("hook", msg, block)),
        )

        result = open_from_payload()

        assert result == 0
        # ANDON file should NOT be created for level 1
        andon_file = state_dir / "andon-open.json"
        assert not andon_file.exists()
        # Should have called print_empty (no ANDON output)
        assert "empty" in captured


class TestLevel2ExistingBehavior:
    """Level 2: Existing behavior preserved (ANDON open + auto-standardize)."""

    def test_level_2_opens_andon(self, tmp_path, monkeypatch):
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        monkeypatch.setattr(_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(_mod, "ANDON_FILE", state_dir / "andon-open.json")
        monkeypatch.setattr(_mod, "KAIZEN_DIR", state_dir / "kaizen")
        monkeypatch.setattr(_mod, "INCIDENTS_DIR", state_dir / "kaizen" / "incidents")
        monkeypatch.setattr(_mod, "HISTORY_DIR", state_dir / "history")
        monkeypatch.setattr(_mod, "STANDARD_REGISTRY", state_dir / "kaizen" / "standardization-registry.json")

        import kaizen_core
        monkeypatch.setattr(kaizen_core, "STATE_DIR", state_dir)
        monkeypatch.setattr(kaizen_core, "ANDON_FILE", state_dir / "andon-open.json")
        monkeypatch.setattr(kaizen_core, "KAIZEN_DIR", state_dir / "kaizen")
        monkeypatch.setattr(kaizen_core, "INCIDENTS_DIR", state_dir / "kaizen" / "incidents")
        monkeypatch.setattr(kaizen_core, "HISTORY_DIR", state_dir / "history")
        monkeypatch.setattr(kaizen_core, "STANDARD_REGISTRY", state_dir / "kaizen" / "standardization-registry.json")

        # permission_denied is level 2; use chmod (not a readonly command)
        payload = _make_payload("chmod 755 /root/secret", "permission denied")
        monkeypatch.setenv("INPUT_JSON", json.dumps(payload))

        captured = []
        monkeypatch.setattr(
            _mod, "print_hook_context",
            lambda msg, block: captured.append(("hook", msg, block)),
        )

        result = open_from_payload()

        assert result == 0
        andon_file = state_dir / "andon-open.json"
        assert andon_file.exists()
        andon = json.loads(andon_file.read_text(encoding="utf-8"))
        assert andon["status"] == "open"
        assert andon.get("action_level") == 2

        # Message should use TPS/ANDON format (existing behavior)
        assert len(captured) == 1
        msg = captured[0][1]
        assert "[TPS/ANDON]" in msg


class TestLevel3ProposeFix:
    """Level 3: ANDON open + proposed fix in additionalContext."""

    def test_level_3_opens_andon_with_proposal(self, tmp_path, monkeypatch):
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        monkeypatch.setattr(_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(_mod, "ANDON_FILE", state_dir / "andon-open.json")
        monkeypatch.setattr(_mod, "KAIZEN_DIR", state_dir / "kaizen")
        monkeypatch.setattr(_mod, "INCIDENTS_DIR", state_dir / "kaizen" / "incidents")
        monkeypatch.setattr(_mod, "HISTORY_DIR", state_dir / "history")
        monkeypatch.setattr(_mod, "STANDARD_REGISTRY", state_dir / "kaizen" / "standardization-registry.json")

        import kaizen_core
        monkeypatch.setattr(kaizen_core, "STATE_DIR", state_dir)
        monkeypatch.setattr(kaizen_core, "ANDON_FILE", state_dir / "andon-open.json")
        monkeypatch.setattr(kaizen_core, "KAIZEN_DIR", state_dir / "kaizen")
        monkeypatch.setattr(kaizen_core, "INCIDENTS_DIR", state_dir / "kaizen" / "incidents")
        monkeypatch.setattr(kaizen_core, "HISTORY_DIR", state_dir / "history")
        monkeypatch.setattr(kaizen_core, "STANDARD_REGISTRY", state_dir / "kaizen" / "standardization-registry.json")

        # timeout is level 3
        payload = _make_payload("curl http://slow", "request timed out")
        monkeypatch.setenv("INPUT_JSON", json.dumps(payload))

        captured = []
        monkeypatch.setattr(
            _mod, "print_hook_context",
            lambda msg, block: captured.append(("hook", msg, block)),
        )

        result = open_from_payload()

        assert result == 0
        andon_file = state_dir / "andon-open.json"
        assert andon_file.exists()
        andon = json.loads(andon_file.read_text(encoding="utf-8"))
        assert andon["status"] == "open"
        assert andon.get("action_level") == 3

        # Message should contain Level-3 proposal
        assert len(captured) == 1
        msg = captured[0][1]
        assert "[ANDON/Level-3]" in msg
        assert "Proposed fix" in msg
        assert captured[0][2] is True  # block=True


class TestLevel4Block:
    """Level 4: ANDON open + block + require approval."""

    def test_level_4_via_pack_override(self, tmp_path, monkeypatch):
        """Use a pack override to force level 4, then verify behavior."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        monkeypatch.setattr(_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(_mod, "ANDON_FILE", state_dir / "andon-open.json")
        monkeypatch.setattr(_mod, "KAIZEN_DIR", state_dir / "kaizen")
        monkeypatch.setattr(_mod, "INCIDENTS_DIR", state_dir / "kaizen" / "incidents")
        monkeypatch.setattr(_mod, "HISTORY_DIR", state_dir / "history")
        monkeypatch.setattr(_mod, "STANDARD_REGISTRY", state_dir / "kaizen" / "standardization-registry.json")

        import kaizen_core
        monkeypatch.setattr(kaizen_core, "STATE_DIR", state_dir)
        monkeypatch.setattr(kaizen_core, "ANDON_FILE", state_dir / "andon-open.json")
        monkeypatch.setattr(kaizen_core, "KAIZEN_DIR", state_dir / "kaizen")
        monkeypatch.setattr(kaizen_core, "INCIDENTS_DIR", state_dir / "kaizen" / "incidents")
        monkeypatch.setattr(kaizen_core, "HISTORY_DIR", state_dir / "history")
        monkeypatch.setattr(kaizen_core, "STANDARD_REGISTRY", state_dir / "kaizen" / "standardization-registry.json")

        # We need to test level 4 behavior. Since stop_ask is empty by default,
        # we test enrich_analysis_for_level directly for the level-4 enrichment,
        # and verify the message format via mocking classify_failure to return
        # action_level=4.
        original_classify = _mod.classify_failure

        def mock_classify(*args, **kwargs):
            result = original_classify(*args, **kwargs)
            result["action_level"] = 4
            return result

        monkeypatch.setattr(_mod, "classify_failure", mock_classify)

        payload = _make_payload("rm -rf /", "permission denied")
        monkeypatch.setenv("INPUT_JSON", json.dumps(payload))

        captured = []
        monkeypatch.setattr(
            _mod, "print_hook_context",
            lambda msg, block: captured.append(("hook", msg, block)),
        )

        result = open_from_payload()

        assert result == 0
        andon_file = state_dir / "andon-open.json"
        assert andon_file.exists()
        andon = json.loads(andon_file.read_text(encoding="utf-8"))
        assert andon["status"] == "open"
        assert andon.get("action_level") == 4

        # Message should contain Level-4 block
        assert len(captured) == 1
        msg = captured[0][1]
        assert "[ANDON/Level-4]" in msg
        assert "requires human approval" in msg
        assert captured[0][2] is True  # block=True


# ============================================================
# DEV-05: Backward compatibility
# ============================================================


class TestBackwardCompatibility:
    """Existing tests and callers remain functional."""

    def test_classify_failure_signature_unchanged(self):
        """Can call classify_failure with only positional args."""
        result = classify_failure("ls", "ls: cannot access: No such file or directory")
        assert "cause_id" in result
        assert "cause_label" in result
        assert "confidence" in result
        assert "action_level" in result

    def test_classify_failure_with_keyword_args(self):
        """Can call with existing keyword args."""
        result = classify_failure(
            "npm run build",
            "Cannot find module 'react'",
            init_packs=None,
            pack_bundle=None,
        )
        assert result["cause_id"] == "node_module_missing"
        assert result["action_level"] == 1

    def test_action_levels_dict_structure(self):
        """ACTION_LEVELS has the expected structure."""
        assert "auto_fix" in ACTION_LEVELS
        assert "auto_fix_log" in ACTION_LEVELS
        assert "pause_propose" in ACTION_LEVELS
        assert "stop_ask" in ACTION_LEVELS
        assert len(ACTION_LEVELS) == 4

    def test_classification_to_level_is_complete(self):
        """All classifications from ACTION_LEVELS are in the reverse lookup."""
        for level_name, classifications in ACTION_LEVELS.items():
            for cls in classifications:
                assert cls in CLASSIFICATION_TO_LEVEL
