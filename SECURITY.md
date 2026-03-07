# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please do **NOT** open a public issue.

Instead, report it privately using one of the following methods:

1. **GitHub Security Advisories** (preferred): Use the "Report a vulnerability" button on the Security tab of this repository.
2. **Direct contact**: Open a confidential issue via [GitHub Security Advisories](https://github.com/allnew-llc/andon-for-llm-agents/security/advisories).

We will acknowledge your report within 48 hours and provide an estimated timeline for a fix.

## Scope

This project is a framework of shell scripts and Python hooks for LLM agent safety. Security-relevant areas include:

- **Input handling**: Shell scripts process JSON payloads from stdin
- **Path traversal**: Pack installation writes files to a user-specified directory
- **Regex patterns**: Safety patterns loaded from YAML files are compiled as regular expressions
- **Secret redaction**: The runtime redacts known API key formats from incident logs

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | Yes       |

## Disclosure Policy

We follow a coordinated disclosure process. Please allow us reasonable time to address the issue before any public disclosure.
