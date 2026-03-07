---
name: api-auth-guide
description: Authentication & authorization patterns for web APIs. Use when encountering 401/403 errors, token issues, or auth architecture decisions.
---

# API Authentication & Authorization Guide

## Common 401/403 Patterns

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `401 Unauthorized` | Missing or expired token | Check token refresh logic |
| `403 Forbidden` | Valid token but insufficient permissions | Check role/scope assignments |
| `401` after deploy | Secret rotation missed | Verify all environments have current secrets |
| `401` intermittent | Token expiry race condition | Add token refresh buffer (e.g., refresh at 80% of TTL) |

## Auth Architecture Decision Tree

```
Is this a public API?
  ├─ Yes → API Key (rate limiting) + optional OAuth for write ops
  └─ No → Is it user-facing?
       ├─ Yes → OAuth 2.0 / OIDC
       └─ No (service-to-service) → mTLS or signed JWT
```

## JWT Checklist

- [ ] Validate signature (don't just decode)
- [ ] Check `exp` (expiry) claim
- [ ] Check `iss` (issuer) claim
- [ ] Check `aud` (audience) claim
- [ ] Use RS256 or ES256 (not HS256 with shared secret)
- [ ] Store refresh tokens securely (httpOnly cookie or encrypted storage)

## Quick Fixes

### Token not refreshing
```python
# Add refresh buffer — don't wait for actual expiry
if token.expires_at - datetime.now() < timedelta(minutes=5):
    token = refresh_token(token.refresh_token)
```

### 403 on correct role
```bash
# Debug: decode JWT and check scopes
echo $TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | jq '.scope'
```
