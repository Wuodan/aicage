# Subtask 16-04: Replace image build with Docker SDK

## Goal

Replace the CLI-based local and extended image builds with Docker SDK usage.

## Current CLI usage

- Location: `src/aicage/docker/build.py`
- Functions: `run_build`, `run_extended_build`, `_cleanup_intermediate_images`
- Commands:
  - `docker build ...` (local build)
  - `docker build ...` (per-extension build)
  - `docker image rm -f <image_ref>` (cleanup)

## Proposed SDK replacement

- Use `docker.from_env().images.build(...)` with `buildargs`, `tag`, `dockerfile`, `nocache=True`
- Stream build logs via SDK and write to log file
- Use `client.images.remove(image_ref, force=True)` for cleanup

## Impact

- Medium to high. Build log format and error handling change to SDK semantics.

## Acceptance criteria

- Builds and cleanup use Docker SDK only
- Log files are populated during build
- Tests updated to mock SDK build/remove behavior

## Tests

- Unit tests in `tests/aicage/docker/test_build.py`
- Unit tests in `tests/aicage/docker/test_extended_build.py`
