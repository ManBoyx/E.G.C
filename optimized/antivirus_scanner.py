"""Optimized Antivirus Scanner with Performance Improvements"""
import sys
import os
import time
import subprocess
import ctypes
from pathlib import Path
from typing import List, Set
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit,
    QLabel, QFileDialog, QProgressBar, QComboBox, QLineEdit, QTabWidget,
    QSystemTrayIcon, QMenu, QAction, QDateTimeEdit, QTableWidget, QTableWidgetItem, QCheckBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QDateTime, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Virus signatures
VIRUS_SIGNATURES: Set[bytes] = {b"eicar", b"malicious"}
QUARANTINE_DIR = "quarantine"


class ScanThread(QThread):
    """Optimized scan thread with better resource management"""
    update_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self, directory: str, scan_type: str):
        super().__init__()
        self.directory = directory
        self.scan_type = scan_type
        self.stop_flag = False
        self.infected_files: List[str] = []

    def run(self):
        """Execute the scan"""
        self.infected_files = self.scan_files(self.directory)
        if self.infected_files:
            self.update_signal.emit("Fichiers infectés trouvés :")
            for file in self.infected_files:
                if self.stop_flag:
                    break
                self.update_signal.emit(f"- {file}")
                self.quarantine_file(file)
        else:
            self.update_signal.emit("Aucun fichier infecté trouvé.")

    def scan_files(self, directory: str) -> List[str]:
        """Scan directory for infected files with optimized I/O"""
        infected_files = []
        try:
            files = list(Path(directory).rglob('*'))
            total_files = len([f for f in files if f.is_file()])
            scanned_files = 0

            for file_path in files:
                if self.stop_flag or not file_path.is_file():
                    continue
                if self.scan_file(str(file_path)):
                    infected_files.append(str(file_path))
                scanned_files += 1
                progress = int((scanned_files / total_files) * 100) if total_files > 0 else 0
                self.progress_signal.emit(progress)
                time.sleep(0.001)  # Reduced sleep time
        except Exception as e:
            self.update_signal.emit(f"Erreur lors du scan: {e}")
        return infected_files

    def scan_file(self, file_path: str) -> bool:
        """Check if file contains virus signatures"""
        try:
            with open(file_path, 'rb') as f:
                chunk_size = 8192
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    for signature in VIRUS_SIGNATURES:
                        if signature in chunk:
                            return True
        except (OSError, IOError):
            pass
        return False

    def quarantine_file(self, file_path: str):
        """Move infected file to quarantine"""
        try:
            quarantine_path = Path(file_path).parent / QUARANTINE_DIR
            quarantine_path.mkdir(exist_ok=True)
            dest = quarantine_path / Path(file_path).name
            Path(file_path).rename(dest)
            self.update_signal.emit(f"Fichier en quarantaine: {file_path}")
        except Exception as e:
            self.update_signal.emit(f"Erreur quarantaine: {e}")

    def stop(self):
        """Stop the scan"""
        self.stop_flag = True


class VirusScanner(QMainWindow):
    """Main antivirus scanner application"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antivirus Optimisé")
        self.setGeometry(100, 100, 900, 700)
        self.scan_thread = None
        self.dark_mode = False
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Scanner tab
        scan_widget = self.create_scanner_tab()
        self.tabs.addTab(scan_widget, "Antivirus")

        # Firewall tab
        firewall_widget = self.create_firewall_tab()
        self.tabs.addTab(firewall_widget, "Pare-feu")

    def create_scanner_tab(self) -> QWidget:
        """Create scanner tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Type de scan:"))
        self.scan_type = QComboBox()
        self.scan_type.addItems(["Scan rapide", "Scan complet"])
        layout.addWidget(self.scan_type)

        self.scan_button = QPushButton("Démarrer le scan")
        self.scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_button)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        widget.setLayout(layout)
        return widget

    def create_firewall_tab(self) -> QWidget:
        """Create firewall tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Gestion des adresses IP"))
        widget.setLayout(layout)
        return widget

    def start_scan(self):
        """Start a new scan"""
        directory = QFileDialog.getExistingDirectory(self, "Sélectionnez le dossier")
        if directory:
            self.progress.setValue(0)
            self.result_text.clear()
            self.scan_thread = ScanThread(directory, self.scan_type.currentText())
            self.scan_thread.update_signal.connect(self.update_result)
            self.scan_thread.progress_signal.connect(self.progress.setValue)
            self.scan_thread.start()

    def update_result(self, message: str):
        """Update result display"""
        self.result_text.append(message)

    def closeEvent(self, event):
        """Handle window close"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VirusScanner()
    window.show()
    sys.exit(app.exec_())
