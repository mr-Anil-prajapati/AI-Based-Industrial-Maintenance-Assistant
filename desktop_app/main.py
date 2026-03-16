from __future__ import annotations

import json
import sys
from pathlib import Path

from backend.assistant_service import AssistantService

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QFileDialog,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
        QComboBox,
    )
except ImportError as exc:  # pragma: no cover - desktop dependency not installed here
    raise SystemExit(
        "PySide6 is required for the Windows desktop application. Install requirements-windows.txt before launch."
    ) from exc


class DesktopAssistantWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.service = AssistantService()
        self.collapsed = False
        self.setWindowTitle("Industrial AI Maintenance Assistant")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.resize(520, 720)
        self._build_ui()

    def _build_ui(self) -> None:
        container = QWidget()
        self.setCentralWidget(container)
        root = QVBoxLayout(container)

        header = QHBoxLayout()
        title = QLabel("Industrial AI Maintenance Assistant")
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        header.addWidget(title)
        collapse_button = QPushButton("Collapse")
        collapse_button.clicked.connect(self.toggle_collapsed)
        header.addWidget(collapse_button)
        root.addLayout(header)

        self.status_label = QLabel("Status: read-only local assistant")
        root.addWidget(self.status_label)

        controls = QGridLayout()
        self.asset_input = QLineEdit("motor-1")
        self.protocol_input = QComboBox()
        self.protocol_input.addItems(["opcua", "modbus", "mqtt", "rest"])
        self.question_input = QTextEdit()
        self.question_input.setPlainText("Why is Motor-1 not running?")
        controls.addWidget(QLabel("Asset"), 0, 0)
        controls.addWidget(self.asset_input, 0, 1)
        controls.addWidget(QLabel("Protocol"), 1, 0)
        controls.addWidget(self.protocol_input, 1, 1)
        controls.addWidget(QLabel("Question"), 2, 0)
        controls.addWidget(self.question_input, 2, 1)
        root.addLayout(controls)

        actions = QHBoxLayout()
        ask_button = QPushButton("Ask")
        ask_button.clicked.connect(self.ask_question)
        import_button = QPushButton("Import Documents")
        import_button.clicked.connect(self.import_documents)
        clipboard_button = QPushButton("Use Clipboard")
        clipboard_button.clicked.connect(self.use_clipboard)
        actions.addWidget(ask_button)
        actions.addWidget(import_button)
        actions.addWidget(clipboard_button)
        root.addLayout(actions)

        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        root.addWidget(self.response_output)

        self.signal_output = QTextEdit()
        self.signal_output.setReadOnly(True)
        self.signal_output.setMaximumHeight(180)
        root.addWidget(self.signal_output)

        self._refresh_health()

    def _refresh_health(self) -> None:
        health = self.service.health()
        self.status_label.setText(
            f"Status: {health.get('status', 'unknown')} | Model: {health.get('model', 'missing')} | Mode: read-only"
        )

    def toggle_collapsed(self) -> None:
        self.collapsed = not self.collapsed
        self.resize(520, 180 if self.collapsed else 720)
        self.response_output.setVisible(not self.collapsed)
        self.signal_output.setVisible(not self.collapsed)

    def use_clipboard(self) -> None:
        text = QApplication.clipboard().text().strip()
        if text:
            self.question_input.setPlainText(f"Analyze this selected engineering text and help troubleshoot it:\n{text}")

    def import_documents(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select engineering documents",
            str(Path.cwd()),
            "Documents (*.txt *.md *.pdf *.docx)",
        )
        if not paths:
            return
        result = self.service.ingest_uploaded_documents([Path(path) for path in paths])
        self.response_output.append(
            f"Imported {result['documents_indexed']} documents and {result['chunks_indexed']} chunks.\n"
        )

    def ask_question(self) -> None:
        try:
            response = self.service.chat(
                question=self.question_input.toPlainText().strip(),
                asset_id=self.asset_input.text().strip() or "motor-1",
                protocol=self.protocol_input.currentText(),
            )
        except Exception as exc:  # pragma: no cover - UI path
            QMessageBox.critical(self, "Assistant Error", str(exc))
            return

        self.response_output.setPlainText(
            f"{response['answer']}\n\nSources:\n{json.dumps(response['sources'], indent=2)}\n\n"
            f"Safety:\n{response['safety_notice']}"
        )
        signals = response["machine_state"].get("signals", {})
        self.signal_output.setPlainText(json.dumps(signals, indent=2))


def main() -> int:
    app = QApplication(sys.argv)
    window = DesktopAssistantWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
