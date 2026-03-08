---
name: privacy-by-design
description: GDPR Art. 25 data protection by design and by default.
---

# Privacy by Design and by Default (Art. 25)

## Principles

### By Design (Art. 25(1))

Implement appropriate technical and organizational measures **at the time
of design** and at the time of processing, to implement data protection
principles effectively.

### By Default (Art. 25(2))

Ensure that **by default** only personal data necessary for each specific
purpose is processed. This applies to:
- Amount of data collected
- Extent of processing
- Period of storage
- Accessibility (who can access)

## The Seven GDPR Principles in Code

| Principle | Article | Code Implementation |
|-----------|---------|-------------------|
| Lawfulness, fairness, transparency | Art. 5(1)(a) | Clear privacy notice, no hidden processing |
| Purpose limitation | Art. 5(1)(b) | Separate data stores per purpose, no repurposing |
| Data minimization | Art. 5(1)(c) | Collect only required fields, no "just in case" |
| Accuracy | Art. 5(1)(d) | Validation rules, update mechanisms, correction API |
| Storage limitation | Art. 5(1)(e) | TTL on records, automated deletion, retention policies |
| Integrity and confidentiality | Art. 5(1)(f) | Encryption at rest and in transit, access controls |
| Accountability | Art. 5(2) | Audit logs, documented decisions, DPIA records |

## Technical Measures

### Data Minimization Patterns

```
GOOD:
- Only collect fields needed for the specific purpose
- Use pseudonymization where full identity is not needed
- Aggregate data for analytics instead of using raw personal data
- Drop unnecessary fields before storage

BAD:
- Collecting "email, phone, address, DOB, gender" for a weather app
- Storing full IP addresses when country-level geolocation suffices
- Keeping raw logs with personal data indefinitely
- "Collect everything, filter later" approach
```

### Storage Limitation Patterns

```
GOOD:
- TTL (Time-To-Live) on database records
- Automated retention policy enforcement
- Separate retention periods per data category
- Anonymization after retention period expires

BAD:
- No deletion mechanism
- "We keep data forever for analytics"
- Same retention for all data types
- Manual deletion only (never actually done)
```

### Pseudonymization (Recital 28-29)

```
Techniques:
├─ Token replacement (replace PII with random token)
├─ Hashing with salt (one-way, for matching without revealing)
├─ Encryption with separate key storage
└─ Data masking (partial: john@***.com)

Key management:
- Store mapping/keys separately from pseudonymized data
- Restrict access to re-identification keys
- Document who can re-identify and under what conditions
```

## Default Settings Checklist

- [ ] Privacy-preserving defaults (opt-in, not opt-out)
- [ ] Minimum data visibility (need-to-know access)
- [ ] Shortest reasonable retention period
- [ ] No public profile by default
- [ ] Analytics/tracking disabled until consent given
- [ ] Most restrictive sharing settings by default

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Adding fields "for future use" | Violates minimization | Only collect what is needed now |
| Debug logging with PII | Unnecessary processing | Sanitize logs, use pseudonyms |
| No retention policy | Storage limitation violation | Define + automate retention |
| All staff can see all data | Excessive accessibility | Role-based access control |
| Tracking enabled by default | Not "by default" compliant | Require opt-in |

**This guide is NOT legal advice. Consult a qualified data protection professional.**
