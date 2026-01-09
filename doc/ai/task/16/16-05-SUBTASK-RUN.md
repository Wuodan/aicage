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
