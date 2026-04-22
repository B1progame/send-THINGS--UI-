from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.components.common import Card, DropList


class SendPage(QWidget):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.current_transfer_id = ""

        root = QVBoxLayout(self)
        title = QLabel("Send")
        title.setStyleSheet("font-size:20px;font-weight:700;")
        root.addWidget(title)

        picker = Card("Files and Folders")
        self.drop = DropList()
        picker.layout.addWidget(self.drop)

        actions = QHBoxLayout()
        btn_file = QPushButton("Add Files")
        btn_folder = QPushButton("Add Folder")
        btn_remove = QPushButton("Remove Selected")
        actions.addWidget(btn_file)
        actions.addWidget(btn_folder)
        actions.addWidget(btn_remove)
        picker.layout.addLayout(actions)

        self.code = QLineEdit()
        self.code.setReadOnly(True)
        self.code.setPlaceholderText("Code phrase will appear after start")

        controls = QHBoxLayout()
        self.start_btn = QPushButton("Start Send")
        self.start_btn.setObjectName("PrimaryButton")
        copy_btn = QPushButton("Copy Code")
        controls.addWidget(self.start_btn)
        controls.addWidget(copy_btn)

        runtime = Card("Live Output")
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        runtime.layout.addWidget(self.output)

        root.addWidget(picker)
        root.addWidget(QLabel("Generated Code"))
        root.addWidget(self.code)
        root.addLayout(controls)
        root.addWidget(runtime)

        btn_file.clicked.connect(self.pick_files)
        btn_folder.clicked.connect(self.pick_folder)
        btn_remove.clicked.connect(self.drop.remove_selected)
        self.start_btn.clicked.connect(self.start_send)
        copy_btn.clicked.connect(self.copy_code)

        self.context.transfer_service.transfer_output.connect(self.on_transfer_output)
        self.context.transfer_service.transfer_updated.connect(self.on_transfer_updated)

    def pick_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select files")
        for file in files:
            self.drop.add_path(file)

    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if folder:
            self.drop.add_path(folder)

    def start_send(self):
        paths = self.drop.paths()
        if not paths:
            QMessageBox.warning(self, "No files", "Add at least one file or folder")
            return
        record = self.context.transfer_service.start_send(paths)
        self.current_transfer_id = record.transfer_id
        self.output.append(f"Started transfer {record.transfer_id}")

    def copy_code(self):
        if not self.code.text().strip():
            return
        QGuiApplication.clipboard().setText(self.code.text().strip())

    def on_transfer_output(self, transfer_id: str, line: str):
        if transfer_id != self.current_transfer_id:
            return
        self.output.append(line)

    def on_transfer_updated(self, transfer_id: str):
        if transfer_id != self.current_transfer_id:
            return
        records = self.context.history_service.list_records()
        record = next((r for r in records if r.transfer_id == transfer_id), None)
        if record and record.code_phrase:
            self.code.setText(record.code_phrase)
