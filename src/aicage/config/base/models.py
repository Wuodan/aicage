from dataclasses import dataclass
from pathlib import Path

BUILD_LOCAL_KEY: str = "build_local"


@dataclass(frozen=True)
class BaseMetadata:
    from_image: str
    base_image_distro: str
    base_image_description: str
    build_local: bool
    local_definition_dir: Path
