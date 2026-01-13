# aicage: Ideas for future enhancements

## Validate image signature and provenance

The images produced by `aicage-image` and `aicage-image-base` are signed and have provenance.

We should add logic to verify we are using signed/provenanced images in:

- `aicage-image`: When we use the base-images in CI pipelines from `aicage-image-base`
- `aicage`: when we pull/use final-images produced by `aicage-image`

## Support symlinks in project-folder

If the project-folder contains symlinks to outside it's structure, then those fail in containers.  
To fix this we could collect such symlinks and propose to mount the targets to the containers.

## Support git submodules

Detect when in submodule and suggest to mount the parent repo.  
Reason: git in container fails without parent repo

## Replace remove `aicage --aicage-entrypoint`

This overrides the same parameter to docker run. And with `docker run --entrypoint` user can do the same. We have it
only for debugging anyway.

## Put agent command in agent.yml

Right now with `agents/<AGENT>`, `AGENT` is the command of the agent. This was done for simplicity in early stages of
development. But by now this:
- prevents having an agent with a second config (also locally)
- is ugly
- the code is mature enough by now to change this

## Avoid `chmod` on users shell scripts

We use `chmod` if the users config has non-executable `*.sh` scripts. But we might avoid changing
those by `chmod` by running them as arguments to `sh` (or `bash` if available on host).

## Prevent starting in HOME

Prevent starting in HOME (error when creating symlink in entrypoint) or `/` or similar. Or warn user at least.  
But accidentally calling `aicage` and forgetting to cd to a project folder happens frequently to me.

## Plugins idea

Aicage could have plugins in the style: Copy of RunConfig is handed to plugin, which returns RunConfig or defined parts
of it.  
The current features:
- ask user about mounting .gitconfig and .gnupg
- handle --docker parameter
could potentially be moved to such plugins.

Maybe we could even allow user added custom plugins.

## Shellcheck version.sh

The `version.sh` scripts for agents are run on the users system or as fallback in the Alpine `version-check` util-image
(from submodule `aicage-image-util`). Those scripts should be strictly POSIX compliant and we should verify that with
`shellcheck` in a GitHub release pipeline for `aicage-image` (where those scripts are defined).

## Replace configi.yml with Python constants

As constants can be imported and must not be passes around.
