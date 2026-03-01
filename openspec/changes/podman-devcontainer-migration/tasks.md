## 1. Modern Packaging (pyproject.toml)

- [ ] 1.1 Audit all dependency version pins in `requirements.txt` for Python 3.12 compatibility and determine updated version ranges
- [ ] 1.2 Create `pyproject.toml` with PEP 621 metadata, `[project.dependencies]` (core), and `[project.optional-dependencies]` (dev extra)
- [ ] 1.3 Set `requires-python = ">=3.12"` and update pythonnet pin to `~=3.0.5`
- [ ] 1.4 Verify `uv pip install -e ".[dev]"` resolves and installs all dependencies in a clean Python 3.12 environment
- [ ] 1.5 Verify `uv build` produces a distributable package from pyproject.toml metadata

## 2. Dockerfile

- [ ] 2.1 Create `python-app/` directory structure
- [ ] 2.2 Write `python-app/Dockerfile` with base image `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- [ ] 2.3 Add system dependency installation (libhdf5-dev, libnetcdf-dev, libxml2-dev, build-essential, etc.)
- [ ] 2.4 Add .NET 10 runtime installation from Microsoft package repository for Debian 12
- [ ] 2.5 Set `PYTHONNET_RUNTIME=coreclr` environment variable
- [ ] 2.6 Create non-root `devuser` (UID/GID 1000) with passwordless sudo
- [ ] 2.7 Install Node.js 22.x and Claude Code CLI (`@anthropic-ai/claude-code`)
- [ ] 2.8 Set up `/opt/venv` with `uv`, install project in editable mode from pyproject.toml
- [ ] 2.9 Install JupyterLab and register IPython kernel
- [ ] 2.10 Create startup script for Jupyter entrypoint
- [ ] 2.11 Build the image and verify: Python 3.12, uv, dotnet runtime, devuser, Claude Code, `import corems`

## 3. Pythonnet + .NET 10 Validation (gate)

- [ ] 3.1 Inside the built container, run `python -c "import pythonnet; pythonnet.load('coreclr'); import clr"` and verify CLR initializes
- [ ] 3.2 Run `clr.AddReference()` for all 3 ThermoFisher assemblies from `ext_lib/dotnet/`
- [ ] 3.3 Verify types are exposed (e.g., instantiate `ThermoFisher.CommonCore.RawFileReader.RawFileReaderAdapter`)
- [ ] 3.4 If validation fails: switch to pythonnet 3.1.0-rc0, rebuild, and re-validate

## 4. Container Orchestration (docker-compose.yaml)

- [ ] 4.1 Create `.env` file with PostgreSQL credentials and `COREMS_DATABASE_URL`
- [ ] 4.2 Write `docker-compose.yaml` with PostgreSQL service (named volume, health check)
- [ ] 4.3 Add python-app service with build context `./python-app`, bind mount source to `/app`
- [ ] 4.4 Add Podman compatibility: `userns_mode: keep-id`, `security_opt: label=disable`
- [ ] 4.5 Add Claude config bind mounts (`~/.claude`, `~/.claude.json`)
- [ ] 4.6 Add `depends_on` with `condition: service_healthy` for PostgreSQL
- [ ] 4.7 Test with `podman compose up` — verify both services start and python-app connects to PostgreSQL
- [ ] 4.8 Test with `docker compose up` — verify identical behavior

## 5. Devcontainer Configuration

- [ ] 5.1 Create `.devcontainer/devcontainer.json` referencing `../docker-compose.yaml` and `python-app` service
- [ ] 5.2 Set `workspaceFolder` to `/app`, `remoteUser` to `devuser`
- [ ] 5.3 Configure port forwarding: 5432 (PostgreSQL), 8888 (Jupyter)
- [ ] 5.4 Add VS Code extensions: Python, Pylance, Ruff, Jupyter, Docker, Claude Code
- [ ] 5.5 Add Claude config volume mounts with `consistency=cached` and `postCreateCommand` for ownership fix
- [ ] 5.6 Test "Reopen in Container" in VS Code — verify full stack starts, extensions load, terminal runs as devuser

## 6. Cleanup and Documentation

- [ ] 6.1 Update `.gitignore` to include new entries (`.env`, container volumes, etc.)
- [ ] 6.2 Add `python-app/` and `.devcontainer/` to `.gitignore` exclusions if needed
- [ ] 6.3 Verify old Dockerfiles and compose files still exist and are not broken
