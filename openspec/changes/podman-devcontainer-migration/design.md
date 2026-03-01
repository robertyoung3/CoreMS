## Context

CoreMS is a mass spectrometry framework with a legacy build system (`setup.py` + `requirements.txt`) targeting Python 3.8-3.11. Its Docker images on DockerHub are stale (last updated 2022-2023) and the CI base image is on a private PNNL registry. The project depends on pythonnet for Thermo .raw file processing, which requires a .NET runtime.

The sister project GraphMZ has a working devcontainer setup using Podman with `ghcr.io/astral-sh/uv:python3.13-bookworm-slim`, `userns_mode: keep-id`, non-root `devuser`, and Claude Code integration. That setup is the architectural model for this migration.

Key constraints:
- Must work with both Podman (personal development) and Docker (work environment)
- Pythonnet requires a .NET runtime (CoreCLR) — this adds complexity to the container image
- PostgreSQL is needed for the molecular formula database
- The Thermo .NET assemblies live in `ext_lib/dotnet/` within the repository

## Goals / Non-Goals

**Goals:**
- Reproducible development environment via `Reopen in Container` (one command)
- Dual Podman/Docker compatibility from a single set of config files
- Modern Python packaging with `pyproject.toml` and `uv`
- Python 3.12 and .NET 10 LTS as the runtime targets
- Claude Code available inside the container for AI-assisted development

**Non-Goals:**
- Production deployment images (this is a development environment)
- CI/CD pipeline updates (downstream impact, separate change)
- Removing or deprecating old Dockerfiles (can coexist during transition)
- Multi-architecture builds (x86_64/amd64 only for now, matching existing images and current hardware)
- Making pythonnet optional (stretch goal tracked separately)

## Decisions

### 1. Base image: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`

**Rationale:** Provides Python 3.12 and `uv` pre-installed on a Debian slim base. Bookworm (Debian 12) has the system libraries needed for scientific Python packages. The `slim` variant keeps image size down while still including enough to compile C extensions. This is the same image family used by GraphMZ (which uses python3.13).

**Alternatives considered:**
- `python:3.12-slim-bookworm` — would require installing `uv` separately
- `python:3.12-bookworm` (full) — larger image, unnecessary extras
- Building from `ubuntu:24.04` — more work, no advantage

### 2. .NET 10 LTS runtime (not SDK)

**Rationale:** Pythonnet only needs the .NET runtime, not the full SDK. The runtime is ~80MB vs ~800MB for the SDK. .NET 10 is the current LTS (through Nov 2028) and avoids the .NET 8 pythonnet type-exposure bug (#2595). Pythonnet 3.1.0-rc0 CI-tests against .NET 10; the stable 3.0.5 targets .NET Standard 2.0 and should be compatible.

**Installation approach:** Use Microsoft's package repository for Debian 12 (`packages.microsoft.com`) to install `dotnet-runtime-10.0`. Set `PYTHONNET_RUNTIME=coreclr` environment variable.

**Alternatives considered:**
- .NET 8 LTS — broken with pythonnet (types not exposed)
- .NET 9 STS — works but support ends May 2026
- Mono runtime — legacy approach, heavier, pythonnet 3.x prefers CoreCLR

### 3. Pythonnet 3.0.5 (stable) with .NET 10 validation gate

**Rationale:** 3.0.5 is the latest stable release, supports Python 3.12, targets .NET Standard 2.0. The combination with .NET 10 is not in pythonnet's CI matrix but is expected to work since .NET 9 works and .NET 10 is backward-compatible. A validation task (CoreMS-fjx) gates the Dockerfile on confirming this works.

**Fallback:** If 3.0.5 + .NET 10 fails, use pythonnet 3.1.0-rc0 which is CI-tested against .NET 10.

**Alternatives considered:**
- pythonnet 3.1.0-rc0 — CI-tested with .NET 10 but pre-release
- pythonnet 3.0.1 (current pin) — does not support Python 3.12

### 4. Project layout: Dockerfile at `python-app/Dockerfile`

**Rationale:** Following the GraphMZ pattern. The Dockerfile lives in a `python-app/` subdirectory which serves as the build context. This separates the container build from the project root and avoids needing a complex `.dockerignore`. The `docker-compose.yaml` references `build: ./python-app`.

**Alternatives considered:**
- Dockerfile at project root — mixes container config with project files, larger build context
- Separate `docker/` directory — would diverge from the GraphMZ pattern

### 5. Podman compatibility via standard compose features

**Rationale:** Use `userns_mode: keep-id` for UID mapping, `security_opt: label=disable` for SELinux, and standard bind mounts without `:Z`/`:z` labels. These are compose spec features that both Docker and Podman support. This is the same approach proven in GraphMZ.

**Key details:**
- `userns_mode: keep-id` maps container UID 1000 to host UID 1000, eliminating permission issues on bind-mounted files
- `security_opt: label=disable` prevents SELinux from blocking access to host-mounted Claude config
- `devuser` is created with UID/GID 1000 in the Dockerfile to match the host user

### 6. PostgreSQL via named volume, database credentials in .env

**Rationale:** The existing `docker-compose.yml` already uses this pattern. PostgreSQL stores data in a named volume for persistence. Credentials are loaded from `.env` (gitignored) and passed to both services. The database connection URL follows the existing `COREMS_DATABASE_URL` pattern.

### 7. Node.js 22.x for Claude Code

**Rationale:** Claude Code requires Node.js. Version 22 is the current LTS. Installed via NodeSource repository in the Dockerfile, same as GraphMZ.

## Risks / Trade-offs

**[Pythonnet 3.0.5 + .NET 10 untested combination]** → Mitigated by validation task (CoreMS-fjx) with clear fallback to pythonnet 3.1.0-rc0. Validation runs early, before other work depends on it.

**[Larger image size due to .NET runtime]** → The .NET runtime adds ~80MB. This is unavoidable for Thermo .raw file support. GraphMZ's image (without .NET) is already ~900MB; CoreMS will be larger. Acceptable for a development image.

**[Python 3.12 dependency compatibility]** → Some pinned versions (e.g., `numpy~=1.24.2`, `pandas~=1.5.3`) may not have Python 3.12 wheels. Mitigated by updating pins during the pyproject.toml migration. All major scientific Python packages support 3.12.

**[Old Dockerfiles coexist with new ones]** → Developers may be confused by multiple Dockerfiles. Mitigated by clear naming and documentation. Old files can be removed in a follow-up change once the new setup is validated.

**[SELinux disabled for container]** → `label=disable` reduces container isolation on SELinux-enforcing systems. This is limited to the Claude config mounts and matches the GraphMZ approach. Acceptable for a development environment.

## Migration Plan

1. Create `pyproject.toml` — can be tested independently with `uv pip install -e ".[dev]"` on the host
2. Create `python-app/Dockerfile` — build and test the image
3. Validate pythonnet + .NET 10 inside the container (gate)
4. Create `docker-compose.yaml` and `.env` — test with `podman compose up`
5. Create `.devcontainer/devcontainer.json` — test with VS Code "Reopen in Container"
6. Old Dockerfiles and compose files remain for reference; no immediate removal

**Rollback:** Each step is additive. New files can be deleted to revert. No existing files are modified (except `.gitignore` to add new entries).

## Open Questions

- Should the Thermo .NET assemblies in `ext_lib/dotnet/` be copied into the image at build time, or relied upon via the bind-mounted source? Bind mount is simpler for development but means the container can't run Thermo processing standalone.
- Should `support_code/requirements-support.txt` (PySide2, comtypes — Windows-only) be included in pyproject.toml as an optional extra, or excluded entirely?
