from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class CrocBinaryInfo:
    path: str = ""
    version: str = ""
    source: str = "not-found"  # bundled/system/downloaded/manual
    release_tag: str = ""
    asset_name: str = ""
    sha256: str = ""
    verified_checksum: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class ParsedTransferEvent:
    level: str = "info"
    message: str = ""
    code_phrase: str = ""
    progress_percent: float | None = None
    speed_text: str = ""
    bytes_done: int | None = None
    bytes_total: int | None = None
    completed: bool = False
    failed: bool = False
