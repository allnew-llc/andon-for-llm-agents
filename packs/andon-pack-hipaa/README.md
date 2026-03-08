# andon-pack-hipaa

ANDON Knowledge Pack for HIPAA compliance in LLM coding agent workflows.
Covers PHI handling, Security Rule, Privacy Rule, Breach Notification,
Business Associate Agreements, and de-identification methods.

## What This Pack Does

When an LLM agent encounters a healthcare compliance failure, this pack:

1. **Classifies** the failure into HIPAA-specific categories
   (PHI exposure, encryption gaps, access control, breach response, etc.)
2. **Recommends** relevant skills with CFR section-level HIPAA guidance
3. **Extends Pack 0** with healthcare-specific unauthorized practice patterns
   to guard against false medical advice and compliance assurances

## Skills Included

| Skill | Description |
|-------|-------------|
| `hipaa-orchestrator` | HIPAA compliance audit entry point and routing |
| `phi-handling-guide` | PHI identification, 18 identifiers, handling patterns |
| `security-rule-guide` | Security Rule technical safeguards (§164.312) |
| `breach-notification` | Breach notification procedures (§164.400-414) |
| `baa-requirements` | Business Associate Agreement requirements |
| `minimum-necessary` | Minimum Necessary standard implementation |
| `deidentification-guide` | Safe Harbor and Expert Determination methods |

## Classification Rules (10)

| Cause ID | Confidence | Detects |
|----------|-----------|---------|
| `phi_exposure` | 0.92 | PHI in logs/output/storage |
| `phi_encryption_gap` | 0.88 | ePHI without encryption |
| `medical_advice_detected` | 0.85 | Unauthorized medical advice |
| `access_control_gap` | 0.82 | Inadequate PHI access controls |
| `minimum_necessary_violation` | 0.80 | Excessive PHI access |
| `breach_response_failure` | 0.80 | Breach notification gaps |
| `baa_missing` | 0.78 | Missing Business Associate Agreement |
| `audit_trail_gap` | 0.77 | Missing PHI access audit trail |
| `deidentification_failure` | 0.75 | Incomplete de-identification |
| `disposal_failure` | 0.72 | PHI not properly disposed |

## Requirements

- **Pack 0 (output-safety-guard)** — required (regulated domain)

## Legal Notice

This pack provides structured guidance based on HIPAA (45 CFR Parts
160 and 164), the HITECH Act, and related HHS guidance. It does NOT
provide medical or legal advice. HIPAA compliance requirements may
vary based on the entity type, state laws, and specific circumstances.
All outputs should be reviewed by a qualified HIPAA compliance officer
or healthcare attorney before use in compliance decision-making.

## License

Apache-2.0
