from dataclasses import dataclass


@dataclass(frozen=True)
class ImageSelection:
    image_ref: str
    base: str
    extensions: list[str]
    base_image_ref: str
