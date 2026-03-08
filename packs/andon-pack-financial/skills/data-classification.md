---
name: data-classification
description: Financial data classification and handling requirements.
---

# Financial Data Classification

## Classification Levels

| Level | Description | Examples | Handling |
|-------|------------|---------|---------|
| **Restricted** | Highest sensitivity, regulatory protection required | PAN, CVV, PIN, SSN, 個人番号 | Encrypted at rest + transit, strict access, audit all access |
| **Confidential** | Business-sensitive financial data | Account balances, transaction history, salary data | Encrypted, need-to-know access |
| **Internal** | Non-public business information | Aggregate statistics, internal reports | Access controls, no public disclosure |
| **Public** | Intended for public consumption | Published rates, public filings | No restrictions |

## PCI-DSS Data Classification

### Cardholder Data (CHD)

| Data Element | Classification | Storage | Display |
|-------------|---------------|---------|---------|
| Primary Account Number (PAN) | Restricted | Encrypted or tokenized | Mask: ****1234 |
| Cardholder name | Confidential | Encrypted recommended | Full display OK |
| Service code | Confidential | Encrypted recommended | Not displayed |
| Expiration date | Confidential | Encrypted recommended | Full display OK |

### Sensitive Authentication Data (SAD) — NEVER STORE

| Data Element | Classification | Storage | After Auth |
|-------------|---------------|---------|-----------|
| Full track data | **Prohibited** | NEVER | Delete immediately |
| CVV/CVC | **Prohibited** | NEVER | Delete immediately |
| PIN / PIN block | **Prohibited** | NEVER | Delete immediately |

## Handling Patterns by Classification

### Restricted Data

```
Storage:
  ├─ AES-256 encryption at rest
  ├─ Separate encryption keys from data
  ├─ Key rotation schedule (annual minimum)
  └─ Tokenize where possible (replace with non-sensitive token)

Transit:
  ├─ TLS 1.2+ mandatory
  ├─ Certificate pinning for mobile apps
  └─ No sensitive data in URL parameters

Access:
  ├─ Role-based access control (RBAC)
  ├─ Multi-factor authentication required
  ├─ Access logged and auditable
  └─ Principle of least privilege

Disposal:
  ├─ Cryptographic erasure (delete encryption keys)
  ├─ Secure overwrite for physical media
  └─ Document disposal in audit trail
```

### Confidential Data

```
Storage:
  ├─ Encryption recommended
  ├─ Access controls enforced
  └─ Retention policy applied

Transit:
  ├─ TLS 1.2+ required
  └─ API authentication required

Access:
  ├─ Need-to-know basis
  ├─ Access logged
  └─ Regular access review (quarterly)
```

## Data Flow Mapping

For compliance, document where financial data flows:

```
1. Entry Point
   ├─ Where does data enter the system?
   ├─ What classification level?
   └─ Who provides it? (customer, processor, partner)

2. Processing
   ├─ Which services touch the data?
   ├─ Is data transformed? (tokenized, aggregated, masked)
   └─ Is data combined with other data?

3. Storage
   ├─ Where is data stored? (database, cache, file, log)
   ├─ How long is it retained?
   └─ How is it encrypted?

4. Exit Point
   ├─ Where does data leave the system?
   ├─ To whom? (processor, regulator, customer)
   └─ How is it transmitted?
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| No data classification policy | Unknown protection requirements | Classify all data before processing |
| Same encryption key for all data | Single key compromise = total exposure | Separate keys per classification |
| Financial data in dev/test environments | Exposure risk | Use synthetic/masked data |
| No data flow documentation | Cannot audit or assess compliance | Map all data flows |
| Log files containing restricted data | Unintended storage of sensitive data | Sanitize before logging |

**This guide covers technical patterns only, NOT financial, investment, or legal advice. Consult a QSA, compliance officer, or licensed financial advisor.**
