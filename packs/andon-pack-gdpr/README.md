# andon-pack-gdpr

ANDON Knowledge Pack for EU General Data Protection Regulation (GDPR)
compliance in LLM coding agent workflows.

## What This Pack Does

When an LLM agent encounters a data protection compliance failure, this pack:

1. **Classifies** the failure into GDPR-specific categories
   (consent, data subject rights, cross-border transfers, breach response, etc.)
2. **Recommends** relevant skills with article-level GDPR guidance
3. **Extends Pack 0** with EU-specific unauthorized practice patterns
   to guard against false compliance assurances

## Skills Included

| Skill | Description |
|-------|-------------|
| `gdpr-orchestrator` | GDPR compliance audit entry point and routing |
| `lawful-basis-guide` | Art. 5-6 lawful basis selection |
| `data-subject-rights` | Art. 12-22 rights implementation patterns |
| `dpia-guide` | Data Protection Impact Assessment (Art. 35-36) |
| `cross-border-transfer` | Art. 44-49 transfer mechanisms (SCCs, adequacy, BCRs) |
| `breach-notification` | Art. 33-34 breach notification procedures |
| `privacy-by-design` | Art. 25 privacy by design and by default |
| `cookie-eprivacy` | Cookie consent and ePrivacy Directive compliance |

## Classification Rules (12)

| Cause ID | Confidence | Detects |
|----------|-----------|---------|
| `consent_violation` | 0.82 | Processing without valid lawful basis |
| `data_subject_rights_gap` | 0.78 | Rights not implemented |
| `cross_border_transfer_violation` | 0.85 | Transfer without safeguards |
| `dpia_missing` | 0.75 | High-risk processing without DPIA |
| `breach_response_failure` | 0.80 | Breach notification failure |
| `privacy_by_design_gap` | 0.72 | Data minimization not applied |
| `special_category_violation` | 0.88 | Art. 9 data without proper basis |
| `processor_compliance_gap` | 0.76 | No Art. 28 agreement |
| `retention_violation` | 0.74 | Data retained beyond purpose |
| `cookie_consent_gap` | 0.70 | Tracking without consent |
| `children_data_violation` | 0.83 | Children's data without parental consent |
| `automated_decision_violation` | 0.79 | Automated decisions without Art. 22 safeguards |

## Requirements

- **Pack 0 (output-safety-guard)** — required (regulated domain)

## Legal Notice

This pack provides structured guidance based on the text of Regulation (EU)
2016/679 (GDPR) and related instruments. It does NOT provide legal advice.
Data protection law varies by EU/EEA Member State. All outputs should be
reviewed by a qualified data protection lawyer or Data Protection Officer
before use in compliance decision-making.

## License

Apache-2.0
