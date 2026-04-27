from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from utils.paths import croc_runtime_dir, tools_dir


class SevenZipServiceError(RuntimeError):
    pass


@dataclass(slots=True)
class PreparedArchive:
    archive_path: Path
    archive_name: str
    cleanup_root: Path


class SevenZipService:
    DOWNLOAD_PAGE_URL = "https://www.7-zip.org/download.html"
    OFFICIAL_DOWNLOAD_PREFIX = "https://github.com/ip7z/7zip/releases/download/"
    MANAGED_BINARY_NAME = "7zr.exe"

    def __init__(self, log_service):
        self.log = log_service.get_logger("sevenzip")

    def create_send_archive(self, source_paths: list[str], compression_level: int = 9) -> PreparedArchive:
        if not source_paths:
            raise SevenZipServiceError("No files or folders were selected for compression.")

        sources = [Path(path).expanduser().resolve() for path in source_paths]
        missing = [str(path) for path in sources if not path.exists()]
        if missing:
            raise SevenZipServiceError(f"Cannot compress missing path(s): {', '.join(missing)}")

        session_root = self._create_session_root("send")
        try:
            seven_zip = self._resolve_cli(session_root)
            archive_name = self._build_archive_name(sources)
            archive_path = session_root / archive_name
            work_dir, members = self._build_archive_members(sources)
            cmd = [str(seven_zip), "a", "-t7z", f"-mx={self._normalize_compression_level(compression_level)}", str(archive_path), *members]
            self._run(cmd, cwd=work_dir, action="compress")
            if not archive_path.exists():
                raise SevenZipServiceError("7-Zip finished without creating the archive.")
            return PreparedArchive(archive_path=archive_path, archive_name=archive_name, cleanup_root=session_root)
        except Exception:
            self.cleanup_path(session_root)
            raise

    def extract_archive(self, archive_path: Path, destination: Path) -> None:
        if not archive_path.exists():
            raise SevenZipServiceError(f"Compressed file was not found for extraction: {archive_path}")

        destination.mkdir(parents=True, exist_ok=True)
        session_root = self._create_session_root("receive")
        try:
            seven_zip = self._resolve_cli(session_root)
            cmd = [str(seven_zip), "x", str(archive_path), f"-o{destination}", "-y"]
            self._run(cmd, cwd=destination, action="extract")
        finally:
            self.cleanup_path(session_root)

    def install_cli(self) -> Path:
        target = self.managed_binary_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = self._request_bytes(self._discover_cli_url())
        target.write_bytes(payload)
        self.log.info("Installed managed 7-Zip CLI at %s", target)
        return target

    def uninstall_cli(self) -> tuple[bool, str]:
        target = self.managed_binary_path()
        if not target.exists():
            return False, f"7-Zip CLI is not installed at {target}"

        try:
            target.unlink()
            if target.parent.exists() and not any(target.parent.iterdir()):
                target.parent.rmdir()
        except OSError as exc:
            return False, f"Failed to uninstall 7-Zip CLI: {exc}"

        self.log.info("Uninstalled managed 7-Zip CLI from %s", target)
        return True, f"Removed 7-Zip CLI from {target}"

    def status(self) -> dict[str, str | bool]:
        path = self.managed_binary_path()
        installed = path.exists()
        return {
            "installed": installed,
            "path": str(path),
            "mode": "installed" if installed else "temporary",
        }

    def cleanup_prepared_archive(self, prepared: PreparedArchive | None) -> None:
        if not prepared:
            return
        self.cleanup_path(prepared.cleanup_root)

    def cleanup_path(self, path: Path | None) -> None:
        if not path:
            return
        try:
            shutil.rmtree(path, ignore_errors=True)
        except Exception as exc:
            self.log.warning("Failed to clean up temporary 7-Zip path %s: %s", path, exc)

    def _create_session_root(self, prefix: str) -> Path:
        root = croc_runtime_dir()
        created = Path(tempfile.mkdtemp(prefix=f"sevenzip-{prefix}-", dir=str(root)))
        return created

    def managed_binary_path(self) -> Path:
        return tools_dir() / "7zip" / self.MANAGED_BINARY_NAME

    def _download_cli(self, session_root: Path) -> Path:
        download_url = self._discover_cli_url()
        target = session_root / "7zr.exe"
        self.log.info("Downloading temporary 7-Zip CLI from %s", download_url)
        payload = self._request_bytes(download_url)
        target.write_bytes(payload)
        return target

    def _resolve_cli(self, session_root: Path) -> Path:
        managed = self.managed_binary_path()
        if managed.exists():
            return managed
        return self._download_cli(session_root)

    def _discover_cli_url(self) -> str:
        html = self._request_text(self.DOWNLOAD_PAGE_URL)
        match = re.search(
            r'href="(?P<url>https://github\.com/ip7z/7zip/releases/download/[^"]+/7zr\.exe)"',
            html,
            re.IGNORECASE,
        )
        if not match:
            raise SevenZipServiceError("Could not find the official temporary 7-Zip CLI download URL.")
        download_url = match.group("url")
        if not download_url.startswith(self.OFFICIAL_DOWNLOAD_PREFIX):
            raise SevenZipServiceError("Refusing to download 7-Zip CLI from a non-official URL.")
        return download_url

    def _request_text(self, url: str) -> str:
        req = Request(url, headers={"User-Agent": "CrocDrop/1.0"})
        try:
            with urlopen(req, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise SevenZipServiceError(f"Failed to contact the official 7-Zip download page: {exc}") from exc

    def _request_bytes(self, url: str) -> bytes:
        req = Request(url, headers={"User-Agent": "CrocDrop/1.0"})
        try:
            with urlopen(req, timeout=60) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise SevenZipServiceError(f"Failed to download the temporary 7-Zip CLI: {exc}") from exc

    def _build_archive_name(self, sources: list[Path]) -> str:
        if len(sources) == 1:
            return f"{sources[0].name}.7z"
        stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        return f"crocdrop-bundle-{stamp}.7z"

    def _build_archive_members(self, sources: list[Path]) -> tuple[Path, list[str]]:
        if len(sources) == 1:
            source = sources[0]
            return source.parent, [source.name]

        try:
            common = Path(os.path.commonpath([str(path) for path in sources]))
        except ValueError as exc:
            raise SevenZipServiceError(
                "Compressed send currently requires all selected paths to be on the same drive."
            ) from exc

        work_dir = common if common.is_dir() else common.parent
        members = [os.path.relpath(str(path), str(work_dir)) for path in sources]
        return work_dir, members

    def _run(self, cmd: list[str], cwd: Path, action: str) -> None:
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except OSError as exc:
            raise SevenZipServiceError(f"Failed to start temporary 7-Zip CLI for {action}: {exc}") from exc

        if proc.returncode == 0:
            return

        detail = (proc.stderr or proc.stdout or "").strip()
        if detail:
            detail = detail.splitlines()[-1]
        else:
            detail = f"exit code {proc.returncode}"
        raise SevenZipServiceError(f"7-Zip could not {action} the transfer payload: {detail}")

    @staticmethod
    def _normalize_compression_level(level: int) -> int:
        return max(0, min(9, int(level)))
