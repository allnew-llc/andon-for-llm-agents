---
name: deidentification-guide
description: PHI de-identification methods (Safe Harbor and Expert Determination).
---

# PHI De-identification Guide

## Purpose

De-identification removes the link between health data and the individual,
allowing the data to be used without HIPAA restrictions. (45 CFR §164.514)

## Two Methods

### Method 1: Safe Harbor (§164.514(b))

Remove ALL 18 identifiers AND have no actual knowledge that the remaining
information could identify an individual.

```
Remove or generalize ALL of the following:

 1. Names
 2. Geographic data smaller than state
    ├─ Exception: first 3 digits of ZIP if population > 20,000
    └─ Otherwise: set to "000"
 3. Dates more specific than year
    ├─ Remove day and month (keep year)
    └─ Ages > 89: aggregate into "90+"
 4. Telephone numbers
 5. Fax numbers
 6. Email addresses
 7. Social Security numbers
 8. Medical record numbers
 9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers (VIN, plates)
13. Device identifiers (serial numbers)
14. Web URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photographs
18. Any other unique identifying number
```

### Method 2: Expert Determination (§164.514(b)(1))

A qualified statistical or scientific expert determines that the risk
of identifying an individual is "very small" and documents the methods
and results.

```
Expert must:
├─ Apply statistical/scientific principles
├─ Determine risk of identification is very small
├─ Document methods and results
└─ Be qualified by knowledge/experience

Advantages over Safe Harbor:
├─ May retain some identifiers with controls
├─ More flexible for research use cases
└─ Risk-based approach

Disadvantages:
├─ Requires qualified expert
├─ More expensive
└─ Must re-evaluate as data environment changes
```

## Implementation Patterns

### Safe Harbor Checklist

```
For each data field in the dataset:

□ Is it one of the 18 identifiers?
  ├─ Yes → Remove or generalize (see rules above)
  └─ No → May retain

□ Could combinations of remaining fields re-identify?
  ├─ Check: rare diseases + demographics = potential re-ID
  ├─ Check: small population groups
  └─ If concerned → additional generalization

□ ZIP code handling:
  ├─ Population ≥ 20,000 for 3-digit ZIP → keep first 3 digits
  └─ Population < 20,000 → set to "000"

□ Date handling:
  ├─ Remove day and month → keep year only
  ├─ Age > 89 → aggregate to "90+"
  └─ Date ranges → use year only

□ No actual knowledge of re-identification possibility
```

### Limited Data Set (§164.514(e))

A middle ground: removes direct identifiers but may retain some
indirect identifiers. Requires a Data Use Agreement (DUA).

```
Limited Data Set MAY include:
├─ Dates (admission, discharge, birth, death)
├─ City, state, ZIP code
└─ Ages (including 90+)

Limited Data Set MUST remove:
├─ Names
├─ Street addresses
├─ Phone/fax numbers
├─ Email addresses
├─ SSN, MRN, health plan numbers
├─ Account numbers
├─ Certificate/license numbers
├─ Vehicle/device identifiers
├─ URLs, IP addresses
├─ Biometric identifiers
└─ Photos

Permitted uses: Research, public health, healthcare operations
Requires: Data Use Agreement (not a BAA)
```

## Re-identification Risk

```
After de-identification, verify:
├─ No single field uniquely identifies (k-anonymity ≥ 5 recommended)
├─ Rare combinations don't narrow to small groups
├─ External datasets cannot be linked to re-identify
├─ Temporal patterns don't reveal identity
└─ Geographic + demographic combinations are sufficiently broad
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Removing names but keeping MRN | MRN is an identifier (#8) | Remove all 18 identifiers |
| Keeping full ZIP code | Only first 3 digits allowed (with population check) | Apply ZIP rules |
| Keeping exact dates | Dates more specific than year must be removed | Year only |
| No re-identification risk check | Combinations may re-identify | k-anonymity analysis |
| Calling it "anonymized" vs "de-identified" | Legal terminology matters | Use "de-identified" per HIPAA |

**This guide covers technical patterns only, NOT legal advice.**
