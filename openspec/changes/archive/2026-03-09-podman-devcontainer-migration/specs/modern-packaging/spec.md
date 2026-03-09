## ADDED Requirements

### Requirement: Single pyproject.toml for all dependency and build configuration
The project SHALL declare all build system configuration, dependencies, and tool settings in a single `pyproject.toml` file at the repository root, using PEP 621 metadata format with a `uv`-compatible build backend.

#### Scenario: Core dependencies declared
- **WHEN** a developer inspects `pyproject.toml`
- **THEN** all 26 core runtime dependencies (currently in `requirements.txt`) SHALL be listed under `[project.dependencies]` with compatible version constraints

#### Scenario: Development dependencies declared
- **WHEN** a developer needs to install dev tools
- **THEN** development dependencies (currently in `requirements-dev.txt`) SHALL be available under `[project.optional-dependencies]` as a `dev` extra

#### Scenario: uv install works
- **WHEN** a developer runs `uv pip install -e .` or `uv pip install -e ".[dev]"`
- **THEN** the project and its dependencies SHALL install successfully on Python 3.12

### Requirement: Python 3.12 minimum version
The project SHALL declare `requires-python = ">=3.12"` in `pyproject.toml`.

#### Scenario: Python version constraint enforced
- **WHEN** a user attempts to install CoreMS on Python < 3.12
- **THEN** the package manager SHALL reject the installation with a clear version error

### Requirement: Pythonnet version updated to 3.0.5
The project SHALL pin pythonnet to `~=3.0.5` to ensure compatibility with Python 3.12 and .NET 10.

#### Scenario: Pythonnet installs on Python 3.12
- **WHEN** dependencies are installed via `uv pip install -e .`
- **THEN** pythonnet 3.0.5 SHALL install without errors on Python 3.12

### Requirement: Dependency version pins reviewed for Python 3.12
All dependency version pins SHALL be updated to versions that are compatible with Python 3.12. Pins that are unnecessarily restrictive (e.g., `numpy~=1.24.2`) SHALL be relaxed to the latest compatible minor version range.

#### Scenario: All dependencies resolve together
- **WHEN** `uv pip install -e ".[dev]"` is run in a clean Python 3.12 environment
- **THEN** all dependencies SHALL resolve without conflicts

### Requirement: Legacy build files superseded
The new `pyproject.toml` SHALL replace `setup.py`, `requirements.txt`, and `requirements-dev.txt` as the canonical dependency and build configuration.

#### Scenario: Package builds from pyproject.toml
- **WHEN** a developer runs `uv build` or `python -m build`
- **THEN** a distributable package SHALL be produced using pyproject.toml metadata
