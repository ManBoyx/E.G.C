import sys
import sounddevice as sd # type: ignore
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider, QLabel
from PyQt5.QtCore import Qt

class SoundAmplifier(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Amplificateur de Son")
        self.setGeometry(100, 100, 300, 200)

        self.layout = QVBoxLayout()

        self.label = QLabel("Niveau d'amplification :")
        self.layout.addWidget(self.label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(10)
        self.slider.setValue(1)
        self.layout.addWidget(self.slider)

        self.start_button = QPushButton("Démarrer l'amplification")
        self.start_button.clicked.connect(self.start_amplification)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Arrêter l'amplification")
        self.stop_button.clicked.connect(self.stop_amplification)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.stream = None

    def start_amplification(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.amplification_factor = self.slider.value()

        def audio_callback(indata, outdata, frames, time, status):
            if status:
                print(status)
            # Assure-toi que les formes des tableaux correspondent
            outdata[:, :indata.shape[1]] = indata * self.amplification_factor

        self.stream = sd.Stream(callback=audio_callback)
        self.stream.start()

    def stop_amplification(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.stream:
            self.stream.stop()
            self.stream.close()

def main():
    app = QApplication(sys.argv)
    window = SoundAmplifier()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
