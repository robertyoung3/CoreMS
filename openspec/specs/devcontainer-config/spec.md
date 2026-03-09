## Requirements

### Requirement: VS Code devcontainer references docker-compose
The `.devcontainer/devcontainer.json` SHALL reference the project's `docker-compose.yaml` and target the `python-app` service, so that "Reopen in Container" starts the full stack.

#### Scenario: Reopen in Container starts all services
- **WHEN** a developer selects "Reopen in Container" in VS Code
- **THEN** both the PostgreSQL and python-app services SHALL start, and VS Code SHALL connect to the python-app container

### Requirement: Workspace folder set to /app
The devcontainer SHALL set `workspaceFolder` to `/app` so that the VS Code file explorer shows the bind-mounted project source.

#### Scenario: Project files visible in VS Code
- **WHEN** VS Code opens in the container
- **THEN** the file explorer SHALL show the CoreMS project files at `/app`

### Requirement: Non-root remote user
The devcontainer SHALL set `remoteUser` to `devuser` so that all VS Code operations run as the non-root user.

#### Scenario: Terminal runs as devuser
- **WHEN** a developer opens a terminal in VS Code
- **THEN** the shell SHALL be running as `devuser`

### Requirement: Port forwarding for PostgreSQL and Jupyter
The devcontainer SHALL forward ports 5432 (PostgreSQL) and 8888 (Jupyter/notebook).

#### Scenario: Jupyter accessible from host browser
- **WHEN** Jupyter Lab is running inside the container
- **THEN** it SHALL be accessible at `localhost:8888` on the host

### Requirement: Development extensions installed
The devcontainer SHALL install VS Code extensions for Python development: Python, Pylance, Ruff, Jupyter, Docker, and Claude Code (`anthropic.claude-code`).

#### Scenario: Extensions available on container open
- **WHEN** VS Code opens in the container
- **THEN** all specified extensions SHALL be installed and active

### Requirement: Claude config volume mounts
The devcontainer SHALL bind-mount `~/.claude` and `~/.claude.json` from the host with `consistency=cached`, and run a `postCreateCommand` to fix ownership.

#### Scenario: Claude Code authenticates inside container
- **WHEN** a developer runs Claude Code inside the devcontainer
- **THEN** it SHALL use the host's existing authentication without requiring re-login
