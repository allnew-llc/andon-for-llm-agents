---
name: financial-orchestrator
description: Financial services compliance audit entry point and routing.
---

# Financial Compliance Orchestrator

## Purpose

Route financial compliance tasks to the appropriate specialist skill.
Start here when a financial services compliance issue is detected.

## Decision Tree

```
Is the code handling payment card data?
├─ Yes → /pci-dss-guide
├─ No  →
│   Is the output providing financial/investment advice?
│   ├─ Yes → /financial-advice-guard
│   ├─ No  →
│   │   Does the system need identity verification?
│   │   ├─ Yes → /aml-kyc-basics
│   │   ├─ No  →
│   │   │   Does the system process financial transactions?
│   │   │   ├─ Yes → /transaction-logging
│   │   │   └─ No  → /data-classification
```

## Compliance Framework Quick Reference

| Framework | Scope | Key Requirement |
|-----------|-------|-----------------|
| PCI-DSS v4.0 | Payment card processing | Protect cardholder data in transit and at rest |
| AML/KYC | Customer onboarding | Verify identity, monitor transactions |
| PSD2/SCA | EU payment services | Strong Customer Authentication |
| 金商法 (FIEA) | Japan securities/investment | Registration for financial instruments business |
| 資金決済法 | Japan payment services | Registration for fund transfer services |

## Universal Security Controls

Regardless of specific regulation, all financial systems must:

- [ ] Encrypt sensitive data at rest and in transit (TLS 1.2+)
- [ ] Implement strong authentication (MFA for administrative access)
- [ ] Maintain comprehensive audit logs (who, what, when, from where)
- [ ] Apply principle of least privilege for data access
- [ ] Conduct regular vulnerability assessments
- [ ] Have an incident response plan documented and tested

## When to Escalate

- Determining whether a service requires financial regulatory registration — consult a **licensed securities or financial regulatory attorney**
- Interpreting specific regulatory requirements for your jurisdiction — consult a **compliance officer or regulatory counsel**
- Designing AML transaction monitoring rules — consult a **certified anti-money laundering specialist (CAMS)**
- PCI-DSS scope determination for complex architectures — consult a **Qualified Security Assessor (QSA)**

**This guide covers technical patterns only, NOT financial, investment, or legal advice. Consult a QSA, compliance officer, or licensed financial advisor.**
