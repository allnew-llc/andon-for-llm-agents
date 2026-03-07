---
name: cors-troubleshoot
description: CORS configuration troubleshooting guide. Use when browser requests fail with CORS errors.
---

# CORS Troubleshooting Guide

## Symptom → Cause → Fix

| Browser Error | Server Issue | Fix |
|--------------|-------------|-----|
| "No 'Access-Control-Allow-Origin' header" | CORS not configured | Add `Access-Control-Allow-Origin` header |
| "not allowed by Access-Control-Allow-Headers" | Custom header not whitelisted | Add header to `Access-Control-Allow-Headers` |
| "Method not allowed" | Preflight rejects method | Add method to `Access-Control-Allow-Methods` |
| Credentials not sent | `withCredentials` + wildcard origin | Use specific origin instead of `*` |

## Express.js Quick Fix

```javascript
const cors = require('cors');
app.use(cors({
  origin: ['https://your-app.com', 'http://localhost:3000'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
}));
```

## Debug Command

```bash
# Test preflight request
curl -v -X OPTIONS https://api.example.com/endpoint \
  -H "Origin: https://your-app.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization,Content-Type" \
  2>&1 | grep -i "access-control"
```
