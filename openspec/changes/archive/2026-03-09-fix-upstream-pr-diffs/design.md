## Context

Five bug fix PRs (#25–#29) were submitted to EMSL-Computing/CoreMS from our fork. Each PR branch was created from our fork's `master`, which contains 2 commits ahead of `upstream/master`:

1. `01767704` — Podman devcontainer migration (pyproject.toml, Dockerfile, compose, devcontainer, .claude/, openspec/, AGENTS.md, .gitignore, .env)
2. The actual bug fix commit (unique per branch)

Because the fix branches were based on our fork master (which includes commit `01767704`), every PR diff includes ~27 extraneous files. The upstream maintainer has asked that each PR contain only the minimal bug fix diff.

Our fork's `master` branch itself is 2 commits ahead of `upstream/master` and should stay that way — those commits are fork-specific.

## Goals / Non-Goals

**Goals:**
- Rewrite each of the 5 fix branches so they are based directly on `upstream/master` with only the bug fix changes
- Force-push the cleaned branches to update the existing PRs in-place (preserving PR numbers, comments, and review history)
- Add guardrails in CLAUDE.md and AGENTS.md so future upstream PRs are always created from `upstream/master`, not fork `master`

**Non-Goals:**
- Changing any of the actual bug fix code — the fixes remain identical
- Modifying our fork's `master` branch — it keeps its devcontainer/tooling commits
- Creating new PRs — we reuse the existing PR numbers by updating the branches
- Adding CI or automated checks — manual process guardrails are sufficient for now

## Decisions

### 1. Rebase strategy: fresh branches from `upstream/master` with cherry-picked diffs

**Chosen**: For each fix branch, create a new branch from `upstream/master`, apply only the relevant file changes from the original fix commit, commit, and force-push.

**Why not `git rebase --onto`**: The fix commits may have been authored on top of the devcontainer commit. A rebase could introduce conflicts or carry over unrelated changes if the commit touched files also modified in the parent. Extracting just the relevant files is cleaner and guarantees a minimal diff.

**Why not interactive rebase to drop the devcontainer commit**: Same risk — if the fix commit's tree state depends on the devcontainer commit (e.g., shared `.gitignore` changes), dropping the parent could alter the fix commit's content. Fresh cherry-pick of specific files is safest.

**Procedure per branch**:
```
git checkout -B <branch> upstream/master
git checkout <old-branch-ref> -- <file1> [file2...]
git commit -m "<original commit message>"
git push origin <branch> --force
```

### 2. Guardrail location: CLAUDE.md (new) + AGENTS.md (append)

**Chosen**: Create `CLAUDE.md` at project root with upstream contribution rules. Append a section to `AGENTS.md` referencing the same rules.

**Rationale**: `CLAUDE.md` is the standard location for Claude Code project instructions and is always loaded into context. `AGENTS.md` is already present and used for session workflow. Both should reference the upstream PR hygiene rules so they're visible regardless of which file an agent or developer reads.

### 3. Rule content: branch-from-upstream + file-scope validation

The guardrail rules will specify:
- Upstream PR branches MUST be created from `upstream/master`, never from fork `master`
- Before pushing, validate that the diff against `upstream/master` only contains intended files (no `.claude/`, `.devcontainer/`, `openspec/`, `docker-compose*`, `pyproject.toml`, `AGENTS.md`, etc.)
- A simple pre-push check command will be documented: `git diff --name-only upstream/master..HEAD`

## Risks / Trade-offs

- **Force-push rewrites PR history** → Acceptable because the PRs haven't been merged and the maintainer explicitly requested the change. PR comments and review threads are preserved by GitHub.
- **Cherry-picking file state vs. commit** → If a fix file had changes from both the devcontainer commit and the fix commit, we'd get both. Mitigated by verifying the diff of each cleaned branch matches only the intended bug fix lines (the devcontainer commit didn't touch any `corems/` source files).
- **Future contributors may not read CLAUDE.md** → Mitigated by also putting rules in AGENTS.md and making the rules concise and prominent.
