# Review TODOS

## Question `_MIN_REMAINING_FOR_DOCKER_ARGS`

There are arguments to `docker run` which have no value, see this extract from `docker run --help`
```
-d, --detach
--help
--init
-i, --interactive
--no-healthcheck
--oom-kill-disable
--privileged
-P, --publish-all
-q, --quiet
--read-only
--rm
-t, --tty
--sig-proxy
```
not all make sense with `aicage` but some like `--privileged` might be applicable.

## Still user-prompts outside `prompts` package

When searching where `prompt_yes_no` from `src/aicage/runtime/prompts/confirm.py` is used and also searching for 
`\?"` in `src/` - then I still find user-prompts outside package `prompts`.  
One idea behind the `prompts` package is to have all strings with user-questions in one place and not spread throughout
the project.

## Document why/how `__all__` is forbidden and why/how visibility is enforced so hard

This might be unusual for seasoned developers, so please add a Markdown file in `doc` explaining this. We will refactor 
documentation in the future, then this will be used.

## Review documents ignore `.pymarkdown.json`

While the review files in `doc/ai/task/12/07` are temporary and thus this is not really tragic, I still wonder how
the long lines in those review documents did not trigger a violation by the linters. Or maybe my line-length indicator 
in PyCharm needs adjusting.