# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.5] - 2026-01-10

### Changed

- Extension builds now run as a strict post-step on a guaranteed-local base+agent image.
- Image pull and local build paths now pass explicit image refs instead of copying run configs.

### Internal

- Centralized base-layer checks for local and extended image decisions.
- Simplified pull decisions to return booleans.
- Added a registry-level ensure entrypoint for local image setup.

## [0.7.4] - 2026-01-10

### Changed

- Image pulls now use the Docker SDK with streaming logs.

### Internal

- Increased Docker SDK and registry HTTP timeouts for slow connections.

## [0.7.3] - 2026-01-10

### Changed

- Builder version checks now pre-pull the util image with a log path notice and reuse local images on pull
  failure.

### Internal

- Moved local image existence checks to the Docker SDK client.
- Ran builder version checks via Docker SDK containers.
- Reworked Docker query helpers to use dedicated image reference dataclasses.

## [0.7.2] - 2026-01-09

### Internal

- Centralized Docker interactions under `aicage.docker` and moved run/build/pull/query helpers into it.
- Split extension metadata helpers into `aicage.registry.extensions` and promoted runtime env vars module.
- Added task 16 Docker SDK migration subtasks in `doc/ai/task/16/`.

## [0.7.1] - 2026-01-09

### Changed

- Custom extension directory moved to `~/.aicage/custom/extensions/`.

### Internal

- Added integration test coverage for extensions with local built-in, remote built-in, and local custom agents.

## [0.7.0] - 2026-01-08

### Added

- Local extensions under `~/.aicage/custom/extensions/` with extension metadata, scripts, and optional Dockerfile.
- Extended final images with local config under `~/.aicage/custom/image-extended/`.
- Image selection flow to pick base images or extended images and apply extensions.
- Local build/update pipeline for extended images with build logs and stored metadata.
- End-user documentation for extension authoring and usage.

### Changed

- Project config now stores extended image refs and extension selections per agent.
- Extension build Dockerfiles no longer include `# syntax` directives or unused build args.

### Internal

- Added test coverage for extension discovery, selection, prompts, and extended image build flows.

## [0.6.4] - 2026-01-08

### Changed

- Local builds now validate base image updates by checking base layers in final images, removing stored base digest
  state.

### Internal

- Consolidated YAML path constants and refreshed integration/CI helpers for clearer test and pipeline output.

## [0.6.3] - 2026-01-07

### Fixed

- Accept lowercase registry digest headers when checking for newer remote images.

## [0.6.2] - 2026-01-07

### Added

- Integration test coverage for remote built-in, local built-in, and local custom agent workflows.

### Changed

- Custom agent directory moved to `~/.aicage/custom/agents/`.
- Renamed `--entrypoint` to `--aicage-entrypoint` to avoid collision with Docker.

## [0.6.1] - 2026-01-04

### Fixed

- Synced the packaged Dockerfile with the updated `entrypoint.sh` from `aicage-image`.

## [0.6.0] - 2026-01-03

### Added

- Support custom local agents under `~/.aicage/custom/agent/` with schema validation and local builds.

## [0.5.14] - 2026-01-03

### Changed

- Update image- and agent-metadata from latest `aicage-image` release.

## [0.5.13] - 2026-01-02

### Added

- Added `local_image_repository` config for consistent local image naming.

### Changed

- Custom and non-redistributable agents now use `local_image_repository` for local image refs.

## [0.5.12] - 2026-01-02

### Fixed

- Agent version checks now run with `/bin/bash` on host and in the util image.
- Entrypoint mount tests now reflect the bash-based entrypoint script.

## [0.5.11] - 2026-01-02

### Fixed

- Version checks now default to the published `aicage-image-util:agent-version` tag.

### Changed

- Agent version checks prefer the host toolchain before pulling the util image.

## [0.5.10] - 2026-01-02

### Fixed

- Package now includes the latest images metadata by downloading and packaging it, not just testing it.
- Publish job now pins the package version to the release tag to avoid local-version uploads.

## [0.5.9] - 2026-01-02

### Added

- Shared pull log location for all image pulls.
- Local `scripts/lint.sh` helper for linting and `__all__` checks.
- Coverage for runtime config persistence/version checks and a dynamic `__all__` test.

### Changed

- Docker pull output is now written to logs; CLI prints a single-line pull message with log path.
- CLI internals moved into `aicage/cli/` for clearer separation.

### Refactored

- Split local build logic into smaller modules (plan, digest, runner).
- Split image pull logic into decision and runner helpers.

## [0.5.8] - 2026-01-02

### Added

- Support non-redistributable agents with local final-image builds and update checks.
- Local build pipeline for non-redistributable agents (local image naming, build metadata, and logs).
- Added `image_base_repository` to global config.
- Packaged non-redistributable agent build context under `config/agent-build/`.
- Remote digest queries consolidated for base-image checks.

## [0.4.10] - 2025-12-31

### Added

- Core runtime that pulls and runs published `aicage` images built by `aicage-image` and `aicage-image-base`.

## [0.4.x] - Historical

### Added

- Initial release series: `aicage` CLI + image build/publish tooling via submodules.

## [Planned]

### [0.8.x]

- Custom local base images and full build pipeline for agents and extensions on top.
