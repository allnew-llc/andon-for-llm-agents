#!/usr/bin/env python3
"""domain_classifier.py — Domain Classification Engine for ANDON

Scores failure output against knowledge domains and recommends
relevant skills from loaded Knowledge Packs.

7 built-in generic domains.  Domain-specific packs (legal, iOS, etc.)
add their own domains + keywords via knowledge-pack.yaml.

Copyright 2026 AllNew LLC
Licensed under Apache License 2.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# ============================================================
# Built-in domains (generic — no vendor/project specifics)
# ============================================================

BUILTIN_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "security": [
        "vulnerability", "injection", "xss", "csrf", "auth", "authentication",
        "authorization", "permission", "credential", "secret", "token",
        "certificate", "ssl", "tls", "encryption", "decrypt",
    ],
    "quality_test": [
        "test", "assert", "failure", "coverage", "regression", "unittest",
        "pytest", "xctest", "spec", "expect", "mock", "stub", "fixture",
    ],
    "architecture": [
        "design pattern", "coupling", "cohesion", "refactor", "dependency",
        "module", "interface", "abstraction", "solid", "dry", "separation",
    ],
    "process": [
        "workflow", "pipeline", "ci/cd", "deploy", "release", "blocker",
        "configuration", "environment", "setup", "install", "migration",
    ],
    "legal": [
        "law", "regulation", "compliance", "privacy", "gdpr", "appi",
        "terms of service", "license", "copyright", "trademark", "patent",
    ],
    "data": [
        "database", "migration", "schema", "query", "sql", "nosql",
        "backup", "restore", "corruption", "integrity",
    ],
    "operations": [
        "incident", "outage", "monitoring", "alert", "log", "metric",
        "health check", "timeout", "retry", "throttle", "rate limit",
    ],
}

# Map common failure cause_ids to domains
BUILTIN_CAUSE_TO_DOMAIN: dict[str, str] = {
    "command_not_found": "process",
    "python_module_missing": "process",
    "node_module_missing": "process",
    "permission_denied": "security",
    "path_missing": "process",
    "timeout": "operations",
    "assertion_failure": "quality_test",
    "unknown_failure": "",
}


@dataclass
class DomainScore:
    """Score for a single domain."""
    domain_id: str
    score: float
    matched_keywords: list[str] = field(default_factory=list)


@dataclass
class SkillRecommendation:
    """A recommended knowledge skill."""
    ref: str
    path: str
    description: str
    priority: str = "primary"  # "primary" or "secondary"


def score_domains(
    text: str,
    extra_keywords: dict[str, list[dict[str, Any]]] | None = None,
) -> list[DomainScore]:
    """Score all domains against *text*.

    Returns a sorted list (highest score first).

    *extra_keywords*: additional domains/keywords from Knowledge Packs.
    Format: {"domain_id": [{"pattern": "...", "weight": 1.0}, ...]}
    """
    lower = text.lower()
    results: list[DomainScore] = []

    # Built-in domains
    for domain_id, keywords in BUILTIN_DOMAIN_KEYWORDS.items():
        score = 0.0
        matched: list[str] = []
        for kw in keywords:
            if kw in lower:
                score += 1.0
                matched.append(kw)
        if score > 0:
            results.append(DomainScore(domain_id=domain_id, score=score, matched_keywords=matched))

    # Pack-provided domains
    if extra_keywords:
        for domain_id, entries in extra_keywords.items():
            score = 0.0
            matched = []
            for entry in entries:
                pattern = entry.get("pattern", "")
                weight = float(entry.get("weight", 1.0))
                if not pattern:
                    continue
                if re.search(pattern, text, re.IGNORECASE):
                    score += weight
                    matched.append(pattern)
            if score > 0:
                # Merge with existing domain if already scored
                existing = next((r for r in results if r.domain_id == domain_id), None)
                if existing:
                    existing.score += score
                    existing.matched_keywords.extend(matched)
                else:
                    results.append(DomainScore(domain_id=domain_id, score=score, matched_keywords=matched))

    results.sort(key=lambda r: r.score, reverse=True)
    return results


def recommend_skills(
    cause_id: str,
    command: str,
    output: str,
    skill_map: dict[str, dict[str, list[dict[str, str]]]] | None = None,
    extra_keywords: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Recommend knowledge skills based on failure context.

    Returns:
        {
            "domain": "security",
            "domain_scores": [...],
            "primary": [...],
            "secondary": [...],
        }
    """
    # Determine primary domain
    domain = BUILTIN_CAUSE_TO_DOMAIN.get(cause_id, "")

    # If cause_id doesn't map cleanly, use keyword scoring
    text = f"{command}\n{output}"
    domain_scores = score_domains(text, extra_keywords)

    if not domain and domain_scores:
        domain = domain_scores[0].domain_id

    result: dict[str, Any] = {
        "domain": domain,
        "domain_scores": [
            {"domain_id": ds.domain_id, "score": ds.score, "matched": ds.matched_keywords}
            for ds in domain_scores[:5]
        ],
        "primary": [],
        "secondary": [],
    }

    # Look up skills from pack-provided skill_map
    if skill_map and domain and domain in skill_map:
        mapping = skill_map[domain]
        result["primary"] = mapping.get("primary", [])
        result["secondary"] = mapping.get("secondary", [])

    return result
