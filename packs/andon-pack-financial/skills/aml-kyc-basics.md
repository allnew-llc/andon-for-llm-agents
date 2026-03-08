---
name: aml-kyc-basics
description: AML/KYC implementation basics for developers.
---

# AML/KYC Implementation Basics

## Overview

Anti-Money Laundering (AML) and Know Your Customer (KYC) are regulatory
requirements for financial services. This guide covers the technical
implementation patterns — not the regulatory strategy.

## KYC Tiers

| Tier | Verification Level | Typical Limits | Required Documents |
|------|-------------------|---------------|-------------------|
| Simplified | Basic identity check | Low-value transactions | Name, email, phone |
| Standard | Document verification | Normal limits | Government ID, proof of address |
| Enhanced | In-depth due diligence | High-value/high-risk | Additional documentation, source of funds |

## Implementation Patterns

### Identity Verification Flow

```
1. COLLECT
   ├─ Full legal name
   ├─ Date of birth
   ├─ Address
   └─ Government-issued ID (document + photo)

2. VERIFY
   ├─ Document authenticity (OCR + liveness detection)
   ├─ Identity match (name + DOB + photo vs. selfie)
   ├─ Sanctions screening (OFAC, EU, UN lists)
   └─ PEP (Politically Exposed Person) check

3. DECIDE
   ├─ Pass → Onboard customer, store verification record
   ├─ Fail → Reject with reason code (do not reveal screening details)
   └─ Review → Flag for manual review by compliance team

4. MONITOR (ongoing)
   ├─ Periodic re-verification (risk-based, e.g., annually)
   ├─ Transaction monitoring (pattern-based)
   └─ Sanctions list updates (check on every list update)
```

### Sanctions Screening

```
MUST CHECK:
- OFAC SDN List (US)
- EU Consolidated Sanctions List
- UN Security Council Sanctions
- Local sanctions lists (jurisdiction-specific)

WHEN TO CHECK:
- At onboarding (KYC)
- At every transaction (if required by jurisdiction)
- When sanctions lists are updated
- Periodic batch re-screening

MATCH HANDLING:
- Exact match → Block + report to compliance
- Fuzzy match → Flag for manual review
- No match → Proceed
- NEVER auto-clear potential matches without human review
```

### Transaction Monitoring

```
Suspicious patterns to detect:
├─ Structuring (splitting transactions to avoid thresholds)
├─ Rapid movement (in → out with no economic purpose)
├─ Round-number transactions
├─ Unusual geographic patterns
├─ Dormant account sudden activity
└─ Transactions inconsistent with customer profile

Report:
├─ STR (Suspicious Transaction Report) → FIU
├─ SAR (Suspicious Activity Report) → FinCEN (US)
└─ 疑わしい取引の届出 → JAFIC (Japan)

NEVER tip off the customer about a suspicious report.
```

## Data Handling

| Data Type | Retention | Access |
|-----------|----------|--------|
| KYC documents | 5-7 years after relationship ends | Compliance team only |
| Transaction records | 5-7 years | Compliance + authorized staff |
| Screening results | Duration of relationship + retention period | Compliance team only |
| STR/SAR filings | As required by regulator | Compliance officer only |

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Revealing sanctions match to customer | Tipping-off violation | Generic rejection message only |
| One-time KYC only | Ongoing monitoring required | Implement periodic review |
| Storing ID documents without encryption | Data breach risk | Encrypt at rest, restrict access |
| Using outdated sanctions lists | False negatives | Subscribe to real-time updates |
| Manual-only screening | Scale and speed issues | Automate with human review for matches |

**This guide covers technical patterns only, NOT financial, investment, or legal advice. Consult a QSA, compliance officer, or licensed financial advisor.**
