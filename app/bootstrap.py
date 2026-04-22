from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QApplication

from services.croc_manager import CrocManager
from services.debug_service import DebugService
from services.history_service import HistoryService
from services.log_service import LogService
from services.settings_service import SettingsService
from services.transfer_service import TransferService
from ui.main_window import MainWindow
from ui.theme import apply_theme


@dataclass(slots=True)
class AppContext:
    log_service: LogService
    settings_service: SettingsService
    history_service: HistoryService
    croc_manager: CrocManager
    transfer_service: TransferService
    debug_service: DebugService


def build_app(debug_peer: bool = False) -> tuple[QApplication, MainWindow]:
    qt_app = QApplication([])
    qt_app.setApplicationName("CrocDrop")
    qt_app.setOrganizationName("CrocDrop")

    settings_service = SettingsService()
    settings = settings_service.load()

    log_service = LogService(debug_enabled=settings.debug_mode)
    history_service = HistoryService(log_service)
    croc_manager = CrocManager(log_service=log_service, settings_service=settings_service)
    transfer_service = TransferService(
        croc_manager=croc_manager,
        history_service=history_service,
        settings_service=settings_service,
        log_service=log_service,
    )
    debug_service = DebugService(
        transfer_service=transfer_service,
        croc_manager=croc_manager,
        log_service=log_service,
    )
    context = AppContext(
        log_service=log_service,
        settings_service=settings_service,
        history_service=history_service,
        croc_manager=croc_manager,
        transfer_service=transfer_service,
        debug_service=debug_service,
    )

    apply_theme(qt_app, settings)
    window = MainWindow(context=context, debug_peer=debug_peer)
    return qt_app, window
