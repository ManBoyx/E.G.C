"""EGC Web Browser - Version Windows"""
import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QTabWidget, QAction, QMessageBox, QMenu
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QFont

logger = logging.getLogger(__name__)

DEFAULT_HOME = "https://www.google.com"
SEARCH_ENGINE = "https://search.brave.com/search?q="

STYLE = """
    QMainWindow {
        background-color: #1e1e2e;
    }
    QWidget {
        background-color: #1e1e2e;
        color: #cdd6f4;
    }
    QTabWidget::pane {
        border: none;
        background-color: #1e1e2e;
    }
    QTabBar::tab {
        background-color: #313244;
        color: #cdd6f4;
        padding: 8px 16px;
        margin: 1px;
        border-radius: 6px 6px 0 0;
        min-width: 120px;
    }
    QTabBar::tab:selected {
        background-color: #45475a;
        color: #89b4fa;
    }
    QLineEdit {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 13px;
        selection-background-color: #89b4fa;
    }
    QLineEdit:focus {
        border-color: #89b4fa;
    }
    QMenuBar {
        background-color: #1e1e2e;
        color: #cdd6f4;
    }
    QMenuBar::item:selected {
        background-color: #45475a;
    }
    QMenu {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
    }
    QMenu::item:selected {
        background-color: #45475a;
    }
    QToolBar {
        background-color: #1e1e2e;
        border: none;
        spacing: 4px;
    }
    QStatusBar {
        background-color: #181825;
        color: #a6adc8;
    }
"""

NAV_BTN_STYLE = (
    "QPushButton { background-color: #313244; color: #cdd6f4; border: none; "
    "border-radius: 4px; padding: 6px 10px; font-size: 14px; min-width: 32px; }"
    "QPushButton:hover { background-color: #45475a; }"
    "QPushButton:pressed { background-color: #585b70; }"
)


class BrowserTab(QWidget):
    """Onglet du navigateur"""
    def __init__(self, url: str = DEFAULT_HOME):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(4)

        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(4)

        for text, tooltip, callback in [
            ("<", "Retour", None),
            (">", "Avancer", None),
            ("R", "Recharger", None),
            ("H", "Accueil", None),
        ]:
            btn = QPushButton(text)
            btn.setFixedSize(32, 32)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(NAV_BTN_STYLE)
            nav_layout.addWidget(btn)
            if text == "<":
                self.back_btn = btn
            elif text == ">":
                self.forward_btn = btn
            elif text == "R":
                self.reload_btn = btn
            elif text == "H":
                self.home_btn = btn

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Entrez une URL ou recherchez sur Brave...")
        nav_layout.addWidget(self.url_bar)

        layout.addLayout(nav_layout)

        self.browser = QWebEngineView()
        self.browser.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        layout.addWidget(self.browser)

        self.setLayout(layout)

        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)
        self.home_btn.clicked.connect(self.go_home)
        self.url_bar.returnPressed.connect(self.load_url)
        self.browser.urlChanged.connect(self.on_url_changed)

        self.browser.setUrl(QUrl(url))

    def load_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if text.lower().startswith(("javascript:", "data:", "file:")):
            logger.warning(f"Protocole bloqué: {text}")
            return
        if '.' in text and ' ' not in text:
            if not text.startswith(("http://", "https://")):
                text = "https://" + text
            self.browser.setUrl(QUrl(text))
        else:
            self.browser.setUrl(QUrl(SEARCH_ENGINE + text))

    def go_home(self):
        self.browser.setUrl(QUrl(DEFAULT_HOME))

    def on_url_changed(self, url: QUrl):
        self.url_bar.setText(url.toString())


class OptimizedBrowser(QMainWindow):
    """Navigateur web pour Windows"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGC Navigateur - Windows")
        self.setGeometry(100, 100, 1280, 850)
        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tabs)
        self.create_menu()

        toolbar = self.addToolBar("Actions")
        new_tab_action = QAction("+ Nouvel Onglet", self)
        new_tab_action.triggered.connect(lambda: self.add_tab())
        toolbar.addAction(new_tab_action)

        self.statusBar().showMessage("Pret")
        self.add_tab()

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Fichier")
        new_tab = QAction("Nouvel Onglet", self)
        new_tab.setShortcut("Ctrl+T")
        new_tab.triggered.connect(lambda: self.add_tab())
        file_menu.addAction(new_tab)

        close_tab = QAction("Fermer l'Onglet", self)
        close_tab.setShortcut("Ctrl+W")
        close_tab.triggered.connect(self.close_current_tab)
        file_menu.addAction(close_tab)

        file_menu.addSeparator()
        exit_action = QAction("Quitter", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("Affichage")
        fullscreen = QAction("Plein Ecran", self)
        fullscreen.setShortcut("F11")
        fullscreen.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen)

        help_menu = menu_bar.addMenu("Aide")
        about = QAction("A Propos", self)
        about.triggered.connect(self.show_about)
        help_menu.addAction(about)

    def add_tab(self, url: str = DEFAULT_HOME):
        tab = BrowserTab(url)
        tab.browser.titleChanged.connect(
            lambda title, t=tab: self.update_tab_title(t, title)
        )
        index = self.tabs.addTab(tab, "Nouvel Onglet")
        self.tabs.setCurrentIndex(index)

    def update_tab_title(self, tab: BrowserTab, title: str):
        index = self.tabs.indexOf(tab)
        if index >= 0:
            display = title[:30] + "..." if len(title) > 30 else title
            self.tabs.setTabText(index, display)

    def close_tab(self, index: int):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def close_current_tab(self):
        if self.tabs.count() > 1:
            self.tabs.removeTab(self.tabs.currentIndex())

    def on_tab_changed(self, index: int):
        tab = self.tabs.widget(index)
        if isinstance(tab, BrowserTab):
            title = tab.browser.title()
            if title:
                self.setWindowTitle(f"{title} - EGC Navigateur")
            self.statusBar().showMessage(tab.url_bar.text())

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_about(self):
        QMessageBox.about(
            self, "A Propos",
            "EGC Navigateur Web v1.0.0\n\n"
            "Navigateur web pour Windows\n"
            "Auteur: ManBoyx"
        )


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setFont(QFont("Segoe UI", 10))
    browser = OptimizedBrowser()
    browser.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
