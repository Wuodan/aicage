# Review TODOS

## Large packages and modules

### image_selection.py and registry package

Both are to large by now and shall be split into a clean package/module structure

### prompts.py

To large, deserves its own package with clean split into modules

## Tests

### tests/aicage/cli/test_cli.py

This file seems to violate `doc/python-test-structure-guidelines.md` meaning: there is no `cli.py` in the `cli` package. There is a `cli/entrypoint.py` but it has no corresponding unit-test file.

### structure of unit-tests vs. source files

The structure does not follow `doc/python-test-structure-guidelines.md`. At first glance you added quite a few python files to `src` but only one unit-test file.

## doc/extensions.md

Show an example of a custom Dockerfile or link to the default builtin Dockerfile so users have an idea on how to write their custom Dockerfiles.

## Keep local docker storage clean

Consider untagging local intermediate image tags once they are no longer used as they live only shortly during the image with extensions build process

## "latest" image tag

Grepping for `latest` in `src` I find it in 3 places as fallback image tag. But `aicage` does not use `latest` tag afaik, so that fallback only leads to an error further down the chain. Please anlyse this, I might be wrong (doubtful but still check quickly).



