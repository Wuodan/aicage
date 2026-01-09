# Subtask 16-05: Replace container run with Docker SDK

## Goal

Evaluate replacing the CLI-based container run with Docker SDK usage.

## Current CLI usage

- Location: `src/aicage/docker/run.py`
- Function: `run_container`
- Command: `docker run --rm -it ...`
- Interactive TTY required

## Proposed SDK replacement

- Use `docker.from_env().containers.run(...)` with `tty=True` and `stdin_open=True`
- Implement explicit attach/stream handling for interactive sessions
- Preserve exit codes and signal handling

## Impact

- High. Interactive TTY behavior is complex in SDK; likely to remain CLI.

## Acceptance criteria

- If SDK can handle interactive TTY reliably, replace CLI
- If not, keep CLI and close subtask as no-change

## Tests

- Existing CLI integration tests remain the main verification

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
