## Requirements

### Requirement: PostgreSQL service for molecular formula database
The docker-compose.yaml SHALL define a PostgreSQL service that provides the molecular formula database required by CoreMS.

#### Scenario: PostgreSQL accessible from python-app
- **WHEN** the python-app service starts
- **THEN** it SHALL be able to connect to the PostgreSQL database using the `COREMS_DATABASE_URL` environment variable

#### Scenario: Database data persists across restarts
- **WHEN** the compose stack is stopped and restarted
- **THEN** PostgreSQL data SHALL persist via a named volume

### Requirement: Python-app service with source code bind mount
The docker-compose.yaml SHALL define a python-app service that builds from the project Dockerfile and bind-mounts the project source code to `/app` for live editing.

#### Scenario: Source code changes reflected without rebuild
- **WHEN** a developer edits a Python file on the host
- **THEN** the change SHALL be immediately visible inside the container at `/app`

### Requirement: Podman compatibility via userns_mode and SELinux config
The docker-compose.yaml SHALL include `userns_mode: keep-id` on the python-app service and `security_opt: label=disable` to ensure correct UID mapping and file access under Podman.

#### Scenario: File permissions correct under Podman
- **WHEN** the stack is started with `podman compose up`
- **THEN** `devuser` (UID 1000) SHALL own and be able to read/write files in `/app`

#### Scenario: Stack works with Docker
- **WHEN** the stack is started with `docker compose up`
- **THEN** all services SHALL start and function identically to the Podman case

### Requirement: Claude config bind-mounted from host
The docker-compose.yaml SHALL bind-mount `~/.claude` and `~/.claude.json` from the host into the container at `/home/devuser/.claude` and `/home/devuser/.claude.json`.

#### Scenario: Claude Code works inside container
- **WHEN** `devuser` runs `claude` inside the container
- **THEN** it SHALL use the host's Claude configuration and authentication

### Requirement: Environment configuration via .env file
The docker-compose.yaml SHALL load database credentials and configuration from a `.env` file.

#### Scenario: Database credentials configured
- **WHEN** a developer sets database credentials in `.env`
- **THEN** both the PostgreSQL service and python-app service SHALL use those credentials

### Requirement: Service health checks and dependency ordering
The PostgreSQL service SHALL include a health check, and the python-app service SHALL depend on PostgreSQL being healthy before starting.

#### Scenario: Python-app waits for database
- **WHEN** the compose stack starts
- **THEN** the python-app service SHALL NOT start until PostgreSQL reports healthy
