## Requirements

### Requirement: Dockerfile based on uv Python 3.12 slim image
The Dockerfile SHALL use `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` as the base image, providing Python 3.12 and the `uv` package manager.

#### Scenario: Base image provides Python 3.12 and uv
- **WHEN** the container is built
- **THEN** `python --version` SHALL report Python 3.12.x and `uv --version` SHALL be available

### Requirement: .NET 10 LTS runtime installed
The Dockerfile SHALL install the .NET 10 runtime to support pythonnet CoreCLR for Thermo .raw file processing.

#### Scenario: .NET runtime available
- **WHEN** the container is running
- **THEN** `dotnet --list-runtimes` SHALL show a .NET 10.x runtime

#### Scenario: Pythonnet CoreCLR loads successfully
- **WHEN** Python code executes `pythonnet.load("coreclr"); import clr`
- **THEN** the CLR runtime SHALL initialize without errors

### Requirement: Non-root devuser with UID 1000
The Dockerfile SHALL create a non-root user `devuser` with UID/GID 1000 and passwordless sudo access. The container SHALL run as `devuser` by default.

#### Scenario: Container runs as non-root
- **WHEN** the container starts
- **THEN** `whoami` SHALL return `devuser` and `id -u` SHALL return `1000`

#### Scenario: Sudo available without password
- **WHEN** `devuser` runs a command with `sudo`
- **THEN** the command SHALL execute without a password prompt

### Requirement: Claude Code CLI installed
The Dockerfile SHALL install Node.js and the `@anthropic-ai/claude-code` npm package globally.

#### Scenario: Claude Code available in container
- **WHEN** `devuser` runs `claude --version`
- **THEN** the Claude Code CLI SHALL respond with its version

### Requirement: Dependencies installed via uv from pyproject.toml
The Dockerfile SHALL use `uv` to create a virtual environment at `/opt/venv` and install the project in editable mode from `pyproject.toml`.

#### Scenario: Project importable after build
- **WHEN** the container is running
- **THEN** `python -c "import corems"` SHALL succeed

### Requirement: Jupyter notebook support
The Dockerfile SHALL install JupyterLab and register an IPython kernel for the project.

#### Scenario: Jupyter Lab starts
- **WHEN** the notebook entrypoint is invoked
- **THEN** JupyterLab SHALL be accessible on port 8888

### Requirement: System dependencies for scientific stack
The Dockerfile SHALL install system libraries required by the scientific Python stack (e.g., `libhdf5-dev` for h5py, `libnetcdf-dev` for netCDF4, `libxml2-dev` for lxml).

#### Scenario: All Python dependencies compile and install
- **WHEN** `uv pip install -e ".[dev]"` runs during the build
- **THEN** all packages including those with C extensions SHALL install successfully
