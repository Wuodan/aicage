# Subtask 16-01: Replace image existence check with Docker SDK

## Goal

Replace the CLI-based image existence check with Docker SDK usage.

## Current CLI usage

- Location: `src/aicage/docker/build.py`
- Function: `local_image_exists`
- Command: `docker image inspect <image_ref>`

## Proposed SDK replacement

- Use `docker.from_env().images.get(image_ref)`
- Treat `ImageNotFound` as false; other exceptions bubble up

## Impact

- Low. Behavior remains a boolean existence check, with SDK error types.

## Acceptance criteria

- `local_image_exists` uses Docker SDK only
- Tests updated to mock SDK client
- No CLI calls remain for this check

## Tests

- Unit tests in `tests/aicage/docker/test_build.py`
