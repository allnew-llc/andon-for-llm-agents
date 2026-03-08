---
name: gdpr-orchestrator
description: GDPR compliance audit entry point and routing guide.
---

# GDPR Compliance Orchestrator

## Purpose

Route GDPR compliance tasks to the appropriate specialist skill.
Start here when a data protection issue is detected or when performing
a compliance audit on code that handles EU personal data.

## Decision Tree

```
Is the code processing personal data of EU/EEA individuals?
├─ No  → GDPR likely does not apply. Check if other privacy laws apply.
├─ Yes →
│   ├─ What lawful basis? → /lawful-basis-guide
│   ├─ Data subject rights implementation? → /data-subject-rights
│   ├─ High-risk processing? → /dpia-guide
│   ├─ Data leaving EEA? → /cross-border-transfer
│   ├─ Data breach occurred? → /breach-notification
│   ├─ New system/feature design? → /privacy-by-design
│   └─ Website with cookies/tracking? → /cookie-eprivacy
```

## Quick Compliance Checklist

| # | Requirement | GDPR Article | Check |
|---|-------------|-------------|-------|
| 1 | Lawful basis identified for each processing activity | Art. 6 | [ ] |
| 2 | Privacy notice provided to data subjects | Art. 13-14 | [ ] |
| 3 | Data subject rights mechanisms implemented | Art. 15-22 | [ ] |
| 4 | Records of processing activities maintained | Art. 30 | [ ] |
| 5 | Data processing agreements with processors | Art. 28 | [ ] |
| 6 | DPIA conducted for high-risk processing | Art. 35 | [ ] |
| 7 | Cross-border transfer safeguards in place | Art. 44-49 | [ ] |
| 8 | Breach notification procedure documented | Art. 33-34 | [ ] |
| 9 | Data protection by design and by default | Art. 25 | [ ] |
| 10 | DPO appointed (if required) | Art. 37 | [ ] |

## Key Definitions

| Term | GDPR Definition | Article |
|------|----------------|---------|
| Personal data | Any information relating to an identified or identifiable natural person | Art. 4(1) |
| Processing | Any operation performed on personal data | Art. 4(2) |
| Controller | Entity determining purposes and means of processing | Art. 4(7) |
| Processor | Entity processing data on behalf of the controller | Art. 4(8) |
| Data subject | The identified or identifiable natural person | Art. 4(1) |

## When to Escalate

- Uncertainty about whether GDPR applies → consult qualified data protection lawyer
- DPO appointment decision → legal assessment required
- Cross-border enforcement risk → consult local counsel in relevant Member State
- Large-scale processing of special categories → mandatory DPIA + consider DPA consultation

**This guide is NOT legal advice. Consult a qualified data protection professional.**
