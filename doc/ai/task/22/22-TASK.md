# Task 22: Complete rewrite of user documentation

## Folder/repo structure

- In folder `aicage` is the main repository - the CLI part of `aicage`.  
- `aicage.wiki` contains the new repo for the documentation. It's empty now.

all other folders in the current root dir are also parts of `aicage`. Possibly relevant for documentation are:

- `aicage-image-base`: Build the base images provided by `aicage`: Basically a Linux distro, plus tons of tools for
  development, plus the `entrypoint.sh` for `aicage`
- `aicage-image`: Builds agent-images provided by `aicage: They are built by adding an` agent` to a base-image from
  `aicage-image-base`. Some agents result in local building of images (non-redistributable agents due to license not
  allowing it)
- `aicage-custom-samples`: Holds ready to use samples for customization of images used by `aicage`:
  - extensions: Additional tools to be added to agent-images by building a new image on users PC
  - agents: User defined agents similar to the ones in `aicage-image`. This results in local building of an image on top
    of a base-image.
  - base-images: User defined base-images to be built on users PC

### Existing documentation to take into account

Scan all repos for '*.md' files to collect existing information. For further information you must read the code or ask
me questions.

> Attention: Documents in `aicage/doc/ai` (except this one) are from historic tasks - the information in them might be
> outdated!

## Target audience

The intended audience is "Users of aicage". This is a CLI development tool, so the users should be tech savy and
somehow familiar with working in a terminal/shell.  
And if they are Linux/backend developers like me then they like clear, brief documentation with a "need to know" focus
first and optionally deep dive later or in another document.  
And flowery advertisement language is usually a bad choice for this target group.

Easy to understand examples are often a good way of showing how things can be done. This is actually one intention
behind `aicage-custom-samples` - "copy that repo to `~/.aicage-custom`" plus explaining documentation is much easier
than trying to understand text which only describes how.

## What goes where

### README.md of `aicage` repo

It's already solid imho but lacks:

- Something like "you can easily add your own agent, see ..." with reference to instructions for customization with
  custom "agents"
- Mention of "images can easily be changed/configured, see ..." with reference to instructions for customization with
  custom "extensions" and "base-images"
- Mentioning that images are kept up to date by `aicage` also for customized images

### New wiki repo

Here I want a strict separation between "user" and "aicage developer" information!  
Don't throw away existing documentation for "aicage developers" but rather drop it in that repo somewhere apart from
"user" documentation.

For users, I want:

- A bit more information about what `aicage` does covering at least:
  - How agent-in-docker works (images with lots of tools, agent installed, key folders mounted from host to container)
  - 3 levels of images (extensions being only custom, the other 2 both built-in and custom), mention that for some
    builtin agents images must be built locally due to license restrictions.
  - when images are updated (see `aicage/doc/update-processes.md`)
  - instructions how images caan be customized.

You can decide yourself how you split it into sections/pages for the first draft, but I favor well-structured small
pages and definitely expect a menu for page navigation.

## Task Workflow

- Don't forget to read AGENTS.md and `doc/python-test-structure-guidelines.md` and respect those rules.
- Always use the existing venv.

You shall follow this order:

1. Read documentation and code to understand the task.
2. Ask me questions if something is not clear to you
3. Present me with an implementation solution - this needs my approval
4. Implement the change autonomously including a loop of running-tests, fixing bugs, running tests
5. Run linters, use `scripts/lint.sh` with active venv
6. Present me the change for review
7. Interactively react to my review feedback
8. Do not commit any changes unless explicitly instructed by the user.
