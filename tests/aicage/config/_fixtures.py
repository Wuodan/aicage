def join_yaml(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def extended_image_definition(
    agent: str,
    base: str,
    extensions: list[str],
    image_ref: str,
    extra_lines: list[str] | None = None,
) -> str:
    lines = [
        f"agent: {agent}",
        f"base: {base}",
    ]
    if extensions:
        lines.append("extensions:")
        lines.extend([f"  - {extension}" for extension in extensions])
    else:
        lines.append("extensions: []")
    lines.append(f"image_ref: {image_ref}")
    if extra_lines:
        lines.extend(extra_lines)
    return join_yaml(lines)
