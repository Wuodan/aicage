# Subtask 03 summary

## Context

- Subtask id and title: 03 - CI and test strategy for non-redistributable agents.
- Related subtasks touched or impacted: Subtask 01, Subtask 02.

## Changes

- Key decisions (why):
  - Non-redistributable agent CI is a separate workflow that builds and tests images without publish/sign/manifest.
  - No persisted digests for non-redistributable rebuild detection; tests run on aicage-image release only.
  - Avoid "NR" abbreviation in code/docs; use "non-redistributable".
  - Remove unused image labels and label tests since labels are decorative and not used at runtime.
  - Keep one image build per job (matrix fan-out) to fit GitHub runner disk constraints.
  - Avoid build caches in CI to prevent stale package installs when scripts pull latest versions.
- User-visible behavior changes:
  - Release pipeline runs non-redistributable agent tests before creating a release.
  - Refresh runs build workflows inline, preventing repeated rebuild loops while builds are in-flight.
- Internal behavior changes:
  - aicage-image: build matrices generated once, then split by redistributable via jq.
  - aicage-image: build.yml consumes matrices only; manual runs use a dummy matrix default.
  - aicage-image: refresh-images.yml resolves latest release tag, builds matrices, and calls build.yml inline.
  - aicage-image: tag-build logic merged into release.yml for tag-triggered runs.
  - aicage-image-base: consolidated per-image workflows into one matrix workflow; release runs after build.
  - aicage-image-base: scheduled builds resolve latest release tag; manual runs use selected ref.
- Files and modules with major changes:
  - aicage-image/.github/workflows/release.yml.
  - aicage-image/.github/workflows/test-non-redistributable-agents.yml.
  - aicage-image/.github/workflows/build.yml.
  - aicage-image/.github/workflows/refresh-images.yml.
  - aicage-image/scripts/debug/build.sh.
  - aicage-image/tests/smoke/01-labels.bats.
  - aicage-image-base/.github/workflows/build-all-images.yml.
  - aicage-image-base/.github/workflows/build-image.yml (removed).
  - aicage-image-base/scripts/debug/build.sh.
  - aicage-image-base/scripts/debug/build-all.sh.
  - aicage-image-base/scripts/debug/test-all.sh.
  - aicage-image-base/scripts/test.sh.
  - aicage-image-base/tests/smoke/minimal/05-labels.bats.
  - aicage-image-base/tests/smoke/default/05-labels.bats.

## Testing and validation

- Tests run:
  - User ran GitHub workflows, including test-non-redistributable-agents.yml and release pipeline checks.
  - User ran act locally for workflow_dispatch during iteration.
- Gaps or skipped tests and why:
  - No automated test runs from this session by the agent; relied on user-run CI tests.

## Follow-ups

- Deferred items (explicitly list):
  - None.
- Known risks or open questions:
  - None.
- Suggested next steps:
  - None.

## Notes

- Lessons learned:
  - Keep matrix JSON one line when writing to GITHUB_OUTPUT; print formatted JSON separately for logs.
  - Avoid unnecessary installations of jq/yq on GitHub runners; they are preinstalled.
  - Split workflows by purpose: build/publish vs test-only for non-redistributable agents.
- Review feedback to carry forward:
  - Do not use the "NR" abbreviation in code/docs.
  - Do not install jq/yq in workflows.
  - Keep workflows readable: comment long matrix generation steps and avoid extra branching.
  - Prefer inline workflow calls over gh dispatch to avoid races.
