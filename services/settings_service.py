from __future__ import annotations

from pathlib import Path

from models.settings import AppSettings
from storage.json_store import JsonStore
from utils.paths import state_dir


class SettingsService:
    def __init__(self):
        self.store = JsonStore(state_dir() / "settings.json")
        self._settings = AppSettings()

    def load(self) -> AppSettings:
        payload = self.store.load(default={})
        self._settings = AppSettings.from_dict(payload) if payload else AppSettings()
        return self._settings

    def save(self, settings: AppSettings | None = None) -> AppSettings:
        if settings is not None:
            self._settings = settings
        self.store.save(self._settings.to_dict())
        return self._settings

    def get(self) -> AppSettings:
        return self._settings

    def set_manual_binary_path(self, path: Path) -> None:
        self._settings.croc_binary_path = str(path)
        self.save(self._settings)

    def add_profile(self, name: str) -> str:
        profile = name.strip()
        if not profile:
            return ""
        if profile not in self._settings.profiles:
            self._settings.profiles.append(profile)
        self._settings.current_profile = profile
        self.save(self._settings)
        return profile

    def set_current_profile(self, name: str) -> None:
        profile = name.strip()
        if profile and profile in self._settings.profiles:
            self._settings.current_profile = profile
            self.save(self._settings)

    def use_guest_mode(self) -> None:
        self._settings.current_profile = ""
        self.save(self._settings)

    def remove_profile(self, name: str) -> bool:
        profile = name.strip()
        if not profile:
            return False
        if profile in self._settings.profiles:
            self._settings.profiles.remove(profile)
            if self._settings.current_profile == profile:
                self._settings.current_profile = ""
            self.save(self._settings)
            return True
        return False
