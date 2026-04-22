from __future__ import annotations

from pathlib import Path

from platformdirs import PlatformDirs

APP_NAME = "CrocDrop"
APP_AUTHOR = "CrocDrop"


def get_dirs() -> PlatformDirs:
    return PlatformDirs(APP_NAME, APP_AUTHOR, roaming=True)


def ensure_path(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def app_data_dir() -> Path:
    return ensure_path(Path(get_dirs().user_data_dir))


def app_cache_dir() -> Path:
    return ensure_path(Path(get_dirs().user_cache_dir))


def app_log_dir() -> Path:
    return ensure_path(Path(get_dirs().user_log_dir))


def tools_dir() -> Path:
    return ensure_path(app_data_dir() / "tools")


def state_dir() -> Path:
    return ensure_path(app_data_dir() / "state")
