#!/usr/bin/env python3
# Copyright 2026 AllNew LLC
# Licensed under Apache License 2.0
"""Tests for Pack 0: Output Safety Guard + Domain Classifier + Pack Loader"""

import sys
from pathlib import Path

# Ensure hooks/ is on sys.path
HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import pytest  # noqa: E402
from domain_classifier import (  # noqa: E402
    BUILTIN_DOMAIN_KEYWORDS,
    recommend_skills,
    score_domains,
)
from output_safety_guard import (  # noqa: E402
    GuardCategory,
    GuardLevel,
    GuardResult,
    OutputSafetyGuard,
    load_all_categories,
)
from pack_loader import PackLoader  # noqa: E402

# ============================================================
# Output Safety Guard — YAML loading
# ============================================================

class TestYAMLLoading:
    def test_load_all_categories_from_builtin(self):
        cats = load_all_categories()
        assert len(cats) == 2, f"Expected 2 categories, got {len(cats)}"
        for expected in GuardCategory:
            assert expected in cats, f"Missing category: {expected}"

    def test_each_category_has_patterns(self):
        cats = load_all_categories()
        for cat, cat_def in cats.items():
            assert len(cat_def.patterns) > 0, f"{cat.value} has no patterns"

    def test_guard_categories_are_correct(self):
        cats = load_all_categories()
        guard_expected = {
            GuardCategory.UPL,
            GuardCategory.UNQUALIFIED,
        }
        for cat in guard_expected:
            assert cats[cat].level == GuardLevel.GUARD, f"{cat.value} should be GUARD"


# ============================================================
# Output Safety Guard — Pattern matching
# ============================================================

class TestPatternMatching:
    @pytest.fixture
    def guard(self):
        return OutputSafetyGuard()

    # --- UPL (GUARD) ---

    def test_upl_legal_advice_en(self, guard):
        r = guard.check("You should file a lawsuit against them immediately.")
        assert r.triggered
        assert r.category == GuardCategory.UPL
        assert r.level == GuardLevel.GUARD

    def test_upl_legal_advice_ja(self, guard):
        r = guard.check("提訴すべきです。法的措置を取るべきです。")
        assert r.triggered
        assert r.category == GuardCategory.UPL

    def test_upl_disclaimer_present(self, guard):
        r = guard.check("I recommend filing a complaint with the court.")
        assert r.triggered
        assert r.disclaimer is not None
        assert "legal advice" in r.disclaimer.lower() or "法的助言" in r.disclaimer

    # --- Unqualified professional (GUARD) ---

    def test_unqualified_tax_advice(self, guard):
        r = guard.check("You should deduct your home office from taxes this year.")
        assert r.triggered
        assert r.category == GuardCategory.UNQUALIFIED
        assert r.level == GuardLevel.GUARD

    # --- Safe content ---

    def test_safe_content_not_triggered(self, guard):
        r = guard.check("The weather in Tokyo is sunny today.")
        assert not r.triggered

    def test_programming_not_triggered(self, guard):
        r = guard.check("def hello(): print('Hello, world!')")
        assert not r.triggered

    def test_general_law_discussion_not_triggered(self, guard):
        # General mention of law without directive language should not trigger
        r = guard.check("The privacy regulation requires companies to handle data carefully.")
        assert not r.triggered


# ============================================================
# Output Safety Guard — apply_guard
# ============================================================

class TestApplyGuard:
    @pytest.fixture
    def guard(self):
        return OutputSafetyGuard()

    def test_guard_adds_disclaimer(self, guard):
        result = GuardResult(
            triggered=True,
            level=GuardLevel.GUARD,
            category=GuardCategory.UPL,
            reason="Output guarded",
            disclaimer="⚠️ Not legal advice",
            professional_referral="Attorney",
        )
        output = guard.apply_guard("Some legal information here.", result)
        assert "⚠️ Not legal advice" in output
        assert "Attorney" in output
        assert "Some legal information here." in output

    def test_warn_appends_note(self, guard):
        result = GuardResult(
            triggered=True,
            level=GuardLevel.WARN,
            category=GuardCategory.UPL,
            reason="Advisory",
            disclaimer="Please consult a professional.",
        )
        output = guard.apply_guard("General discussion.", result)
        assert "General discussion." in output
        assert "professional" in output.lower()

    def test_safe_passthrough(self, guard):
        result = GuardResult(triggered=False)
        output = guard.apply_guard("Normal text", result)
        assert output == "Normal text"


# ============================================================
# Output Safety Guard — merge_pack_extensions
# ============================================================

class TestPackExtensions:
    def test_merge_adds_patterns(self):
        guard = OutputSafetyGuard()
        initial_count = len(guard._cats[GuardCategory.UPL].patterns)

        guard.merge_pack_extensions([{
            "category": "unauthorized_practice_of_law",
            "extra_patterns": [
                {"pattern": "(弁護士法72条|非弁行為)", "weight": 1.0},
            ],
        }])

        assert len(guard._cats[GuardCategory.UPL].patterns) == initial_count + 1

    def test_merged_pattern_triggers(self):
        guard = OutputSafetyGuard()
        guard.merge_pack_extensions([{
            "category": "unauthorized_practice_of_law",
            "extra_patterns": [
                {"pattern": "非弁行為", "weight": 1.0},
            ],
        }])
        r = guard.check("これは非弁行為に該当する可能性があります")
        assert r.triggered
        assert r.category == GuardCategory.UPL

    def test_merge_unknown_category_ignored(self):
        guard = OutputSafetyGuard()
        # Should not raise — unknown category is silently skipped
        guard.merge_pack_extensions([{
            "category": "nonexistent_category",
            "extra_patterns": [
                {"pattern": "test", "weight": 1.0},
            ],
        }])


# ============================================================
# Domain Classifier
# ============================================================

class TestDomainClassifier:
    def test_builtin_domains_exist(self):
        assert len(BUILTIN_DOMAIN_KEYWORDS) == 7

    def test_score_security_domain(self):
        scores = score_domains("Found XSS vulnerability in authentication module")
        assert len(scores) > 0
        assert scores[0].domain_id == "security"

    def test_score_test_domain(self):
        scores = score_domains("pytest assertion failure in test_login: expected True")
        assert len(scores) > 0
        top = scores[0]
        assert top.domain_id == "quality_test"

    def test_score_with_extra_keywords(self):
        extra = {
            "japan_legal": [
                {"pattern": "個人情報", "weight": 2.0},
                {"pattern": "特定商取引", "weight": 1.5},
            ]
        }
        scores = score_domains("個人情報保護法に基づく同意が必要です", extra)
        assert any(s.domain_id == "japan_legal" for s in scores)

    def test_recommend_skills_with_map(self):
        skill_map = {
            "security": {
                "primary": [{"ref": "sec-guide", "path": "skills/sec.md", "description": "Security guide"}],
                "secondary": [],
            }
        }
        result = recommend_skills(
            "permission_denied", "chmod 600 secret.key",
            "Permission denied: /etc/secret.key",
            skill_map=skill_map,
        )
        assert result["domain"] == "security"
        assert len(result["primary"]) == 1
        assert result["primary"][0]["ref"] == "sec-guide"

    def test_recommend_skills_empty_map(self):
        result = recommend_skills("unknown_failure", "foo", "bar")
        assert result["primary"] == []
        assert result["secondary"] == []


# ============================================================
# Pack Loader
# ============================================================

class TestPackLoader:
    def test_empty_dir(self, tmp_path):
        loader = PackLoader()
        bundle = loader.load_all(tmp_path)
        assert len(bundle.packs) == 0

    def test_load_valid_pack(self, tmp_path):
        pack_dir = tmp_path / "test-pack"
        pack_dir.mkdir()
        (pack_dir / "knowledge-pack.yaml").write_text(
            """
apiVersion: andon/v1
kind: KnowledgePack
metadata:
  name: test-pack
  version: "1.0.0"
  license: Apache-2.0
domains:
  - id: test_domain
    keywords:
      - pattern: "test keyword"
        weight: 1.0
skill_map:
  test_domain:
    primary:
      - ref: test-skill
        path: skills/test.md
        description: A test skill
    secondary: []
""",
            encoding="utf-8",
        )
        loader = PackLoader()
        bundle = loader.load_all(tmp_path)
        assert len(bundle.packs) == 1
        assert bundle.packs[0].name == "test-pack"
        assert "test_domain" in bundle.extra_keywords
        assert "test_domain" in bundle.skill_map

    def test_regulated_pack_without_pack0_blocked(self, tmp_path):
        pack_dir = tmp_path / "legal-pack"
        pack_dir.mkdir()
        (pack_dir / "knowledge-pack.yaml").write_text(
            """
apiVersion: andon/v1
kind: KnowledgePack
metadata:
  name: legal-pack
  version: "1.0.0"
requires:
  - name: output-safety-guard
    version: ">=1.0.0"
domains:
  - id: japan_legal
    keywords: []
""",
            encoding="utf-8",
        )
        # Pack 0 NOT available
        loader = PackLoader(pack0_available=False)
        bundle = loader.load_all(tmp_path)
        assert len(bundle.packs) == 0  # Should be blocked

    def test_regulated_pack_with_pack0_allowed(self, tmp_path):
        pack_dir = tmp_path / "legal-pack"
        pack_dir.mkdir()
        (pack_dir / "knowledge-pack.yaml").write_text(
            """
apiVersion: andon/v1
kind: KnowledgePack
metadata:
  name: legal-pack
  version: "1.0.0"
requires:
  - name: output-safety-guard
    version: ">=1.0.0"
domains:
  - id: japan_legal
    keywords: []
""",
            encoding="utf-8",
        )
        loader = PackLoader(pack0_available=True)
        bundle = loader.load_all(tmp_path)
        assert len(bundle.packs) == 1

    def test_validate_missing_manifest(self, tmp_path):
        loader = PackLoader()
        result = loader.validate_pack(tmp_path)
        assert not result.valid
        assert any("not found" in e for e in result.errors)

    def test_validate_missing_name(self, tmp_path):
        (tmp_path / "knowledge-pack.yaml").write_text(
            "apiVersion: andon/v1\nmetadata:\n  version: '1.0.0'\n",
            encoding="utf-8",
        )
        loader = PackLoader()
        result = loader.validate_pack(tmp_path)
        assert not result.valid

    def test_validate_regulated_without_requires(self, tmp_path):
        (tmp_path / "knowledge-pack.yaml").write_text(
            """
apiVersion: andon/v1
metadata:
  name: bad-legal-pack
  version: "1.0.0"
domains:
  - id: japan_legal
    keywords: []
""",
            encoding="utf-8",
        )
        loader = PackLoader()
        result = loader.validate_pack(tmp_path)
        assert not result.valid
        assert any("output-safety-guard" in e for e in result.errors)
