# Task 15: Local build base-image digest validation

Our current base-image check for locally built images (built-in or custom agents layered on top of a base image) relies
on a base-image digest stored as text in local state. This is weaker than what we do for built-in agents with remote
final images, where we compare the actual remote digest to the local image digest.

In `aicage-image` we already have a stronger model: the pipeline
`.github/workflows/refresh-images.yml` checks whether the current remote base-image digest is contained in the final
image layers. That is the intended behavior for locally built images too. This task is about bringing local builds in
`aicage` up to that standard.

## Base-image digest validation for local builds

Goal: For locally built images (local built-in agents and local custom agents), validate whether the remote base-image
digest is contained in the local final image, rather than trusting stored text state. Align the local build check with
the logic used by `aicage-image`’s refresh workflow.

Constraints:

- Use real remote digests for base images, not stored text values.
- Avoid adding new config fields unless explicitly asked.
- Keep changes minimal and consistent with existing code structure.

## Task Workflow

Don't forget to read AGENTS.md and always use the existing venv.

You shall follow this order:
1. Read documentation and code to understand the task.
2. Ask me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters as in the pipeline `.github/workflows/publish.yml` or `scripts/lint.sh` (does the same)
6. Present me the change for review
7. Interactively react to my review feedback
8. Do not commit any changes unless explicitly instructed by the user. Remind him about it when you think committing
   is due.
