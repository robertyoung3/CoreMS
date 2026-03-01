## Why

CoreMS development relies on Docker images published under `corilo/corems` and `emslcomputing/corems-*` on DockerHub, but these are stale — `corilo/corems:latest` was last updated July 2022, and the EMSL images in October 2023. The CI pipeline uses a private PNNL registry image (`corems-base-310-dotnet6`) that external contributors cannot access. The project still uses a legacy `setup.py` + `requirements.txt` build system targeting Python 3.8-3.11, while modern Python tooling has moved to `pyproject.toml` and faster resolvers like `uv`. We need a reproducible, self-contained development environment that works on both Podman (personal) and Docker (work), uses current Python and .NET runtimes, and follows the devcontainer pattern already proven in the GraphMZ sister project.

## What Changes

- **Replace `setup.py` + `requirements.txt` with `pyproject.toml`**: Consolidate all dependency declarations into a single file, compatible with `uv` and modern Python packaging standards.
- **Target Python 3.12**: Upgrade from the current 3.8-3.11 range. Python 3.12 offers improved performance, better error messages, and is well within its support window.
- **Target .NET 10 LTS runtime**: Replace the .NET 6 runtime used in existing Dockerfiles. .NET 10 is the current LTS release (supported through November 2028) and avoids the pythonnet CoreCLR type-exposure bug in .NET 8 (pythonnet/pythonnet#2595). Pythonnet 3.0.5 works with .NET 9, and .NET 10 is backward-compatible; pythonnet 3.1.0-rc0 CI-tests against .NET 10 directly.
- **Create new Dockerfile**: Based on `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`, modeled on the GraphMZ devcontainer pattern. Includes .NET 10, non-root `devuser` (UID 1000), Claude Code CLI, and Jupyter support.
- **Create new `docker-compose.yaml`**: PostgreSQL service (molecular formula database) + python-app service. Podman-compatible with `userns_mode: keep-id` and `security_opt: label=disable`. Works identically with `docker compose` and `podman compose`.
- **Create `.devcontainer/devcontainer.json`**: VS Code devcontainer configuration referencing the compose file, with extensions, port forwarding, and Claude config volume mounts.
- **Pythonnet updated to 3.0.5**: From the currently pinned 3.0.1. Required for Python 3.12 and .NET 10 compatibility.

## Capabilities

### New Capabilities
- `container-build`: Dockerfile and build configuration for Python 3.12 + .NET 10 + uv development image
- `container-orchestration`: docker-compose.yaml with PostgreSQL and python-app services, Podman/Docker compatible
- `devcontainer-config`: VS Code devcontainer integration with extensions, port forwarding, and volume mounts
- `modern-packaging`: pyproject.toml with uv-compatible build system, replacing setup.py + requirements.txt

### Modified Capabilities

## Impact

- **Build system**: `setup.py`, `requirements.txt`, `requirements-dev.txt` superseded by `pyproject.toml`. Existing Dockerfiles (`Dockerfile`, `DockerfileDevEnv`, `Dockerfile_py310_dotnet_base`) and compose files (`docker-compose.yml`, `docker-compose-jupyter.yml`) superseded by new versions.
- **Python version**: Minimum bumped from 3.8 to 3.12. Code using syntax or features deprecated between 3.8-3.12 may need updates.
- **Dependencies**: All 26 core dependency version pins need review for Python 3.12 compatibility. Pythonnet upgraded from 3.0.1 to 3.0.5. Pythonnet + .NET 10 compatibility must be validated before finalizing.
- **CI/CD**: `.gitlab-ci.yml` and `.github/workflows/pypi_publish.yml` will need updates to reference the new build system and Python version (not in scope for this change, but a downstream impact).
- **Makefile**: Docker-related targets (`build-image`, `db-up`, `all-up`, etc.) will need updating to reference new compose file.
- **Developer workflow**: Developers gain a one-command devcontainer setup (`Reopen in Container`) that works on both Podman and Docker with no additional configuration.
