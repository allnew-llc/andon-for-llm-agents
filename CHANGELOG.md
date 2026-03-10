# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-10

### Added

- **Analysis Paralysis Guard** — detects consecutive Read/Grep/Glob without code changes
  - Threshold 5 (normal) / 3 (ANDON open) consecutive read-only tool calls
  - Warning injected via additionalContext (non-blocking)
  - Counter state persisted in `~/.claude/state/andon-analysis-counter.json`
- **Context Quality Monitor** — proxy-based context window degradation detection
  - Tool call count as proxy metric (PEAK/GOOD/DEGRADING/POOR)
  - Warnings at 60+ calls (DEGRADING) and 100+ calls (POOR)
  - Additional warning when Five Whys runs in degraded context
  - Warn-once semantics (no duplicate warnings per level transition)
- **Self-Check Protocol Enhancement** — stronger validation on ANDON close
  - File size minimum (10 bytes) for JSON artifacts
  - JSON parse validation for evidence/analysis/actions
  - Required key check for evidence.json (command, exit_code, output_snippet)
  - Section header count check for report.md (minimum 2)
- **Deviation Rules Hierarchy** — action level system for failure classifications
  - Level 1 (auto_fix): auto-fix, log only, no ANDON open
  - Level 2 (auto_fix_log): auto-fix + incident record (existing behavior)
  - Level 3 (pause_propose): ANDON open + proposed fix injection
  - Level 4 (stop_ask): ANDON open + complete block (user approval required)
  - Pack-extensible: Knowledge Packs can override action levels per classification

## [0.1.2] - 2026-03-10

### Fixed

- Replace "compliance" terminology with "statute retrieval" across japan-legal pack
  (README, knowledge-pack.yaml, all 6 skills, CONTRIBUTING-PACKS.md, CHANGELOG.md)
- Remove incorrect "compatible with CC BY 4.0" claim from japan-legal pack README
  (Government Standard Terms of Use v2.0 is a separate framework)
- Reframe Pack 0 as keyword-based heuristic filter (not a guarantee of detection)
- Add disclaimer to Knowledge Packs section clarifying no compliance guarantee

## [0.1.1] - 2026-03-08

### Fixed

- Add CLI entry point (`andon` command) via `[project.scripts]`
- Fix PEP 639 License classifier conflict with `license = "Apache-2.0"`
- Fix setuptools flat-layout auto-detection error (explicit `packages = ["hooks"]`)

## [0.1.0] - 2026-03-08

### Added

- **ANDON Runtime Engine** — PostToolUse/PreToolUse hooks for Claude Code
  - Automatic failure detection on non-zero exit codes
  - Pattern-based root cause classification with confidence scoring
  - Incident report generation (evidence, analysis, report)
  - Standardization registry for proactive prevention rules
  - Line stop enforcement — blocks `git push`/deploy until ANDON is closed
- **Output Safety Guard (Pack 0)** — deterministic scan for unauthorized professional practice
  - YAML-based pattern files for legal, tax, and financial advice detection
  - GUARD level: preserves content + injects disclaimer and professional referral
  - English and Japanese pattern support
- **Meta-ANDON** — repeated failure pattern detection
  - Triggers on 3+ consecutive full-run failures
  - Forces plan mode (read-only) until structured analysis is complete
  - Requires 4 mandatory artifacts: Five Whys, Risk Table, Sweep Report, Batch Fix Plan
- **Domain Classifier** — keyword-based failure domain scoring engine
- **Knowledge Pack System** — extensible YAML manifests for domain expertise
  - Pack loader with validation, regulated domain enforcement (Pack 0 dependency)
  - CLI: `andon pack validate`, `andon pack list`
- **Built-in Knowledge Packs**
  - `andon-pack-japan-legal` — Japanese law statute retrieval (e-Gov API) (Stable)
  - `andon-pack-ios-development` — iOS / App Store development (Stable)
  - `andon-pack-gdpr` — EU GDPR compliance (Alpha)
  - `andon-pack-financial` — PCI-DSS, AML/KYC (Alpha)
  - `andon-pack-hipaa` — HIPAA healthcare compliance (Alpha)
  - `sample-web-api-security` — API security example pack
- **Interactive Demo** — 5-stage guided tour with retro-game UI
  - English/Japanese i18n support
  - README viewer with section navigation
- **Documentation**
  - README.md / README.ja.md — comprehensive project overview
  - INTEGRATION.md / INTEGRATION.ja.md — full setup guide
  - CONTRIBUTING.md / CONTRIBUTING.ja.md — contribution guidelines
  - CONTRIBUTING-PACKS.md — Knowledge Pack specification
  - SECURITY.md — vulnerability disclosure policy
- **CI/CD** — GitHub Actions workflow testing Python 3.10–3.14

[0.2.0]: https://github.com/allnew-llc/andon-for-llm-agents/releases/tag/v0.2.0
[0.1.2]: https://github.com/allnew-llc/andon-for-llm-agents/releases/tag/v0.1.2
[0.1.1]: https://github.com/allnew-llc/andon-for-llm-agents/releases/tag/v0.1.1
[0.1.0]: https://github.com/allnew-llc/andon-for-llm-agents/releases/tag/v0.1.0
