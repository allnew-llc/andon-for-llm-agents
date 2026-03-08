---
name: breach-notification
description: HIPAA breach notification procedures for developers.
---

# HIPAA Breach Notification

## Definition

A breach is the acquisition, access, use, or disclosure of PHI in a manner
not permitted by the Privacy Rule that compromises the security or privacy
of the PHI. (45 CFR §164.402)

## Breach Presumption

Any impermissible use or disclosure of PHI is presumed to be a breach
UNLESS the covered entity demonstrates a LOW probability that the PHI
has been compromised, based on a risk assessment of:

1. **Nature and extent of PHI** — types of identifiers, likelihood of re-identification
2. **Unauthorized person** — who received/accessed the PHI
3. **Whether PHI was actually acquired or viewed** — vs. mere opportunity
4. **Extent of risk mitigation** — steps taken to reduce harm

## Notification Requirements

| Condition | Notify Whom | Timeline | Method |
|-----------|------------|----------|--------|
| Breach affecting < 500 individuals | Affected individuals | Within 60 days of discovery | Written notice |
| Breach affecting < 500 individuals | HHS | Annual log (within 60 days of year end) | HHS portal |
| Breach affecting ≥ 500 individuals | Affected individuals | Within 60 days of discovery | Written notice |
| Breach affecting ≥ 500 individuals | HHS | Within 60 days of discovery | HHS portal |
| Breach affecting ≥ 500 in a state | Prominent media | Within 60 days of discovery | Press release |
| Business Associate discovers breach | Covered Entity | Within 60 days of discovery | Per BAA terms |

## Exceptions (NOT a Breach)

| Exception | Requirement |
|-----------|-------------|
| Unintentional acquisition by workforce | Good faith, within scope of authority, no further use |
| Inadvertent disclosure between authorized persons | Within same organization, PHI not further used |
| Good faith belief PHI not retained | Recipient unable to retain the information |

## Breach Response Procedure

```
1. DETECT
   ├─ Automated: IDS/IPS alerts, DLP alerts, audit log anomalies
   ├─ Manual: Workforce reporting, patient complaints
   └─ Timeline: Discovery = when entity knows or should have known

2. CONTAIN
   ├─ Isolate affected systems
   ├─ Revoke compromised credentials
   ├─ Preserve forensic evidence
   └─ Do NOT destroy evidence

3. ASSESS
   ├─ 4-factor risk assessment (see above)
   ├─ Determine if breach exception applies
   ├─ Determine number of affected individuals
   └─ Document assessment findings

4. NOTIFY (if breach confirmed)
   ├─ Individual notification (within 60 days)
   │   ├─ Description of breach
   │   ├─ Types of information involved
   │   ├─ Steps individuals should take
   │   ├─ What entity is doing in response
   │   └─ Contact information
   ├─ HHS notification (within 60 days if ≥500, annual if <500)
   └─ Media notification (if ≥500 in a state/jurisdiction)

5. REMEDIATE
   ├─ Address root cause
   ├─ Update policies and procedures
   ├─ Conduct additional training
   └─ Document all actions taken
```

## Technical Detection Patterns

```
Systems should detect:
├─ Unusual data access patterns (volume, time, role mismatch)
├─ Bulk data exports or downloads
├─ Access from unusual locations or devices
├─ Failed authentication attempts followed by success
├─ Unauthorized API access to PHI endpoints
├─ Data exfiltration indicators (large outbound transfers)
└─ Privilege escalation events
```

## Unsecured PHI

Breach notification applies only to **unsecured PHI**. PHI is considered
"secured" (and exempt from notification) if:

- Encrypted per NIST standards (AES-128/256, etc.)
- Destroyed per NIST SP 800-88 guidelines

If PHI was properly encrypted at the time of breach, notification may
not be required (but document the analysis).

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| No breach detection capability | Cannot discover breaches | Implement monitoring/alerting |
| No documented risk assessment | Cannot demonstrate low probability | Template and process |
| Missing 60-day deadline | HIPAA violation | Automated deadline tracking |
| Incomplete individual notification | Missing required elements | Notification template |
| No forensic evidence preservation | Cannot complete investigation | Incident response plan |

**This guide covers technical patterns only, NOT medical or legal advice.**
