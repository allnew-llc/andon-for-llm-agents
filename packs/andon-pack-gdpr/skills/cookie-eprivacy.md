---
name: cookie-eprivacy
description: Cookie consent and ePrivacy Directive compliance guide.
---

# Cookie Consent and ePrivacy (Directive 2002/58/EC)

## Legal Framework

Cookie consent is governed by **two** overlapping regulations:
- **ePrivacy Directive** (2002/58/EC, amended by 2009/136/EC) — governs
  storage/access of information on user devices
- **GDPR** — governs the processing of personal data collected via cookies

Both must be satisfied simultaneously.

## Cookie Categories

| Category | Consent Required? | Examples |
|----------|------------------|---------|
| Strictly necessary | **No** (exempt) | Session ID, shopping cart, CSRF token, cookie consent preference |
| Functional | **Yes** | Language preference, UI customization, font size |
| Analytics | **Yes** | Google Analytics, Matomo, page view counters |
| Advertising/tracking | **Yes** | Ad networks, retargeting pixels, social media trackers |

## Consent Requirements

```
Valid cookie consent must be:
├─ Prior         → No cookies set before consent given
├─ Informed      → Clear description of each cookie category and purpose
├─ Specific      → Granular choice per category (not "accept all" only)
├─ Freely given  → Service must work without non-essential cookies
├─ Withdrawable  → Easy mechanism to change preferences
└─ Documented    → Record of consent for accountability
```

## Implementation Pattern

```
Page Load:
  1. Check for existing consent cookie
  2. If no consent → show banner, block non-essential cookies/scripts
  3. If consent exists → load cookies per saved preferences

Banner Requirements:
  ├─ "Accept All" button
  ├─ "Reject All" button (equally prominent as Accept)
  ├─ "Manage Preferences" → granular per-category toggles
  ├─ Link to cookie policy
  └─ No pre-ticked boxes for non-essential categories

Script Loading:
  ├─ Strictly necessary → load immediately
  ├─ Analytics → load only after analytics consent
  ├─ Advertising → load only after advertising consent
  └─ Use tag manager with consent mode integration

Consent Storage:
  ├─ Store in a strictly necessary cookie (exempt from consent)
  ├─ Record: categories accepted, timestamp, version
  └─ Expire and re-request periodically (6-12 months recommended)
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Cookie wall (no access without consent) | Not freely given | Allow basic access without consent |
| "Accept" prominent, "Reject" hidden | Manipulative design (dark pattern) | Equal prominence |
| Pre-ticked non-essential categories | Not valid consent | Default to unchecked |
| Scripts load before consent | Cookies set before consent | Defer loading until consent |
| No "reject all" option | EDPB guidance requires it | Add equally accessible reject |
| Consent banner reappears every visit | Annoying but not the issue — check if consent cookie is saved | Fix consent storage |
| No consent renewal | Stale consent | Re-request every 6-12 months |

## Server-Side Considerations

```
HTTP Headers:
- Set-Cookie with SameSite=Lax or Strict (not None unless needed)
- Secure flag for HTTPS-only
- HttpOnly for session cookies
- Appropriate expiry (no indefinite cookies)

Analytics Alternatives (consent-free):
- Server-side analytics (no client cookies)
- Aggregated, anonymized counters
- Matomo/Plausible with cookieless mode
- First-party analytics without unique identifiers
```

## Member State Variations

Cookie enforcement varies by Member State. Notable differences:
- **France (CNIL)**: Strict enforcement, significant fines for cookie violations
- **Germany**: State-level DPAs, Planet49 ruling reinforced consent requirements
- **Italy (Garante)**: Cookie guidelines updated 2021, 6-month consent validity
- **Spain (AEPD)**: Cookie guide aligned with EDPB guidance

**This guide is NOT legal advice. Consult a qualified data protection professional.**
