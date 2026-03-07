---
name: appi-guide
description: Personal Information Protection Act (APPI) compliance guide.
---

# APPI Compliance Guide

## Overview

The Act on the Protection of Personal Information (個人情報の保護に関する法律,
Act No. 57 of 2003, as amended) is Japan's primary data protection law.

**law_id**: `415AC0000000057`

## Key Concepts

| Concept | Japanese | Article | Description |
|---------|----------|---------|-------------|
| Personal Information | 個人情報 | Art. 2(1) | Info identifying a living individual |
| Personal Data | 個人データ | Art. 16(3) | Personal info in a database |
| Sensitive Data | 要配慮個人情報 | Art. 2(3) | Race, creed, medical history, etc. |
| Anonymized Data | 匿名加工情報 | Art. 2(6) | De-identified data |
| Business Operator | 個人情報取扱事業者 | Art. 16(2) | Entity handling personal data |

## Compliance Checklist

### Collection (取得)

- [ ] Purpose of use specified (Art. 17)
- [ ] Purpose notified or published (Art. 21)
- [ ] Consent obtained for sensitive data (Art. 20(2))
- [ ] No deceptive collection (Art. 20(1))

### Use (利用)

- [ ] Use within stated purpose (Art. 18)
- [ ] No purpose change beyond reasonable scope (Art. 17(2))

### Storage (保管)

- [ ] Accuracy maintained (Art. 22)
- [ ] Security measures implemented (Art. 23)
- [ ] Employee supervision (Art. 24)
- [ ] Subcontractor supervision (Art. 25)

### Third-Party Transfer (第三者提供)

- [ ] Consent obtained (Art. 27(1)) or exception applies
- [ ] Opt-out procedure if applicable (Art. 27(2))
- [ ] Transfer records maintained (Art. 29, 30)
- [ ] Foreign transfer: consent + information provision (Art. 28)

### Data Subject Rights (本人の権利)

- [ ] Disclosure request procedure (Art. 33)
- [ ] Correction/deletion procedure (Art. 34)
- [ ] Use cessation procedure (Art. 35)

## Common Issues in App Development

| Issue | Risk | Remediation |
|-------|------|-------------|
| No privacy policy | High | Draft and publish before data collection |
| Missing consent for sensitive data | High | Add explicit consent flow |
| Third-party SDK sharing data | Medium | Audit SDK data flows, add disclosure |
| No deletion mechanism | Medium | Implement account/data deletion |
| Unclear purpose of use | Low | Specify concrete purposes |

## e-Gov API Quick Reference

```bash
# Get APPI full text
curl -s 'https://laws.e-gov.go.jp/api/1/lawdata/415AC0000000057'

# Get specific article (Art. 27 — third-party transfer)
curl -s 'https://laws.e-gov.go.jp/api/1/lawdata/415AC0000000057?elm=MainProvision-Article[27]'
```

## Guardrails

- This guide provides structured compliance checks, NOT legal advice
- Final compliance decisions require review by a licensed professional
- Always verify against current statute text via e-Gov API
