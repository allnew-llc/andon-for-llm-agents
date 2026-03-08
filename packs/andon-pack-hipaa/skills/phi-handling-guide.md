---
name: phi-handling-guide
description: PHI identification and handling patterns for developers.
---

# PHI Handling Guide

## What is PHI?

Protected Health Information (PHI) is individually identifiable health
information that relates to:

- Past, present, or future physical or mental health condition
- Provision of healthcare to an individual
- Past, present, or future payment for healthcare

## The 18 HIPAA Identifiers

If health data contains ANY of these, it is PHI:

| # | Identifier | Examples |
|---|-----------|----------|
| 1 | Names | Full name, maiden name |
| 2 | Geographic data (smaller than state) | Street address, city, ZIP code |
| 3 | Dates (except year) related to individual | Birth date, admission date, discharge date |
| 4 | Telephone numbers | Any phone number |
| 5 | Fax numbers | Any fax number |
| 6 | Email addresses | Any email |
| 7 | Social Security numbers | SSN |
| 8 | Medical record numbers | MRN |
| 9 | Health plan beneficiary numbers | Insurance ID |
| 10 | Account numbers | Any account number |
| 11 | Certificate/license numbers | Driver's license, professional license |
| 12 | Vehicle identifiers | VIN, license plate |
| 13 | Device identifiers | Serial numbers, UDI |
| 14 | Web URLs | Personal URLs |
| 15 | IP addresses | Any IP address |
| 16 | Biometric identifiers | Fingerprints, voice prints |
| 17 | Full-face photos | Comparable images |
| 18 | Any other unique identifier | Any number that could identify |

## Handling Patterns

### Storage

```
MUST:
- Encrypt ePHI at rest (AES-256 recommended)
- Use separate encryption keys for PHI vs. non-PHI data
- Implement key management with rotation schedule
- Store PHI in designated, access-controlled systems only

MUST NOT:
- Store PHI in plaintext
- Store PHI in client-side storage (localStorage, cookies)
- Store PHI in source code or configuration files
- Store PHI in general-purpose logging systems
```

### Transit

```
MUST:
- TLS 1.2+ for all ePHI transmissions
- End-to-end encryption for PHI in messages/emails
- Authenticate all endpoints that send or receive PHI

MUST NOT:
- Transmit PHI over unencrypted channels
- Include PHI in URL parameters
- Send PHI via unencrypted email without patient consent
```

### Display

```
MUST:
- Show minimum necessary PHI for the task
- Implement role-based display controls
- Log all PHI access events

SHOULD:
- Mask patient identifiers where full display is unnecessary
- Use session timeouts to prevent unattended display
- Provide break-the-glass procedures for emergency access
```

### Disposal

```
MUST:
- Define retention periods based on federal and state law
- Implement secure deletion (cryptographic erasure or overwrite)
- Document disposal in audit trail
- Apply disposal to all copies (backups, caches, replicas)

Typical retention: 6 years from creation or last effective date
(some states require longer)
```

## Code Patterns

### Log Sanitization

```
MUST sanitize before logging:
- Replace patient names with tokens (e.g., "PATIENT_TOKEN_abc")
- Replace MRN with masked value (e.g., "MRN:****1234")
- Remove all 18 identifiers from log entries
- Never log diagnosis, treatment, or clinical notes

Audit log (separate from application log):
- WHO accessed (user ID, role)
- WHAT was accessed (record ID, data category)
- WHEN (timestamp with timezone)
- WHERE (system, IP address)
- WHY (stated purpose/authorization)
```

### API Design

```
Endpoints handling PHI:
├─ Authentication required (no anonymous access)
├─ Authorization checked (role-based, minimum necessary)
├─ Request/response encrypted (TLS 1.2+)
├─ Audit logged (every access)
├─ Rate limited (prevent bulk extraction)
└─ Response filtered (return only requested fields)

Example response pattern:
{
  "patient_id": "pt_token_abc",    // tokenized
  "encounter_date": "2026-03-01",  // only if authorized
  "diagnosis": "..."               // only if minimum necessary
}
// Never return full record unless specifically authorized
```

## Common Mistakes

| Mistake | HIPAA Section | Fix |
|---------|--------------|-----|
| PHI in application logs | §164.312(b) | Sanitize before logging |
| Returning full patient record | §164.502(b) | Minimum necessary filtering |
| No access logging for PHI | §164.312(b) | Audit controls |
| PHI in error messages | §164.312(a)(1) | Generic error messages |
| PHI in dev/test databases | §164.502 | Use synthetic data |

**This guide covers technical patterns only, NOT medical or legal advice.**
