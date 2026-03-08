---
name: transaction-logging
description: Financial transaction logging and audit trail requirements.
---

# Transaction Logging and Audit Trail

## Core Principle

Every financial transaction must be **traceable, tamper-evident, and auditable**.

## What to Log

| Event | Required Fields | Regulation |
|-------|----------------|-----------|
| Transaction initiation | Timestamp, user ID, amount, currency, type | PCI-DSS Req. 10 |
| Authorization request | Transaction ID, processor response, auth code | PCI-DSS Req. 10.2.1 |
| Transaction completion | Final status, settlement ID, fees | General audit |
| Transaction failure | Error code, reason, retry count | General audit |
| Refund/chargeback | Original transaction ID, reason, amount | General audit |
| Access to transaction data | User ID, timestamp, data accessed | PCI-DSS Req. 10.2.1 |
| Admin actions on transactions | Admin ID, action, before/after state | PCI-DSS Req. 10.2.2 |

## Log Record Structure

```json
{
  "event_id": "evt_unique_id",
  "timestamp": "2026-03-08T12:00:00.000Z",
  "event_type": "transaction.completed",
  "actor": {
    "user_id": "usr_abc123",
    "ip_address": "203.0.113.42",
    "user_agent": "..."
  },
  "transaction": {
    "id": "txn_xyz789",
    "amount": 1000,
    "currency": "JPY",
    "type": "purchase",
    "status": "completed"
  },
  "metadata": {
    "idempotency_key": "...",
    "correlation_id": "..."
  }
}
```

## Security Requirements

### Tamper Evidence

```
MUST:
- Write-once storage (append-only log)
- Cryptographic chaining (each entry hashes previous)
- Separate log storage from application database
- Restrict log deletion to security team only

MUST NOT:
- Allow application code to modify log entries
- Store logs on same server as application
- Allow bulk deletion without audit trail of the deletion
```

### Retention

| Data Type | Minimum Retention | Regulation |
|-----------|------------------|-----------|
| Transaction logs | 5 years (Japan), 7 years (US) | 金商法, SOX |
| Access logs | 1 year minimum | PCI-DSS Req. 10.7 |
| Audit trail modifications | Same as transaction logs | General |

### Access Control

```
- Read access: Compliance team, authorized auditors
- Write access: Application service account only (append)
- Deletion: Security team with documented approval
- Export: Compliance team for regulatory reporting
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Logging PAN in transaction logs | PCI-DSS violation | Log token or masked value only |
| Mutable log entries | Tamper risk, audit failure | Append-only storage |
| Insufficient timestamp precision | Cannot order concurrent events | Use microsecond precision + monotonic counter |
| No correlation ID | Cannot trace distributed transactions | Add correlation ID across services |
| Logs on same server as app | Single point of failure | Separate log infrastructure |

**This guide covers technical patterns only, NOT financial, investment, or legal advice. Consult a QSA, compliance officer, or licensed financial advisor.**
