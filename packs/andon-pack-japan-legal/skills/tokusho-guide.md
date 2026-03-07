---
name: tokusho-guide
description: Specified Commercial Transactions Act (特定商取引法) compliance guide.
---

# Specified Commercial Transactions Act Guide

## Overview

The Act on Specified Commercial Transactions (特定商取引法, Act No. 57 of 1976,
as amended) regulates specific forms of commercial transactions to protect consumers.

**law_id**: `351AC0000000057`

## Transaction Types

| Type | Japanese | Articles | App Relevance |
|------|----------|----------|---------------|
| Mail-Order Sales | 通信販売 | Art. 11-15-4 | **High** — covers online/app sales |
| Door-to-Door Sales | 訪問販売 | Art. 2-10 | Low |
| Telemarketing | 電話勧誘販売 | Art. 16-25 | Medium — in-app calls |
| Continuous Services | 特定継続的役務提供 | Art. 41-50 | Medium — subscriptions |
| Multi-Level Marketing | 連鎖販売取引 | Art. 33-40-3 | Low |
| Business Opportunity | 業務提供誘引販売取引 | Art. 51-58 | Low |

## Mail-Order Sales Requirements (通信販売)

Most relevant for app developers.

### Mandatory Disclosures (Art. 11)

Display the following to consumers BEFORE purchase:

- [ ] Price and payment method
- [ ] Delivery/provision timing
- [ ] Return/cancellation policy (Art. 15-3)
- [ ] Seller name and address
- [ ] Contact information (phone/email)
- [ ] Additional charges (shipping, handling)

### Cooling-Off Equivalent

Mail-order sales do NOT have a cooling-off period by default.
However, you MUST clearly display your return policy.
If no policy is displayed, consumers may return within 8 days (Art. 15-3).

### Misleading Advertisements (Art. 12)

Prohibited:
- Exaggerated performance claims
- Misleading price comparisons
- False urgency or scarcity

### Email Marketing (Art. 12-3, 12-4)

- Opt-in required (prior consent)
- Unsubscribe mechanism required
- Sender identification required

## App Store Compliance Notes

| Requirement | iOS App Implementation |
|-------------|----------------------|
| Seller info display | Settings/About screen or linked webpage |
| Price display | App Store handles IAP pricing |
| Return policy | Link to policy in app + App Store description |
| Contact info | Support URL in App Store metadata |

## e-Gov API Quick Reference

```bash
# Get Specified Commercial Transactions Act
curl -s 'https://laws.e-gov.go.jp/api/1/lawdata/351AC0000000057'

# Mail-order provisions (Art. 11)
curl -s 'https://laws.e-gov.go.jp/api/1/lawdata/351AC0000000057?elm=MainProvision-Article[11]'
```

## Guardrails

- This guide provides structured compliance checks, NOT legal advice
- Verify current text via e-Gov API — this law is amended frequently
- Consult a licensed professional for binding compliance decisions
