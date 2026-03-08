---
name: data-subject-rights
description: GDPR Art. 12-22 data subject rights implementation guide.
---

# Data Subject Rights (Art. 12-22)

## Rights Overview

| Right | Article | Deadline | Must Implement? |
|-------|---------|----------|-----------------|
| Information (at collection) | Art. 13 | At collection time | Always |
| Information (indirect collection) | Art. 14 | Within 1 month | Always |
| Access | Art. 15 | 1 month | Always |
| Rectification | Art. 16 | 1 month | Always |
| Erasure ("right to be forgotten") | Art. 17 | 1 month | When applicable |
| Restriction of processing | Art. 18 | 1 month | Always |
| Data portability | Art. 20 | 1 month | When basis is consent or contract |
| Object | Art. 21 | Without undue delay | Always for direct marketing |
| Automated decision-making | Art. 22 | Before processing | When automated decisions have legal effects |

## Implementation Patterns

### Access Request (Art. 15)

```
API: GET /api/v1/data-subject/me
Auth: Verified identity of data subject
Response: {
  "personal_data": { ... all categories ... },
  "processing_purposes": ["..."],
  "recipients": ["..."],
  "retention_period": "...",
  "source": "...",
  "automated_decisions": true/false,
  "safeguards_for_transfers": "..."
}
Deadline: 1 month (extendable to 3 months for complex requests)
Format: Commonly used, machine-readable (JSON, CSV)
```

### Erasure Request (Art. 17)

```
API: DELETE /api/v1/data-subject/me
Steps:
  1. Verify identity of requester
  2. Check if erasure exception applies (Art. 17(3))
  3. Delete personal data from active systems
  4. Delete from backups (or mark for deletion on next cycle)
  5. Notify processors to delete (Art. 17(2))
  6. Confirm deletion to data subject
Exceptions: Legal obligation, public interest, legal claims
```

### Portability (Art. 20)

```
API: GET /api/v1/data-subject/me/export
Format: JSON or CSV (structured, commonly used, machine-readable)
Scope: Only data provided BY the data subject
        + Only when basis is consent or contract
        + Processed by automated means
Optional: Direct transfer to another controller (Art. 20(2))
```

## Identity Verification

Before fulfilling any request:
- Verify the requester IS the data subject
- Do NOT request excessive identification documents
- If identity uncertain, may request additional info (Art. 12(6))
- Do NOT use the request as an excuse to collect more data

## Response Requirements (Art. 12)

- Respond within **1 month** of receipt
- Extension to **3 months** if complex or numerous (notify within 1 month)
- **Free of charge** (may charge reasonable fee for manifestly unfounded/excessive)
- Communicate in **clear and plain language**
- If refusing: explain reasons + right to complain to DPA + right to judicial remedy

## Common Implementation Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| No identity verification | Privacy risk | Add auth + identity check |
| Manual-only process | Scalability, deadline risk | Automate via API |
| Erasure ignores backups | Incomplete deletion | Schedule backup purge |
| Portability returns all data | Over-broad scope | Only data "provided by" subject |
| No audit trail of requests | Accountability gap | Log all requests + responses |

**This guide is NOT legal advice. Consult a qualified data protection professional.**
