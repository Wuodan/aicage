# Task 13: Version-check builder image (initial)

## Goal

Implement the first minimal "version-check" builder image only (no build image yet). Keep it KISS.

## Requirements

- Single Docker image for running `agent version.sh` scripts.
- Must work with all `agents/*/version.sh` scripts in submodule `aicage-image`.
- Base image: `ubuntu:latest` or a Node image based on Ubuntu (prefer simplicity and arm64 support).
- Include: `bash`, `curl`, `git`, `tar`, `python3 + pip`, `nodejs + npm`.
- Default command should be `/bin/sh` (or no entrypoint if simpler).
- Keep Dockerfile small and readable; no extra layers or features.
- Provide a brief README or DEVELOPMENT note if needed (keep user docs clean).
- Add CI/publishing for the image via GitHub Actions to publish to `aicage/aicage-image-util`.
- Do not commit unless explicitly asked.

## Deliverables

- `Dockerfile` (and any minimal support files).
- Short notes on how to build locally (if not obvious).
- No extra abstractions or helper scripts unless requested.

## Constraints

- Follow repo AGENTS/DEVELOPMENT instructions.
- Avoid optional configs, extra flags, or unused settings.

## Workflow

If anything is unclear, ask before coding.
