# Subtask 08 notes (custom bases)

This file captures implementation decisions and fine-tuning details discussed for Subtask 08.

## Custom base definitions

- Location: `~/.aicage/custom/base-images/<BASE>/`.
- Definition files: `base.yaml` or `base.yml`.
- Required fields (schema):
  - `from_image`
  - `base_image_distro`
  - `base_image_description`
- Required files:
  - `Dockerfile` (must be provided by user).
- Users provide all scripts/assets needed by their Dockerfile. No bundled base scripts.

## Selection behavior

- Custom bases are available to all agents (built-in remote, built-in local, custom local).
- Custom base names override built-in bases with the same name.
- Prompt shows custom base descriptions exactly as provided. No grouping or suffix.
- Base validation applies `base_exclude` and `base_distro_exclude` to custom bases.

## Build/update behavior

- Custom base image ref: `aicage-image-base:<BASE>`.
- Build uses user Dockerfile with `--build-arg FROM_IMAGE=<from_image>`.
- When a custom base is selected, the agent image is always built locally on top of the custom base
  for all agents.
- Extensions build on top of the local agent image as usual.

## Digest checks

- Digest lookup must support ghcr.io and docker.io.
- Implement as a Python package (not a single file), with internal parsing and registry-specific
  logic.
- The docker.io flow is based on `scripts/debug/get-remote-digest-anon.sh`.

## Integration test matrix

- Scenarios (each with and without extensions):
  - Custom base + built-in remote-built agent.
  - Custom base + built-in local-built agent.
  - Custom base + custom local-built agent.
- Rebuild triggers to validate in tests:
  - Agent version changes.
  - Digest mismatch by switching `from_image` tag.

## Test images

- docker.io: `php:8.4.15` -> `php:latest`.
- ghcr.io: `ghcr.io/rblaine95/debian:12` -> `ghcr.io/rblaine95/debian:latest`.
