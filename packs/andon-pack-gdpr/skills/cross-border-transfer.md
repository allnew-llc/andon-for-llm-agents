---
name: cross-border-transfer
description: GDPR Art. 44-49 cross-border data transfer mechanisms.
---

# Cross-Border Data Transfers (Art. 44-49)

## Rule

Personal data may only be transferred outside the EEA if one of the
following mechanisms is in place. No mechanism = no transfer.

## Transfer Mechanisms (in order of preference)

### 1. Adequacy Decision (Art. 45)

The European Commission has determined the country provides adequate protection.

| Country/Territory | Decision Date | Notes |
|-------------------|--------------|-------|
| Japan | Jan 2019 | Mutual adequacy with APPI |
| South Korea | Dec 2021 | |
| UK | Jun 2021 | Reviewed every 4 years |
| Switzerland | Jul 2000 | |
| Canada | Dec 2001 | Commercial organizations only |
| Israel | Jan 2011 | |
| EU-US Data Privacy Framework | Jul 2023 | Self-certification required |

> **Note**: This table is non-exhaustive. Check the [European Commission's
> adequacy decisions page](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en)
> for the current list. Table last verified: March 2026.

If destination country has adequacy decision → transfer permitted (no further
safeguards needed).

### 2. Standard Contractual Clauses — SCCs (Art. 46(2)(c))

When no adequacy decision exists:
- Use the **2021 SCCs** (Commission Implementing Decision 2021/914)
- Four modules: C2C, C2P, P2C, P2P
- Must conduct a **Transfer Impact Assessment (TIA)** alongside SCCs
- Supplementary measures may be required if local laws undermine protections

### 3. Binding Corporate Rules — BCRs (Art. 47)

For intra-group transfers in multinational organizations:
- Must be approved by lead supervisory authority
- Approval process takes 12-18 months typically
- Suitable for large organizations with frequent intra-group transfers

### 4. Derogations (Art. 49) — Last Resort Only

| Derogation | Use Case | Limitation |
|-----------|----------|------------|
| Explicit consent | User informed of risks and consents | Must be truly informed |
| Contract performance | Transfer necessary for user's contract | Occasional, not systematic |
| Public interest | Required by EU or Member State law | Narrow interpretation |
| Legal claims | Necessary for legal proceedings | Case-by-case |
| Vital interests | Life-threatening emergency | Rare |

Derogations are for **occasional** transfers, not systematic/bulk transfers.

## Transfer Impact Assessment (TIA)

Required alongside SCCs. Must assess:

1. **Laws of destination country** — do they require disclosure to government?
2. **Practical enforcement** — is mass surveillance occurring?
3. **Supplementary measures** — encryption, pseudonymization, split processing

## Code Patterns

```
CHECK BEFORE ANY API CALL TO NON-EEA SERVICE:
1. Where is the server located?
2. Is there an adequacy decision for that country?
3. If not, are SCCs in place with the provider?
4. Has a TIA been conducted?
5. Are supplementary measures implemented?

COMMON PITFALL:
- Using a US cloud provider without checking EU-US DPF certification
- CDN nodes in non-adequate countries
- Analytics services sending data to non-EEA destinations
- Third-party SDKs with undisclosed server locations
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Assuming all cloud = EEA | Many providers route through non-EEA | Verify data residency |
| Old SCCs (pre-2021) | No longer valid since Dec 2022 | Update to 2021 SCCs |
| SCC without TIA | Schrems II requires assessment | Conduct TIA |
| Relying on consent for bulk transfers | Derogation is for occasional only | Use SCCs |
| Ignoring sub-processors' locations | Chain of transfers | Map full data flow |

**This guide is NOT legal advice. Consult a qualified data protection professional.**
