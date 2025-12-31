# aicage: Ideas for future enhancements

## Enable and document custom images by user

I can build and use locally but need to use the same image-names. It would be nice if we could (by config?) add any 
custom image to `aicage`. I'm not yet sure how, possibly by name (regex?), possibly by setting an image registry and 
filtering there based on image metadata (see other idea).

### Let user define extra installed packages

We could let user define a list (or installation script) for his chosen `aicage` image. Those packages would then be 
locally added to a local image and that image used by `aicage`.

Extra nice and rather cheap would then be: Whenever aicage pulls a new image, the custom packages are auto-added and a 
new local image is built.

This might also be helpful or fulfill most custom image use-cases.
