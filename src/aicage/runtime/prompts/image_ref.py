from ._tty import ensure_tty_for_prompt


def prompt_for_image_ref(default_ref: str) -> str:
    ensure_tty_for_prompt()
    response = input(f"Enter image name:tag [{default_ref}]: ").strip()
    if not response:
        return default_ref
    if ":" not in response:
        return f"aicage-extended:{response}"
    return response
