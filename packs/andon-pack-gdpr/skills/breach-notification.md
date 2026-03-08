---
name: breach-notification
description: GDPR Art. 33-34 data breach notification procedures.
---

# Data Breach Notification (Art. 33-34)

## Definition

A personal data breach is a security incident leading to accidental or unlawful
destruction, loss, alteration, unauthorized disclosure of, or access to personal
data (Art. 4(12)).

## Notification Obligations

### To Supervisory Authority (Art. 33)

| Requirement | Detail |
|-------------|--------|
| Deadline | **72 hours** after becoming aware |
| Exception | Unless unlikely to result in risk to individuals |
| If late | Must explain reasons for delay |
| Content | See notification contents below |

### To Data Subjects (Art. 34)

| Requirement | Detail |
|-------------|--------|
| Trigger | Breach likely to result in **high risk** to rights and freedoms |
| Deadline | **Without undue delay** |
| Exception | Data was encrypted/anonymized, or risk mitigated, or disproportionate effort (use public communication) |
| Language | Clear and plain language |

## Notification Contents (Art. 33(3))

```
To DPA (supervisory authority):
├─ Nature of breach (categories + approximate number of subjects/records)
├─ Contact details of DPO or other contact point
├─ Likely consequences of the breach
└─ Measures taken or proposed to address the breach

To Data Subjects (Art. 34(2)):
├─ Nature of breach (in clear, plain language)
├─ Contact details of DPO or other contact point
├─ Likely consequences
└─ Measures taken or proposed + what individuals can do
```

## Breach Response Procedure

```
1. DETECT
   └─ Security monitoring, employee report, third-party notification

2. CONTAIN (immediately)
   ├─ Isolate affected systems
   ├─ Revoke compromised credentials
   └─ Preserve evidence for investigation

3. ASSESS (within hours)
   ├─ What data was affected?
   ├─ How many data subjects?
   ├─ What is the likely impact?
   ├─ Is there a risk to individuals? (→ notify DPA)
   └─ Is there a HIGH risk? (→ notify individuals)

4. NOTIFY (within 72 hours of awareness)
   ├─ Supervisory authority (unless no risk)
   └─ Data subjects (if high risk)

5. REMEDIATE
   ├─ Fix root cause
   ├─ Implement additional safeguards
   └─ Update DPIA if applicable

6. DOCUMENT (Art. 33(5))
   ├─ Facts of the breach
   ├─ Effects
   ├─ Remedial actions
   └─ Retain regardless of whether notification was required
```

## Implementation Checklist

- [ ] Breach detection mechanisms in place (logging, monitoring, alerting)
- [ ] Incident response team identified with contact details
- [ ] DPA contact details for relevant Member States documented
- [ ] Breach notification template prepared
- [ ] Internal breach register maintained (Art. 33(5))
- [ ] Staff trained on breach recognition and reporting
- [ ] Processor contracts require immediate breach notification (Art. 28(3)(f))

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| No breach detection system | Cannot start 72-hour clock | Implement monitoring + alerting |
| Processor delays reporting | Clock starts at controller awareness | Art. 28 contract: "without undue delay" |
| Notifying all breaches to subjects | Only high-risk breaches require it | Assess risk level first |
| No internal breach register | Art. 33(5) requires documentation of ALL breaches | Maintain register |
| 72 hours from discovery, not awareness | Misunderstanding of "awareness" | Clock starts when reasonably certain |

**This guide is NOT legal advice. Consult a qualified data protection professional.**
