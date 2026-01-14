# Custom base images

Custom base images let you build and update base layers locally. They live under
`~/.aicage-custom/base-images/` and show up in base selection alongside built-in bases.

If a custom base name matches a packaged base name, the custom base overrides it.

## Directory layout

Each custom base is a directory under `~/.aicage-custom/base-images/`:

```text
~/.aicage-custom/base-images/<BASE>/
├─ base.yml (or base.yaml)
└─ Dockerfile
```

The `<BASE>` directory name is the base id used for selection.

## base.yml

`base.yml` (or `base.yaml`) defines metadata and must contain these keys:

```yaml
from_image: debian:bookworm
base_image_distro: Debian
base_image_description: "Debian base image"
```

Notes:

- `from_image` is used both as the Docker build arg and for update checks.
- `base_image_distro` is used for agent filtering (`base_distro_exclude`).
- No additional keys are supported.

## Dockerfile

The Dockerfile builds the custom base image. The build arg `FROM_IMAGE` is provided:

```Dockerfile
ARG FROM_IMAGE
FROM ${FROM_IMAGE} AS from_image
```

Keep the build non-interactive and deterministic. If you need extra tools, install them here.

## Build and update flow

Custom bases always build locally. The base is rebuilt when any of the following are true:

- The local base image does not exist.
- The `from_image` value changes.
- The remote digest of `from_image` changes.

Agent images built on top of a custom base follow the usual local build rules.

Build logs are stored under `~/.aicage/logs/base-image/build/`.

## Example

Sample custom base files live in `doc/sample/custom/base-images/`:

```text
doc/sample/custom/base-images/php/
doc/sample/custom/base-images/debian-mirror/
```

Copy one to `~/.aicage-custom/base-images/<BASE>/` and select it on first run:

```bash
aicage codex
```
