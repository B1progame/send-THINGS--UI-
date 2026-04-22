from __future__ import annotations

import platform


def platform_key() -> tuple[str, str]:
    system = platform.system().lower()
    machine = platform.machine().lower()
    return system, machine


def select_windows_asset_token(machine: str) -> str:
    if "arm" in machine:
        return "Windows-ARM64"
    return "Windows-64bit"
