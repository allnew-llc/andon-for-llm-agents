---
name: consumer-contract-guide
description: Consumer Contract Act (消費者契約法) compliance guide.
---

# Consumer Contract Act Guide

## Overview

The Consumer Contract Act (消費者契約法, Act No. 61 of 2000, as amended) protects
consumers in B2C contracts by providing rescission rights and invalidating
unfair contract terms.

**law_id**: `412AC0000000061`

## Key Principles

### Rescission Rights (取消権) — Art. 4

Consumers may rescind contracts formed under:

| Ground | Article | Example |
|--------|---------|---------|
| Misrepresentation | Art. 4(1)(i) | False claims about product features |
| Definitive prediction | Art. 4(1)(ii) | "This stock will definitely go up" |
| Disadvantage concealment | Art. 4(2) | Hiding cancellation penalties |
| Excessive solicitation | Art. 4(3) | Pressure tactics, refusing to leave |

### Invalid Contract Terms (無効条項) — Art. 8-10

| Invalid Term | Article | Example |
|-------------|---------|---------|
| Full liability exclusion | Art. 8(1) | "We are not liable for any damages" |
| Cancellation penalty > actual damage | Art. 9(1) | ¥50,000 penalty for ¥500 service |
| Against consumer interest | Art. 10 | Unilateral terms change clause |

## App Development Checklist

### Terms of Service Review

- [ ] No blanket liability exclusion (Art. 8)
- [ ] Cancellation fees proportional to actual damages (Art. 9)
- [ ] No unilateral terms modification without consent (Art. 10)
- [ ] Auto-renewal terms clearly disclosed
- [ ] Free trial → paid transition clearly explained

### Subscription/IAP Considerations

| Issue | Risk | Guidance |
|-------|------|---------|
| Hidden auto-renewal | High | Clear disclosure + easy cancellation |
| Excessive cancellation fee | High | Must be proportional to actual damage |
| Unclear free trial terms | Medium | Show exactly when billing starts |
| Unilateral price increase | Medium | Require consent or provide opt-out |

### 2023 Amendment — Dark Patterns

The 2023 amendments added provisions against:

- Confusing cancellation procedures (Art. 4(3)(vii-viii))
- Misleading "confirm purchase" screens
- Burying cancellation options in deep menu hierarchies

## e-Gov API Quick Reference

```bash
# Get Consumer Contract Act
curl -s 'https://laws.e-gov.go.jp/api/1/lawdata/412AC0000000061'

# Invalid terms provisions (Art. 8)
curl -s 'https://laws.e-gov.go.jp/api/1/lawdata/412AC0000000061?elm=MainProvision-Article[8]'
```

## Guardrails

- This guide provides structured compliance checks, NOT legal advice
- The Act applies to ALL B2C contracts — including app subscriptions
- Verify current text via e-Gov API
- Consult a licensed professional for binding compliance decisions
