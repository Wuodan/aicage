# Aicage custom base-image: `php` (Debian)

This custom base-image is based on the official `php:latest` image.

The [Dockerfile](Dockerfile) can be used as a template for a full installation equal to the base-images provided by
`aicage`.  
For a minimal Dockerfile, see [../debian-mirror](../debian-mirror).

About:

- Image homepage: [https://hub.docker.com/_/php/](https://hub.docker.com/_/php/)

> Developer notes:  
> One reason for having this in `aicage` is to test the lookup of image digests which is different on docker.io (https://hub.docker.com)
> compare to ghcr.io (https://github.com/)
