---
name: financial-advice-guard
description: Detecting and guarding against unauthorized financial advice.
---

# Financial Advice Guard

## Purpose

LLM coding agents may generate content that constitutes unauthorized financial,
investment, or tax advice. This skill helps detect and guard against such output.

## What Constitutes Financial Advice

| Category | Examples | Risk |
|----------|---------|------|
| Investment advice | "You should buy X stock" | Securities regulation violation |
| Tax advice | "File your taxes this way" | Unauthorized tax practice |
| Financial planning | "Allocate 60% to equities" | Requires licensed advisor |
| Insurance advice | "This policy is best for you" | Requires licensed agent |
| Credit advice | "Take this loan, not that one" | Lending regulation |

## Detection Patterns

### High-Risk Phrases (GUARD level)

```
English:
- "you should invest in..."
- "I recommend buying/selling..."
- "guaranteed return"
- "risk-free investment"
- "this stock/fund will..."
- "as your financial advisor..."
- "in my professional financial opinion..."

Japanese:
- 「投資すべき」「買い推奨」
- 「確実に儲かる」「元本保証」
- 「この銘柄は上がる」
- 「ファイナンシャルアドバイザーとして」
```

### Acceptable Patterns (No guard)

```
General information (OK):
- "Stocks historically return ~7-10% annually"
- "Diversification reduces portfolio risk"
- "Index funds have lower fees than actively managed funds"
- "Consider consulting a financial advisor"

Code implementation (OK):
- "Use this function to calculate compound interest"
- "Implement the portfolio rebalancing algorithm"
- "Add input validation for transaction amounts"
```

## Guard Response

When financial advice is detected, Pack 0 applies:

```
Level: GUARD (preserve output + inject disclaimer)

Disclaimer:
  ⚠️ Financial Information Notice
  This output provides general information only and is NOT financial,
  investment, or tax advice. Financial decisions should be made with
  the guidance of a qualified financial advisor.
```

## Regulatory Context

| Jurisdiction | Law | Requirement |
|-------------|-----|-------------|
| Japan | 金融商品取引法 (FIEA) | Investment advice requires registration as 投資助言業 |
| US | Securities Exchange Act | Investment advice requires SEC/state registration |
| EU | MiFID II | Investment advice requires authorization |
| UK | Financial Services Act | Financial advice requires FCA authorization |

## When to Escalate

- Any output that recommends specific securities, funds, or financial products
- Tax filing instructions specific to a user's situation
- Insurance coverage recommendations
- Loan or credit product comparisons with recommendations

**This guide covers technical patterns only, NOT financial, investment, or legal advice. Consult a QSA, compliance officer, or licensed financial advisor.**
