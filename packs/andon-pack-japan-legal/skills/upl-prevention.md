---
name: upl-prevention
description: Unauthorized Practice of Law (UPL) prevention guide for LLM agents.
---

# UPL Prevention Guide

## Background

### Attorney Act Art. 72 (弁護士法第72条)

> 弁護士又は弁護士法人でない者は、報酬を得る目的で訴訟事件、非訟事件及び
> 審査請求、再調査の請求、再審査請求等行政庁に対する不服申立事件その他
> 一般の法律事件に関して鑑定、代理、仲裁若しくは和解その他の法律事務を
> 取り扱い、又はこれらの周旋をすることを業とすることができない。

Non-attorneys are prohibited from handling legal affairs for profit.

### Nippon Life v. OpenAI (2026)

In March 2026, Nippon Life Insurance sued OpenAI in the Northern District
of Illinois (1:26-cv-02448), alleging that ChatGPT provided unauthorized
legal advice that caused $10.3M in claimed damages.  This case
demonstrates the real-world risk of LLM agents crossing the UPL boundary.

## Safe vs. Unsafe Output Patterns

### SAFE — Information Retrieval

| Pattern | Example | Why Safe |
|---------|---------|----------|
| Statute text quotation | "APPI Art. 23(1) states..." | Primary source, no interpretation |
| Compliance checklist | "Items to verify: [list]" | Procedural, not advisory |
| General explanation | "The APPI applies to..." | Educational, non-specific |
| Professional referral | "Consult a 弁護士 for..." | Directing to licensed professional |

### UNSAFE — Legal Advice

| Pattern | Example | Why Unsafe |
|---------|---------|-----------|
| Specific recommendation | "You should file a claim under Art. 4" | Applying law to specific facts |
| Legal conclusion | "This contract is void" | Legal judgment |
| Litigation strategy | "Sue them for breach of..." | Legal representation |
| Risk assessment | "You will likely win because..." | Legal prediction for specific case |

## Implementation Guidelines for LLM Agents

### DO

1. Quote primary sources with full citation (law_id, article, timestamp)
2. Present information as structured facts, not advice
3. Include disclaimers on every output containing legal information
4. Direct users to licensed professionals for decisions
5. Use phrases like "generally," "according to the statute," "for reference"

### DO NOT

1. Apply law to a user's specific situation
2. Recommend legal actions ("you should sue," "you must file")
3. Predict legal outcomes ("you will likely win")
4. Draft legal documents (contracts, complaints, motions)
5. Interpret ambiguous legal provisions definitively

## Pack 0 Integration

This pack extends Pack 0's `unauthorized_practice_of_law` category with
Japan-specific patterns:

- 弁護士法72条 / 非弁行為 detection
- 法律相談 / 法律事務 boundary patterns
- 訴訟代理 / 示談交渉代行 detection

When triggered, Pack 0 injects:
- Disclaimer stating output is not legal advice
- Source attribution to e-Gov
- Referral to licensed 弁護士

## ANDON Response

When ANDON detects UPL risk in agent output:

1. **GUARD** level activates (output is not blocked, but guarded)
2. Disclaimer is prepended and appended to output
3. Professional referral is included
4. Incident is logged for audit trail

## Guardrails

- This guide itself is informational, not legal advice
- The UPL boundary depends on jurisdiction and specific facts
- When in doubt, err on the side of caution — add disclaimers
- Review Pack 0 safety patterns regularly for coverage gaps
