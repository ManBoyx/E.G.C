"""Scanner de virus optimisé pour Linux"""
import sys
import logging
from pathlib import Path
from typing import List, Set
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit,
    QLabel, QFileDialog, QProgressBar, QComboBox, QTabWidget
)
from PyQt5.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)

VIRUS_SIGNATURES: Set[bytes] = {b"eicar", b"malicious"}
QUARANTINE_DIR = ".quarantine"


class ScanThread(QThread):
    """Thread optimisé pour le scan"""
    update_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self, directory: str, scan_type: str):
        super().__init__()
        self.directory = directory
        self.scan_type = scan_type
        self.stop_flag = False
        self.infected_files: List[str] = []

    def run(self):
        """Exécute le scan"""
        try:
            self.infected_files = self.scan_files(self.directory)
            if self.infected_files:
                self.update_signal.emit(f"⚠️ {len(self.infected_files)} fichier(s) infecté(s) trouvé(s)")
                for file in self.infected_files:
                    if self.stop_flag:
                        break
                    self.update_signal.emit(f"  🔴 {file}")
                    self.quarantine_file(file)
            else:
                self.update_signal.emit("✅ Aucun fichier infecté trouvé")
        except Exception as e:
            self.update_signal.emit(f"❌ Erreur: {str(e)}")
            logger.error(f"Erreur lors du scan: {e}")

    def scan_files(self, directory: str) -> List[str]:
        """Scan le répertoire avec optimisation I/O"""
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
        """Vérifie si le fichier contient des signatures"""
        try:
            with open(file_path, 'rb') as f:
                chunk_size = 8192
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    for sig in VIRUS_SIGNATURES:
                        if sig in chunk:
                            return True
        except (OSError, IOError):
            pass
        return False

    def quarantine_file(self, file_path: str):
        """Déplace le fichier en quarantaine"""
        try:
            qdir = Path(file_path).parent / QUARANTINE_DIR
            qdir.mkdir(exist_ok=True)
            dest = qdir / Path(file_path).name
            Path(file_path).rename(dest)
            self.update_signal.emit(f"  ✓ Fichier en quarantaine: {file_path}")
            logger.info(f"Quarantaine: {file_path}")
        except Exception as e:
            self.update_signal.emit(f"  ✗ Erreur quarantaine: {e}")
            logger.error(f"Erreur quarantaine: {e}")

    def stop(self):
        """Arrête le scan"""
        self.stop_flag = True


class VirusScanner(QMainWindow):
    """Application scanner antivirus"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGC Antivirus - Optimisé pour Linux")
        self.setGeometry(100, 100, 900, 700)
        self.scan_thread = None
        self.init_ui()
        logger.info("Antivirus Scanner démarré")

    def init_ui(self):
        """Initialise l'interface"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Onglet Scanner
        scan_widget = self.create_scanner_tab()
        self.tabs.addTab(scan_widget, "Scanner")

    def create_scanner_tab(self) -> QWidget:
        """Crée l'onglet scanner"""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Type de scan:"))
        self.scan_type = QComboBox()
        self.scan_type.addItems(["Scan rapide", "Scan complet"])
        layout.addWidget(self.scan_type)

        self.scan_button = QPushButton("🔍 Démarrer le scan")
        self.scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_button)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        widget.setLayout(layout)
        return widget

    def start_scan(self):
        """Démarre un nouveau scan"""
        directory = QFileDialog.getExistingDirectory(self, "Sélectionnez le dossier")
        if directory:
            self.progress.setValue(0)
            self.result_text.clear()
            self.result_text.append("🔄 Scan en cours...\n")
            self.scan_thread = ScanThread(directory, self.scan_type.currentText())
            self.scan_thread.update_signal.connect(self.update_result)
            self.scan_thread.progress_signal.connect(self.progress.setValue)
            self.scan_thread.start()

    def update_result(self, message: str):
        """Met à jour l'affichage"""
        self.result_text.append(message)

    def closeEvent(self, event):
        """Gère la fermeture"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()
        event.accept()
