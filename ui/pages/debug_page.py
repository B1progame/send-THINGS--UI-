from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QWidget

from ui.components.common import Card


class DebugPage(QWidget):
    def __init__(self, context):
        super().__init__()
        self.context = context

        root = QVBoxLayout(self)
        title = QLabel("Debug")
        title.setStyleSheet("font-size:20px;font-weight:700;")
        root.addWidget(title)

        controls = Card("Self-Test and Tools")
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 2048)
        self.size_spin.setValue(5)

        row = QHBoxLayout()
        row.addWidget(QLabel("Dummy size (MB):"))
        row.addWidget(self.size_spin)

        self.selftest_btn = QPushButton("Run Self-Test")
        self.selftest_btn.setObjectName("PrimaryButton")
        self.launch_dual_btn = QPushButton("Launch Second Instance")
        self.health_btn = QPushButton("Backend Health Check")
        self.bundle_btn = QPushButton("Save Diagnostic Bundle")

        controls.layout.addLayout(row)
        controls.layout.addWidget(self.selftest_btn)
        controls.layout.addWidget(self.launch_dual_btn)
        controls.layout.addWidget(self.health_btn)
        controls.layout.addWidget(self.bundle_btn)

        logs = Card("Debug Output")
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        logs.layout.addWidget(self.output)

        root.addWidget(controls)
        root.addWidget(logs)

        self.selftest_btn.clicked.connect(self.run_self_test)
        self.launch_dual_btn.clicked.connect(self.launch_second)
        self.health_btn.clicked.connect(self.health_check)
        self.bundle_btn.clicked.connect(self.save_bundle)

        self.context.debug_service.self_test_progress.connect(self.on_self_test_progress)
        self.context.debug_service.self_test_finished.connect(self.on_self_test_finished)

    def run_self_test(self):
        self.output.append("Starting self-test...")
        self.context.debug_service.run_self_test(size_mb=self.size_spin.value())

    def launch_second(self):
        self.context.debug_service.launch_second_instance()
        self.output.append("Second instance launched with --debug-peer")

    def health_check(self):
        diag = self.context.debug_service.backend_health()
        self.output.append(str(diag))

    def save_bundle(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save diagnostics", "crocdrop_diagnostics.txt", "Text Files (*.txt)")
        if not path:
            return
        records = self.context.history_service.list_records()[:20]
        diag = self.context.debug_service.backend_health()
        lines = ["CrocDrop Diagnostic Bundle", "", "Backend:", str(diag), "", "Recent transfers:"]
        for r in records:
            lines.append(str(r.to_dict()))
        Path(path).write_text("\n".join(lines), encoding="utf-8")
        self.output.append(f"Diagnostics saved to {path}")

    def on_self_test_progress(self, msg: str):
        self.output.append(msg)

    def on_self_test_finished(self, ok: bool, msg: str):
        self.output.append(("PASS" if ok else "FAIL") + " | " + msg)
