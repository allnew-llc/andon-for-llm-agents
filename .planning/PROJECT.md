# ANDON for LLM Agents

## What This Is

TPS (Toyota Production System) inspired safety and continuous improvement framework for LLM coding agents. Provides Claude Code hooks that detect anomalies, stop defect propagation, perform root cause analysis (Five Whys), and standardize learnings. Open source (Apache 2.0), published as `andon-for-llm-agents` on PyPI.

## Core Value

Stop defects from flowing downstream and learn from every failure — applied to LLM-assisted coding through Jidoka (autonomation) and Kaizen (continuous improvement).

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ **JIDOKA-01**: ANDON line stop on non-zero exit codes — v0.1.0
- ✓ **JIDOKA-02**: Forward-progress blocking (push, deploy, publish) during ANDON — v0.1.0
- ✓ **JIDOKA-03**: ANDON close with 4-artifact validation (evidence, analysis, actions, report) — v0.1.0
- ✓ **JIDOKA-04**: Confidence threshold (0.70) for close approval — v0.1.0
- ✓ **JIDOKA-05**: ANDON rollback support — v0.1.0
- ✓ **KAIZEN-01**: Five Whys root cause analysis framework — v0.1.0
- ✓ **KAIZEN-02**: Kaizen learning capture and routing — v0.1.0
- ✓ **KAIZEN-03**: Improvement Kata cycle (understand/grasp/target/experiment) — v0.1.0
- ✓ **KAIZEN-04**: 3M waste audit (Muda/Mura/Muri) — v0.1.0
- ✓ **GUARD-01**: Analysis paralysis detection (consecutive read-only tools) — v0.2.0
- ✓ **GUARD-02**: Context quality monitor (tool call count proxy) — v0.2.0
- ✓ **GUARD-03**: Self-check protocol (artifact size/parse/key validation) — v0.2.0
- ✓ **GUARD-04**: Deviation rules hierarchy (Level 1-4 action system) — v0.2.0
- ✓ **PACK-01**: Domain-specific knowledge packs (financial, GDPR, HIPAA, iOS, japan-legal) — v0.1.0
- ✓ **SEC-01**: Process-safe state files with flock — v0.2.0
- ✓ **SEC-02**: Prompt injection boundary markers — v0.2.0
- ✓ **SEC-03**: Path traversal validation — v0.2.0
- ✓ **SEC-04**: Secret redaction patterns — v0.2.0

### Active

<!-- Current scope. Building toward these. -->

## Current Milestone: v0.3.0 Skill Quality & Ecosystem

**Goal:** Anthropic ベストプラクティスに基づくスキル品質向上と Claude 環境エコシステム拡充

**Target features:**
- tps-kaizen スキルの全面改善（description, gotchas, scripts, persistent data, composability）
- /qc-audit スキル新設（品質自己評価の能動的実行・トレンド分析）
- 環境スキルの SKILL.md 昇格と On-Demand Hooks 化
- 新スキルカテゴリ追加（freee-analysis, cleanup-artifacts, standup）

### Out of Scope

- GUI dashboard — CLI-first, no web UI
- Non-Claude Code agents — Claude Code hooks only for now
- Real-time metrics collection — Batch analysis sufficient

## Context

- Published on GitHub: allnew-llc/andon-for-llm-agents
- Python 3.10+, single dependency (PyYAML)
- Includes TPS Kaizen skill for Claude Code (`skills/tps-kaizen/`)
- Integrated with AllNew LLC's ios-app-factory pipeline
- User's local Claude environment has 8 custom skills, 18 hooks, 36 plugins

## Constraints

- **License**: Apache 2.0 — all additions must be compatible
- **Python**: >=3.10, minimal dependencies
- **Backward compat**: Existing hooks/packs must continue working
- **OSS**: All improvements must be suitable for public repository

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Shell hooks + Python guards | Claude Code hooks are shell-based, complex logic in Python | ✓ Good |
| Knowledge Packs for domain rules | Extensible without core changes | ✓ Good |
| Deviation rules hierarchy (L1-L4) | Different failures need different responses | ✓ Good |
| TPS terminology throughout | Consistent mental model, educational value | ✓ Good |

---
*Last updated: 2026-03-19 after brownfield initialization*
