---
name: legal-orchestrator
description: Multi-law statute reference entry point for Japanese digital services.
---

# Japan Digital Service Legal Orchestrator

## Purpose

Entry point for multi-law statute reference reviews.  Routes issues to the
relevant domain-law skills and ensures primary source evidence via e-Gov.

## Workflow

### Step 1: Freeze Service Facts

| Question | Examples |
|----------|---------|
| Service type? | iOS app, SaaS, marketplace, content platform |
| Monetization? | Subscription, IAP, one-time purchase, free |
| Data handled? | Personal data, health data, payment info |
| Content flow? | UGC, messaging, email, push notifications |
| Target users? | Consumers (B2C), businesses (B2B), both |

### Step 2: Select Applicable Law Modules

| Module | Trigger |
|--------|---------|
| **APPI** (個人情報保護法) | Any personal data handling |
| **Tokusho** (特定商取引法) | Online sales to consumers |
| **Consumer Contract** (消費者契約法) | B2C contracts with auto-renewal or cancellation terms |
| **Telecommunications** (電気通信事業法) | Communication services, messaging features |
| **Copyright** (著作権法) | UGC, content display, media handling |
| **Keihin** (景品表示法) | Advertising, promotional claims, premium offers |
| **Email** (特定電子メール法) | Marketing emails, push notification marketing |

### Step 3: Lock Primary Sources

Before any analysis, retrieve current statute text:

```bash
# Resolve law identity
curl -s 'https://laws.e-gov.go.jp/api/1/laws?law_title=個人情報の保護に関する法律&limit=3'

# Get specific article
curl -s 'https://laws.e-gov.go.jp/api/1/lawdata/415AC0000000057?elm=MainProvision-Article[23]'
```

Record `law_id`, `law_revision_id`, and retrieval timestamp for citations.

### Step 4: Produce Integrated Report

```markdown
## Statute Reference Report

### Facts
- [Service description, data flows, monetization]

### Applicable Laws
| Law | law_id | Relevant Articles | Status |
|-----|--------|-------------------|--------|

### Findings
#### High Priority
- [Issue + article citation + evidence]

#### Medium Priority
- [Issue + article citation + evidence]

### Uncertainty
- [Items requiring specialist review]

### Action Plan
- [ ] [Specific remediation steps]
```

## Guardrails

- Distinguish legal text (fact) from interpretation (opinion)
- Attach exact article citation and access date to each claim
- Escalate final legal judgment to licensed professionals (弁護士)
- Do not skip `law_id` and revision checks
