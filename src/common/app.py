"""Utilitaires de lancement d'applications pour EGC Suite"""
import sys
import logging
import tkinter as tk
from typing import Callable, Type

from PyQt5.QtWidgets import QApplication, QMainWindow

from src.common.logging_config import setup_logging

logger = logging.getLogger(__name__)


class EGCMainWindow(QMainWindow):
    """Classe de base pour les fenêtres principales EGC Suite.

    Sous-classes doivent définir ``window_title`` et ``window_size``,
    puis implémenter ``init_ui()``.
    """

    window_title: str = "EGC Application"
    window_size: tuple = (100, 100, 800, 600)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(self.window_title)
        self.setGeometry(*self.window_size)
        self.init_ui()
        logger.info("%s démarré", self.window_title)

    def init_ui(self) -> None:
        raise NotImplementedError


def run_pyqt_app(window_class: Type[QMainWindow]) -> None:
    """Lance une application PyQt5 avec la configuration standard EGC."""
    setup_logging()
    try:
        app = QApplication(sys.argv)
        window = window_class()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error("Erreur au démarrage: %s", e)
        sys.exit(1)


def run_tk_app(app_factory: Callable[[tk.Tk], object]) -> None:
    """Lance une application Tkinter avec la configuration standard EGC."""
    setup_logging()
    try:
        root = tk.Tk()
        app_factory(root)
        root.mainloop()
    except Exception as e:
        logger.error("Erreur au démarrage: %s", e)
        sys.exit(1)
