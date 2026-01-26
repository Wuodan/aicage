# Subtask 16-04: Replace image build with Docker SDK

## Status: Skipped

This subtask was skipped to keep the Docker CLI path because the Docker SDK does not
support BuildKit yet. See: <https://github.com/docker/docker-py/issues/2230>

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

## Subtask Guidelines and Workflow

Don't forget to read `AGENTS.md` and `doc/python-test-structure-guidelines.md`; always use the existing venv.

You shall follow this order:

1. Read documentation and code to understand the task.
2. Ask me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters with `scripts/lint.sh`
6. Present me the change for review
7. Interactively react to my review feedback
8. Do not commit any changes unless explicitly instructed by the user.
