# andon-pack-japan-legal

ANDON Knowledge Pack for Japanese law statute retrieval, powered by
[e-Gov Law API v2](https://laws.e-gov.go.jp/apitop/).

## What This Pack Does

When an LLM agent encounters a legal-domain failure, this pack:

1. **Classifies** the failure into Japan-specific legal domains
   (APPI, specified commercial transactions, consumer contract, etc.)
2. **Recommends** relevant skills with e-Gov API workflows
3. **Extends Pack 0** with Japan-specific UPL (unauthorized practice of law)
   patterns to guard against 弁護士法72条 violations

## Skills Included

| Skill | Description |
|-------|-------------|
| `legal-orchestrator` | Multi-law statute retrieval and audit entry point |
| `egov-api-guide` | e-Gov Law API v2 usage guide |
| `appi-guide` | Personal Information Protection Act (APPI) |
| `tokusho-guide` | Specified Commercial Transactions Act |
| `consumer-contract-guide` | Consumer Contract Act |
| `upl-prevention` | Unauthorized Practice of Law prevention |

## Requirements

- **Pack 0 (output-safety-guard)** — required (regulated domain)

## Legal Notice

This pack provides structured access to primary legal sources via the
Digital Agency's e-Gov Law API. It does **NOT** provide legal advice
and does **NOT** guarantee legal compliance. All outputs are
reference information derived from statute retrieval and should be
reviewed by a licensed attorney (弁護士) before use in legal
decision-making.

The e-Gov Law API data is published under the
[Government Standard Terms of Use (Version 2.0)](https://www.e-gov.go.jp/policy/terms.html).

## License

Apache-2.0
