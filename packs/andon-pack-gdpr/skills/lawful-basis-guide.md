---
name: lawful-basis-guide
description: GDPR Art. 5-6 lawful basis selection and documentation guide.
---

# Lawful Basis Guide (Art. 5-6)

## The Six Lawful Bases (Art. 6(1))

| Basis | Article | When to Use | Key Requirement |
|-------|---------|-------------|-----------------|
| Consent | Art. 6(1)(a) | User actively opts in | Freely given, specific, informed, unambiguous |
| Contract | Art. 6(1)(b) | Processing necessary for contract performance | Must be genuinely necessary, not just useful |
| Legal obligation | Art. 6(1)(c) | Required by EU or Member State law | Identify the specific legal provision |
| Vital interests | Art. 6(1)(d) | Life-threatening emergency | Last resort only |
| Public interest | Art. 6(1)(e) | Official authority or public interest task | Basis in EU or Member State law required |
| Legitimate interest | Art. 6(1)(f) | Business need balanced against data subject rights | Requires documented balancing test (LIA) |

## Consent Requirements (Art. 7, Recital 32)

```
Valid consent must be:
├─ Freely given    → No imbalance of power, no bundling with T&C
├─ Specific        → Separate consent per purpose
├─ Informed        → Clear language, identity of controller stated
├─ Unambiguous     → Affirmative action (no pre-ticked boxes)
└─ Withdrawable    → As easy to withdraw as to give
```

### Code Patterns

```
GOOD:
- Separate checkbox per purpose (unchecked by default)
- Clear "Withdraw consent" button in account settings
- Consent receipt stored with timestamp + version

BAD:
- Pre-ticked consent checkbox
- "By using this service you consent to..."
- Consent bundled with Terms of Service acceptance
- No mechanism to withdraw consent
```

## Legitimate Interest Assessment (LIA)

When relying on Art. 6(1)(f), document:

1. **Purpose test** — What is the legitimate interest?
2. **Necessity test** — Is processing necessary for that interest?
3. **Balancing test** — Do data subject rights override the interest?

## Special Categories (Art. 9)

Processing health, biometric, genetic, racial/ethnic, political, religious,
trade union, sex life, or sexual orientation data requires BOTH:
- A lawful basis under Art. 6, AND
- An Art. 9(2) exception (typically: explicit consent or substantial public interest)

## Common Mistakes in Code

| Mistake | Problem | Fix |
|---------|---------|-----|
| Single "I agree" for all processing | Not specific | Granular consent per purpose |
| No consent withdrawal API endpoint | Art. 7(3) violation | Add DELETE /consent/{purpose} endpoint |
| Consent stored without timestamp | Cannot prove validity | Store timestamp + consent text version |
| Using consent when contract basis applies | Unnecessary, creates withdrawal risk | Use correct basis |
| No re-consent on purpose change | Art. 6(4) violation | Trigger re-consent flow |

**This guide is NOT legal advice. Consult a qualified data protection professional.**
