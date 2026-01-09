# Subtask 16-02: Replace version check container run with Docker SDK

## Goal

Replace the CLI-based version check container run with Docker SDK usage.

## Current CLI usage

- Location: `src/aicage/docker/run.py`
- Function: `run_builder_version_check`
- Command: `docker run --rm -v <definition_dir>:/agent:ro -w /agent <image_ref> /bin/bash /agent/version.sh`

## Proposed SDK replacement

- Use `docker.from_env().containers.run(...)`
- Parameters:
  - `image=image_ref`
  - `command=["/bin/bash", "/agent/version.sh"]`
  - `volumes={"<definition_dir>": {"bind": "/agent", "mode": "ro"}}`
  - `working_dir="/agent"`
  - `remove=True`
  - capture stdout/stderr

## Impact

- Low to medium. Non-interactive run, but output handling must map to current error behavior.

## Acceptance criteria

- `run_builder_version_check` uses Docker SDK only
- Output and error semantics remain consistent for `AgentVersionChecker`
- Tests updated to mock SDK client

## Tests

- Unit tests in `tests/aicage/registry/agent_version/test_checker.py`
