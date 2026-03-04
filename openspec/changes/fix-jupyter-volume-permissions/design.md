## Context

Both CoreMS and GraphMZ devcontainer setups use `userns_mode: keep-id` in `docker-compose.yaml` so that bind-mounted host files appear with the correct UID (1000) inside the container. However, both also use a named volume (`jupyter-settings`) for `/home/devuser/.jupyter`. Named volumes are initialized as root-owned inside the container's user namespace. With `keep-id`, container root maps to host subuid 524288, not host UID 1000, so `devuser` cannot write to the volume. This causes Jupyter Lab to crash on startup with a `PermissionError`.

Current mount strategy:
```
Bind mounts (working):     .:/app, ~/.claude:/home/devuser/.claude
Named volume (broken):     jupyter-settings:/home/devuser/.jupyter
```

## Goals / Non-Goals

**Goals:**
- Eliminate the PermissionError on Jupyter startup in both CoreMS and GraphMZ
- Ensure all user-writable mounts use a pattern compatible with both `keep-id` and Docker
- Clean up orphaned named volumes

**Non-Goals:**
- Changing the `keep-id` strategy (it's correct for bind mounts)
- Modifying the Dockerfile or devcontainer.json
- Addressing Jupyter configuration content (only the mount mechanism)

## Decisions

### Use bind mount to `~/.jupyter` instead of named volume

**Choice**: Replace `jupyter-settings:/home/devuser/.jupyter` with `~/.jupyter:/home/devuser/.jupyter`

**Rationale**: Bind mounts inherit host filesystem ownership. With `keep-id`, host UID 1000 maps to container UID 1000 (`devuser`), so permissions work correctly. This is the same pattern already used for `.:/app` and `~/.claude`.

**Alternatives considered**:
- `:U` flag on named volume — Podman-only, breaks Docker compatibility
- `chown` in entrypoint — band-aid, masks root cause, needs repeating for each new volume
- Drop the volume entirely — loses Jupyter settings across rebuilds

### Share `~/.jupyter` across projects

The bind mount means CoreMS and GraphMZ containers share the same host `~/.jupyter` directory. This is acceptable because Jupyter settings (themes, keyboard shortcuts, extensions) are user preferences, not project-specific.

## Risks / Trade-offs

- **`~/.jupyter` created on host** → Acceptable; standard Jupyter config location, created by any `pip install jupyterlab` anyway.
- **Shared settings across containers** → Low risk; Jupyter settings are user-level, not project-level. If isolation is ever needed, can use project-specific paths like `~/.jupyter-corems`.
- **Stale named volumes left behind** → Must explicitly remove `corems_jupyter-settings` and `graphmz_jupyter-settings` volumes after switching to bind mounts.
