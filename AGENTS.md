# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

## Upstream PR Hygiene

This is a fork of EMSL-Computing/CoreMS. Upstream PRs must contain **only** the minimal bug fix or feature diff.

1. `git fetch upstream master`
2. `git checkout -b fix/my-fix upstream/master` — branch from **upstream**, not fork master
3. Make only the relevant code changes
4. Validate: `git diff --name-only upstream/master..HEAD` — must show only intended files
5. Reject if diff includes: `.claude/`, `.devcontainer/`, `openspec/`, `docker-compose*`, `pyproject.toml`, `python-app/`, `AGENTS.md`, `CLAUDE.md`, `.env`, `.gitignore`

See `CLAUDE.md` for full details.

