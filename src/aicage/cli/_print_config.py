from pathlib import Path

from aicage._logging import get_logger
from aicage.config import SettingsStore


def print_project_config() -> None:
    logger = get_logger()
    store = SettingsStore()
    project_path = Path.cwd().resolve()
    config_path = store.project_config_path(project_path)
    logger.info("Printing project config at %s", config_path)
    print("Project config path:")
    print(config_path)
    print()
    print("Project config content:")
    if config_path.exists():
        contents = config_path.read_text(encoding="utf-8").rstrip()
        if contents:
            print(contents)
        else:
            print("(empty)")
    else:
        print("(missing)")
