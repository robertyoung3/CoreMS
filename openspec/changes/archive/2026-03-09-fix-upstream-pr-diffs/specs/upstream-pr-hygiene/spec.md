## ADDED Requirements

### Requirement: Upstream PR branches based on upstream/master
All branches intended for pull requests against the upstream repository (EMSL-Computing/CoreMS) SHALL be created from `upstream/master`, never from the fork's `master` or any fork-specific branch.

#### Scenario: Creating a new upstream bug fix branch
- **WHEN** a developer or agent creates a branch for an upstream PR
- **THEN** the branch MUST be based on `upstream/master` (e.g., `git checkout -b fix/my-fix upstream/master`)

#### Scenario: Fork master is ahead of upstream
- **WHEN** the fork's `master` contains commits not present in `upstream/master` (e.g., devcontainer migration, tooling)
- **THEN** upstream PR branches MUST still be based on `upstream/master`, not fork `master`

### Requirement: Minimal diff scope for upstream PRs
The diff of any upstream PR branch against `upstream/master` SHALL contain only files directly related to the bug fix or feature being proposed. Fork-specific files MUST NOT be included.

#### Scenario: PR diff contains only intended files
- **WHEN** a developer runs `git diff --name-only upstream/master..HEAD` on an upstream PR branch
- **THEN** the output SHALL list only files in the `corems/` source tree (or other files directly relevant to the fix), and SHALL NOT include any of: `.claude/`, `.devcontainer/`, `openspec/`, `docker-compose*`, `pyproject.toml`, `python-app/`, `AGENTS.md`, `.env`, or `.gitignore`

#### Scenario: Pre-push validation catches extraneous files
- **WHEN** a developer is about to push an upstream PR branch
- **THEN** they SHALL verify the diff scope by running `git diff --name-only upstream/master..HEAD` and confirming no fork-specific files are present

### Requirement: Upstream remote kept up to date
The `upstream` remote SHALL be fetched before creating or updating any upstream PR branch to ensure the branch is based on the latest upstream state.

#### Scenario: Fetching before branch creation
- **WHEN** a developer is about to create an upstream PR branch
- **THEN** they MUST run `git fetch upstream master` first

### Requirement: Guardrails documented in project configuration
The upstream PR hygiene rules SHALL be documented in both `CLAUDE.md` and `AGENTS.md` at the project root so that both AI agents and human developers are aware of the workflow.

#### Scenario: CLAUDE.md contains upstream PR rules
- **WHEN** a Claude Code agent loads the project
- **THEN** `CLAUDE.md` SHALL contain a section on upstream contribution workflow specifying branch creation from `upstream/master` and diff validation

#### Scenario: AGENTS.md contains upstream PR rules
- **WHEN** a developer or agent reads `AGENTS.md`
- **THEN** it SHALL contain a section referencing upstream PR hygiene rules with the pre-push validation command
