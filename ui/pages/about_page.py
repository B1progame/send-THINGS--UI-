from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from ui.components.common import Card


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        title = QLabel("About CrocDrop")
        title.setStyleSheet("font-size:20px;font-weight:700;")
        root.addWidget(title)

        card = Card("Project")
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(
            "CrocDrop is a Windows-first desktop GUI for the official croc transfer tool.\n\n"
            "Backend engine: https://github.com/schollz/croc\n"
            "GUI stack: Python + PySide6\n\n"
            "Security note:\n"
            "CrocDrop does not invent cryptographic guarantees. It relies on croc's protocol and behavior."
        )
        card.layout.addWidget(text)
        root.addWidget(card)
        root.addStretch(1)
