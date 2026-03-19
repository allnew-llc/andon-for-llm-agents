---
name: cherry-pick-prod
description: Safely cherry-pick commits to a release/prod branch using an isolated git worktree. Use when: hotfix, backport, cherry-pick, production fix, release branch patch, emergency deploy.
---

# /cherry-pick-prod — Isolated Worktree Cherry-Pick

Cherry-picks one or more commits onto a target branch using a **temporary git worktree** so your working tree stays clean. Handles conflict resolution and creates a PR.

## Usage

```
/cherry-pick-prod <commit-sha> [--onto main]           # single commit
/cherry-pick-prod <sha1> <sha2> <sha3> [--onto release/1.2]  # multiple commits
/cherry-pick-prod --range HEAD~3..HEAD [--onto main]    # range
```

Default `--onto` target: `main`

## Workflow

### 1. Preflight
- Verify all commit SHAs exist
- Verify target branch exists and is up to date with remote
- Check for uncommitted changes in current worktree (warn if dirty)

### 2. Create Isolated Worktree
```bash
git worktree add /tmp/cherry-pick-<timestamp> <target-branch>
cd /tmp/cherry-pick-<timestamp>
git checkout -b cherry-pick/<short-desc>-<date>
```

### 3. Cherry-Pick
```bash
git cherry-pick <sha1> [<sha2> ...]
```

If conflicts arise:
- Show the conflicting files and diff
- Attempt auto-resolution for trivial conflicts (import ordering, whitespace)
- For non-trivial conflicts: present both sides and ask the user to choose
- After resolution: `git add` resolved files and `git cherry-pick --continue`

### 4. Verify
- Run a quick sanity check (build/lint if available)
- Show the final diff against the target branch
- Ask user for confirmation before pushing

### 5. Push & PR
```bash
git push -u origin cherry-pick/<short-desc>-<date>
gh pr create --base <target-branch> --title "cherry-pick: <description>" --body "..."
```

For the standard PR template and extended body guidance, see `references/pr-template.md`.

### 6. Cleanup
```bash
cd -
git worktree remove /tmp/cherry-pick-<timestamp>
```

## Gotchas

### Stale Target Branch

Always fetch before worktree creation because the worktree is based on the local branch ref, not the remote. If you skip `git fetch origin <branch>` before `git worktree add`, the worktree starts from a stale point and your cherry-pick lands on old history. The resulting PR will include commits that are already on the target branch, leading to confusing diffs and potentially failing CI checks.

### Force Push Prohibition

Never force-push the cherry-pick branch. If a rebase is needed (e.g., the target branch moved significantly), recreate the worktree from scratch — the worktree's history should be a clean fork of the current remote target. Force-pushing a cherry-pick branch risks rewriting shared history on the PR branch and causes confusion for reviewers who already fetched it.

### Mid-Sequence Abort

If cherry-pick fails partway through a multi-commit sequence, abort in the worktree before cleanup, otherwise the worktree is left in a dirty mid-cherry-pick state. Run `git cherry-pick --abort` inside the worktree before `git worktree remove`. Skipping the abort leaves unresolved conflicts and a detached HEAD state that prevents clean worktree removal.

### Worktree Cleanup on Failure

Worktree must be removed even on error. Use a trap or finally-equivalent to prevent `/tmp` accumulation of orphaned worktrees. Each failed cherry-pick attempt that skips cleanup leaves a `/tmp/cherry-pick-<timestamp>` directory consuming disk space. More critically, git tracks all worktrees in the main repo's `.git/worktrees/` — orphaned entries degrade git performance and can cause confusing errors in subsequent operations.

### Merge Commit Parents

Don't cherry-pick merge commits without the `--mainline` flag. When a commit is a merge, it has two parents and git cannot infer which side of the merge represents the intended mainline. Ask the user which parent before proceeding — for a merge commit `M` that merged feature branch into main, the mainline is typically parent 1. Using the wrong parent produces an unexpected diff and silently cherry-picks the wrong changes.

## Additional Resources

When detailed template content is needed, read these files:

- **`references/pr-template.md`** — Standard PR template, extended body guidance, source commits listing format, conflict resolution details, and verification status fields
