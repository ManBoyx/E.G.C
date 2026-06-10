"""Scanner de virus optimisé pour Linux"""
import sys
import logging
from pathlib import Path
from typing import List, Set
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTextEdit, QLabel, QFileDialog, QProgressBar,
    QComboBox, QTabWidget, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

logger = logging.getLogger(__name__)

VIRUS_SIGNATURES: Set[bytes] = {b"eicar", b"malicious"}
QUARANTINE_DIR = ".quarantine"


class ScanThread(QThread):
    """Thread optimisé pour le scan"""
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
        """Exécute le scan"""
        try:
            self.update_signal.emit(f"Scan de: {self.directory}")
            self.infected_files = self.scan_files(self.directory)
            total = self._count_files(self.directory)
            if self.infected_files:
                self.update_signal.emit(
                    f"⚠️ {len(self.infected_files)} fichier(s) infecté(s) trouvé(s)"
                )
                for file in self.infected_files:
                    if self.stop_flag:
                        break
                    self.update_signal.emit(f"  🔴 {file}")
                    self.quarantine_file(file)
            else:
                self.update_signal.emit("✅ Aucun fichier infecté trouvé")
            self.finished_signal.emit(total, len(self.infected_files))
        except Exception as e:
            self.update_signal.emit(f"❌ Erreur: {str(e)}")
            logger.error(f"Erreur lors du scan: {e}")

    def _count_files(self, directory: str) -> int:
        """Compte le nombre de fichiers dans le répertoire"""
        try:
            return len([f for f in Path(directory).rglob('*') if f.is_file()])
        except Exception:
            return 0

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
            self.update_signal.emit(f"❌ Erreur lors du scan du répertoire: {e}")
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
        except PermissionError:
            self.update_signal.emit(f"  ⚠️ Accès refusé: {file_path}")
            logger.warning(f"Permission denied: {file_path}")
        except (OSError, IOError) as e:
            self.update_signal.emit(f"  ⚠️ Impossible de lire: {file_path}")
            logger.warning(f"Cannot read file {file_path}: {e}")
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
        self.scan_history: List[str] = []
        self.init_ui()
        logger.info("Antivirus Scanner démarré")

    def init_ui(self):
        """Initialise l'interface"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        scan_widget = self.create_scanner_tab()
        self.tabs.addTab(scan_widget, "🔍 Scanner")

        quarantine_widget = self.create_quarantine_tab()
        self.tabs.addTab(quarantine_widget, "🔒 Quarantaine")

        history_widget = self.create_history_tab()
        self.tabs.addTab(history_widget, "📋 Historique")

    def create_scanner_tab(self) -> QWidget:
        """Crée l'onglet scanner"""
        widget = QWidget()
        layout = QVBoxLayout()

        header = QLabel("EGC Antivirus Scanner")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        layout.addWidget(QLabel("Type de scan:"))
        self.scan_type = QComboBox()
        self.scan_type.addItems(["Scan rapide", "Scan complet", "Scan personnalisé"])
        layout.addWidget(self.scan_type)

        btn_layout = QHBoxLayout()
        self.scan_button = QPushButton("🔍 Démarrer le scan")
        self.scan_button.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; padding: 10px; "
            "border-radius: 5px; font-size: 14px; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        self.scan_button.clicked.connect(self.start_scan)
        btn_layout.addWidget(self.scan_button)

        self.stop_button = QPushButton("⏹️ Arrêter")
        self.stop_button.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; padding: 10px; "
            "border-radius: 5px; font-size: 14px; }"
            "QPushButton:hover { background-color: #d32f2f; }"
        )
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        btn_layout.addWidget(self.stop_button)

        layout.addLayout(btn_layout)

        self.progress = QProgressBar()
        self.progress.setStyleSheet(
            "QProgressBar { border: 1px solid grey; border-radius: 5px; text-align: center; }"
            "QProgressBar::chunk { background-color: #4CAF50; }"
        )
        layout.addWidget(self.progress)

        self.status_label = QLabel("Prêt")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        widget.setLayout(layout)
        return widget

    def create_quarantine_tab(self) -> QWidget:
        """Crée l'onglet quarantaine"""
        widget = QWidget()
        layout = QVBoxLayout()

        header = QLabel("Fichiers en quarantaine")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        self.quarantine_list = QListWidget()
        layout.addWidget(self.quarantine_list)

        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Rafraîchir")
        refresh_btn.clicked.connect(self.refresh_quarantine)
        btn_layout.addWidget(refresh_btn)

        delete_btn = QPushButton("🗑️ Supprimer sélection")
        delete_btn.clicked.connect(self.delete_quarantined)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)

        widget.setLayout(layout)
        return widget

    def create_history_tab(self) -> QWidget:
        """Crée l'onglet historique"""
        widget = QWidget()
        layout = QVBoxLayout()

        header = QLabel("Historique des scans")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)

        widget.setLayout(layout)
        return widget

    def start_scan(self):
        """Démarre un nouveau scan"""
        directory = QFileDialog.getExistingDirectory(self, "Sélectionnez le dossier")
        if directory:
            self.progress.setValue(0)
            self.result_text.clear()
            self.result_text.append("🔄 Scan en cours...\n")
            self.status_label.setText(f"Scan de {directory}...")
            self.scan_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            self.scan_thread = ScanThread(directory, self.scan_type.currentText())
            self.scan_thread.update_signal.connect(self.update_result)
            self.scan_thread.progress_signal.connect(self.progress.setValue)
            self.scan_thread.finished_signal.connect(self.scan_finished)
            self.scan_thread.start()

    def stop_scan(self):
        """Arrête le scan en cours"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.result_text.append("\n⏹️ Scan arrêté par l'utilisateur")
            self.status_label.setText("Scan arrêté")
            self.scan_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def scan_finished(self, total: int, infected: int):
        """Appelé quand le scan est terminé"""
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Terminé - {total} fichiers scannés, {infected} infectés")
        from datetime import datetime
        entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {total} fichiers, {infected} infectés"
        self.scan_history.append(entry)
        self.history_text.append(entry)

    def update_result(self, message: str):
        """Met à jour l'affichage"""
        self.result_text.append(message)

    def refresh_quarantine(self):
        """Rafraîchit la liste des fichiers en quarantaine"""
        self.quarantine_list.clear()
        home = Path.home()
        for qdir in home.rglob(QUARANTINE_DIR):
            if qdir.is_dir():
                for f in qdir.iterdir():
                    self.quarantine_list.addItem(QListWidgetItem(str(f)))

    def delete_quarantined(self):
        """Supprime le fichier sélectionné de la quarantaine"""
        item = self.quarantine_list.currentItem()
        if item:
            path = Path(item.text())
            reply = QMessageBox.question(
                self, "Confirmation",
                f"Supprimer définitivement ?\n{path.name}",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    path.unlink()
                    self.refresh_quarantine()
                except Exception as e:
                    QMessageBox.warning(self, "Erreur", str(e))

    def closeEvent(self, event):
        """Gère la fermeture"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()
        event.accept()


def main():
    """Point d'entrée principal"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app = QApplication(sys.argv)
    scanner = VirusScanner()
    scanner.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
