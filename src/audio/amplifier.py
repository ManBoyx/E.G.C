"""Amplificateur audio optimisé pour Linux"""
import logging
import numpy as np
from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QPushButton, QSlider, QLabel
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
    window_size = (100, 100, 400, 250)

    def __init__(self):
        self.stream = None
        super().__init__()

    def init_ui(self):
        """Initialise l'interface"""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Niveau d'amplification:"))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 10)
        self.slider.setValue(5)
        layout.addWidget(self.slider)

        self.start_btn = QPushButton("▶️ Démarrer")
        self.start_btn.clicked.connect(self.start_amplification)
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ Arrêter")
        self.stop_btn.clicked.connect(self.stop_amplification)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start_amplification(self):
        """Démarre l'amplification"""
        if not SOUNDDEVICE_AVAILABLE:
            logger.error("sounddevice non disponible")
            return
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        factor = self.slider.value() / 5.0

        def callback(indata, outdata, frames, time_info, status):
            if status:
                logger.warning(f"Statut audio: {status}")
            outdata[:] = np.clip(indata * factor, -1, 1)

        try:
            self.stream = sd.Stream(callback=callback)
            self.stream.start()
            logger.info("Amplification démarrée")
        except Exception as e:
            logger.error(f"Erreur amplification: {e}")

    def stop_amplification(self):
        """Arrête l'amplification"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        logger.info("Amplification arrêtée")


def main():
    """Point d'entrée pour console_scripts."""
    run_pyqt_app(SoundAmplifier)
