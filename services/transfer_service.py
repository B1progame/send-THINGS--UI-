from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from models.transfer import TransferRecord
from services.sevenzip_service import PreparedArchive, SevenZipServiceError
from services.transfer_parser import TransferOutputParser
from utils.codegen import generate_code_phrase
from utils.transfer_code import COMPRESSION_7ZIP, build_share_code, parse_share_code


class TransferRuntime(QObject):
    output_line = Signal(str, str)  # transfer_id, line
    state_changed = Signal(str, str)  # transfer_id, status
    code_found = Signal(str, str)  # transfer_id, code
    progress = Signal(str, float)  # transfer_id, percent
    finished = Signal(str, int)  # transfer_id, exit_code

    def __init__(self, transfer_id: str, process: subprocess.Popen, parser: TransferOutputParser):
        super().__init__()
        self.transfer_id = transfer_id
        self.process = process
        self.parser = parser
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        self.state_changed.emit(self.transfer_id, "running")
        self._threads = [
            threading.Thread(target=self._pump, args=(self.process.stdout, "stdout"), daemon=True),
            threading.Thread(target=self._pump, args=(self.process.stderr, "stderr"), daemon=True),
            threading.Thread(target=self._wait, daemon=True),
        ]
        for t in self._threads:
            t.start()

    def _pump(self, stream, stream_name: str) -> None:
        if stream is None:
            return
        for line in iter(stream.readline, ""):
            if not line:
                break
            channel = "system" if stream_name in {"stdout", "stderr"} else stream_name
            text = f"[{channel}] {line.rstrip()}"
            self.output_line.emit(self.transfer_id, text)
            event = self.parser.parse(line)
            if event.code_phrase:
                self.code_found.emit(self.transfer_id, event.code_phrase)
            if event.progress_percent is not None:
                self.progress.emit(self.transfer_id, event.progress_percent)

    def _wait(self) -> None:
        code = self.process.wait()
        self.finished.emit(self.transfer_id, code)

    def cancel(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            self.state_changed.emit(self.transfer_id, "canceled")


@dataclass(slots=True)
class ActiveTransfer:
    record: TransferRecord
    runtime: TransferRuntime
    prepared_archive: PreparedArchive | None = None


@dataclass(slots=True)
class ReservedCode:
    code_phrase: str
    expires_at: datetime


class TransferService(QObject):
    transfer_updated = Signal(str)
    transfer_output = Signal(str, str)
    transfer_finished = Signal(str, str)
    next_code_ready = Signal(str, str, str)  # transfer_id, code, expires_at_iso

    def __init__(self, croc_manager, sevenzip_service, history_service, settings_service, log_service):
        super().__init__()
        self.croc_manager = croc_manager
        self.sevenzip_service = sevenzip_service
        self.history_service = history_service
        self.settings_service = settings_service
        self.log = log_service.get_logger("transfer")
        self.parser = TransferOutputParser()
        self.active: dict[str, ActiveTransfer] = {}
        self._reserved_codes: dict[str, ReservedCode] = {}

    def get_record(self, transfer_id: str) -> TransferRecord | None:
        active = self.active.get(transfer_id)
        if active is not None:
            return active.record
        return self.history_service.get_record(transfer_id)

    def start_send(
        self,
        paths: list[str],
        code_phrase: str = "",
        direction: str = "send",
        compress_7zip: bool = False,
    ) -> TransferRecord:
        active_profile = (self.settings_service.get().current_profile or "guest").strip() or "guest"
        base_code = code_phrase.strip()
        if not base_code:
            reserved = self._take_reserved_code(active_profile)
            base_code = reserved if reserved else generate_code_phrase(active_profile)

        prepared_archive: PreparedArchive | None = None
        effective_paths = list(paths)
        compression_mode = ""
        archive_name = ""
        if compress_7zip:
            compression_level = self.settings_service.get().sevenzip_compression_level
            prepared_archive = self.sevenzip_service.create_send_archive(paths, compression_level=compression_level)
            effective_paths = [str(prepared_archive.archive_path)]
            compression_mode = COMPRESSION_7ZIP
            archive_name = prepared_archive.archive_name

        share_code = build_share_code(base_code, compression_mode=compression_mode, archive_name=archive_name)
        try:
            process = self.croc_manager.launch_send(paths=effective_paths, code_phrase=base_code)
        except Exception:
            self.sevenzip_service.cleanup_prepared_archive(prepared_archive)
            raise

        record = TransferRecord(direction=direction, source_paths=paths, relay=self.settings_service.get().relay_mode)
        record.code_phrase = share_code
        record.connection_code = base_code
        record.compression_mode = compression_mode
        record.archive_name = archive_name
        record.croc_version = self.croc_manager.get_version(Path(self.croc_manager.detect_binary().path))
        self.history_service.add(record)
        self.history_service.mark_started(record)

        next_code, expires_at = self._reserve_next_code(active_profile)
        self.next_code_ready.emit(record.transfer_id, next_code, expires_at.isoformat())

        runtime = TransferRuntime(record.transfer_id, process, self.parser)
        self._wire_runtime(record, runtime)
        self.active[record.transfer_id] = ActiveTransfer(record=record, runtime=runtime, prepared_archive=prepared_archive)
        self.transfer_updated.emit(record.transfer_id)
        runtime.start()
        return record

    def start_receive(self, code_phrase: str, destination: str, overwrite: bool, direction: str = "receive") -> TransferRecord:
        parsed = parse_share_code(code_phrase)
        if not parsed.connection_code:
            raise ValueError("Missing croc code phrase.")

        process = self.croc_manager.launch_receive(
            code_phrase=parsed.connection_code,
            destination=destination,
            overwrite=overwrite,
        )
        record = TransferRecord(
            direction=direction,
            source_paths=[],
            destination_folder=destination,
            code_phrase=parsed.share_code,
            connection_code=parsed.connection_code,
            compression_mode=parsed.compression_mode,
            archive_name=parsed.archive_name,
            relay=self.settings_service.get().relay_mode,
        )
        record.croc_version = self.croc_manager.get_version(Path(self.croc_manager.detect_binary().path))
        self.history_service.add(record)
        self.history_service.mark_started(record)

        runtime = TransferRuntime(record.transfer_id, process, self.parser)
        self._wire_runtime(record, runtime)
        self.active[record.transfer_id] = ActiveTransfer(record=record, runtime=runtime)
        runtime.start()
        return record

    def _wire_runtime(self, record: TransferRecord, runtime: TransferRuntime) -> None:
        runtime.output_line.connect(lambda tid, line: self._on_output(record, tid, line))
        runtime.code_found.connect(lambda tid, code: self._on_code(record, tid, code))
        runtime.progress.connect(lambda tid, pct: self._on_progress(record, tid, pct))
        runtime.finished.connect(lambda tid, exit_code: self._on_finished(record, tid, exit_code))

    def _on_output(self, record: TransferRecord, transfer_id: str, line: str) -> None:
        lowered = line.lower()
        # Keep transfer logs platform-neutral in UI.
        if "(for windows)" in lowered or "(for linux/macos)" in lowered:
            return
        if "croc_secret=" in lowered:
            return

        if len(record.output_excerpt) > 400:
            record.output_excerpt = record.output_excerpt[-400:]
        record.output_excerpt.append(line)
        event = self.parser.parse(line)
        changed = False
        if event.speed_text:
            if record.speed_text != event.speed_text:
                record.speed_text = event.speed_text
                changed = True
        if event.failed and not record.error_message:
            record.error_message = line
            changed = True
        # Avoid saving history on every output line; this is a major UI freeze source on large transfers.
        self.transfer_output.emit(transfer_id, line)
        if changed:
            self.transfer_updated.emit(transfer_id)

    def _on_code(self, record: TransferRecord, transfer_id: str, code: str) -> None:
        if not record.code_phrase:
            record.code_phrase = code
            self.history_service.update(record)
            self.transfer_updated.emit(transfer_id)

    def _on_progress(self, record: TransferRecord, transfer_id: str, pct: float) -> None:
        new_progress = int(pct)
        if record.bytes_done == new_progress:
            return
        record.bytes_done = new_progress
        self.transfer_updated.emit(transfer_id)

    def _on_finished(self, record: TransferRecord, transfer_id: str, exit_code: int) -> None:
        active = self.active.get(transfer_id)
        if transfer_id not in self.active and record.status == "canceled":
            return
        no_files_transferred = any("no files transferred" in line.lower() for line in record.output_excerpt[-80:])
        room_not_ready = any(
            ("room (secure channel) not ready" in line.lower() or "peer disconnected" in line.lower())
            for line in record.output_excerpt[-80:]
        )
        status = "completed" if exit_code == 0 and not no_files_transferred else "failed"
        if no_files_transferred and not record.error_message:
            record.error_message = "No files transferred (likely destination collision or skipped write)."
        if room_not_ready and not record.error_message:
            record.error_message = "Receive session is no longer active. Ask sender for a new code."

        try:
            if status == "completed" and record.direction in {"receive", "selftest-receive"} and record.compression_mode == COMPRESSION_7ZIP:
                try:
                    self._auto_extract_received_archive(record, transfer_id)
                except SevenZipServiceError as exc:
                    status = "failed"
                    record.error_message = str(exc)
                    self._append_system_line(record, transfer_id, f"[system] Auto-extract failed: {exc}")

            if status == "completed":
                self._append_system_line(record, transfer_id, "[system] DONE")
                self._auto_remember_device(record)

            self.history_service.mark_finished(record, status=status, error=record.error_message)
            self.transfer_finished.emit(transfer_id, status)
            self.transfer_updated.emit(transfer_id)
        finally:
            if active is not None and active.prepared_archive is not None:
                self.sevenzip_service.cleanup_prepared_archive(active.prepared_archive)
            self.active.pop(transfer_id, None)

    def cancel(self, transfer_id: str) -> None:
        active = self.active.get(transfer_id)
        if not active:
            return
        active.runtime.cancel()
        self.sevenzip_service.cleanup_prepared_archive(active.prepared_archive)
        self.history_service.mark_finished(active.record, status="canceled", error="Canceled by user")
        self.transfer_finished.emit(transfer_id, "canceled")
        self.active.pop(transfer_id, None)

    def retry(self, transfer_id: str) -> TransferRecord | None:
        records = self.history_service.list_records()
        record = next((r for r in records if r.transfer_id == transfer_id), None)
        if not record:
            return None
        if record.direction in ("send", "selftest-send"):
            return self.start_send(
                paths=record.source_paths,
                code_phrase="",
                direction=record.direction,
                compress_7zip=record.compression_mode == COMPRESSION_7ZIP,
            )
        if record.direction in ("receive", "selftest-receive") and record.code_phrase:
            return self.start_receive(
                code_phrase=record.code_phrase,
                destination=record.destination_folder or str(Path.home() / "Downloads"),
                overwrite=False,
                direction=record.direction,
            )
        return None

    def _take_reserved_code(self, profile_name: str) -> str:
        self._prune_reserved_codes()
        reserved = self._reserved_codes.pop(profile_name, None)
        if not reserved:
            return ""
        if reserved.expires_at <= datetime.now(timezone.utc):
            return ""
        return reserved.code_phrase

    def _reserve_next_code(self, profile_name: str) -> tuple[str, datetime]:
        self._prune_reserved_codes()
        code = generate_code_phrase(profile_name)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        self._reserved_codes[profile_name] = ReservedCode(code_phrase=code, expires_at=expires_at)
        return code, expires_at

    def _prune_reserved_codes(self) -> None:
        now = datetime.now(timezone.utc)
        expired = [profile for profile, reserved in self._reserved_codes.items() if reserved.expires_at <= now]
        for profile in expired:
            self._reserved_codes.pop(profile, None)

    def _auto_remember_device(self, record: TransferRecord) -> None:
        code = (record.connection_code or record.code_phrase or "").strip()
        if not code:
            return
        settings = self.settings_service.get()
        if code in settings.trusted_devices:
            return
        peer_label = code.rsplit("-", 1)[-1].strip() if "-" in code else "peer"
        if not peer_label:
            peer_label = "peer"
        # App-level convenience only: this alias is inferred from code text, not cryptographic identity.
        settings.trusted_devices[code] = f"Auto: {peer_label}"
        self.settings_service.save(settings)

    def _auto_extract_received_archive(self, record: TransferRecord, transfer_id: str) -> None:
        archive_path = self._resolve_received_archive(record)
        self._append_system_line(record, transfer_id, f"[system] Auto-extracting {archive_path.name} with temporary 7-Zip CLI...")
        self.sevenzip_service.extract_archive(archive_path=archive_path, destination=Path(record.destination_folder))
        record.auto_extracted = True
        try:
            archive_path.unlink()
        except OSError as exc:
            self.log.warning("Failed to delete extracted archive %s: %s", archive_path, exc)
            self._append_system_line(
                record,
                transfer_id,
                f"[system] Extracted successfully, but could not delete {archive_path.name}.",
            )
        else:
            self._append_system_line(record, transfer_id, f"[system] Auto-extracted {archive_path.name} into {record.destination_folder}")

    def _resolve_received_archive(self, record: TransferRecord) -> Path:
        destination = Path(record.destination_folder)
        archive_name = record.archive_name.strip()
        if archive_name:
            expected = destination / archive_name
            if expected.exists():
                return expected
            raise SevenZipServiceError(
                f"Expected compressed file '{archive_name}' was not found in {destination} after download."
            )

        candidates = sorted(destination.glob("*.7z"), key=lambda item: item.stat().st_mtime, reverse=True)
        if len(candidates) == 1:
            return candidates[0]
        raise SevenZipServiceError("Received compressed transfer, but the downloaded .7z file could not be identified.")

    def _append_system_line(self, record: TransferRecord, transfer_id: str, line: str) -> None:
        record.output_excerpt.append(line)
        self.transfer_output.emit(transfer_id, line)
