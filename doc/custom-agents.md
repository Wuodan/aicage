# Custom agents

Custom agents let you define local agent installs that build into local Docker images. They live under
`~/.aicage-custom/agents/` and behave like locally built built-in agents.

If a custom agent name matches a packaged agent name, the custom agent overrides it.

## Directory layout

Each custom agent is a directory under `~/.aicage-custom/agents/`:

```text
~/.aicage-custom/agents/<AGENT>/
├─ agent.yaml (or agent.yml)
├─ install.sh
└─ version.sh
```

The `<AGENT>` directory name is the agent id used on the CLI, for example: `aicage <AGENT> ...`.

## agent.yaml

`agent.yaml` (or `agent.yml`) defines metadata and must contain these keys:

```yaml
agent_path: ~/.forge
agent_full_name: Forge Code
agent_homepage: https://forgecode.dev/
```

Optional keys:

```yaml
base_exclude:
  - alpine
base_distro_exclude:
  - debian
```

Notes:

- `agent_path` is a host path used for agent config. Inside the container it is available at the same path.
- `base_exclude` excludes named base images. `base_distro_exclude` excludes bases by their distro name.
- No additional keys are supported.

## install.sh

`install.sh` runs during the Docker build of the local image. It must be executable and non-interactive.

Keep the script deterministic and fail fast on errors. Install any additional dependencies your agent needs.

## version.sh

`version.sh` returns the agent version that drives rebuild decisions. It must output a non-empty version string.

## Build and update flow

Custom agents always build locally.

The image is rebuilt when any of the following are true:

- The local image does not exist.
- The `version.sh` output changes.
- The remote base image has changed.

Build logs are stored under `~/.aicage/logs/build/`.

## Example

Sample custom agent files live in `doc/sample/custom/agents/forge/`:

```text
doc/sample/custom/agents/forge/
├─ agent.yaml
├─ install.sh
└─ version.sh
```

Copy that directory to `~/.aicage-custom/agents/forge/` and run:

```bash
aicage forge
```
