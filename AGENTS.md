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

## Testing

Tests must run inside the Podman container — packages are not available on the host.

```bash
podman exec corems_python_app python -m pytest <test_path> -v
```

## Upstream PR Hygiene

This is a fork of EMSL-Computing/CoreMS. Upstream PRs must contain **only** the minimal bug fix or feature diff.

**Always use a git worktree** — never switch branches in the main working directory. Upstream tracks files (`.env`) that our fork gitignores, so branch switching destroys fork-specific state.

1. `git fetch upstream master`
2. `git worktree add /tmp/corems-fix-name upstream/master -b fix/my-fix`
3. `cd /tmp/corems-fix-name` — work in the worktree
4. Make only the relevant code changes
5. Validate: `git diff --name-only upstream/master..HEAD` — must show only intended files
6. Reject if diff includes: `.claude/`, `.devcontainer/`, `openspec/`, `docker-compose*`, `pyproject.toml`, `python-app/`, `AGENTS.md`, `CLAUDE.md`, `.env`, `.gitignore`
7. Push and create PR with `--head robertyoung3:fix/my-fix`
8. Clean up: `cd ~/VScodeProjects/CoreMS && git worktree remove /tmp/corems-fix-name`

See `CLAUDE.md` for full details.

