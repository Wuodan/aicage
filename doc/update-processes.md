# Update processes overview

This document summarizes what gets built or updated, when it is updated, and where it runs. It
includes current and planned behavior.

## Update triggers matrix

| Item                           | Source                          | Trigger                        | Runs        |
|--------------------------------|---------------------------------|--------------------------------|-------------|
| Base image (aicage-image-base) | Base config or root image       | Weekly schedule + manual       | CI          |
| Final image (prebuilt)         | Agent version or base image     | CI build+publish, runtime pull | CI + client |
| Final image (build_local=true) | Agent version or base image     | Local rebuild on change        | Client      |
| Local custom agent             | Agent version or base image     | Local rebuild on change        | Client      |
| Local extension                | Extension or base/final changes | Local rebuild on change        | Client      |
| Local custom base (planned)    | Custom base or root image       | Local rebuild on change        | Client      |

## Artifact responsibilities

<!-- pyml disable line-length -->
| Artifact                          | Built from                                   | Stored             | Update signal                     |
|-----------------------------------|----------------------------------------------|--------------------|-----------------------------------|
| Base image                        | aicage-image-base `bases/BASE`               | Registry (ghcr.io) | Weekly schedule + manual          |
| Final image (prebuilt)            | base image + `agents/AGENT`                  | Registry (ghcr.io) | Agent version + base updates      |
| Local final image (build_local)   | `agent-build/AGENT` on base image            | Local Docker       | Agent version + base digest       |
| Local final image (custom agent)  | base image + `~/.aicage-custom/agents/AGENT` | Local Docker       | Agent version + base digest       |
| Local extended image              | final image + extensions                     | Local Docker       | Extension changes + base/final    |
| Local custom base image (planned) | custom base definition                       | Local Docker       | Definition changes + root updates |
<!-- pyml enable line-length -->

## Notes

- "Agent version" refers to running the agent's version.sh (builder image first, host fallback).
- "Base image digest change" refers to the registry digest for the base image tag changing; a
  local pull updates the base before rebuilding the local final image.
