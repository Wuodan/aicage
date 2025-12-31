# Task 12: aicage-builder idea

## Purpose

`aicage-builder` is a dedicated Docker image used for:

- Local image builds for non-redistributable agents, extensions, and custom base images.
- Agent `version.sh` checks when required tools are not available on the host.

The goal is to make local builds reproducible and independent of host tooling.

## Options

### Single builder image

One image that contains both build tooling and agent version check tooling.

Pros:

- Simpler distribution and runtime logic.
- Single cache to manage for local builds.

Cons:

- Larger image.
- Higher maintenance surface for tools that are not always needed.

### Split images

Two images: one for building, one for version checks.

Pros:

- Smaller images per use case.
- Cleaner dependency separation.

Cons:

- More configuration and runtime branching.
- Additional image to maintain and publish.

### No builder image

Rely on host tooling for `docker build` and agent version checks.

Pros:

- No additional image to maintain.
- Less complexity in `aicage` runtime.

Cons:

- Fails on hosts without required tools (e.g., `npm`).
- Harder to ensure reproducibility and consistency.

## Repository layout options

- Separate git repo for `aicage-builder`.
- In-repo under a new top-level folder.
- Two repos if split images are used.

## Expected toolchain

Likely tools needed in builder images:

- Docker CLI / BuildKit support
- Python + pip
- `git`, `curl`, `tar`
- Node.js + `npm` (for version checks)

## Open questions

- Should the builder image be pinned to a specific base distro?
- How to version builder images relative to `aicage` releases?
- Should the builder image be optional, with a host-tooling fallback?
- Should build logs be captured from inside the builder or by `aicage`?
