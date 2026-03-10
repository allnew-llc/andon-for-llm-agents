[日本語](./README.ja.md)

# ANDON for LLM Agents

[![CI](https://github.com/allnew-llc/andon-for-llm-agents/actions/workflows/test.yml/badge.svg)](https://github.com/allnew-llc/andon-for-llm-agents/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**Lean manufacturing (TPS) principles applied to LLM-assisted coding.**

Stop defects from flowing downstream. Learn from every failure. Standardize improvements automatically.

---

## The Problem

LLM coding agents have structural weaknesses that waste time and produce poor results:

1. **Blind retry loops** — When a command fails, agents retry the same thing or make random changes
2. **Whack-a-mole debugging** — Fix one error, hit a different one, repeat forever
3. **Volatile learning** — Knowledge from debugging sessions evaporates between conversations
4. **Silent spec drift** — Agents quietly relax requirements to make things pass
5. **Gate gaming** — Agents optimize for passing checks rather than producing quality work

These are not bugs in any specific LLM — they are **structural properties** of goal-optimizing systems.

## The Solution: TPS for LLM Agents

Lean manufacturing solves analogous problems with two pillars:

### Pillar 1: Jidoka (Autonomation) — Stop on Abnormality

When a defect is detected, **stop the line immediately**. Don't pass defects to the next process.

```
Detect → Stop → Fix → Investigate → Prevent Recurrence → Update Standards
```

In LLM coding:
| TPS Concept | Software Practice |
|-------------|-------------------|
| Abnormality detection | Non-zero exit code, test failure, build error |
| Line stop (ANDON) | Block forward-progress commands (push, deploy, publish) |
| Fix | Revert or minimal patch to restore normal state |
| Investigate | Five Whys root cause analysis on actual code/logs |
| Poka-yoke | Add compile-time checks, tests, pre-commit hooks |

### Pillar 2: Kaizen (Continuous Improvement) — Learn and Standardize

Every failure is a learning opportunity. Capture knowledge, route it to the right place, and update standards so the same problem never recurs.

```
Capture Learning → Route to Standard → Update → Verify
```

Prevention levels (always aim for L1-L2):
| Level | Type | Reliability | Example |
|-------|------|-------------|---------|
| L1 | Poka-yoke (make it impossible) | Highest | Compile error, type constraint |
| L2 | Auto-detect | High | Test, CI check, linter rule |
| L3 | Standardize | Medium | Documentation, checklist |
| L4 | Alert | Low | Comment, reminder |

---

## Where ANDON Fits

ANDON is not a replacement for your coding agent — it's the safety and learning
layer that wraps around it.

Major AI companies have introduced safety mechanisms for coding agents: sandbox
isolation (OpenAI Codex), hook systems (Anthropic Claude Code), planning critics
(Google Jules), security scanning (GitHub Copilot), and iteration limits (Amazon Q).
These focus on making agents **smarter** or making environments **safer**.

ANDON addresses a different gap: **learning from failures and preventing recurrence**.

| Concern | Addressed By | ANDON's Role |
|---------|-------------|--------------|
| Code generation quality | Codex (RL-trained), Jules (Planning Critic) | Complementary — not addressed |
| Code security scanning | Copilot (CodeQL), Claude Code Security | Complementary — not addressed |
| Sandbox isolation | Codex (containers), GitHub Actions | Complementary — not addressed |
| Failure → line stop → root cause | **ANDON** | Primary solution |
| Repeated failure pattern detection | **ANDON (Meta-ANDON)** | Primary solution (no equivalent elsewhere) |
| Failure → standardized prevention | **ANDON (Kaizen)** | Primary solution (no equivalent elsewhere) |
| Output safety for professional practice | **ANDON (Pack 0)** | Primary solution for coding agents |
| Specification drift prevention | **ANDON** | Primary solution |
| Domain-specific failure classification | **ANDON (Knowledge Packs)** | Extensible plugin system |

ANDON works with any LLM coding agent that supports hooks or callbacks —
Claude Code, Codex, custom AutoGPT/LangChain implementations, or bespoke CLI agents.

Academic research supports the need: UC Berkeley's MAST taxonomy (2025) found
**41–86.7% failure rates** in multi-agent LLM systems, with 79% of failures
stemming from orchestration issues. ANDON's structural approach — detect, stop,
analyze, standardize — directly addresses these systemic failures rather than
optimizing individual agent performance.

---

## What's Included

```
andon-for-llm-agents/
├── README.md                          # This file
├── LICENSE                            # Apache-2.0
├── NOTICE                             # Copyright & patent notice
├── CONTRIBUTING.md                    # Contribution guide & CLA
├── CONTRIBUTING-PACKS.md              # Knowledge Pack specification
├── CODE_OF_CONDUCT.md                 # Contributor Covenant
├── SECURITY.md                        # Vulnerability reporting policy
├── INTEGRATION.md                     # Full integration guide
├── pyproject.toml                     # PEP 621 project metadata
├── .github/                           # CI & community templates
│   └── workflows/test.yml            # GitHub Actions CI
├── rules/                             # CLAUDE.md / AGENTS.md rule modules
│   ├── 70-kaizen-learning.md          # Core ANDON + Kaizen rules
│   └── 45-quality-driven-execution.md # Gate-gaming prevention
├── hooks/                             # Claude Code hook scripts
│   ├── tps-kaizen-runtime.py          # ANDON runtime engine (incident mgmt)
│   ├── tps-andon-control.sh           # User-facing ANDON control CLI
│   ├── tps-andon-pretool-guard.sh     # PreToolUse: block forward-progress when ANDON open
│   ├── tps-andon-posttool-guard.sh    # PostToolUse: auto-detect failures
│   ├── kaizen-learning-capture.sh     # PostToolUse: prompt knowledge capture on fix commits
│   ├── meta_andon_guard.py            # Meta-ANDON: detect repeated failure patterns
│   ├── output_safety_guard.py         # Pack 0: Output Safety Guard engine
│   ├── domain_classifier.py           # Domain classification + skill routing
│   ├── pack_loader.py                 # Knowledge Pack loader + validator
│   ├── andon_cli.py                   # Pack management CLI
│   └── safety_patterns/               # Pack 0 guard pattern definitions
│       ├── upl.yaml                   #   Unauthorized Practice of Law
│       └── unqualified.yaml           #   Unauthorized Professional Practice
├── packs/                             # Knowledge Packs
│   ├── andon-pack-japan-legal/        # Japanese law statute retrieval (e-Gov API)
│   ├── andon-pack-ios-development/    # iOS app development & App Store
│   ├── andon-pack-gdpr/              # EU GDPR compliance
│   ├── andon-pack-financial/         # Financial services (PCI-DSS, AML/KYC)
│   └── andon-pack-hipaa/             # HIPAA healthcare compliance
├── skills/                            # Skill definitions (slash commands)
│   └── tps-kaizen/
│       ├── tps-kaizen.md              # Main skill entry point
│       ├── SKILL.md                   # Full skill documentation
│       └── references/
├── tests/                             # Test suite
│   └── test_output_safety_guard.py    # Tests for Pack 0 + classifier + loader
└── examples/                          # Integration examples
    ├── demo-run.py                    # Interactive demo (try it now!)
    ├── locales/                       # i18n locale files
    │   ├── en.json                    #   English (default)
    │   └── ja.json                    #   Japanese
    ├── sample-pack/                   # Sample Knowledge Pack (Web API Security)
    ├── claude-code-settings.json      # Hook registration example
    └── minimal-setup.md               # Quick start with 3 files
```

---

## Pack 0: Output Safety Guard

Bundled with the core runtime.  A keyword-based heuristic filter that scans
LLM coding agent outputs for patterns associated with professional practice
domains (law, medicine, finance) and injects appropriate disclaimers.  This is
a best-effort safety net, not a guarantee of detection or suppression.

| # | Category | Level | Action |
|---|----------|-------|--------|
| 1 | Unauthorized Practice of Law | GUARD | Disclaimer + attorney referral |
| 2 | Unauthorized Professional Practice | GUARD | Disclaimer + specialist referral |

**Guard levels**: GUARD injects disclaimers while preserving the original
output. WARN appends advisory notes. The framework also supports BLOCK
(replace output entirely) for use by Knowledge Packs.

Content moderation (violence, self-harm, discrimination, etc.) is
intentionally out of scope — the underlying LLM's own safety layer handles
those categories. Pack 0 focuses on professional practice concerns specific
to LLM coding agents that may generate legal, financial, or architectural
advice in documentation or comments.

---

## Knowledge Packs

Extend ANDON with domain-specific failure detection, classification, and
skill recommendations.  Packs are self-contained plugins defined by a
`knowledge-pack.yaml` manifest.

### Available Packs

| Pack | Domain | Regulated | Skills | Status |
|------|--------|-----------|--------|--------|
| `andon-pack-japan-legal` | Japanese law (e-Gov API) | Yes | 6 | Stable |
| `andon-pack-ios-development` | iOS / App Store | No | 5 | Stable |
| `andon-pack-gdpr` | EU GDPR | Yes | 8 | Alpha |
| `andon-pack-financial` | Financial services (PCI-DSS, AML/KYC) | Yes | 6 | Alpha |
| `andon-pack-hipaa` | HIPAA healthcare | Yes | 7 | Alpha |
| `sample-web-api-security` | API security (example) | No | 3 | Example |

### Pack CLI

```bash
# List installed packs
andon pack list

# Validate a pack
andon pack validate packs/andon-pack-japan-legal

# Show pack details
andon pack info andon-pack-japan-legal

# Install a pack
andon pack install ./my-custom-pack
```

### Creating Your Own Pack

See [CONTRIBUTING-PACKS.md](./CONTRIBUTING-PACKS.md) for the full specification.

```bash
# Start from the sample
cp -r examples/sample-pack my-pack
# Edit knowledge-pack.yaml, add skills to skills/
andon pack validate ./my-pack
```

### Regulated Domain Enforcement

Packs covering licensed professions (law, medicine, finance) MUST declare
Pack 0 as a dependency.  The pack loader **refuses to load** packs that
cover regulated domains without this dependency — preventing domain expertise
from being deployed without output safety guards.

> **Note**: Knowledge Packs do not guarantee legal compliance, regulatory
> conformance, or professional practice standards.  They provide heuristic
> failure detection and skill references only.  Consult qualified professionals
> (attorneys, physicians, auditors) for authoritative guidance.

### Try the Demo

```bash
python3 examples/demo-run.py
```

Runs 5 interactive scenarios: ANDON incident detection, Pack 0 safety guards,
output transformation, Knowledge Pack skill recommendations, and Meta-ANDON
pattern detection.

---

## Quick Start (3 files, 5 minutes)

For the minimal setup that gives you ANDON line-stop on failures:

### Install

```bash
pip install andon-for-llm-agents
```

Or install from source:

```bash
git clone https://github.com/allnew-llc/andon-for-llm-agents.git
cd andon-for-llm-agents
pip install .
```

### 1. Copy the hooks

```bash
# From your project root
mkdir -p .claude/hooks
cp hooks/tps-kaizen-runtime.py .claude/hooks/
cp hooks/tps-andon-posttool-guard.sh .claude/hooks/
cp hooks/tps-andon-pretool-guard.sh .claude/hooks/
cp hooks/tps-andon-control.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
```

### 2. Register hooks in Claude Code settings

Add to your `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [".claude/hooks/tps-andon-pretool-guard.sh"]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [".claude/hooks/tps-andon-posttool-guard.sh"]
      }
    ]
  }
}
```

### 3. Add the rule to CLAUDE.md

Append the contents of `rules/70-kaizen-learning.md` to your project's `CLAUDE.md` or `.claude/rules/` directory.

**That's it.** Now when a Bash command fails:
- ANDON opens automatically with incident tracking
- Forward-progress commands (git push, deploy) are blocked
- Root cause analysis artifacts are auto-generated
- You close ANDON after fixing the root cause

---

## Full Setup

See [INTEGRATION.md](./INTEGRATION.md) for:
- Adding the Kaizen learning capture hook
- Adding Meta-ANDON for repeated failure detection
- Setting up the `/tps-kaizen` skill command
- Adding quality-driven execution rules
- Customizing failure classification and domain mapping

---

## Key Concepts

### ANDON (Line Stop)

When a Bash command exits with a non-zero code:

1. **PostToolUse hook** detects the failure
2. **Runtime** classifies the failure (7 categories with confidence scores)
3. **Incident** is created with evidence, analysis, and prevention actions
4. **ANDON state** is set to "open"
5. **PreToolUse hook** blocks forward-progress commands:
   - `git push`, `git merge`, `git rebase`
   - `vercel deploy`, `firebase deploy`, `npm publish`
   - `xcodebuild archive`
6. **Allowed during ANDON**: diagnostic commands, fixes, `kaizen:` commits

**Close ANDON** after root cause analysis:
```bash
.claude/hooks/tps-andon-control.sh close "root cause: missing dep; fix: added to requirements"
```

### Meta-ANDON (Pattern Detection)

Detects when the agent is stuck in a whack-a-mole loop:

**Triggers:**
- 3+ consecutive full-run failures (even at different phases)
- 2+ ANDON opens in one session at different phases *(planned)*
- Fix → run → different failure → fix → run → different failure, 2 cycles *(planned)*

**Response:**
0. **Plan Mode** — enter `EnterPlanMode` immediately (read-only exploration, no implementation)
1. **Pattern Five Whys** — "Why does it keep failing at different points?"
2. **Desk Walk-Through** — review ALL remaining phases on paper before running
3. **Batch Fix Plan** — write the plan, get user approval via `ExitPlanMode`
4. **Implement** — only after plan approval, fix all discovered issues at once

### Human Trial Limit

**Max 2 consecutive attempts** for operations that involve the user (login, manual input, re-auth):
- After 2 failures: line stop
- Resume requires: root cause hypothesis, verification, new approach

### Specification Boundary Guard

Prevents the agent from silently relaxing requirements to make things pass:
- Requirements meaning cannot be changed without explicit user approval
- "Proposal first, implement after approval" — never implement spec changes as bug fixes
- Violations trigger immediate stop and rollback

### Quality-Driven Execution (Gate-Gaming Prevention)

LLMs optimize for whatever target function they can see. If they see gate conditions, they produce the minimum output to pass the gate.

**Solution: Purpose-driven execution**

```
Thinking order:
1. What is the PURPOSE of this phase?
2. What deliverables at what quality?
3. Create deliverables comprehensively
4. Self-assess quality
5. Submit to gate (without having looked at gate conditions)

NOT:
❌ Read gate conditions → produce minimum to pass → next phase
```

---

## How It Works Under the Hood

### Failure Classification

The runtime classifies failures into 7 categories with confidence scores:

| Category | Confidence | Pattern |
|----------|-----------|---------|
| `command_not_found` | 0.94 | `command not found` |
| `python_module_missing` | 0.88 | `ModuleNotFoundError` |
| `node_module_missing` | 0.84 | `Cannot find module` |
| `permission_denied` | 0.82 | `Permission denied` |
| `path_missing` | 0.79 | `No such file or directory` |
| `timeout` | 0.68 | `timed out` |
| `assertion_failure` | 0.62 | `AssertionError`, `failed` |
| `unknown_failure` | 0.35 | (fallback) |

### Auto-Standardization

When confidence >= 0.70, prevention rules are automatically added to a standardization registry:

```json
{
  "type": "required_command",
  "value": "uv",
  "source_incident": "INC-20260305-abc123",
  "active": true
}
```

Rollback is always available:
```bash
.claude/hooks/tps-andon-control.sh rollback INC-20260305-abc123
```

### Incident Artifacts

Each incident generates:
```
~/.claude/state/kaizen/incidents/INC-YYYYMMDD-HHMMSS-hash/
├── evidence.json      # Failed command, exit code, output, git context
├── analysis.json      # Classification, confidence, prevention actions
├── actions.json       # Auto-generated prevention + standardization
├── report.md          # Human-readable incident report
├── events.json        # All failure events (if ANDON stays open across multiple failures)
├── payload-latest.json # Raw hook payload
└── rollback/
    └── standardization-registry.before.json  # Pre-standardization state
```

---

## Customization

### Adding Custom Failure Patterns

Edit the `rules` list in `tps-kaizen-runtime.py`:

```python
rules = [
    # (cause_id, label, confidence, regex_pattern)
    ("my_custom_error", "Custom error description", 0.90, r"my specific pattern"),
    # ... existing rules ...
]
```

### Adding Domain-Specific Skill Recommendations

The `DOMAIN_SKILL_MAP` and `DOMAIN_KEYWORDS` in `tps-kaizen-runtime.py` map failure contexts to recommended skills. Customize these for your project's skill set.

### Adjusting Confidence Thresholds

```python
CONFIDENCE_AUTOMATION_THRESHOLD = 0.70    # Auto-apply standardization
CONFIDENCE_MANUAL_REVIEW_THRESHOLD = 0.70  # Require manual approval for close
```

---

## Philosophy

> "Build quality into the process, not inspect it in at the end." — W. Edwards Deming

> "Standards should not be forced down from above but rather set by the production workers themselves." — Taiichi Ohno

> "Without standards there can be no kaizen." — Taiichi Ohno

This framework embodies three core beliefs:

1. **Detection alone doesn't stop defects.** You need detection → immediate exception → line stop. Logging violations that nobody reads is theater.

2. **LLMs don't self-reflect unless told to.** They excel at solving the problem in front of them but won't step back to see patterns in their own behavior. Rules must explicitly force them to stop and analyze.

3. **Every failure is a gift** — but only if you capture the learning, route it to the right standard, and verify it prevents recurrence.

---

## Background

This framework was developed at [AllNew LLC](https://www.allnew.work) for iOS app development with Claude Code and Codex. It emerged from real incidents where LLM agents:

- Shipped an app with zero tests
- Bypassed 14 out of 14 pipeline safeguards in a single run
- Silently changed requirement semantics to pass gates
- Got stuck in 5+ retry loops involving user authentication

Each incident was analyzed with Five Whys, and the prevention measures were codified into this framework.

---

## Contributing

Contributions welcome! Areas of interest:

- **Additional failure classification patterns** for other languages/frameworks
- **IDE integrations** beyond Claude Code (Cursor, Windsurf, etc.)
- **Translations** (currently English + Japanese)
- **Case studies** of ANDON/Kaizen applied to your LLM coding workflows

---

## Acknowledgments

This project is inspired by the **Toyota Production System (TPS)** and the broader **Lean manufacturing** tradition. The concepts of ANDON, Kaizen, Jidoka, and Poka-yoke were developed at Toyota Motor Corporation over decades of collective effort by engineers, managers, and production workers on the factory floor.

Their insight that *quality must be built into the process, not inspected in at the end* has transformed manufacturing worldwide and continues to influence fields far beyond its origins.

Applying these ideas to LLM-assisted software development is a small tribute to that profound body of knowledge. Any merit in this framework belongs to the tradition; any shortcomings are our own.

We offer our sincere respect and gratitude to all who have contributed to the TPS legacy — the originators, the practitioners who refined it, and the shop-floor workers who live these principles every day.

---

## License

Apache License 2.0. See [LICENSE](./LICENSE).

Patent Notice: Certain methods implemented in this software are subject to pending patent
applications filed by AllNew LLC (patent pending). If patents are granted, Apache 2.0 Section 3
provides users a perpetual, royalty-free patent license. See [NOTICE](./NOTICE) for details.

Trademark Notice: ANDON, Kaizen, Jidoka, Poka-yoke, and TPS are terms originating from lean
manufacturing. Claude is a product of Anthropic, PBC. Cursor, Windsurf, and Codex are products
of their respective owners. This project is not affiliated with or endorsed by any of the above
companies.
