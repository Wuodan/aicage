from __future__ import annotations

import hashlib
from typing import Protocol


class HashWriter(Protocol):
    def update(self, data: bytes, /) -> None:
        ...

    def hexdigest(self) -> str:
        ...


def new_hasher() -> HashWriter:
    return hashlib.sha256()
