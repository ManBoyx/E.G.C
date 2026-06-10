"""EGC Antivirus Scanner - Version Windows"""
import sys
import os
import logging
from pathlib import Path
from typing import List, Set
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTextEdit, QLabel, QFileDialog, QProgressBar,
    QComboBox, QTabWidget, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QFont

logger = logging.getLogger(__name__)

VIRUS_SIGNATURES: Set[bytes] = {b"eicar", b"malicious"}
QUARANTINE_DIR = ".quarantine"

STYLE = """
    QMainWindow {
        background-color: #1e1e2e;
    }
    QWidget {
        background-color: #1e1e2e;
        color: #cdd6f4;
    }
    QTabWidget::pane {
        border: 1px solid #45475a;
        background-color: #1e1e2e;
        border-radius: 8px;
    }
    QTabBar::tab {
        background-color: #313244;
        color: #cdd6f4;
        padding: 10px 20px;
        margin: 2px;
        border-radius: 6px 6px 0 0;
    }
    QTabBar::tab:selected {
        background-color: #45475a;
        color: #89b4fa;
    }
    QTextEdit {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 6px;
        padding: 8px;
        font-family: 'Consolas', 'Courier New', monospace;
    }
    QProgressBar {
        border: 1px solid #45475a;
        border-radius: 6px;
        text-align: center;
        background-color: #313244;
        color: #cdd6f4;
    }
    QProgressBar::chunk {
        background-color: #a6e3a1;
        border-radius: 5px;
    }
    QComboBox {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 6px;
        padding: 6px;
    }
    QListWidget {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 6px;
    }
    QLabel {
        color: #cdd6f4;
    }
"""


class ScanThread(QThread):
    """Thread pour le scan de fichiers"""
    update_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(int, int)

    def __init__(self, directory: str, scan_type: str):
        super().__init__()
        self.directory = directory
        self.scan_type = scan_type
        self.stop_flag = False
        self.infected_files: List[str] = []

    def run(self):
        try:
            self.update_signal.emit(f"Scan de: {self.directory}")
            self.infected_files = self.scan_files(self.directory)
            total = self._count_files(self.directory)
            if self.infected_files:
                self.update_signal.emit(
                    f"[!] {len(self.infected_files)} fichier(s) suspect(s)"
                )
                for f in self.infected_files:
                    if self.stop_flag:
                        break
                    self.update_signal.emit(f"  INFECTE: {f}")
                    self.quarantine_file(f)
            else:
                self.update_signal.emit("[OK] Aucune menace detectee")
            self.finished_signal.emit(total, len(self.infected_files))
        except Exception as e:
            self.update_signal.emit(f"[ERREUR] {e}")
            logger.error(f"Erreur scan: {e}")

    def _count_files(self, directory: str) -> int:
        try:
            return len([f for f in Path(directory).rglob('*') if f.is_file()])
        except Exception:
            return 0

    def scan_files(self, directory: str) -> List[str]:
        infected = []
        try:
            files = list(Path(directory).rglob('*'))
            total = len([f for f in files if f.is_file()])
            scanned = 0
            for file_path in files:
                if self.stop_flag or not file_path.is_file():
                    continue
                if self.scan_file(str(file_path)):
                    infected.append(str(file_path))
                scanned += 1
                progress = int((scanned / total) * 100) if total > 0 else 0
                self.progress_signal.emit(progress)
        except Exception as e:
            logger.error(f"Erreur scan: {e}")
        return infected

    def scan_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    for sig in VIRUS_SIGNATURES:
                        if sig in chunk:
                            return True
        except (OSError, IOError):
            pass
        return False

    def quarantine_file(self, file_path: str):
        try:
            qdir = Path(file_path).parent / QUARANTINE_DIR
            qdir.mkdir(exist_ok=True)
            dest = qdir / Path(file_path).name
            Path(file_path).rename(dest)
            self.update_signal.emit(f"  -> Quarantaine: {dest}")
        except Exception as e:
            self.update_signal.emit(f"  -> Erreur quarantaine: {e}")

    def stop(self):
        self.stop_flag = True


class VirusScanner(QMainWindow):
    """Antivirus Scanner pour Windows"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGC Antivirus - Windows")
        self.setGeometry(100, 100, 950, 700)
        self.scan_thread = None
        self.scan_history: List[str] = []
        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.addTab(self.create_scanner_tab(), "Scanner")
        self.tabs.addTab(self.create_quarantine_tab(), "Quarantaine")
        self.tabs.addTab(self.create_history_tab(), "Historique")

    def create_scanner_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()

        header = QLabel("EGC Antivirus Scanner")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        layout.addWidget(QLabel("Type de scan:"))
        self.scan_type = QComboBox()
        self.scan_type.addItems(["Scan rapide", "Scan complet", "Scan personnalise"])
        layout.addWidget(self.scan_type)

        btn_layout = QHBoxLayout()
        self.scan_button = QPushButton("Demarrer le scan")
        self.scan_button.setStyleSheet(
            "QPushButton { background-color: #89b4fa; color: #1e1e2e; padding: 12px; "
            "border-radius: 6px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #74c7ec; }"
        )
        self.scan_button.clicked.connect(self.start_scan)
        btn_layout.addWidget(self.scan_button)

        self.stop_button = QPushButton("Arreter")
        self.stop_button.setStyleSheet(
            "QPushButton { background-color: #f38ba8; color: #1e1e2e; padding: 12px; "
            "border-radius: 6px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #eba0ac; }"
        )
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        btn_layout.addWidget(self.stop_button)
        layout.addLayout(btn_layout)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.status_label = QLabel("Pret")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        widget.setLayout(layout)
        return widget

    def create_quarantine_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        header = QLabel("Fichiers en quarantaine")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(header)
        self.quarantine_list = QListWidget()
        layout.addWidget(self.quarantine_list)
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Rafraichir")
        refresh_btn.setStyleSheet(
            "QPushButton { background-color: #89b4fa; color: #1e1e2e; padding: 8px 16px; "
            "border-radius: 6px; font-weight: bold; }"
        )
        refresh_btn.clicked.connect(self.refresh_quarantine)
        btn_layout.addWidget(refresh_btn)
        delete_btn = QPushButton("Supprimer selection")
        delete_btn.setStyleSheet(
            "QPushButton { background-color: #f38ba8; color: #1e1e2e; padding: 8px 16px; "
            "border-radius: 6px; font-weight: bold; }"
        )
        delete_btn.clicked.connect(self.delete_quarantined)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        return widget

    def create_history_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        header = QLabel("Historique des scans")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(header)
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        widget.setLayout(layout)
        return widget

    def start_scan(self):
        directory = QFileDialog.getExistingDirectory(self, "Selectionnez le dossier")
        if directory:
            self.progress.setValue(0)
            self.result_text.clear()
            self.result_text.append("Scan en cours...\n")
            self.status_label.setText(f"Scan de {directory}...")
            self.scan_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.scan_thread = ScanThread(directory, self.scan_type.currentText())
            self.scan_thread.update_signal.connect(self.result_text.append)
            self.scan_thread.progress_signal.connect(self.progress.setValue)
            self.scan_thread.finished_signal.connect(self.scan_finished)
            self.scan_thread.start()

    def stop_scan(self):
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.result_text.append("\nScan arrete par l'utilisateur")
            self.status_label.setText("Scan arrete")
            self.scan_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def scan_finished(self, total: int, infected: int):
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Termine - {total} fichiers, {infected} menaces")
        from datetime import datetime
        entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {total} fichiers, {infected} menaces"
        self.scan_history.append(entry)
        self.history_text.append(entry)

    def refresh_quarantine(self):
        self.quarantine_list.clear()
        home = Path.home()
        for qdir in home.rglob(QUARANTINE_DIR):
            if qdir.is_dir():
                for f in qdir.iterdir():
                    self.quarantine_list.addItem(QListWidgetItem(str(f)))

    def delete_quarantined(self):
        item = self.quarantine_list.currentItem()
        if item:
            path = Path(item.text())
            reply = QMessageBox.question(
                self, "Confirmation",
                f"Supprimer definitivement ?\n{path.name}",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    path.unlink()
                    self.refresh_quarantine()
                except Exception as e:
                    QMessageBox.warning(self, "Erreur", str(e))

    def closeEvent(self, event):
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()
        event.accept()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setFont(QFont("Segoe UI", 10))
    scanner = VirusScanner()
    scanner.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
