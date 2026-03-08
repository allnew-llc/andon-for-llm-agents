---
name: minimum-necessary
description: HIPAA Minimum Necessary standard implementation patterns.
---

# Minimum Necessary Standard

## Core Principle

A covered entity must make reasonable efforts to limit PHI to the
minimum necessary to accomplish the intended purpose of the use,
disclosure, or request. (45 CFR §164.502(b))

## When Minimum Necessary Applies

| Applies | Does NOT Apply |
|---------|---------------|
| Uses within the organization | Disclosures to the individual |
| Disclosures to business associates | Treatment purposes |
| Requests for PHI | Uses/disclosures required by law |
| Internal access policies | Uses/disclosures authorized by individual |
| Routine and recurring disclosures | Disclosures to HHS for enforcement |

## Implementation Patterns

### Role-Based Access

```
Define access levels by role:

Role: Clinician (treating physician)
├─ Access: Full clinical record for assigned patients
├─ Justification: Treatment purpose
└─ Note: Treatment exception (minimum necessary does not apply)

Role: Billing Staff
├─ Access: Demographics, insurance, diagnosis codes, procedure codes
├─ Justification: Payment purpose
└─ Excluded: Clinical notes, lab results, imaging

Role: Researcher
├─ Access: De-identified or limited data set only
├─ Justification: Research with IRB approval
└─ Excluded: All 18 identifiers (unless waiver granted)

Role: IT Administrator
├─ Access: System-level access (no routine PHI viewing)
├─ Justification: Operations and maintenance
└─ Controls: Access logged, break-the-glass for emergencies
```

### API Field Filtering

```
Instead of returning full records, filter by purpose:

Treatment API:
GET /patients/{id}/clinical
→ Returns: full clinical record (treatment exception)

Billing API:
GET /patients/{id}/billing
→ Returns: demographics, insurance, codes
→ Excludes: clinical notes, lab details

Research API:
GET /patients/{id}/research
→ Returns: de-identified data only
→ Excludes: all 18 identifiers

Audit:
GET /patients/{id}/access-log
→ Returns: who accessed what, when, why
→ Available to: compliance/security only
```

### Database Design

```
Separation strategies:
├─ Logical separation
│   ├─ Views that filter columns by role
│   ├─ Row-level security policies
│   └─ Column-level encryption for sensitive fields
├─ Physical separation
│   ├─ Clinical data in separate database/schema
│   ├─ De-identified research database
│   └─ Billing database with limited PHI
└─ Access patterns
    ├─ No SELECT * on PHI tables
    ├─ Named column queries only
    └─ Query audit logging
```

### Request Validation

```
For incoming PHI requests:

1. IDENTIFY the requester (authentication)
2. VERIFY authorization (role, purpose)
3. DETERMINE minimum necessary
   ├─ What specific data elements are needed?
   ├─ For what purpose?
   └─ Is there a less identifiable alternative?
4. FILTER response to authorized fields only
5. LOG the access (who, what, when, why)
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| SELECT * on patient tables | Returns more PHI than needed | Named column queries |
| Same API returns all fields to all roles | No role-based filtering | Role-based API responses |
| Full records sent for billing | Billing doesn't need clinical data | Separate billing views |
| No purpose tracking | Cannot audit minimum necessary | Log access purpose |
| Bulk data exports without filtering | Excessive PHI disclosure | Field-level export controls |

**This guide covers technical patterns only, NOT legal advice.**
