# Cherry-Pick PR Template

Use this template when creating a PR for a cherry-pick to a release or production branch.

## Standard PR Template

```markdown
## Cherry-pick to `<target-branch>`

**Source commits:**
- `<sha1>` — <commit message>
- `<sha2>` — <commit message>

**Conflicts resolved:** <count> file(s) / None

**Verification:** <build/lint status or "manual review needed">
```

## Extended PR Body Guidance

For production hotfixes or high-stakes backports, include additional context:

### Source Commits Listing

List every cherry-picked commit with its full 40-character SHA and the original commit message. This allows reviewers to cross-reference the source branch history without switching contexts.

```markdown
**Source commits (full SHAs):**
- `a1b2c3d4e5f6...` — fix: prevent null pointer in payment processor (#1234)
- `b2c3d4e5f6a7...` — fix: add nil guard to UserSession.validate (#1235)
```

### Conflict Resolution Details

When conflicts were resolved, document how each conflict was resolved and why. This is critical for production branches where reviewers need to trust the resolution:

```markdown
**Conflict resolution:**
- `src/payment/processor.py` — Kept main branch's error handling, applied hotfix's nil check. The main branch refactored error types in #1200; the hotfix predates that refactor.
```

### Verification Status

Document what verification was performed. For production deployments, include at minimum:

```markdown
**Verification:**
- [ ] Build passes in worktree (`make build`)
- [ ] Unit tests pass (`make test`)
- [ ] Manual smoke test in staging environment
- [ ] Diff reviewed against original commit — no unintended changes
```

If no automated verification was available (e.g., hotfix urgency):

```markdown
**Verification:** Manual review only — automated tests not run due to urgency. Reviewer should pay close attention to <specific concern>.
```

## PR Title Format

Use one of these formats for the PR title:

- `cherry-pick: <description> onto <target-branch>`
- `hotfix(<target-branch>): <description>`
- `backport: <description> from main to release/x.y`

Keep titles under 72 characters. Reference the original PR or issue number when applicable: `cherry-pick: fix null payment processor (backport #1234)`.
