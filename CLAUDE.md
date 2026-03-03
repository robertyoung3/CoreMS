# CoreMS Project Instructions

## Upstream Contribution Workflow

This is a fork of [EMSL-Computing/CoreMS](https://github.com/EMSL-Computing/CoreMS). The fork contains local development setup (devcontainers, OpenSpec, Claude tooling) that must never appear in upstream PRs.

### Creating upstream PR branches

1. **Fetch upstream first**: `git fetch upstream master`
2. **Branch from upstream/master**: `git checkout -b fix/my-fix upstream/master`
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
6. **Create PR** targeting `EMSL-Computing/CoreMS:master`

### Fork-only work

For changes that stay in our fork (devcontainer, tooling, config), work on fork `master` or fork-specific branches. These are never pushed upstream.
