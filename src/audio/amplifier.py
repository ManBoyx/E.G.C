"""Amplificateur audio optimisé pour Linux"""
import logging
import numpy as np
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QSlider, QLabel, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt

from src.common.app import EGCMainWindow, run_pyqt_app

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

logger = logging.getLogger(__name__)


class SoundAmplifier(EGCMainWindow):
    """Amplificateur audio optimisé"""

    window_title = "EGC Amplificateur Audio - Optimisé pour Linux"
    window_size = (100, 100, 450, 350)

    def __init__(self):
        self.stream = None
        self.is_running = False
        super().__init__()

    def init_ui(self):
        """Initialise l'interface"""
        widget = QWidget()
        layout = QVBoxLayout()

        header = QLabel("EGC Amplificateur Audio")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Groupe amplification
        amp_group = QGroupBox("Contrôle de l'amplification")
        amp_layout = QVBoxLayout()

        amp_layout.addWidget(QLabel("Niveau d'amplification:"))

        slider_layout = QHBoxLayout()
        self.min_label = QLabel("1x")
        slider_layout.addWidget(self.min_label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 10)
        self.slider.setValue(5)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_level_label)
        slider_layout.addWidget(self.slider)

        self.max_label = QLabel("10x")
        slider_layout.addWidget(self.max_label)

        amp_layout.addLayout(slider_layout)

        self.level_label = QLabel("Niveau: 5x (normal)")
        self.level_label.setAlignment(Qt.AlignCenter)
        self.level_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        amp_layout.addWidget(self.level_label)

        amp_group.setLayout(amp_layout)
        layout.addWidget(amp_group)

        # Boutons
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ Démarrer")
        self.start_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 10px; "
            "border-radius: 5px; font-size: 14px; }"
            "QPushButton:hover { background-color: #388E3C; }"
            "QPushButton:disabled { background-color: #ccc; }"
        )
        self.start_btn.clicked.connect(self.start_amplification)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹ Arrêter")
        self.stop_btn.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; padding: 10px; "
            "border-radius: 5px; font-size: 14px; }"
            "QPushButton:hover { background-color: #d32f2f; }"
            "QPushButton:disabled { background-color: #ccc; }"
        )
        self.stop_btn.clicked.connect(self.stop_amplification)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)

        layout.addLayout(btn_layout)

        # Status
        self.status_label = QLabel("État: Arrêté")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        if not SOUNDDEVICE_AVAILABLE:
            warning = QLabel("⚠ Module 'sounddevice' non installé.\n"
                             "Installez-le avec: pip3 install sounddevice")
            warning.setStyleSheet("color: #f44336; padding: 10px;")
            warning.setAlignment(Qt.AlignCenter)
            layout.addWidget(warning)
            self.start_btn.setEnabled(False)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_level_label(self, value: int):
        """Met à jour l'étiquette du niveau"""
        descriptions = {
            1: "très faible", 2: "faible", 3: "modéré-",
            4: "modéré", 5: "normal", 6: "modéré+",
            7: "fort", 8: "très fort", 9: "intense", 10: "maximum"
        }
        desc = descriptions.get(value, "")
        self.level_label.setText(f"Niveau: {value}x ({desc})")

        if value <= 3:
            color = "#4CAF50"
        elif value <= 6:
            color = "#2196F3"
        elif value <= 8:
            color = "#FF9800"
        else:
            color = "#f44336"
        self.level_label.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {color};"
        )

    def start_amplification(self):
        """Démarre l'amplification"""
        if not SOUNDDEVICE_AVAILABLE:
            QMessageBox.warning(
                self, "Erreur",
                "Le module 'sounddevice' n'est pas installé.\n"
                "Installez-le avec: pip3 install sounddevice"
            )
            return

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.slider.setEnabled(False)
        factor = self.slider.value() / 5.0

        def callback(indata, outdata, frames, time_info, status):
            if status:
                logger.warning(f"Statut audio: {status}")
            outdata[:] = np.clip(indata * factor, -1, 1)

        try:
            self.stream = sd.Stream(callback=callback)
            self.stream.start()
            self.is_running = True
            self.status_label.setText(f"État: En cours (amplification {self.slider.value()}x)")
            self.status_label.setStyleSheet("color: #4CAF50;")
            logger.info(f"Amplification démarrée (facteur: {factor})")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de démarrer l'amplification:\n{e}")
            logger.error(f"Erreur amplification: {e}")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.slider.setEnabled(True)

    def stop_amplification(self):
        """Arrête l'amplification"""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logger.error(f"Erreur arrêt: {e}")
            self.stream = None
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.slider.setEnabled(True)
        self.status_label.setText("État: Arrêté")
        self.status_label.setStyleSheet("color: #666;")
        logger.info("Amplification arrêtée")

    def closeEvent(self, event):
        """Gère la fermeture propre"""
        if self.is_running:
            self.stop_amplification()
        event.accept()


def main():
    """Point d'entrée pour console_scripts."""
    run_pyqt_app(SoundAmplifier)
