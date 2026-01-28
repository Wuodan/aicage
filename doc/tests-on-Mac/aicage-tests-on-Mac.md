# aicage: tests on MacOS

---

## Preparation

### Prerequisites

Make sure these tools are installed:

- docker
- Python 3.10+ and `pipx`

### Installation

Run this to install `aicage`:

```shell
pipx install aicage
```

---

## Tests

Create a new blank folder in `/tmp/aicage-test` and open a terminal in it.  
For the rest of this document we call that the _project folder_.

### Test 1: Builtin agent works (docker pull and run)

In the project folder, run this:

```shell
aicage codex
```

Then select base "Ubuntu" and answer other questions with yes (or press Enter).

#### Expectation

1. `aicage` pulls a docker image for `cosign`.
2. `aicage` pulls the docker image `ghcr.io/aicage/aicage:codex-ubuntu`.
3. You should see the start screen of `codex` (it probably asks for authentication).

Press Ctrl-C repeatedly to exit.

---

### Test 2: Builtin non-redistributable agent works (docker buildx)

In the project folder, run this:

```shell
aicage claude
```

Then select base "Ubuntu" and answer other questions with yes (or press Enter).

#### Expectation

1. `aicage` should locally build the image `aicage:claude-ubuntu`.
2. You should see the start screen of `claude`.

Press Ctrl-C repeatedly to exit.

---

### Test 3: Docker in container

In the project folder, run this:

```shell
aicage --docker -e AICAGE_ENTRYPOINT_CMD=bash -- codex -lc 'docker run --rm hello-world'
```

Select base "Ubuntu" and answer other questions with yes (or press Enter).

#### Expectation

1. The hello-world docker image should be started from inside the container.
2. You should see 'Hello from Docker!'

> This test might fail as docker on Mac is different from Windows and Linux.  
> If it fails, note the error and continue.

---

### Test 4: Custom extensions work (reading from `~/.aicage-custom` works)

Run:

```shell
git clone https://github.com/aicage/aicage-custom-samples.git ~/.aicage-custom
```

Then, in the project folder, run this:

```shell
aicage gemini
```

Select base "Ubuntu" and when asked to select extensions pick `marker`.  
Confirm defaults for other choices.

> If you accidentally did not select an extension, print the config with `aicage --config info` and delete the
> `Project config path` file.

#### Expectation

1. `aicage` should locally build the image `aicage:gemini-ubuntu-marker`.
2. You should see the start screen of `gemini`.

Press Ctrl-C repeatedly to exit.

---

### Test Logs: Send logs and local config to me

`aicage` locally stores config and logs in `~/.aicage`. I would like to see that folder.

Run:

```shell
tar -C "$HOME" -czf /tmp/aicage-on-Mac.tar.gz .aicage
```

and send me the file `/tmp/aicage-on-Mac.tar.gz` please.

---

### Clean-up

Delete docker images with:

```shell
docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}}' \
  | grep -Ei '(aicage|cosign)' \
  | awk '{print $2}' \
  | sort -u \
  | xargs -n 1 docker image rm || true
```

Clean up docker build cache with:

```shell
docker buildx prune
```

Clean folders with:

```shell
rm -rf ~/.aicage ~/.aicage-custom
```

Uninstall `aicage` with:

```shell
pipx uninstall aicage
```
