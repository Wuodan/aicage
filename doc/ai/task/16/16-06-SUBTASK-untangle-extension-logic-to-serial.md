# Subtask 16-06: Untangle logic for extensions

## Duplicated logic in `should_build` and `should_build_extended`

`should_build_extended` does not use `should_build`. And also does not perform a version check
of agent. `extensions` generally come on top of previous layers and you copying code here makes
it hard to manage.

The version check of agent is only relevant for locally built agents (both builtin-local and
custom-local). To me this looks like locally built images for a such an agent plus an added
extension will not perform the agent-version check and thus might not update when that version
changes.

To be analyzed. But at the very least this looks like code copied not smartly written and then
re-used.

Method `_base_layer_missing` for example seems to be exactly duplicated.

### After further analysis

Further up the chain `ensure_extended_image` uses `ensure_local_image` so the code seems reused
(but still with duplications). And even further up in `entrypoint.py` the different paths are taken
by:

```python
if run_config.extensions:
    ensure_extended_image(run_config)
elif agent_metadata.local_definition_dir is None:
    pull_image(run_config)
else:
    ensure_local_image(run_config)
```

But entrypoint.py is the very top layer. This if-elif-else decision is basically: "From given
config make sure the image is local and up-to-date" or even shorter "from config setup image".
I think this if-elif-if for different paths to a local up-to-date image is to high up.

Plus I think those paths are not neatly woven, at least when the extensions came into the code. Or
maybe the real problem is that they are woven. In simple thoughts it might be possible to do
everything up to "have local up-to-date image with agent" (no matter if built locally or not, with
the given standard image-name/-tag). And then, if extensions are in config, do a digest compare,
meaning: The agent-image is now up-to-date, no matter if unchanged locally, newly pulled or newly
built locally. All we have to check to decide if the image with extensions should be built is:

- image with extensions locally not present: -> build using local agent-image
- image with extensions locally present: check if last layer of local agent-image is in image
  with extensions. if not -> build using local agent-image

Thus for images with extensions we would not check locally if the base-image-digest or the
agent-version has changed. By this chain of image checks and setup those changes were already done.

## Subtask Guidelines and Workflow

Don't forget to read `AGENTS.md` and `doc/python-test-structure-guidelines.md`; always use the
existing venv.

You shall follow this order:

1. Read documentation and code to understand the task.
2. Ask me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running
   tests
5. Run linters with `scripts/lint.sh`
6. Present me the change for review
7. Interactively react to my review feedback
8. Do not commit any changes unless explicitly instructed by the user.
