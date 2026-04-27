from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote, unquote

COMPRESSION_NONE = ""
COMPRESSION_7ZIP = "7zip"
_MARKER = "::cd1:"
_FORMAT_7ZIP = "z7"


@dataclass(slots=True)
class ParsedShareCode:
    share_code: str
    connection_code: str
    compression_mode: str = COMPRESSION_NONE
    archive_name: str = ""


def build_share_code(connection_code: str, compression_mode: str = COMPRESSION_NONE, archive_name: str = "") -> str:
    base_code = connection_code.strip()
    if not base_code:
        raise ValueError("Connection code is required.")
    if compression_mode != COMPRESSION_7ZIP:
        return base_code
    archive = archive_name.strip()
    if not archive:
        raise ValueError("Archive name is required for compressed share codes.")
    return f"{base_code}{_MARKER}{_FORMAT_7ZIP}:{quote(archive, safe='')}"


def parse_share_code(code: str) -> ParsedShareCode:
    share_code = code.strip()
    if not share_code:
        return ParsedShareCode(share_code="", connection_code="")
    if _MARKER not in share_code:
        return ParsedShareCode(share_code=share_code, connection_code=share_code)

    connection_code, payload = share_code.split(_MARKER, 1)
    connection_code = connection_code.strip()
    if not connection_code:
        return ParsedShareCode(share_code=share_code, connection_code=share_code)

    format_token, _, raw_archive_name = payload.partition(":")
    if format_token.lower() != _FORMAT_7ZIP:
        return ParsedShareCode(share_code=share_code, connection_code=connection_code)

    archive_name = unquote(raw_archive_name).strip()
    return ParsedShareCode(
        share_code=share_code,
        connection_code=connection_code,
        compression_mode=COMPRESSION_7ZIP,
        archive_name=archive_name,
    )
