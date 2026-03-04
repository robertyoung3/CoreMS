## Why

Podman rootless named volumes are initialized as root-owned inside the container user namespace. With `userns_mode: keep-id`, container root (UID 0) maps to a host subuid (524288), not the host user (UID 1000). This means `devuser` cannot write to named volume directories, causing Jupyter Lab to crash with `PermissionError` on startup and preventing VS Code devcontainer reconnection. The same issue affects both CoreMS and GraphMZ.

## What Changes

- Replace the `jupyter-settings` named volume with a bind mount to `~/.jupyter` on the host in both CoreMS and GraphMZ `docker-compose.yaml` files
- Remove the `jupyter-settings` named volume definition from both compose files
- Remove the stale `corems_jupyter-settings` and `graphmz_jupyter-settings` Podman volumes

## Capabilities

### New Capabilities

- `devcontainer-volume-hygiene`: Ensure all user-writable mounts in devcontainer compose files use bind mounts (not named volumes) when `userns_mode: keep-id` is configured, so that host UID ownership is preserved via the keep-id mapping.

### Modified Capabilities

(none)

## Impact

- **Files**: `docker-compose.yaml` (CoreMS), `docker-compose.yaml` (GraphMZ)
- **Runtime**: Existing `jupyter-settings` named volumes become orphaned and should be removed
- **Compatibility**: Bind mounts work identically with both Docker and Podman; no behavioral change for upstream CoreMS users or GraphMZ users running Jupyter Lab in the browser
- **Host side effect**: Creates `~/.jupyter/` on the host if it doesn't exist (standard Jupyter config location)
