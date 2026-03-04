## 1. CoreMS compose fix

- [x] 1.1 Replace `jupyter-settings:/home/devuser/.jupyter` with `~/.jupyter:/home/devuser/.jupyter` in CoreMS `docker-compose.yaml`
- [x] 1.2 Remove `jupyter-settings:` from the top-level `volumes:` section in CoreMS `docker-compose.yaml`

## 2. GraphMZ compose fix

- [x] 2.1 Replace `jupyter-settings:/home/devuser/.jupyter` with `~/.jupyter:/home/devuser/.jupyter` in GraphMZ `docker-compose.yaml`
- [x] 2.2 Remove `jupyter-settings:` from the top-level `volumes:` section in GraphMZ `docker-compose.yaml`

## 3. Volume cleanup

- [x] 3.1 Remove stale `corems_jupyter-settings` Podman volume
- [x] 3.2 Remove stale `graphmz_jupyter-settings` Podman volume (if exists)

## 4. Verify

- [x] 4.1 Restart CoreMS container and confirm Jupyter Lab starts without PermissionError
- [x] 4.2 Confirm `~/.jupyter` exists on host with correct ownership (UID 1000)
