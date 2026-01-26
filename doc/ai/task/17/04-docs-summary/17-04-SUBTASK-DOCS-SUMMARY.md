# Subtask 17-04: Update documentation and write summary

## Goal

Update docs affected by the migration away from `images_metadata`, and write a Task 17 summary.

## Current state

- Documentation may still reference `config/images-metadata.yaml` and the old loading flow.

## Proposed changes

- Review `README.md` and `DEVELOPMENT.md` for any references that need updates.
- Update or remove docs that point to `images-metadata.yaml` if no longer accurate.
- Write a Task 17 summary Markdown in `doc/ai/task/17`.

## Impact

- Low: documentation-only change.

## Acceptance criteria

- Docs reflect the new configuration flow and paths.
- Task 17 summary exists and is accurate.

## Tests

- None.

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
