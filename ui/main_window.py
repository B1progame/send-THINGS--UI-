from __future__ import annotations

from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QStackedWidget, QVBoxLayout, QWidget, QMainWindow

from ui.pages.about_page import AboutPage
from ui.pages.debug_page import DebugPage
from ui.pages.devices_page import DevicesPage
from ui.pages.home_page import HomePage
from ui.pages.logs_page import LogsPage
from ui.pages.receive_page import ReceivePage
from ui.pages.send_page import SendPage
from ui.pages.settings_page import SettingsPage
from ui.pages.transfers_page import TransfersPage


class MainWindow(QMainWindow):
    def __init__(self, context, debug_peer: bool = False):
        super().__init__()
        self.context = context
        self.setWindowTitle("CrocDrop")
        self.resize(1320, 860)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        side_layout = QVBoxLayout(sidebar)

        brand = QLabel("CrocDrop")
        brand.setStyleSheet("font-size:24px;font-weight:800;padding:12px;")
        mode = QLabel("Debug Peer Instance" if debug_peer else "Primary Instance")
        mode.setProperty("role", "muted")
        mode.setStyleSheet("padding-left:12px;padding-bottom:6px;")

        self.nav = QListWidget()
        self.nav.setObjectName("NavList")
        for item in ["Home", "Send", "Receive", "Transfers", "Devices", "Logs", "Settings", "Debug", "About"]:
            self.nav.addItem(QListWidgetItem(item))

        side_layout.addWidget(brand)
        side_layout.addWidget(mode)
        side_layout.addWidget(self.nav)

        panel = QFrame()
        panel.setObjectName("MainPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 14, 18, 14)

        header = QFrame()
        header.setObjectName("Card")
        header_layout = QHBoxLayout(header)
        title = QLabel("Context")
        title.setStyleSheet("font-size:16px;font-weight:700;")
        self.context_label = QLabel("Ready")
        self.context_label.setProperty("role", "muted")

        check_btn = QPushButton("Check Croc")
        check_btn.clicked.connect(self.check_croc)
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.context_label)
        header_layout.addWidget(check_btn)

        self.pages = QStackedWidget()
        self.home_page = HomePage(context)
        self.send_page = SendPage(context)
        self.receive_page = ReceivePage(context)
        self.transfers_page = TransfersPage(context)
        self.devices_page = DevicesPage(context)
        self.logs_page = LogsPage(context)
        self.settings_page = SettingsPage(context, QApplication.instance())
        self.debug_page = DebugPage(context)
        self.about_page = AboutPage()

        for page in [
            self.home_page,
            self.send_page,
            self.receive_page,
            self.transfers_page,
            self.devices_page,
            self.logs_page,
            self.settings_page,
            self.debug_page,
            self.about_page,
        ]:
            self.pages.addWidget(page)

        panel_layout.addWidget(header)
        panel_layout.addWidget(self.pages, 1)

        layout.addWidget(sidebar)
        layout.addWidget(panel, 1)

        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.nav.currentRowChanged.connect(self.on_page_changed)
        self.home_page.navigate_requested.connect(self.navigate_to)
        self.context.history_service.history_changed.connect(self.home_page.refresh)

        self.nav.setCurrentRow(0)
        self.check_croc()

    def navigate_to(self, page_name: str):
        mapping = {self.nav.item(i).text(): i for i in range(self.nav.count())}
        if page_name in mapping:
            self.nav.setCurrentRow(mapping[page_name])

    def on_page_changed(self, index: int):
        name = self.nav.item(index).text() if index >= 0 else ""
        self.context_label.setText(name)
        if name == "Home":
            self.home_page.refresh()
        elif name == "Transfers":
            self.transfers_page.refresh()
        elif name == "Devices":
            self.devices_page.refresh()

    def check_croc(self):
        info = self.context.croc_manager.detect_binary()
        self.context_label.setText(f"{info.source} | {info.version or 'missing'}")
