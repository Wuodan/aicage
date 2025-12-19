# Task 04: Image registry migration to GitHub 

I moved the registries for the docker images produced by git submodules:
- aicage-image-base
- aicage-image
from `docker.io` to `ghcr.io`.

This brings a few changes:
- Images must now be specified with the registry:
  - Before: aicage/aicage:some-tag
  - Now: ghcr.io/aicage/aicage:some-tag
- The API of ghcr.io to query available images is different.

## Status of the migration

I added 3 new fields to:
- src/aicage/config/config.yaml
- src/aicage/config/global_config.py
- for the registry and for urls needed to query the GitHub API.

## Your tasks

### Images must now be specified with the registry

Make sure that new way to specify images is used throughout this project.

### The API of ghcr.io to query available images is different

The current approach to read available images in `src/aicage/runtime/base_image.py` is for `docker.io` and no longer 
valid.

As the submodule `aicage-image` does something similar (queries base images), look at `scripts/common.sh` in the 
submodule to see how it's done there. Use the same technique but of course in python in this project.

#### Make querying images a package

To me `src/aicage/runtime/base_image.py` is quite separate from the rest. And with added complexity for the token I want
this moved into a submodule of its own.

## General coding guidelines

I come from Java and greatly value `Clean Code` and `Separation/Encapsulation`.  
Meaning:
- I want to see datatypes explicitly.
- I want clean capsulation with private/public visibility. Default is always private and visibility is only increased 
  when needed - for files, classes, methods, variables ... everywhere. If this is violated I stop my review immediately
  so get this right.

## Task Workflow

Don't forget to read AGENTS.md and always use the existing venv.

You shall follow this order:
1. Read documentation and code to understand the task. 
2. Aks me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters as in the pipeline `.github/workflows/publish.yml`
6. Present me the change for review
7. Interactively react to my review feedback