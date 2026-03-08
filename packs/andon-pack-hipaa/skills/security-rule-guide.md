---
name: security-rule-guide
description: HIPAA Security Rule technical safeguards for developers.
---

# HIPAA Security Rule Guide

## Core Principle

The Security Rule (45 CFR §164.302-318) requires covered entities and
business associates to implement safeguards to ensure the confidentiality,
integrity, and availability of ePHI.

## Three Safeguard Categories

### Administrative Safeguards (§164.308)

| Standard | Key Requirement | Developer Action |
|----------|----------------|-----------------|
| Security Management | Risk analysis and management | Document threats and mitigations |
| Workforce Security | Authorization procedures | Implement user provisioning/deprovisioning |
| Information Access | Access authorization | Role-based access control |
| Security Awareness | Training program | Security training documentation |
| Security Incidents | Response procedures | Incident detection and logging |
| Contingency Plan | Emergency access, backups | Backup and disaster recovery |
| Evaluation | Periodic assessment | Security testing schedule |

### Physical Safeguards (§164.310)

| Standard | Key Requirement | Developer Action |
|----------|----------------|-----------------|
| Facility Access | Limit physical access | (Infrastructure team) |
| Workstation Use | Policies for workstation use | Session timeouts, screen locks |
| Workstation Security | Physical safeguards | (Infrastructure team) |
| Device and Media | Disposal, reuse procedures | Secure data wiping |

### Technical Safeguards (§164.312)

| Standard | Specification | Implementation Pattern |
|----------|-------------|----------------------|
| Access Control (§164.312(a)) | Unique User ID | Every user has unique identifier |
| | Emergency Access | Break-the-glass procedure |
| | Automatic Logoff | Session timeout (15-30 min recommended) |
| | Encryption/Decryption | AES-256 for ePHI at rest |
| Audit Controls (§164.312(b)) | Audit logging | Log all ePHI access events |
| Integrity (§164.312(c)) | Integrity mechanisms | Checksums, digital signatures |
| Authentication (§164.312(d)) | Person/Entity auth | MFA for ePHI access |
| Transmission Security (§164.312(e)) | Integrity controls | TLS 1.2+ |
| | Encryption | End-to-end encryption |

## Implementation Patterns

### Access Control

```
Required controls:
├─ Unique user identification
│   ├─ No shared accounts
│   ├─ Service accounts have individual owners
│   └─ Audit trail traces to individual
├─ Role-based access
│   ├─ Define roles: clinician, admin, billing, research
│   ├─ Map roles to minimum necessary PHI access
│   └─ Review assignments quarterly
├─ Emergency access (break-the-glass)
│   ├─ Predefined elevated access for emergencies
│   ├─ Requires documented justification
│   ├─ Automatically logged and flagged for review
│   └─ Time-limited (auto-reverts)
└─ Session management
    ├─ Automatic logoff after inactivity (15-30 min)
    ├─ Re-authentication for sensitive operations
    └─ Concurrent session limits
```

### Audit Controls

```
MUST log for every ePHI access:
├─ User ID (who)
├─ Timestamp (when) — use UTC, microsecond precision
├─ Action (what) — read, create, update, delete, export
├─ Resource (which record/field)
├─ Outcome (success/failure)
├─ Source (IP, device, application)
└─ Purpose (treatment, payment, operations, other)

Log retention: minimum 6 years
Log storage: separate from application, tamper-evident
Log access: restricted to security/compliance team
```

### Encryption Requirements

```
At rest:
├─ AES-256 (or equivalent) for all ePHI
├─ Key management separate from data
├─ Key rotation schedule (annual minimum)
└─ Reference: NIST SP 800-111

In transit:
├─ TLS 1.2+ mandatory
├─ Strong cipher suites only
├─ Certificate validation enforced
└─ Reference: NIST SP 800-52
```

## Risk Analysis Pattern

```
For each system component:
1. Identify ePHI → what data, where stored, how transmitted
2. Identify threats → unauthorized access, data loss, malware
3. Identify vulnerabilities → unpatched systems, weak auth
4. Assess likelihood → high/medium/low
5. Assess impact → high/medium/low
6. Determine risk level → likelihood × impact
7. Document mitigations → controls, timelines, owners
```

## Common Mistakes

| Mistake | Section | Fix |
|---------|---------|-----|
| Shared accounts for ePHI access | §164.312(a)(2)(i) | Unique user IDs |
| No automatic logoff | §164.312(a)(2)(iii) | Session timeout |
| Audit logs on same server | §164.312(b) | Separate log infrastructure |
| No MFA for remote access | §164.312(d) | Implement MFA |
| Unencrypted ePHI in transit | §164.312(e)(1) | TLS 1.2+ |

**This guide covers technical patterns only, NOT legal advice.**
