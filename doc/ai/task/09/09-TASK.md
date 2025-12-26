# Task 08: Use Release Images Metadata

The submodule `aicage-image` now produces a metadata file per release. See in the submodule:
- .github/workflows/release.yml 
- doc/images-metadata.md 
- doc/validation/images-metadata.schema.json

Also see here in this repo a downloaded example (latest release):
- doc/ai/task/09/images-metadata.yaml

I want to use this Release Images Metadata to replace the clumsy online lookup for available image:tags that we now use.

The Release Images Metadata contains the same info (currently we read only base-aliases per tool) and can be used for 
more (base description, etc.).

## Subtask 1: Metadata file mapping and downloading

1. Create clean dataclasses for that metadata file
2. Then a download and mapping process for that file from latest release of `aicage-image`
3. Cache that file locally in `~/.aicage/`. Try to download each time `aicage` starts, if download fails use cache else
   use downloaded and overwrite cache.

This has to be completed, approved, reviewed and pushed before next subtask.

## Subtask 2: Use metadata info to replace current logic

Replace:
- image lookup
- image label reading

This has to be completed, approved, reviewed and pushed before next subtask.

## Subtask 3: Use metadata info to add features

For now:
- Use base description in user-dialog to select a base.

This has to be completed, approved, reviewed and pushed before next subtask.

## Per Sub-Task Workflow

Don't forget to read AGENTS.md and always use the existing venv.

You shall follow this order:
1. Read documentation and code to understand the task. 
2. Aks me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters as in the pipeline `.github/workflows/publish.yml`
6. Present me the change for review
7. Interactively react to my review feedback

Visibility note: apply the "defining scope" rule from AGENTS.md (tests are exempt when deciding "outside").
