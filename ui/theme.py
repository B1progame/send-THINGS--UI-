from __future__ import annotations

from models.settings import AppSettings


def apply_theme(app, settings: AppSettings) -> None:
    accent = settings.accent_color or "#35c9a5"
    if settings.dark_mode:
        palette = {
            "base_bg": "#0c1118",
            "surface_0": "#121923",
            "surface_1": "#171f2c",
            "surface_2": "#1d2736",
            "line": "#2a374b",
            "line_soft": "#212d3f",
            "text": "#e6edf7",
            "text_soft": "#a0afc5",
            "input_bg": "#101722",
            "input_bg_alt": "#0f1621",
            "hover": "#22334a",
            "pressed": "#1a2a3f",
            "success": "#49d59e",
            "danger": "#ff6f6f",
        }
    else:
        palette = {
            "base_bg": "#eef3f8",
            "surface_0": "#f6f9fc",
            "surface_1": "#ffffff",
            "surface_2": "#f4f7fb",
            "line": "#cfd8e4",
            "line_soft": "#dbe2ec",
            "text": "#1a2634",
            "text_soft": "#5f7186",
            "input_bg": "#ffffff",
            "input_bg_alt": "#f8fbff",
            "hover": "#ecf3fb",
            "pressed": "#dfebf8",
            "success": "#1f9768",
            "danger": "#c23d3d",
        }

    app.setStyleSheet(
        f"""
        QWidget {{
            background: {palette['base_bg']};
            color: {palette['text']};
            font-family: "Segoe UI";
            font-size: 13px;
        }}
        QMainWindow, QFrame#MainPanel {{
            background: {palette['base_bg']};
        }}
        QFrame#Sidebar {{
            background: {palette['surface_1']};
            border-right: 1px solid {palette['line']};
        }}
        QFrame#BrandShell {{
            background: {palette['surface_2']};
            border: 1px solid {palette['line']};
            border-radius: 14px;
        }}
        QLabel#BrandTitle {{
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 0.3px;
        }}
        QLabel#PageTitle {{
            font-size: 22px;
            font-weight: 700;
            letter-spacing: 0.2px;
        }}
        QLabel#PageSubtitle {{
            font-size: 13px;
        }}
        QFrame#HeaderBar {{
            background: {palette['surface_1']};
            border-radius: 12px;
            border: 1px solid {palette['line']};
        }}
        QLabel#HeaderTitle {{
            font-size: 16px;
            font-weight: 700;
        }}
        QLabel#HeaderStatus {{
            color: {palette['text_soft']};
            background: {palette['surface_2']};
            border: 1px solid {palette['line']};
            border-radius: 8px;
            padding: 4px 8px;
        }}
        QListWidget#NavList {{
            background: transparent;
            border: 0;
            padding: 2px;
            outline: 0;
        }}
        QListWidget#NavList::item {{
            padding: 10px 12px;
            border-radius: 9px;
            margin-bottom: 4px;
            color: {palette['text_soft']};
        }}
        QListWidget#NavList::item:hover {{
            background: {palette['hover']};
            color: {palette['text']};
        }}
        QListWidget#NavList::item:selected {{
            background: {accent};
            color: #08121a;
            font-weight: 700;
        }}
        QFrame#Card {{
            background: {palette['surface_1']};
            border-radius: 12px;
            border: 1px solid {palette['line']};
        }}
        QLabel#CardTitle {{
            font-size: 14px;
            font-weight: 700;
        }}
        QPushButton {{
            background: {palette['surface_2']};
            border: 1px solid {palette['line']};
            border-radius: 8px;
            padding: 8px 12px;
        }}
        QPushButton:hover {{
            background: {palette['hover']};
            border-color: {accent};
        }}
        QPushButton:pressed {{
            background: {palette['pressed']};
        }}
        QPushButton#PrimaryButton {{
            background: {accent};
            color: #071118;
            font-weight: 700;
            border: 0;
        }}
        QPushButton#PrimaryButton:hover {{
            background: {accent};
            border: 0;
        }}
        QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox, QListWidget, QTableWidget {{
            background: {palette['input_bg']};
            border: 1px solid {palette['line_soft']};
            border-radius: 8px;
            padding: 6px;
            selection-background-color: {accent};
            selection-color: #071118;
        }}
        QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border-color: {accent};
        }}
        QHeaderView::section {{
            background: {palette['surface_2']};
            color: {palette['text_soft']};
            border: 0;
            border-bottom: 1px solid {palette['line']};
            padding: 7px 8px;
            font-weight: 600;
        }}
        QProgressBar {{
            border: 1px solid {palette['line_soft']};
            border-radius: 8px;
            text-align: center;
            background: {palette['input_bg_alt']};
            color: {palette['text_soft']};
            min-height: 18px;
        }}
        QProgressBar::chunk {{
            border-radius: 7px;
            background: {accent};
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {palette['line']};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QLabel[role="muted"] {{
            color: {palette['text_soft']};
        }}
        """
    )
