# CoreMS DevContainer Setup Documentation

This document describes the customized development container setup for CoreMS, explains the key modifications made to the original repository, and outlines the procedures for maintaining the branch while staying in sync with upstream changes.

## Overview

This customized setup provides a development environment for CoreMS inside a container, making it easier to develop, test, and run the library with consistent dependencies. The DevContainer configuration includes:

1. A Python 3.10 development environment
2. Integration with Visual Studio Code
3. PostgreSQL database preconfigured for CoreMS
4. Improved Dockerfile configurations
5. Debugging and testing tools

## Key Customizations

### 1. DevContainer Configuration

A complete DevContainer setup was added in the `.devcontainer` directory with:

- `devcontainer.json` - Configuration for VS Code integration
- `Dockerfile.dev` - Development container with debugging tools
- `docker-compose.extend.yml` - Container orchestration for development

### 2. Docker Configuration

- Modernized Dockerfiles with improved layering and dependencies
- Added Python 3.10 support via `Dockerfile_py310`
- Maintained legacy Python 3.7 setup in `Dockerfile_py37`
- Updated `docker-compose.yml` with health checks and networking improvements

### 3. Database Configuration

- Configured PostgreSQL database with proper credentials
- Set up environment variables for database connections
- Modified connection strings in CoreMS code to work with containers

### 4. Molecular Formula Settings

- Modified default atom ranges in `MolecularLookupDictSettings` class
- Added utility scripts for database initialization

### 5. Environment and Settings

- Added default `SettingsCoreMS.json` configuration file
- Modified `.env` file for container communication
- Updated `.gitignore` to accommodate development files

## Maintenance Procedures

### Updating from Upstream

To keep your branch current with upstream changes while preserving your devcontainer customizations:

1. **Update master branch from upstream:**

```bash
git checkout master
git pull upstream master     # Get latest from original project
git push origin master       # Update fork's main
```

2. **Rebase customized branch:**

```bash
git checkout CoreMS_NOM
git rebase master            # Put your changes on top of updated main
```

3. **Resolve any conflicts:**

Focus on preserving your devcontainer customizations during conflict resolution:

* Keep custom Docker/DevContainer files
* Maintain your database connection strings
* Preserve your modified parameter settings
* Accept upstream improvements to core functionality

```bash
git add .                    # Mark resolved files
git rebase --continue
```

4. **Push updated branch:**

```bash
git push -f origin CoreMS_NOM  # Force push needed after rebase
```

### Creating a Patch File (Reference)

After successfully rebasing, create a patch file to document your customizations:

```bash
git diff master..CoreMS_NOM > devcontainer-changes.patch
```

This patch file serves as documentation and backup of your customizations.


## Development Workflow

### Building the Environment

```bash
# Start with standard cache
docker-compose up -d

# After changes to Dockerfile.dev
docker-compose up --build -d
```

### Cleaning Docker Resources

When you need to start fresh:

```bash
# Stop CoreMS containers
docker-compose down

# Remove CoreMS images
docker rmi corems_notebook
docker rmi corems_dev

# Remove CoreMS volume
docker volume rm corems_db-volume

# Remove CoreMS network
docker network rm corems_corems-network
```

### Verify the Setup

```bash
docker-compose ps
docker logs corems_dev
```

### Rebuilding After Repository Updates

When you've updated your repository from upstream, perform a clean rebuild:

```bash
# Step 1: Stop existing containers
docker-compose down
docker images | findstr corems

# Step 2: Remove existing images
docker rmi corems-corems_notebook

# Stop and remove container first if necessary using the container ID 
# Superior to `docker rmi -f corems-corems_dev`
docker ps -a | findstr corems-corems_dev
docker stop 32c47bf6ae5a
docker rm 32c47bf6ae5a
docker rmi corems-corems_dev

# Step 3: Rebuild and start containers
docker-compose up --build -d

# Step 4: Verify the setup
docker-compose ps
docker logs corems_dev
```

## Benefits of This Approach

- **Clean history:** Rebasing keeps your commit history organized
- **Easier upstream syncs:** Regular updates keep your branch current
- **Branch stays current:** You get both custom environment and latest features
- **No merge commits:** Maintains a linear history
- **DevContainer integration:** Seamless development experience in VS Code

## Warning

- Only force push to personal branches
- Communicate with team members if working on shared branches