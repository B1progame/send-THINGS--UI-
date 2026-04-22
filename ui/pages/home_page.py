from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.components.common import Card


class HomePage(QWidget):
    navigate_requested = Signal(str)

    def __init__(self, context):
        super().__init__()
        self.context = context

        root = QVBoxLayout(self)
        title = QLabel("CrocDrop Dashboard")
        title.setStyleSheet("font-size:22px;font-weight:700;")
        subtitle = QLabel("Fast, friendly transfers powered by official croc")
        subtitle.setProperty("role", "muted")

        root.addWidget(title)
        root.addWidget(subtitle)

        grid = QGridLayout()
        root.addLayout(grid)

        self.binary_label = QLabel("Checking croc binary...")
        self.relay_label = QLabel("Relay: public")

        status = Card("Engine Status")
        status.layout.addWidget(self.binary_label)
        status.layout.addWidget(self.relay_label)

        quick = Card("Quick Actions")
        for name, page in [("Send", "Send"), ("Receive", "Receive"), ("Self-Test", "Debug"), ("Open History", "Transfers")]:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _=False, p=page: self.navigate_requested.emit(p))
            quick.layout.addWidget(btn)

        self.recent = Card("Recent Transfers")
        self.recent_label = QLabel("No transfers yet")
        self.recent_label.setProperty("role", "muted")
        self.recent.layout.addWidget(self.recent_label)

        grid.addWidget(status, 0, 0)
        grid.addWidget(quick, 0, 1)
        grid.addWidget(self.recent, 1, 0, 1, 2)

        root.addStretch(1)
        self.refresh()

    def refresh(self) -> None:
        info = self.context.croc_manager.detect_binary()
        self.binary_label.setText(f"Binary: {info.source} | {info.version or 'missing'}")
        settings = self.context.settings_service.get()
        self.relay_label.setText(f"Relay mode: {settings.relay_mode} {'(' + settings.custom_relay + ')' if settings.custom_relay else ''}")

        records = self.context.history_service.list_records()[:5]
        if not records:
            self.recent_label.setText("No transfers yet")
            return
        lines = [f"{r.direction} | {r.status} | {r.code_phrase or '-'}" for r in records]
        self.recent_label.setText("\n".join(lines))
