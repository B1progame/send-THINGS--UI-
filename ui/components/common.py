from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)


class Card(QFrame):
    def __init__(self, title: str = ""):
        super().__init__()
        self.setObjectName("Card")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(8)
        if title:
            label = QLabel(title)
            label.setStyleSheet("font-weight:700;font-size:14px;")
            self.layout.addWidget(label)


class DropList(QListWidget):
    paths_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.exists():
                self.add_path(str(path))
        self.paths_changed.emit(self.paths())
        event.acceptProposedAction()

    def add_path(self, path: str):
        if path not in self.paths():
            self.addItem(QListWidgetItem(path))

    def remove_selected(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))
        self.paths_changed.emit(self.paths())

    def paths(self) -> list[str]:
        return [self.item(i).text() for i in range(self.count())]
