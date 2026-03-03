# CoreMS Project Instructions

## Upstream Contribution Workflow

This is a fork of [EMSL-Computing/CoreMS](https://github.com/EMSL-Computing/CoreMS). The fork contains local development setup (devcontainers, OpenSpec, Claude tooling) that must never appear in upstream PRs.

### Creating upstream PR branches (use git worktree)

**Important:** Always use a git worktree for upstream PRs. Switching branches in the main working directory destroys fork-specific untracked files (`.env`, etc.) because upstream tracks files our fork gitignores.

1. **Fetch upstream first**: `git fetch upstream master`
2. **Create a worktree from upstream/master**:
   ```bash
   git worktree add /tmp/corems-fix-name upstream/master -b fix/my-fix
   cd /tmp/corems-fix-name
   ```
3. **Make only the bug fix or feature changes** — no fork-specific files
4. **Validate before pushing**:
   ```bash
   git diff --name-only upstream/master..HEAD
   ```
   The output must contain only files directly related to the fix (typically under `corems/`). If you see any of the following, the branch is contaminated:
   - `.claude/`, `.devcontainer/`, `openspec/`
   - `docker-compose*`, `pyproject.toml`, `python-app/`
   - `AGENTS.md`, `CLAUDE.md`, `.env`, `.gitignore`
5. **Push to origin**: `git push origin fix/my-fix`
6. **Create PR** targeting `EMSL-Computing/CoreMS:master` (use `--head robertyoung3:fix/my-fix`)
7. **Clean up the worktree**:
   ```bash
   cd ~/VScodeProjects/CoreMS
   git worktree remove /tmp/corems-fix-name
   ```

### Fork-only work

For changes that stay in our fork (devcontainer, tooling, config), work on fork `master` or fork-specific branches. These are never pushed upstream.
