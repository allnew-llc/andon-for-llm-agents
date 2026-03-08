---
name: dpia-guide
description: Data Protection Impact Assessment (DPIA) guide per Art. 35-36.
---

# Data Protection Impact Assessment (Art. 35-36)

## When a DPIA Is Required

A DPIA is **mandatory** when processing is likely to result in a **high risk**
to data subjects' rights and freedoms. Art. 35(3) lists three cases where a
DPIA is always required:

| Trigger | Article | Example |
|---------|---------|---------|
| Systematic, extensive profiling with significant effects | Art. 35(3)(a) | Credit scoring, behavioral advertising |
| Large-scale processing of special categories | Art. 35(3)(b) | Hospital patient records, biometric access |
| Systematic monitoring of publicly accessible area | Art. 35(3)(c) | CCTV with facial recognition |

### Additional Indicators (WP29 Guidelines)

Two or more of the following factors → DPIA likely required:

1. Evaluation or scoring (profiling)
2. Automated decision-making with legal or significant effects
3. Systematic monitoring
4. Sensitive data or highly personal data
5. Large-scale processing
6. Matching or combining datasets
7. Data concerning vulnerable subjects (children, employees, patients)
8. Innovative use of technology
9. Data transfer outside EEA

## DPIA Contents (Art. 35(7))

A DPIA must contain at minimum:

```
1. Description of Processing
   ├─ Nature, scope, context, and purposes
   ├─ Personal data categories and data subjects
   ├─ Data flows (collection → processing → storage → deletion)
   └─ Technology used

2. Necessity and Proportionality Assessment
   ├─ Lawful basis (Art. 6, and Art. 9 if applicable)
   ├─ Purpose limitation compliance
   ├─ Data minimization compliance
   └─ Storage limitation compliance

3. Risk Assessment
   ├─ Risks to data subjects' rights and freedoms
   ├─ Likelihood and severity of each risk
   └─ Risk matrix (likelihood × impact)

4. Mitigation Measures
   ├─ Technical measures (encryption, pseudonymization, access controls)
   ├─ Organizational measures (policies, training, DPO involvement)
   └─ Residual risk after mitigation
```

## Prior Consultation (Art. 36)

If the DPIA indicates that residual risk remains **high** despite mitigation:
- **Must** consult the supervisory authority (DPA) before processing
- DPA has 8 weeks to respond (extendable by 6 weeks)
- Processing must not begin until DPA responds

## DPIA Review

A DPIA is not a one-time exercise:
- Review when processing operations **change**
- Review at regular intervals (annually recommended)
- Document review dates and findings

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| DPIA done after launch | Art. 35(1) requires "prior to processing" | Conduct during design phase |
| Generic risk assessment | Does not address specific data subjects | Tailor to actual processing context |
| No DPO consultation | Art. 35(2) requires DPO advice | Involve DPO from start |
| Missing data flow diagram | Cannot assess risks without understanding flows | Map data lifecycle |
| DPIA never updated | Stale assessment | Schedule annual review |

**This guide is NOT legal advice. Consult a qualified data protection professional.**
