# Subtask 08.2: Custom base build/update flow and digest package

## Goal

Add custom base build/update behavior and the multi-registry digest lookup package.

## Rationale

Building custom bases and tracking updates touches local build, pull checks, and registry
integration. Keeping this separate reduces risk.

## Dependencies

- Task 12 overview: doc/ai/task/12/12-TASK.md
- Subtask 08: doc/ai/task/12/08/08-SUBTASK.md
- Subtask 08.1: doc/ai/task/12/08/01-discovery-selection/01-SUBTASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Build custom base images locally using user Dockerfiles.
- Base image ref for custom bases: `aicage-image-base:<BASE>`.
- Digest lookup package for ghcr.io and docker.io (anon) with registry-aware parsing.
- Integrate digest checks into base update logic.
- Build agent images locally on custom bases for all agents.

## Out of scope

- Integration tests that exercise custom bases end-to-end.

## Expected outputs

- Custom bases build locally and rebuild on digest changes.
- Digest lookup works for ghcr.io and docker.io.

## Sequencing

Run before Subtask 08.3.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md. See the `## Task/SubTask Workflow`
section. Do not write a subtask summary unless explicitly requested.
