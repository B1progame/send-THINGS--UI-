from __future__ import annotations

from pathlib import Path
import shutil

from platformdirs import PlatformDirs

APP_NAME = "CrocDrop"
APP_AUTHOR = False


def get_dirs() -> PlatformDirs:
    return PlatformDirs(APP_NAME, APP_AUTHOR, roaming=True)


def legacy_dirs() -> PlatformDirs:
    # Legacy location used appauthor="CrocDrop", which produced ...\CrocDrop\CrocDrop\...
    return PlatformDirs(APP_NAME, "CrocDrop", roaming=True)


def ensure_path(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def app_data_dir() -> Path:
    new_path = ensure_path(Path(get_dirs().user_data_dir))
    old_path = Path(legacy_dirs().user_data_dir)
    if old_path.exists():
        try:
            # Migrate once if new path appears empty.
            has_any_file = any(new_path.rglob("*"))
            if not has_any_file:
                shutil.copytree(old_path, new_path, dirs_exist_ok=True)
        except Exception:
            pass
    return new_path


def app_cache_dir() -> Path:
    return ensure_path(Path(get_dirs().user_cache_dir))


def app_log_dir() -> Path:
    return ensure_path(Path(get_dirs().user_log_dir))


def tools_dir() -> Path:
    return ensure_path(app_data_dir() / "tools")


def state_dir() -> Path:
    return ensure_path(app_data_dir() / "state")


def croc_runtime_dir() -> Path:
    # Runtime scratch for spawned croc processes (stdin/temp artifacts, etc.).
    return ensure_path(app_cache_dir() / "croc-runtime")
