"""Navigateur web optimisé pour Linux"""
import sys
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QTabWidget, QToolBar, QAction
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

logger = logging.getLogger(__name__)


class OptimizedBrowser(QMainWindow):
    """Navigateur web léger"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGC Navigateur - Optimisé pour Linux")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()
        logger.info("Navigateur web démarré")

    def init_ui(self):
        """Initialise l'interface"""
        # Créer les onglets
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Créer la barre d'outils
        toolbar = self.addToolBar("Navigation")
        toolbar.addAction("➕ Nouvel Onglet", self.add_tab)

        self.add_tab()

    def add_tab(self):
        """Ajoute un nouvel onglet"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Barre d'URL
        url_bar = QLineEdit()
        url_bar.setPlaceholderText("Entrez une URL...")
        url_bar.returnPressed.connect(lambda: self.load_url(url_bar, browser))
        layout.addWidget(url_bar)

        # Vue navigateur
        browser = QWebEngineView()
        browser.setUrl(QUrl("https://www.google.com"))
        layout.addWidget(browser)

        widget.setLayout(layout)
        self.tabs.addTab(widget, "Nouvel Onglet")
        self.tabs.setCurrentWidget(widget)
        logger.info("Nouvel onglet ajouté")

    def load_url(self, url_bar: QLineEdit, browser: QWebEngineView):
        """Charge l'URL"""
        url = url_bar.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        browser.setUrl(QUrl(url))
        logger.info(f"URL chargée: {url}")

    def close_tab(self, index: int):
        """Ferme un onglet"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            logger.info(f"Onglet {index} fermé")
