# Subtask 08: Custom local base images

## Goal

Allow users to define custom base images under ~/.aicage/custom/image-base/ and integrate them into
selection and local build/update logic.

## Rationale

Custom bases add complexity across selection and updates. They should be layered after the local
build pipeline and extensions are stable.

## Dependencies

- Architecture decisions from Subtask 01.
- Runtime discovery/version checks from Subtask 04.
- Local build pipeline from Subtask 05.
- Extensions flow from Subtask 07.
- Task 12 overview: doc/ai/task/12/12-TASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Discover custom base definitions and validate base.yml.
- Build local base images with the defined naming rules.
- Update checks based on the base "from image" and agent version.
- Integrate custom bases into selection flow with extensions.

## Out of scope

- New feature requests outside Task 12.

## Expected outputs

- Custom base images build and update locally.
- Selection flow includes custom bases without breaking existing behavior.

## Sequencing

Run after Subtask 07.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md and include a subtask summary at completion.

## Implementation logic (current intent)

This section captures the intended flow and constraints for custom local base images.

### 1) Source and location

- Custom base configs live at `~/.aicage/custom/image-base/`, alongside `custom/agents` and
  `custom/extensions`.
- The config format is analogous to custom agents/extensions and must be schema-validated.
- Each custom base config includes a `from_image` that is used for update checks.

### 2) Selection flow

- Run starts with `aicage <AGENT>`. User answers all configuration prompts before any build/pull.
- Base selection is the first prompt. Custom bases appear alongside built-in bases, optionally grouped.
- The selected base is stored in `RunConfig.selection` as it is today (possibly with a minimal extension).

### 3) Build flow (base + agent, then extensions)

- The pipeline stays a serial "input image + optional additions = next input image":
  1. Ensure base+agent image is local (either pulled from remote or built locally).
  2. If extensions are selected, build an extended image on top of the local base+agent image.

### 4) Custom base handling

- If the selected base is a custom base, the base+agent image is built locally using the custom base.
- Update checks reuse existing logic: compare the remote digest of `from_image` against local image
  layers. If the digest is not present, rebuild the local base+agent image.
- The derivation of the base+agent image ref must be centralized (currently in local-build ref helpers)
  so custom-base overrides can plug in cleanly.
  - Note: multi-stage builds or squashed layers can remove the `from_image` layers and bypass the
    digest-based update check; this is acceptable for advanced custom workflows.

### 5) Minimal changes to existing flow

- The extension pipeline remains unchanged once the base+agent image is locally present.
- Only the selection and base-image resolution steps need to account for custom bases.
