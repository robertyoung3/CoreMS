## ADDED Requirements

### Requirement: User-writable mounts use bind mounts with keep-id
All user-writable mount points in `docker-compose.yaml` services that use `userns_mode: keep-id` SHALL use bind mounts (not named volumes) so that host UID ownership is preserved inside the container.

#### Scenario: Jupyter settings directory is writable by devuser
- **WHEN** the `python-app` container starts with `userns_mode: keep-id`
- **THEN** `/home/devuser/.jupyter` SHALL be writable by `devuser` (UID 1000) and Jupyter Lab SHALL start without PermissionError

#### Scenario: Jupyter settings persist across container rebuilds
- **WHEN** the container image is rebuilt and the container is recreated
- **THEN** Jupyter settings previously saved in `~/.jupyter` on the host SHALL be available inside the container at `/home/devuser/.jupyter`

### Requirement: No named volumes for user home subdirectories
The `docker-compose.yaml` SHALL NOT define named volumes that mount into `/home/devuser/` subdirectories when `userns_mode: keep-id` is configured.

#### Scenario: Compose file has no named volume for jupyter settings
- **WHEN** `docker-compose.yaml` is inspected
- **THEN** the `volumes:` top-level section SHALL NOT contain a `jupyter-settings` entry
- **AND** the `python-app` service SHALL mount `~/.jupyter:/home/devuser/.jupyter` as a bind mount

### Requirement: Docker and Podman compatibility
The `docker-compose.yaml` mount configuration SHALL work with both Docker and Podman without Podman-specific flags (e.g., `:U`).

#### Scenario: Bind mount syntax is engine-agnostic
- **WHEN** the compose file is used with Docker Compose or Podman Compose
- **THEN** the `~/.jupyter:/home/devuser/.jupyter` bind mount SHALL function correctly on both engines
