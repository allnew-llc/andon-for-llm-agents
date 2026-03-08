# andon-pack-financial

> **Alpha** — This pack has not been verified by qualified financial
> compliance professionals. Classification rules and skill content may
> contain errors or omissions. Review all outputs with a QSA, compliance
> officer, or licensed financial advisor before use in compliance
> decision-making.

ANDON Knowledge Pack for financial services compliance in LLM coding agent
workflows. Covers PCI-DSS, financial advice detection, AML/KYC basics,
and secure transaction handling patterns.

## What This Pack Does

When an LLM agent encounters a financial compliance failure, this pack:

1. **Classifies** the failure into financial-specific categories
   (cardholder data exposure, financial advice, AML/KYC gaps, etc.)
2. **Recommends** relevant skills with regulation-level guidance
3. **Extends Pack 0** with financial-specific unauthorized practice patterns
   to guard against false financial advice and compliance assurances

## Skills Included

| Skill | Description |
|-------|-------------|
| `financial-orchestrator` | Financial compliance audit entry point and routing |
| `pci-dss-guide` | PCI-DSS v4.0 compliance patterns for developers |
| `financial-advice-guard` | Detecting unauthorized financial/investment advice |
| `aml-kyc-basics` | AML/KYC implementation patterns |
| `transaction-logging` | Financial transaction logging and audit trail |
| `data-classification` | Financial data classification and handling |

## Classification Rules (9)

| Cause ID | Confidence | Detects |
|----------|-----------|---------|
| `pci_cardholder_exposure` | 0.90 | Cardholder data in logs/output/storage |
| `pci_encryption_gap` | 0.85 | Payment data without encryption |
| `financial_advice_detected` | 0.82 | Unauthorized financial advice in output |
| `pci_scope_violation` | 0.80 | CDE boundary violation |
| `transaction_logging_gap` | 0.78 | Transaction not properly logged |
| `key_management_failure` | 0.77 | Encryption key management failure |
| `aml_kyc_gap` | 0.75 | AML/KYC verification missing |
| `authentication_weakness` | 0.73 | Weak auth in financial system |
| `data_retention_financial` | 0.70 | Data retained beyond requirement |

## Requirements

- **Pack 0 (output-safety-guard)** — required (regulated domain)

## Legal Notice

This pack provides structured guidance based on PCI-DSS v4.0 and general
financial compliance patterns. It does NOT provide financial, investment,
tax, or legal advice. All outputs should be reviewed by qualified
professionals (QSA, compliance officer, licensed financial advisor)
before use in compliance decision-making.

## License

Apache-2.0
