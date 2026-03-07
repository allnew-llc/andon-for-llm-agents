---
name: api-security-checklist
description: OWASP API Security Top 10 quick checklist. Use during security reviews or when investigating API vulnerabilities.
---

# API Security Quick Checklist (OWASP Top 10)

## Pre-deployment Check

| # | Risk | Check | Status |
|---|------|-------|--------|
| 1 | Broken Object Level Auth | Every endpoint checks object ownership | [ ] |
| 2 | Broken Authentication | Rate limit login, use strong tokens | [ ] |
| 3 | Broken Object Property Auth | Filter response fields per role | [ ] |
| 4 | Unrestricted Resource Consumption | Rate limiting + pagination limits | [ ] |
| 5 | Broken Function Level Auth | Admin endpoints require admin role | [ ] |
| 6 | Unrestricted Access to Sensitive Flows | CAPTCHA or step-up auth for sensitive ops | [ ] |
| 7 | Server-Side Request Forgery | Validate/allowlist outbound URLs | [ ] |
| 8 | Security Misconfiguration | No debug mode, proper CORS, HTTPS only | [ ] |
| 9 | Improper Inventory Management | No shadow/deprecated endpoints exposed | [ ] |
| 10 | Unsafe Consumption of APIs | Validate all third-party API responses | [ ] |

## Quick Wins

```bash
# Check for exposed debug endpoints
curl -s https://api.example.com/debug | head -1
curl -s https://api.example.com/swagger.json | head -1

# Check CORS headers
curl -s -I -X OPTIONS https://api.example.com/api/v1/users \
  -H "Origin: https://evil.com" | grep -i access-control

# Check rate limiting
for i in $(seq 1 20); do
  curl -s -o /dev/null -w "%{http_code}\n" https://api.example.com/api/v1/login
done | sort | uniq -c
```
