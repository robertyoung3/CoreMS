FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install system dependencies for scientific Python stack and Node.js
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    sudo \
    build-essential \
    g++ \
    cmake \
    # HDF5 for h5py
    libhdf5-dev \
    pkg-config \
    # NetCDF for netCDF4
    libnetcdf-dev \
    # XML for lxml
    libxml2-dev \
    libxslt1-dev \
    # PostgreSQL client for psycopg2
    libpq-dev \
    # Rendering for matplotlib
    libxrender1 \
    libfontconfig1 \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install .NET 10 LTS runtime for pythonnet/Thermo .raw file support
RUN wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y dotnet-runtime-10.0 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with UID 1000 (matches typical host user)
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid $USER_GID devuser \
    && useradd --uid $USER_UID --gid $USER_GID -m devuser \
    && echo "devuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/devuser \
    && chmod 0440 /etc/sudoers.d/devuser

# Install Claude Code
RUN npm install -g @anthropic-ai/claude-code

WORKDIR /app

# Environment setup
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/home/devuser/.local/bin:/opt/venv/bin:/usr/local/bin:/usr/bin:/bin:$PATH" \
    PYTHONPATH=/app:$PYTHONPATH \
    PYTHONNET_RUNTIME=coreclr

# Copy project files needed for dependency installation
COPY pyproject.toml ./
COPY corems/ ./corems/
COPY ext_lib/ ./ext_lib/
COPY README.md ./

# Create venv and install dependencies
RUN uv venv /opt/venv \
    && . /opt/venv/bin/activate \
    && uv pip install -e ".[dev]" \
    && uv pip install jupyter jupyterlab ipykernel

# Configure Jupyter
RUN python -m ipykernel install --prefix=/usr/local --name=corems --display-name="CoreMS" \
    && jupyter lab --generate-config \
    && mkdir -p /home/devuser/.local/share/jupyter \
    && chown -R devuser:devuser /home/devuser/.local

COPY . .

# Set ownership of app directory and venv to devuser
RUN chown -R devuser:devuser /app /opt/venv

EXPOSE 8888

# Startup script for Jupyter
RUN echo '#!/bin/bash\n\
echo "Starting Jupyter Lab..."\n\
exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser' > /start.sh && chmod +x /start.sh

# Switch to non-root user
USER devuser

CMD ["/start.sh"]
