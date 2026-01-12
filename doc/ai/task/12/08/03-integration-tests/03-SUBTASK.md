# Subtask 08.3: Custom base integration tests

## Goal

Add integration coverage for custom bases across agent types and extension flow.

## Rationale

Custom bases touch selection, build, and update logic. Integration tests verify digest-based
rebuilds and agent version rebuilds in real workflows.

## Dependencies

- Task 12 overview: doc/ai/task/12/12-TASK.md
- Subtask 08: doc/ai/task/12/08/08-SUBTASK.md
- Subtask 08.2: doc/ai/task/12/08/02-build-digest/02-SUBTASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Integration tests for custom base + agent combinations:
  - Built-in remote-built agent.
  - Built-in local-built agent.
  - Custom local-built agent.
  - Each of the above with extensions.
- Rebuild coverage for:
  - Agent version changes.
  - Digest mismatch by switching `from_image` tags.
- Use real network for digest checks.

## Out of scope

- Changes to runtime logic.
- Documentation for end users.

## Expected outputs

- Integration suite verifies custom base selection/build/update behavior.
- Digest-based rebuilds are validated against docker.io and ghcr.io.

## Sequencing

Run after Subtask 08.2.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md. See the `## Task/SubTask Workflow`
section. Do not write a subtask summary unless explicitly requested.
