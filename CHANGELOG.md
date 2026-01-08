# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### [0.7.x]

- Custom local extensions that build new final images on top of existing final images.

### [0.8.x]

- Custom local base images and full build pipeline for agents and extensions on top.
