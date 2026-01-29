# aicage: Ideas for future enhancements

## Support symlinks in project-folder

If the project-folder contains symlinks to outside it's structure, then those fail in containers.  
To fix this we could collect such symlinks and propose to mount the targets to the containers.

## Put agent command in agent.yml

Right now with `agents/<AGENT>`, `AGENT` is the command of the agent. This was done for simplicity in early stages of
development. But by now this:

- prevents having an agent with a second config (also locally)
- is ugly
- the code is mature enough by now to change this

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
(from repo `aicage-image-util`). Those scripts should be strictly POSIX compliant and we should verify that with
`shellcheck` in a GitHub release pipeline for `aicage-image` (where those scripts are defined).

## Tune locking of ~/.aicage

The implementation is from an earlier state where we had less files. New files are not locked.

## Fix config file locking

It was disabled due to problems on Windows, see commit with message:  
"Disable locking of config files - needs to use the lock-connection to files on Windows"
