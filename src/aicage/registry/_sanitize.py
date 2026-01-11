from __future__ import annotations


def sanitize(value: str) -> str:
    return value.replace("/", "_").replace(":", "_")
