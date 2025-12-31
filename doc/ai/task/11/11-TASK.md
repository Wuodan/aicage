# Task 11: Get image:tag from `images-metadata.yaml`

I changed `config/images-metadata.yaml` (produced by submodule `aicage-image`, already changed there) to now
have a map in `valid_bases`. Keys are the valid base-image aliases and values are the docker image:tag to it.

We can now use this in `src/aicage/registry/image_selection.py` (and possibly other places) where we no longer have to 
cobble together the image:tag as in method `select_agent_image`:
```python
    image_tag = f"{agent}-{base}"
    image_ref = f"{context.image_repository_ref()}:{image_tag}"
```
but instead can pull the value from the map directly.

Also go through the documentation and see if it needs updating for this change too.

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