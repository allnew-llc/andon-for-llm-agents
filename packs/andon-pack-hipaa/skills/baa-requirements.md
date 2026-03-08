---
name: baa-requirements
description: Business Associate Agreement requirements for developers.
---

# Business Associate Agreement (BAA) Requirements

## When is a BAA Required?

A BAA is required when a covered entity engages a business associate to
perform functions or activities involving PHI. (45 CFR §164.502(e))

## What is a Business Associate?

| Entity Type | BAA Required? | Examples |
|------------|--------------|---------|
| Performs functions involving PHI | Yes | Claims processing, billing, data analysis |
| Provides services involving PHI access | Yes | Cloud hosting, IT support, shredding |
| Subcontractor of BA handling PHI | Yes | Sub-processors, SaaS platforms |
| Member of covered entity's workforce | No | Employees (covered by employment relationship) |
| Treatment relationship | No | Physician-to-physician referral |
| Conduit (transient possession) | No | Postal service, ISPs |

## Required BAA Provisions (§164.504(e))

```
A BAA MUST include:

1. PERMITTED USES
   ├─ Establish permitted uses and disclosures of PHI
   ├─ Must not violate Privacy Rule
   └─ Must be consistent with covered entity's obligations

2. SAFEGUARDS
   ├─ BA must use appropriate safeguards (Security Rule)
   ├─ BA must implement administrative, physical, technical safeguards
   └─ BA must report security incidents

3. REPORTING
   ├─ Report to CE any use or disclosure not provided for in BAA
   ├─ Report security incidents
   └─ Report breaches of unsecured PHI

4. SUBCONTRACTORS
   ├─ Ensure subcontractors agree to same restrictions
   ├─ BAA must flow down to sub-business associates
   └─ BA is responsible for subcontractor compliance

5. ACCESS RIGHTS
   ├─ Make PHI available for individual access rights
   ├─ Make PHI available for amendment
   └─ Provide accounting of disclosures

6. AVAILABILITY TO HHS
   ├─ Make internal practices available to HHS
   ├─ Books, records, policies
   └─ For compliance determination

7. RETURN/DESTROY
   ├─ Return or destroy PHI at termination
   ├─ If not feasible, extend protections
   └─ Limit further uses and disclosures

8. TERMINATION
   ├─ Authorize termination if BA violates material term
   └─ Define cure period if applicable
```

## Developer Checklist for Third-Party Integrations

```
Before integrating a service that may handle PHI:

□ Does the service access, store, or transmit PHI?
  ├─ If yes → BAA required
  └─ If no → BAA not required (but document analysis)

□ Does the vendor offer a BAA?
  ├─ If yes → Review and execute before integration
  └─ If no → DO NOT integrate for PHI use cases

□ What PHI will the service handle?
  ├─ Document specific data elements
  └─ Apply minimum necessary principle

□ Where will data be stored?
  ├─ US servers? (check for non-US transfer)
  └─ Encryption at rest and in transit?

□ What security certifications does the vendor have?
  ├─ SOC 2 Type II
  ├─ HITRUST CSF
  └─ ISO 27001
```

## Common Cloud Services and BAA Status

| Service Category | BAA Typically Available | Notes |
|-----------------|----------------------|-------|
| Major cloud providers (AWS, Azure, GCP) | Yes | Request and execute BAA |
| EHR platforms | Yes | Standard in healthcare |
| Email services | Varies | Enterprise tiers may offer |
| Analytics tools | Rarely | Avoid sending PHI to analytics |
| Free/consumer services | No | Never use for PHI |

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Using service without BAA | HIPAA violation | Execute BAA before integration |
| Assuming cloud = compliant | BAA is separate from infrastructure | Explicit BAA required |
| No subcontractor BAA | BA responsible for subcontractors | Flow-down agreements |
| BAA not reviewed by legal | May have inadequate terms | Legal review of all BAAs |
| No termination provisions | Cannot enforce compliance | Include termination clause |

**This guide covers technical patterns only, NOT legal advice.**
