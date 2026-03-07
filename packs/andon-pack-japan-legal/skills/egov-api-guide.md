---
name: egov-api-guide
description: e-Gov Law API v2 usage guide for retrieving Japanese statutes.
---

# e-Gov Law API v2 Guide

## Overview

The [e-Gov Law API](https://laws.e-gov.go.jp/apitop/) provides
machine-readable access to all Japanese statutes, cabinet orders,
and ministerial ordinances.  Published by the Digital Agency under
Government Standard Terms of Use (Version 2.0).

**Base URL**: `https://laws.e-gov.go.jp/api/1`

## Endpoints

### Search Laws by Title

```
GET /laws?law_title={title}&limit={n}
```

```bash
curl -s 'https://laws.e-gov.go.jp/api/1/laws?law_title=個人情報の保護に関する法律&limit=3'
```

### Search by Keyword

```
GET /keyword?keyword={text}&limit={n}
```

```bash
curl -s 'https://laws.e-gov.go.jp/api/1/keyword?keyword=業務委託&limit=5'
```

### Get Law Data (Full Text or Article)

```
GET /lawdata/{law_id_or_num_or_revision_id}
GET /lawdata/{id}?elm={element}&response_format=json&law_full_text_format=json
```

```bash
# Full text
curl -s 'https://laws.e-gov.go.jp/api/1/lawdata/415AC0000000057'

# Specific article (APPI Art. 23)
curl -s 'https://laws.e-gov.go.jp/api/1/lawdata/415AC0000000057?elm=MainProvision-Article[23]'
```

### Get Revision History

```
GET /law_revisions/{law_id_or_num}
```

```bash
curl -s 'https://laws.e-gov.go.jp/api/1/law_revisions/415AC0000000057'
```

## Key Law IDs

| Law | law_id | Common Name |
|-----|--------|-------------|
| 個人情報保護法 (APPI) | `415AC0000000057` | Personal Information Protection |
| 特定商取引法 | `351AC0000000057` | Specified Commercial Transactions |
| 消費者契約法 | `412AC0000000061` | Consumer Contract Act |
| 電気通信事業法 | `359AC0000000086` | Telecommunications Business Act |
| 著作権法 | `345AC0000000048` | Copyright Act |
| 景品表示法 | `337AC0000000134` | Premiums & Representations |

## Response Format

```json
{
  "law_info": {
    "law_id": "415AC0000000057",
    "law_num": "平成十五年法律第五十七号",
    "law_title": "個人情報の保護に関する法律"
  },
  "law_full_text": "..."
}
```

## Citation Format

For every substantive claim, include:

```
法令名: {law_title}
法令番号: {law_num}
法令ID: {law_id}
改正ID: {law_revision_id}
該当条文: 第{n}条
取得日時: {ISO 8601 timestamp}
API: e-Gov Law API v2
```

## Guardrails

- Treat API responses as primary-source snapshots (point-in-time)
- Always record retrieval timestamp — laws can be amended
- Check revision history when temporal accuracy matters
- Distinguish statutory text from interpretation
