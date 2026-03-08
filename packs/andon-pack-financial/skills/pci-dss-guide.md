---
name: pci-dss-guide
description: PCI-DSS compliance patterns for developers.
---

# PCI-DSS Developer Guide

## Core Principle

**Never store what you don't need. Never expose what you do store.**

## What You Must Protect

| Data Element | Storage Allowed? | Must Encrypt? | Must Mask? |
|-------------|-----------------|---------------|------------|
| PAN (card number) | Yes (if needed) | Yes | Yes (show only last 4) |
| Cardholder name | Yes | Recommended | No |
| Expiration date | Yes | Recommended | No |
| CVV/CVC | **Never** | N/A | N/A |
| PIN / PIN block | **Never** | N/A | N/A |
| Full track data | **Never** | N/A | N/A |

## The 12 Requirements (PCI-DSS v4.0)

| # | Requirement | Developer Action |
|---|-------------|-----------------|
| 1 | Network security controls | Firewall rules, network segmentation |
| 2 | Secure configurations | No default passwords, harden systems |
| 3 | Protect stored account data | Encrypt PAN, never store CVV |
| 4 | Encrypt transmissions | TLS 1.2+ for all cardholder data |
| 5 | Anti-malware | Keep systems patched, scan regularly |
| 6 | Secure development | SDLC, code review, vulnerability management |
| 7 | Restrict access | Need-to-know, role-based access |
| 8 | Identify and authenticate | Unique IDs, MFA for admin, strong passwords |
| 9 | Physical security | (Infrastructure team responsibility) |
| 10 | Log and monitor | Audit trails for all access to cardholder data |
| 11 | Test regularly | Vulnerability scans, penetration tests |
| 12 | Security policies | Document everything, train staff |

## Code Patterns

### PAN Handling

```
GOOD:
- Tokenize PAN immediately at point of entry
- Store tokens, not actual card numbers
- If PAN must be stored: AES-256 encryption + separate key management
- Display: mask all but last 4 digits (****-****-****-1234)
- Logs: NEVER log PAN, even partially

BAD:
- Storing PAN in plain text anywhere
- Logging request bodies that contain card data
- Passing PAN in URL query parameters
- Storing PAN in client-side storage (localStorage, cookies)
- Including PAN in error messages
```

### Tokenization

```
Flow:
1. Customer enters card → sent directly to payment processor (iframe/SDK)
2. Processor returns a token (e.g., tok_abc123)
3. Your system stores only the token
4. For charges, send token to processor (never raw card data)

Benefits:
- Your system is OUT of PCI scope for card storage
- Tokens are useless if stolen
- Dramatically reduces compliance burden
```

### Logging (Req. 10)

```
MUST LOG:
- All access to cardholder data (Req. 10.2.1)
- All actions by administrators (Req. 10.2.2)
- Access to audit trails (Req. 10.2.3)
- Invalid logical access attempts (Req. 10.2.4)
- Changes to authentication mechanisms (Req. 10.2.5)
- Initialization/stopping of audit logs (Req. 10.2.6)

MUST NEVER LOG:
- Full PAN
- CVV/CVC
- PIN data
- Full track data
```

## Common Mistakes

| Mistake | PCI Requirement | Fix |
|---------|----------------|-----|
| CVV stored in database | Req. 3.3.2 | Delete after authorization |
| PAN in application logs | Req. 3.4 | Mask/tokenize before logging |
| HTTP (not HTTPS) for payment forms | Req. 4.2.1 | Enforce TLS 1.2+ |
| Shared admin accounts | Req. 8.2.1 | Unique ID per user |
| No MFA for admin access to CDE | Req. 8.4.2 | Implement MFA |

**This guide covers technical patterns only, NOT financial, investment, or legal advice. Consult a QSA, compliance officer, or licensed financial advisor.**
