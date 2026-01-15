def sanitize(value: str) -> str:
    return value.replace("/", "_").replace(":", "_")
