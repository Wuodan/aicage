# Integration Tests

## Purpose

Integration tests exercise real user flows with Docker, network access, and external installs. They are intentionally
heavier than unit tests and aim to verify that the full `aicage` CLI workflow works with real images, real
version checks, and real local build behavior. The tests are opt-in via the `AICAGE_RUN_INTEGRATION` env var and run
in a sandboxed HOME during test execution to avoid touching a developer's real `~/.aicage` state.

## Scope and philosophy

- Use real Docker images and real network resources; no fake Docker stubs in integration tests.
- Keep the test state isolated by setting `HOME` to a temporary directory.
- Validate behavior via the build record written under `~/.aicage/state/local-build`.
- Run the CLI in a pseudo-TTY so the normal `docker run -it` flow works as in real usage.

## Running integration tests locally

For Linux or MacOS:

```bash
AICAGE_RUN_INTEGRATION=1 pytest -m integration
```

For Windows:

```shell
$old = $env:AICAGE_RUN_INTEGRATION
$env:AICAGE_RUN_INTEGRATION="1"
pytest -m integration
$env:AICAGE_RUN_INTEGRATION = $old
```

## CI workflow

The reusable workflow `/.github/workflows/integration-test.yml` discovers integration tests and runs each test in its
own job. The release workflow `/.github/workflows/publish.yml` calls the reusable workflow.

## Current integration tests

### Remote built-in agents

Files: `tests/aicage/integration/remote_builtin/test_run.py`,
`tests/aicage/integration/remote_builtin/test_pull_newer.py`,
`tests/aicage/integration/remote_builtin/test_extensions.py`

- `test_builtin_agent_runs`
  - Uses the built-in `codex` agent and runs `aicage codex --version`.
  - Ensures the CLI can pull and run a prebuilt image and that the version output is non-empty.

- `test_builtin_agent_pulls_newer_digest`
  - Uses the built-in `copilot` agent.
  - Tags a locally built dummy image with the same name:tag as the remote image.
  - Runs `aicage copilot -c "echo ok"` with docker args preseeded to `--entrypoint=/bin/bash`, then verifies the local
    image ID changes and a repo digest is present.

- `test_remote_builtin_extension_rebuilds_on_base_change`
  - Uses the built-in `codex` agent with a local `marker` extension.
  - Builds the extended image, then replaces the base image tag with a dummy image.
  - Runs the agent again and verifies the base image is pulled and the extended image is rebuilt.

### Local built-in agents

Files: `tests/aicage/integration/local_builtin/test_rebuild_agent_version.py`,
`tests/aicage/integration/local_builtin/test_rebuild_base_layer.py`,
`tests/aicage/integration/local_builtin/test_extensions.py`

- `test_local_builtin_agent_rebuilds`
  - Uses the built-in `claude` agent (local build required).
  - Runs `aicage claude --version` to build and validate the image once.
  - Forces a rebuild by editing the build record to use an outdated `agent_version`, then runs again and asserts that
    the build record updates.

- `test_local_builtin_agent_rebuilds_on_base_layer`
  - Uses the built-in `claude` agent (local build required).
  - Runs `aicage claude --version` to build and validate the image once.
  - Replaces the final image tag with a dummy image, then runs again and asserts that the build record updates.

- `test_local_builtin_extension_builds_and_runs`
  - Copies the `marker` sample extension from `doc/sample/custom/extensions/marker` into the sandboxed extension
    directory.
  - Preseeds the project config with the extension and an `aicage-extended` image tag for `claude`.
  - Runs `aicage claude -c "test -f /usr/local/share/aicage-extensions/marker.txt"` with an entrypoint override and
    verifies the marker file exists in the container.

- `test_local_builtin_extension_rebuilds_on_agent_version`
  - Uses the built-in `claude` agent with a local `marker` extension.
  - Forces a rebuild by editing the build record to use an outdated `agent_version`, then runs again and asserts that
    the build record updates and the extended image matches the rebuilt base image.

- `test_local_builtin_extension_rebuilds_on_base_layer`
  - Uses the built-in `claude` agent with a local `marker` extension.
  - Replaces the extended image tag with a dummy image, runs again, and verifies the extended image rebuilds.

### Local custom agents

Files: `tests/aicage/integration/local_custom/test_build_and_version.py`,
`tests/aicage/integration/local_custom/test_rebuild_agent_version.py`,
`tests/aicage/integration/local_custom/test_rebuild_base_layer.py`,
`tests/aicage/integration/local_custom/test_extensions.py`

- `test_custom_agent_build_and_version`
  - Copies the `forge` sample from `doc/sample/custom/agents/forge` into the sandboxed custom agent directory.
  - Runs `aicage forge --version` in a pseudo-TTY and asserts non-empty output.
  - Confirms a build record exists for the custom agent.

- `test_custom_agent_rebuilds`
  - Uses the custom `forge` agent from `doc/sample/custom/agents/forge`.
  - Runs `aicage forge --version` to build and validate the image once.
  - Forces a rebuild by editing the build record to use an outdated `agent_version`, then runs again and asserts that
    the build record updates.

- `test_custom_agent_rebuilds_on_base_layer`
  - Uses the custom `forge` agent from `doc/sample/custom/agents/forge`.
  - Runs `aicage forge --version` to build and validate the image once.
  - Replaces the final image tag with a dummy image, then runs again and asserts that the build record updates.

- `test_local_custom_extension_builds_and_runs`
  - Copies the `forge` agent sample and the `marker` extension sample into the sandboxed custom directories.
  - Preseeds the project config with the extension and an `aicage-extended` image tag for `forge`.
  - Runs `aicage forge -c "test -f /usr/local/share/aicage-extensions/marker.txt"` with an entrypoint override and
    verifies the marker file exists in the container.

- `test_local_custom_extension_rebuilds_on_agent_version`
  - Uses the custom `forge` agent with a local `marker` extension.
  - Forces a rebuild by editing the build record to use an outdated `agent_version`, then runs again and asserts that
    the build record updates and the extended image matches the rebuilt base image.

- `test_local_custom_extension_rebuilds_on_base_layer`
  - Uses the custom `forge` agent with a local `marker` extension.
  - Replaces the extended image tag with a dummy image, runs again, and verifies the extended image rebuilds.

### Extensions

Files: `tests/aicage/integration/extensions/test_build.py`

- `test_extension_builds_and_runs`
  - Copies the `marker` sample extension from `doc/sample/custom/extensions/marker` into the sandboxed extension
    directory.
  - Preseeds the project config with the extension and an `aicage-extended` image tag.
  - Runs `aicage codex -c "test -f /usr/local/share/aicage-extensions/marker.txt"` with an entrypoint override
    and verifies the marker file exists in the container.

- `test_extension_rebuilds_on_base_image_change`
  - Copies the `marker` sample extension from `doc/sample/custom/extensions/marker` into the sandboxed extension
    directory.
  - Preseeds the project config with the extension and an `aicage-extended` image tag.
  - Replaces the base image tag with a dummy image, runs the agent again, and verifies the extended image rebuilds.

### Version check fallback

File: `tests/aicage/integration/test_version_check.py`

- `test_version_check_falls_back_to_builder`
  - Creates a version script that requires `npm` and injects a shim `npm` that always fails on the host.
  - Verifies that the version check falls back to the builder image and returns a non-empty version.

## Notes and constraints

- Integration tests are intentionally slow and require Docker and network access.
- The tests run with `HOME` set to a temporary directory to avoid writing to real user state.
- The `forge` sample files are used as-is and should remain a valid example for users.

## Expected failures (current)

- `tests/aicage/integration/remote_builtin/test_pull_newer.py`
  - `test_builtin_agent_pulls_newer_digest` currently fails because `aicage` does not yet pull a newer remote image
    when a local image with the same tag exists. This is intentional to capture the missing behavior.
