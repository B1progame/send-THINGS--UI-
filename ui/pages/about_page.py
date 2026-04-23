from __future__ import annotations

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app.version import APP_NAME, APP_REPOSITORY, APP_VERSION
from ui.components.common import Card, PageHeader


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)
        root.addWidget(PageHeader("About CrocDrop", "A polished Windows-first transfer shell for the official croc backend."))

        hero = QFrame()
        hero.setObjectName("AboutHero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(20, 20, 20, 20)
        hero_layout.setSpacing(16)

        mark = QLabel("CD")
        mark.setObjectName("AboutLogoMark")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setFixedSize(64, 64)

        copy = QVBoxLayout()
        copy.setContentsMargins(0, 0, 0, 0)
        copy.setSpacing(5)
        title = QLabel(APP_NAME)
        title.setObjectName("AboutTitle")
        description = QLabel("Secure file transfers with a friendly desktop workflow, powered by croc.")
        description.setObjectName("AboutDescription")
        description.setWordWrap(True)
        version = QLabel(f"Version {APP_VERSION}")
        version.setObjectName("AboutVersionPill")
        copy.addWidget(title)
        copy.addWidget(description)
        copy.addWidget(version, 0, Qt.AlignmentFlag.AlignLeft)

        hero_layout.addWidget(mark)
        hero_layout.addLayout(copy, 1)

        overview = Card("Project Overview")
        overview_grid = QGridLayout()
        overview_grid.setContentsMargins(0, 2, 0, 0)
        overview_grid.setHorizontalSpacing(18)
        overview_grid.setVerticalSpacing(10)
        for row, (label_text, value) in enumerate(
            [
                ("Author", "B1progame"),
                ("Repository", APP_REPOSITORY),
                ("Backend engine", "schollz/croc"),
                ("GUI stack", "Python + PySide6"),
                ("License", "MIT"),
                ("Warranty", "Provided AS IS, without warranty or liability."),
            ]
        ):
            label = QLabel(label_text)
            label.setObjectName("SettingLabel")
            value_label = QLabel(value)
            value_label.setObjectName("SettingDescription")
            value_label.setWordWrap(True)
            overview_grid.addWidget(label, row, 0)
            overview_grid.addWidget(value_label, row, 1)
        overview_grid.setColumnMinimumWidth(0, 150)
        overview_grid.setColumnStretch(1, 1)
        overview.layout.addLayout(overview_grid)

        links = Card("Useful Links")
        link_hint = QLabel("Open project and backend references when you need release notes, source, or protocol details.")
        link_hint.setObjectName("SettingDescription")
        link_hint.setWordWrap(True)
        link_row = QHBoxLayout()
        link_row.setContentsMargins(0, 0, 0, 0)
        link_row.setSpacing(10)
        repo_btn = QPushButton("CrocDrop Repository")
        backend_btn = QPushButton("croc Backend")
        license_btn = QPushButton("MIT License")
        repo_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"https://github.com/{APP_REPOSITORY}")))
        backend_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/schollz/croc")))
        license_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"https://github.com/{APP_REPOSITORY}/blob/main/LICENSE")))
        link_row.addWidget(repo_btn)
        link_row.addWidget(backend_btn)
        link_row.addWidget(license_btn)
        link_row.addStretch(1)
        links.layout.addWidget(link_hint)
        links.layout.addLayout(link_row)

        security = Card("Security Note")
        note = QLabel(
            "CrocDrop does not invent new cryptographic guarantees. It provides a desktop workflow around "
            "the official croc transfer protocol and follows croc's backend behavior."
        )
        note.setObjectName("SettingDescription")
        note.setWordWrap(True)
        security.layout.addWidget(note)

        root.addWidget(hero)
        root.addWidget(overview)
        root.addWidget(links)
        root.addWidget(security)
        root.addStretch(1)
