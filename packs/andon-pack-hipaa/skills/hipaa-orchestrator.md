---
name: hipaa-orchestrator
description: HIPAA compliance audit entry point and routing.
---

# HIPAA Compliance Orchestrator

## When to Use This Skill

Use this skill as the entry point when a HIPAA compliance issue is
detected by the ANDON classification engine.

## Quick Decision Tree

```
Is the system handling Protected Health Information (PHI)?
├─ Yes → Is the entity a Covered Entity or Business Associate?
│   ├─ Covered Entity → Full HIPAA compliance required
│   │   ├─ Privacy Rule → See: phi-handling-guide, minimum-necessary
│   │   ├─ Security Rule → See: security-rule-guide
│   │   └─ Breach Notification → See: breach-notification
│   ├─ Business Associate → BAA + Security Rule required
│   │   ├─ BAA in place? → See: baa-requirements
│   │   └─ Security safeguards → See: security-rule-guide
│   └─ Neither → HIPAA may not apply (but state laws may)
├─ No → HIPAA likely does not apply
└─ Unsure → See: phi-handling-guide (identification section)
```

## HIPAA Applicability Checklist

```
Does HIPAA apply to this system?

□ The entity is a Covered Entity (health plan, healthcare provider,
  healthcare clearinghouse) OR a Business Associate
□ The system creates, receives, maintains, or transmits PHI
□ PHI includes individually identifiable health information

If ANY are false → HIPAA may not apply (but check state laws)
If ALL are true → Full HIPAA compliance required
```

## Compliance Framework Reference

| Rule | CFR Section | Key Requirement | Skill |
|------|------------|-----------------|-------|
| Privacy Rule | 45 CFR §164.500-534 | Permitted uses/disclosures of PHI | phi-handling-guide |
| Security Rule | 45 CFR §164.302-318 | Safeguards for ePHI | security-rule-guide |
| Breach Notification | 45 CFR §164.400-414 | Notification after breach | breach-notification |
| Minimum Necessary | 45 CFR §164.502(b) | Limit PHI to what is needed | minimum-necessary |
| De-identification | 45 CFR §164.514 | Remove identifiers from PHI | deidentification-guide |
| BAA | 45 CFR §164.502(e) | Agreements with business associates | baa-requirements |

## Common Failure Patterns

| Pattern | Root Cause | Recommended Skill |
|---------|-----------|-------------------|
| PHI in application logs | No log sanitization | phi-handling-guide |
| ePHI transmitted over HTTP | Missing TLS enforcement | security-rule-guide |
| No access audit trail | Audit controls not implemented | security-rule-guide |
| PHI shared without BAA | Third-party integration without agreement | baa-requirements |
| Full record returned when subset needed | Minimum necessary not enforced | minimum-necessary |
| Breach detected but no notification | No breach response plan | breach-notification |
| Research data contains identifiers | Incomplete de-identification | deidentification-guide |

## Escalation

If any of the following apply, escalate to a qualified HIPAA compliance
officer or healthcare attorney:

- Uncertainty about whether an entity is a Covered Entity
- Actual or suspected breach of unsecured PHI
- State law conflicts with HIPAA requirements
- OCR (Office for Civil Rights) inquiry or investigation
- Complex authorization or consent scenarios

**This guide covers technical patterns only, NOT legal or medical advice.**
