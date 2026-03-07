# Contributing to ANDON for LLM Agents

Thank you for your interest in contributing! This document covers the process
for contributing to this project.

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or suggest features.
- Include steps to reproduce, expected behavior, and actual behavior.
- For security vulnerabilities, see [Security](#security) below.

### Pull Requests

1. Fork the repository and create a feature branch.
2. Make your changes with clear, descriptive commits.
3. Add or update tests as appropriate.
4. Run the test suite: `python3 -m pytest tests/ -q`
5. Submit a PR with a description of what and why.

### Areas of Interest

- Additional failure classification patterns for other languages/frameworks
- IDE integrations beyond Claude Code (Cursor, Windsurf, etc.)
- Translations (currently English + Japanese)
- Knowledge Pack contributions (see [CONTRIBUTING-PACKS.md](./CONTRIBUTING-PACKS.md))
- Case studies of ANDON/Kaizen applied to your LLM coding workflows

## Contributor License Agreement (CLA)

By submitting a pull request or other contribution to this project, you agree
to the following terms:

1. **License Grant**: Your contribution is submitted under the Apache License
   2.0, the same license that covers this project. You grant AllNew LLC and
   all recipients a perpetual, worldwide, non-exclusive, royalty-free license
   to use, reproduce, modify, and distribute your contribution.

2. **Patent Grant**: If your contribution is covered by any patent or patent
   application you own or control, you grant a royalty-free patent license
   consistent with Apache License 2.0 Section 3.

3. **Original Work**: You represent that your contribution is your original
   work, or that you have the right to submit it under these terms.

4. **No Obligation**: Submitting a contribution does not obligate AllNew LLC
   to accept, merge, or maintain it.

This CLA is consistent with the Apache License 2.0 Section 5 (Submission of
Contributions) and is intended to clarify intellectual property rights given
that certain methods in this project are subject to pending patent applications.

## Code Style

- Python: Follow PEP 8. Use type annotations.
- Shell: Use `set -euo pipefail`. Quote variables.
- Markdown: One sentence per line in source (for clean diffs).

## Testing

```bash
# Run all tests
python3 -m pytest tests/ -q

# Run with verbose output
python3 -m pytest tests/ -v
```

All PRs must pass the existing test suite. Add tests for new functionality.

## Security

If you discover a security vulnerability, please do NOT open a public issue.
Instead, report it privately via GitHub's security advisory feature or contact
the maintainers directly. We will respond within 48 hours.

## Code of Conduct

We are committed to providing a welcoming and respectful environment.
All participants are expected to:

- Be respectful and constructive in communication.
- Accept constructive criticism gracefully.
- Focus on what is best for the project and its users.
- Show empathy toward other community members.

Unacceptable behavior includes harassment, trolling, personal attacks, and
publishing others' private information without consent.

Violations may result in being banned from the project.

## License

By contributing, you agree that your contributions will be licensed under the
Apache License 2.0. See [LICENSE](./LICENSE) for details.
