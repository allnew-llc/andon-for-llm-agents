# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/allnew-llc/andon-for-llm-agents/releases/tag/v0.1.0
