"""Navigateur web optimisé pour Linux"""
import logging
from PyQt5.QtWidgets import (
    QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QTabWidget, QToolBar, QAction, QMenu,
    QMenuBar, QMessageBox, QStatusBar
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt

from src.common.app import EGCMainWindow, run_pyqt_app

logger = logging.getLogger(__name__)

DEFAULT_HOME = "https://www.google.com"
SEARCH_ENGINE = "https://search.brave.com/search?q="


class BrowserTab(QWidget):
    """Widget pour un onglet du navigateur"""
    def __init__(self, url: str = DEFAULT_HOME):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        nav_layout = QHBoxLayout()

        self.back_btn = QPushButton("◀")
        self.back_btn.setFixedWidth(35)
        self.back_btn.setToolTip("Retour")
        nav_layout.addWidget(self.back_btn)

        self.forward_btn = QPushButton("▶")
        self.forward_btn.setFixedWidth(35)
        self.forward_btn.setToolTip("Avancer")
        nav_layout.addWidget(self.forward_btn)

        self.reload_btn = QPushButton("⟳")
        self.reload_btn.setFixedWidth(35)
        self.reload_btn.setToolTip("Recharger")
        nav_layout.addWidget(self.reload_btn)

        self.home_btn = QPushButton("🏠")
        self.home_btn.setFixedWidth(35)
        self.home_btn.setToolTip("Accueil")
        nav_layout.addWidget(self.home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Entrez une URL ou une recherche...")
        self.url_bar.setStyleSheet(
            "QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 4px; }"
        )
        nav_layout.addWidget(self.url_bar)

        layout.addLayout(nav_layout)

        self.browser = QWebEngineView()
        self.browser.settings().setAttribute(
            QWebEngineSettings.PluginsEnabled, True
        )
        layout.addWidget(self.browser)

        self.setLayout(layout)

        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)
        self.home_btn.clicked.connect(self.go_home)
        self.url_bar.returnPressed.connect(self.load_url)
        self.browser.urlChanged.connect(self.on_url_changed)
        self.browser.titleChanged.connect(self.on_title_changed)

        self.browser.setUrl(QUrl(url))

    def load_url(self):
        """Charge l'URL ou fait une recherche"""
        text = self.url_bar.text().strip()
        if not text:
            return
        if '.' in text and ' ' not in text:
            if not text.startswith(("http://", "https://")):
                text = "https://" + text
            self.browser.setUrl(QUrl(text))
        else:
            self.browser.setUrl(QUrl(SEARCH_ENGINE + text))
        logger.info(f"Navigation: {text}")

    def go_home(self):
        """Retour à la page d'accueil"""
        self.browser.setUrl(QUrl(DEFAULT_HOME))

    def on_url_changed(self, url: QUrl):
        """Met à jour la barre d'URL"""
        self.url_bar.setText(url.toString())

    def on_title_changed(self, title: str):
        """Signale le changement de titre"""
        pass


class OptimizedBrowser(EGCMainWindow):
    """Navigateur web léger avec onglets"""

    window_title = "EGC Navigateur - Optimisé pour Linux"
    window_size = (100, 100, 1200, 800)

    def init_ui(self):
        """Initialise l'interface"""
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tabs)

        self.create_menu()

        toolbar = self.addToolBar("Navigation")
        toolbar.addAction("➕Nouvel Onglet", self.add_tab)

        self.statusBar().showMessage("Prêt")

        self.add_tab()

    def create_menu(self):
        """Crée la barre de menus"""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Fichier")
        new_tab_action = QAction("Nouvel Onglet", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self.add_tab)
        file_menu.addAction(new_tab_action)

        close_tab_action = QAction("Fermer l'Onglet", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(self.close_current_tab)
        file_menu.addAction(close_tab_action)

        file_menu.addSeparator()
        exit_action = QAction("Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("Affichage")
        fullscreen_action = QAction("Plein Écran", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        help_menu = menu_bar.addMenu("Aide")
        about_action = QAction("À Propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def add_tab(self, url: str = DEFAULT_HOME):
        """Ajoute un nouvel onglet"""
        tab = BrowserTab(url)
        tab.on_title_changed = lambda title, t=tab: self.update_tab_title(t, title)
        tab.browser.titleChanged.connect(
            lambda title, t=tab: self.update_tab_title(t, title)
        )
        index = self.tabs.addTab(tab, "Nouvel Onglet")
        self.tabs.setCurrentIndex(index)
        logger.info("Nouvel onglet ajouté")

    def update_tab_title(self, tab: BrowserTab, title: str):
        """Met à jour le titre de l'onglet"""
        index = self.tabs.indexOf(tab)
        if index >= 0:
            display_title = title[:25] + "..." if len(title) > 25 else title
            self.tabs.setTabText(index, display_title)

    def close_tab(self, index: int):
        """Ferme un onglet"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            logger.info(f"Onglet {index} fermé")

    def close_current_tab(self):
        """Ferme l'onglet courant"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(self.tabs.currentIndex())

    def on_tab_changed(self, index: int):
        """Met à jour le titre de la fenêtre"""
        tab = self.tabs.widget(index)
        if isinstance(tab, BrowserTab):
            title = tab.browser.title()
            if title:
                self.setWindowTitle(f"{title} - EGC Navigateur")
            self.statusBar().showMessage(tab.url_bar.text())

    def toggle_fullscreen(self):
        """Bascule en plein écran"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_about(self):
        """Affiche la boîte À Propos"""
        QMessageBox.about(
            self, "À Propos",
            "EGC Navigateur Web v1.0.0\n\n"
            "Navigateur web optimisé pour Linux\n"
            "Auteur: ManBoyx"
        )


def main():
    """Point d'entrée pour console_scripts."""
    run_pyqt_app(OptimizedBrowser)
