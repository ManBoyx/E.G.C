"""EGC Audio Amplifier - Version Windows"""
import sys
import logging
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QSlider, QLabel, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

logger = logging.getLogger(__name__)

STYLE = """
    QMainWindow {
        background-color: #1e1e2e;
    }
    QWidget {
        background-color: #1e1e2e;
        color: #cdd6f4;
    }
    QGroupBox {
        border: 1px solid #45475a;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 16px;
        color: #cdd6f4;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
    }
    QSlider::groove:horizontal {
        height: 8px;
        background: #313244;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #89b4fa;
        width: 20px;
        height: 20px;
        margin: -6px 0;
        border-radius: 10px;
    }
    QSlider::sub-page:horizontal {
        background: #89b4fa;
        border-radius: 4px;
    }
    QLabel {
        color: #cdd6f4;
    }
"""


class SoundAmplifier(QMainWindow):
    """Amplificateur audio pour Windows"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGC Amplificateur Audio - Windows")
        self.setGeometry(100, 100, 500, 400)
        self.stream = None
        self.is_running = False
        self.init_ui()

    def init_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()

        header = QLabel("EGC Amplificateur Audio")
        header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #89b4fa; padding: 10px;")
        layout.addWidget(header)

        amp_group = QGroupBox("Controle de l'amplification")
        amp_layout = QVBoxLayout()

        amp_layout.addWidget(QLabel("Niveau d'amplification:"))

        slider_layout = QHBoxLayout()
        self.min_label = QLabel("1x")
        self.min_label.setStyleSheet("font-size: 12px;")
        slider_layout.addWidget(self.min_label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 10)
        self.slider.setValue(5)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_level_label)
        slider_layout.addWidget(self.slider)

        self.max_label = QLabel("10x")
        self.max_label.setStyleSheet("font-size: 12px;")
        slider_layout.addWidget(self.max_label)

        amp_layout.addLayout(slider_layout)

        self.level_label = QLabel("Niveau: 5x (normal)")
        self.level_label.setAlignment(Qt.AlignCenter)
        self.level_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.level_label.setStyleSheet("color: #89b4fa;")
        amp_layout.addWidget(self.level_label)

        amp_group.setLayout(amp_layout)
        layout.addWidget(amp_group)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Demarrer")
        self.start_btn.setStyleSheet(
            "QPushButton { background-color: #a6e3a1; color: #1e1e2e; padding: 12px; "
            "border-radius: 6px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #94e2d5; }"
            "QPushButton:disabled { background-color: #45475a; color: #6c7086; }"
        )
        self.start_btn.clicked.connect(self.start_amplification)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Arreter")
        self.stop_btn.setStyleSheet(
            "QPushButton { background-color: #f38ba8; color: #1e1e2e; padding: 12px; "
            "border-radius: 6px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #eba0ac; }"
            "QPushButton:disabled { background-color: #45475a; color: #6c7086; }"
        )
        self.stop_btn.clicked.connect(self.stop_amplification)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        self.status_label = QLabel("Etat: Arrete")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        if not SOUNDDEVICE_AVAILABLE:
            warning = QLabel("Module 'sounddevice' non installe.\n"
                             "Installez-le avec: pip install sounddevice")
            warning.setStyleSheet("color: #f38ba8; padding: 10px;")
            warning.setAlignment(Qt.AlignCenter)
            layout.addWidget(warning)
            self.start_btn.setEnabled(False)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_level_label(self, value: int):
        descriptions = {
            1: "tres faible", 2: "faible", 3: "modere-",
            4: "modere", 5: "normal", 6: "modere+",
            7: "fort", 8: "tres fort", 9: "intense", 10: "maximum"
        }
        desc = descriptions.get(value, "")
        self.level_label.setText(f"Niveau: {value}x ({desc})")

        if value <= 3:
            color = "#a6e3a1"
        elif value <= 6:
            color = "#89b4fa"
        elif value <= 8:
            color = "#fab387"
        else:
            color = "#f38ba8"
        self.level_label.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {color};"
        )

    def start_amplification(self):
        if not SOUNDDEVICE_AVAILABLE:
            QMessageBox.warning(self, "Erreur",
                                "Module 'sounddevice' non installe.\n"
                                "pip install sounddevice")
            return
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.slider.setEnabled(False)
        factor = self.slider.value() / 5.0

        def callback(indata, outdata, frames, time_info, status):
            if status:
                logger.warning(f"Audio: {status}")
            outdata[:] = np.clip(indata * factor, -1, 1)

        try:
            self.stream = sd.Stream(callback=callback)
            self.stream.start()
            self.is_running = True
            self.status_label.setText(f"Etat: En cours ({self.slider.value()}x)")
            self.status_label.setStyleSheet("color: #a6e3a1;")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de demarrer:\n{e}")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.slider.setEnabled(True)

    def stop_amplification(self):
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logger.error(f"Erreur arret: {e}")
            self.stream = None
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.slider.setEnabled(True)
        self.status_label.setText("Etat: Arrete")
        self.status_label.setStyleSheet("color: #6c7086;")

    def closeEvent(self, event):
        if self.is_running:
            self.stop_amplification()
        event.accept()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setFont(QFont("Segoe UI", 10))
    amplifier = SoundAmplifier()
    amplifier.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
