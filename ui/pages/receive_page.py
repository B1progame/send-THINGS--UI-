from __future__ import annotations

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QComboBox,
    QVBoxLayout,
    QWidget,
)

from ui.components.common import Card


class ReceivePage(QWidget):
    def __init__(self, context):
        super().__init__()
        self.context = context
        self.current_transfer_id = ""

        root = QVBoxLayout(self)
        title = QLabel("Receive")
        title.setStyleSheet("font-size:20px;font-weight:700;")
        root.addWidget(title)

        form = Card("Receive Setup")
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Paste code phrase")
        self.dest_input = QLineEdit()
        self.dest_input.setText(self.context.settings_service.get().default_download_folder)
        self.collision = QComboBox()
        self.collision.addItems(["ask", "rename", "overwrite-disabled", "skip"])

        row1 = QHBoxLayout()
        paste_btn = QPushButton("Paste")
        row1.addWidget(self.code_input)
        row1.addWidget(paste_btn)

        row2 = QHBoxLayout()
        browse_btn = QPushButton("Browse")
        row2.addWidget(self.dest_input)
        row2.addWidget(browse_btn)

        start_btn = QPushButton("Start Receive")
        start_btn.setObjectName("PrimaryButton")

        form.layout.addWidget(QLabel("Code"))
        form.layout.addLayout(row1)
        form.layout.addWidget(QLabel("Destination"))
        form.layout.addLayout(row2)
        form.layout.addWidget(QLabel("Collision Handling"))
        form.layout.addWidget(self.collision)
        form.layout.addWidget(start_btn)

        logs = Card("Live Output")
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        logs.layout.addWidget(self.output)

        root.addWidget(form)
        root.addWidget(logs)

        browse_btn.clicked.connect(self.browse_destination)
        start_btn.clicked.connect(self.start_receive)
        paste_btn.clicked.connect(self.paste_code)

        self.context.transfer_service.transfer_output.connect(self.on_transfer_output)

    def paste_code(self):
        from PySide6.QtGui import QGuiApplication

        self.code_input.setText(QGuiApplication.clipboard().text().strip())

    def browse_destination(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose destination", self.dest_input.text())
        if folder:
            self.dest_input.setText(folder)

    def start_receive(self):
        code = self.code_input.text().strip()
        destination = self.dest_input.text().strip()
        if not code:
            QMessageBox.warning(self, "Missing code", "Enter a croc code phrase")
            return
        if not destination:
            QMessageBox.warning(self, "Missing destination", "Choose destination folder")
            return

        strategy = self.collision.currentText()
        overwrite = False
        if strategy in {"rename", "skip"}:
            self.output.append(f"Note: '{strategy}' is handled best-effort because croc CLI behavior varies by version.")

        record = self.context.transfer_service.start_receive(code_phrase=code, destination=destination, overwrite=overwrite)
        self.current_transfer_id = record.transfer_id
        self.output.append(f"Started receive {record.transfer_id}")

    def on_transfer_output(self, transfer_id: str, line: str):
        if transfer_id != self.current_transfer_id:
            return
        self.output.append(line)
