from pathlib import Path

from aicage._logging import get_logger
from aicage.config.config_store import SettingsStore


def remove_project_config() -> None:
    logger = get_logger()
    store = SettingsStore()
    project_path = Path.cwd().resolve()
    config_path = store.project_config_path(project_path)
    logger.info("Removing project config at %s", config_path)
    if config_path.exists():
        config_path.unlink()
        print("Project config removed:")
        print(config_path)
    else:
        print("Project config not found:")
        print(config_path)
