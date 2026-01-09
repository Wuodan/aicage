# Subtask 16-03: Replace image pull with Docker SDK

## Goal

Replace the CLI-based image pull with Docker SDK usage and adjust logging/error handling.

## Current CLI usage

- Location: `src/aicage/docker/pull.py`
- Function: `run_pull`
- Command: `docker pull <image_ref>`
- Logging: stdout lines streamed to a log file

## Proposed SDK replacement

- Use `docker.from_env().images.pull(image_ref)` or low-level API for streaming progress
- Write SDK log events to the same log file (format change allowed)
- Propagate SDK exceptions directly (no CLI fallback behavior)

## Impact

- Medium. Logging and error behavior will shift to SDK semantics.

## Acceptance criteria

- `run_pull` uses Docker SDK only
- Log file continues to be written during pull
- Tests updated to mock SDK client and log stream

## Tests

- Unit tests in `tests/aicage/registry/test_image_pull.py`
