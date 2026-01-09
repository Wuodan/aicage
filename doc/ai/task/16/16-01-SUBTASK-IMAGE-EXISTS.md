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
