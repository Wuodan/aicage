from ...constants import DEFAULT_EXTENDED_IMAGE_NAME
from ._tty import ensure_tty_for_prompt


def prompt_for_image_ref(default_ref: str) -> str:
    ensure_tty_for_prompt()
    response = input(f"Enter image name:tag [{default_ref}]: ").strip()
    if not response:
        return default_ref
    if ":" not in response:
        return f"{DEFAULT_EXTENDED_IMAGE_NAME}:{response}"
    return response
