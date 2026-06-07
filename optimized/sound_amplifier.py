"""Optimized Sound Amplifier"""
import sys
import numpy as np
try:
    import sounddevice as sd
except ImportError:
    sd = None

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider, QLabel
)
from PyQt5.QtCore import Qt


class SoundAmplifier(QMainWindow):
    """Optimized audio amplifier with error handling"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Amplificateur de Son")
        self.setGeometry(100, 100, 400, 250)
        self.stream = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Niveau d'amplification:"))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 10)
        self.slider.setValue(5)
        layout.addWidget(self.slider)

        self.start_btn = QPushButton("Démarrer")
        self.start_btn.clicked.connect(self.start_amplification)
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Arrêter")
        self.stop_btn.clicked.connect(self.stop_amplification)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start_amplification(self):
        """Start audio amplification"""
        if not sd:
            return
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        factor = self.slider.value() / 5.0

        def callback(indata, outdata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")
            outdata[:] = np.clip(indata * factor, -1, 1)

        try:
            self.stream = sd.Stream(callback=callback)
            self.stream.start()
        except Exception as e:
            print(f"Erreur: {e}")

    def stop_amplification(self):
        """Stop audio amplification"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoundAmplifier()
    window.show()
    sys.exit(app.exec_())
