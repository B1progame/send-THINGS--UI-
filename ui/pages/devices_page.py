from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QListWidget, QPushButton, QVBoxLayout, QWidget

from ui.components.common import Card, PageHeader


class DevicesPage(QWidget):
    def __init__(self, context):
        super().__init__()
        self.context = context

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)
        root.addWidget(PageHeader("Devices", "Manage remembered aliases for peers and session labels."))

        card = Card("Remembered Aliases")
        self.list = QListWidget()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Code/session label")
        self.alias_input = QLineEdit()
        self.alias_input.setPlaceholderText("Friendly alias")

        actions = QHBoxLayout()
        save_btn = QPushButton("Save Alias")
        remove_btn = QPushButton("Remove Selected")
        actions.addWidget(save_btn)
        actions.addWidget(remove_btn)
        actions.addStretch(1)

        card.layout.addWidget(self.list)
        card.layout.addWidget(self.code_input)
        card.layout.addWidget(self.alias_input)
        card.layout.addLayout(actions)
        root.addWidget(card, 1)

        save_btn.clicked.connect(self.save_alias)
        remove_btn.clicked.connect(self.remove_selected)
        self.refresh()

    def refresh(self):
        self.list.clear()
        devices = self.context.settings_service.get().trusted_devices
        for key, alias in devices.items():
            self.list.addItem(f"{key} -> {alias}")

    def save_alias(self):
        key = self.code_input.text().strip()
        alias = self.alias_input.text().strip()
        if not key or not alias:
            return
        settings = self.context.settings_service.get()
        settings.trusted_devices[key] = alias
        self.context.settings_service.save(settings)
        self.refresh()

    def remove_selected(self):
        item = self.list.currentItem()
        if not item:
            return
        key = item.text().split(" -> ")[0]
        settings = self.context.settings_service.get()
        settings.trusted_devices.pop(key, None)
        self.context.settings_service.save(settings)
        self.refresh()
