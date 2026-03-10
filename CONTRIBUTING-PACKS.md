# Knowledge Pack Specification

> **apiVersion**: `andon/v1`
> **Status**: Stable (v1.0)

This document defines the structure, validation rules, and authoring guidelines
for ANDON Knowledge Packs.

## What Is a Knowledge Pack?

A Knowledge Pack is a self-contained plugin that teaches the ANDON runtime about
a specific domain — adding failure-detection keywords, classification rules,
skill recommendations, and (optionally) output safety extensions.

When an LLM agent hits an error, ANDON classifies the failure, opens an
incident, and recommends relevant skills.  Packs expand that classification
and skill set for domains the built-in runtime doesn't cover.

## Directory Layout

```
andon-pack-{name}/
├── knowledge-pack.yaml   # REQUIRED — manifest
├── skills/               # REQUIRED — at least one .md file
│   ├── skill-a.md
│   └── skill-b.md
├── LICENSE               # REQUIRED
├── README.md             # REQUIRED
└── tests/                # RECOMMENDED
    └── test_pack.py
```

## Manifest Reference (`knowledge-pack.yaml`)

### Preamble

```yaml
apiVersion: andon/v1          # REQUIRED — fixed string
kind: KnowledgePack            # REQUIRED — fixed string
```

### `metadata` (REQUIRED)

| Field         | Type       | Required | Description |
|---------------|------------|----------|-------------|
| `name`        | `string`   | YES      | Unique pack identifier (kebab-case) |
| `version`     | `string`   | YES      | SemVer (`1.0.0`) |
| `description` | `string`   | YES      | One-line summary |
| `author`      | `string`   | no       | Author name or organization |
| `license`     | `string`   | no       | SPDX identifier (e.g. `Apache-2.0`) |
| `homepage`    | `string`   | no       | URL to project page |
| `tags`        | `string[]` | no       | Searchable tags |

### `requires` (CONDITIONAL)

Declare dependencies on other packs.

```yaml
requires:
  - name: "output-safety-guard"   # Pack 0
    version: ">=1.0.0"
    reason: "Regulated domain (legal) requires UPL/disclaimer guards"
```

**Rule**: If any domain in `domains` has an `id` that matches a
**regulated domain**, `requires` MUST include `output-safety-guard`.

Regulated domains:
`legal`, `medical`, `financial`, `pharmaceutical`,
`japan_legal`, `us_legal`, `eu_legal`

If the dependency is missing, the pack loader **refuses to load** the pack.

### `domains` (REQUIRED)

Define domain-specific keywords for the classifier.  Each entry extends or
creates a domain in the scoring engine.

```yaml
domains:
  - id: "japan_legal"             # Domain identifier (snake_case)
    keywords:
      - pattern: "(個人情報|APPI)"  # Regex pattern
        weight: 0.8                # Scoring weight (0.0–2.0, default 1.0)
      - pattern: "(弁護士法|非弁行為)"
        weight: 1.0
```

| Field    | Type    | Required | Description |
|----------|---------|----------|-------------|
| `id`     | string  | YES      | Domain identifier |
| `keywords` | list  | YES      | Pattern entries (see below) |

#### Keyword Entry

| Field     | Type   | Default | Description |
|-----------|--------|---------|-------------|
| `pattern` | string | —       | Regex pattern (IGNORECASE applied) |
| `weight`  | float  | `1.0`   | Score contribution when matched |

### `classification_rules`

Map failure output to cause IDs with confidence scores.

```yaml
classification_rules:
  - cause_id: "legal_statute_gap"
    label: "Legal statute requirement not addressed"
    confidence: 0.75
    pattern: "(compliance|法令|規制|違反)"
```

| Field        | Type   | Required | Description |
|--------------|--------|----------|-------------|
| `cause_id`   | string | YES      | Unique cause identifier |
| `label`      | string | YES      | Human-readable label |
| `confidence` | float  | YES      | 0.0–1.0 confidence score |
| `pattern`    | string | YES      | Regex pattern for matching |

### `cause_to_domain`

Map cause IDs to their primary domain.

```yaml
cause_to_domain:
  legal_statute_gap: "japan_legal"
  privacy_violation: "japan_legal"
```

### `skill_map` (REQUIRED)

Route domains to recommended skills.  Skills are `.md` files in the `skills/`
directory.

```yaml
skill_map:
  japan_legal:
    primary:
      - ref: "legal-orchestrator"
        path: "skills/legal-orchestrator.md"
        description: "Multi-law statute retrieval and audit orchestrator"
    secondary:
      - ref: "appi-guide"
        path: "skills/appi-guide.md"
        description: "Personal Information Protection Act guide"
```

| Field         | Type   | Required | Description |
|---------------|--------|----------|-------------|
| `ref`         | string | YES      | Skill identifier (kebab-case) |
| `path`        | string | YES      | Relative path from pack root |
| `description` | string | YES      | One-line description |

**Primary** skills are shown first in ANDON incident reports.
**Secondary** skills are shown as additional references.

### `safety_extensions` (CONDITIONAL)

Extend Pack 0's output safety patterns for your domain.
Only valid when `requires` includes `output-safety-guard`.

```yaml
safety_extensions:
  - category: "unauthorized_practice_of_law"
    extra_patterns:
      - pattern: "(弁護士法72条|非弁行為)"
        weight: 1.0
    jurisdiction: "JP"
    disclaimer_override:
      text: "⚠️ 本出力は法的助言ではありません。弁護士にご相談ください。"
      source_attribution: "出典: e-Gov法令検索"
```

#### Valid Categories

Built-in categories shipped with Pack 0:

| Category | Guard Level | Description |
|----------|------------|-------------|
| `unauthorized_practice_of_law` | GUARD | Legal advice without license |
| `unauthorized_professional_practice` | GUARD | Unlicensed professional advice |

Community packs may define additional categories via `safety_extensions`.

#### Guard Levels

| Level | Behavior |
|-------|----------|
| **BLOCK** | Replace output entirely with refusal message |
| **GUARD** | Allow output but inject disclaimer + professional referral |
| **WARN**  | Append advisory note to output |

### `quality_criteria`

Informational checklist for pack quality audits.

```yaml
quality_criteria:
  - "All skill files reference primary sources"
  - "Patterns tested against 10+ positive and negative examples"
  - "Disclaimers reviewed by domain expert"
```

## Skill File Format

Skills are Markdown files with YAML front matter:

```markdown
---
name: api-auth-guide
description: Authentication & authorization patterns for web APIs.
---

# API Authentication Guide

## Content here...
```

### Front Matter

| Field         | Required | Description |
|---------------|----------|-------------|
| `name`        | YES      | Matches `ref` in skill_map |
| `description` | YES      | One-line summary |

### Content Guidelines

- Lead with **actionable patterns** (symptom → cause → fix tables)
- Include code snippets with language tags
- Reference primary sources (official docs, RFCs, statutes)
- Keep each skill focused on one topic (< 200 lines recommended)
- For regulated domains: clearly state what the skill is NOT
  (e.g. "This is not legal advice")

## Validation Rules

The pack loader (`pack_loader.py`) enforces these rules at load time:

| Rule | Severity | Description |
|------|----------|-------------|
| `metadata.name` present | ERROR | Pack won't load |
| `metadata.version` present | ERROR | Pack won't load |
| `skills/` directory exists | WARNING | Pack loads but issues warning |
| `skills/` has `.md` files | WARNING | Pack loads but issues warning |
| Regulated domain + no Pack 0 dep | ERROR | Pack won't load |
| `license` present | WARNING | Pack loads but issues warning |

### CLI Validation

```bash
andon pack validate ./my-pack
```

Output:
```
✓ metadata.name: my-domain-pack
✓ metadata.version: 1.0.0
✓ skills/ directory: 3 skill files
✓ Pack 0 dependency: not required (no regulated domains)
⚠ license: not specified
Result: VALID (1 warning)
```

## Quick Start

1. Copy `examples/sample-pack/` as a template
2. Edit `knowledge-pack.yaml` with your domain
3. Add skill `.md` files to `skills/`
4. Validate: `andon pack validate ./your-pack`
5. Install: copy to `packs/` directory or `andon pack install ./your-pack`

## Example Packs

| Pack | Domain | Regulated | Skills | Status |
|------|--------|-----------|--------|--------|
| `sample-web-api-security` | API security | No | 3 | Example |
| `andon-pack-japan-legal` | Japanese law (e-Gov) | Yes | 6 | Stable |
| `andon-pack-ios-development` | iOS/App Store | No | 5 | Stable |
| `andon-pack-gdpr` | EU GDPR | Yes | 8 | Alpha |
| `andon-pack-financial` | Financial services (PCI-DSS, AML/KYC) | Yes | 6 | Alpha |
| `andon-pack-hipaa` | HIPAA healthcare compliance | Yes | 7 | Alpha |

## Legal Considerations for Pack Authors

### Regulated Domains

If your pack covers a licensed profession (law, medicine, finance, pharmacy,
architecture), you MUST:

1. Declare `requires: output-safety-guard`
2. Add `safety_extensions` with domain-specific patterns
3. Include disclaimers that clearly state the output is NOT professional advice
4. Reference primary sources, not secondary interpretations
5. Review patterns with a domain expert before publishing

### Intellectual Property

- Pack content must comply with its declared license
- When using government APIs (e.g. e-Gov), follow their terms of use
- Do not include proprietary content without permission
- Apple trademarks: follow [Apple Trademark Guidelines](https://www.apple.com/legal/intellectual-property/trademark/appletmlist.html) — use descriptive references, not branding

### Data Privacy

- Packs MUST NOT collect, transmit, or store user data
- Pattern matching runs locally — no external API calls from packs
- Skill content is static Markdown — no executable code
