import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QTabWidget, QToolBar, QAction, QMenu, QMessageBox, QShortcut
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, QSettings
from PyQt5.QtGui import QIcon, QKeySequence

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGC Navigateur web")
        self.setGeometry(100, 100, 1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.add_tab()

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.create_toolbar()
        self.create_menu()

        self.settings = QSettings("BraveLikeBrowser", "Settings")

    def create_toolbar(self):
        home_action = QAction(QIcon("home.png"), "Accueil", self)
        home_action.triggered.connect(self.navigate_home)
        self.toolbar.addAction(home_action)

        back_action = QAction(QIcon("back.png"), "Retour", self)
        back_action.triggered.connect(self.go_back)
        self.toolbar.addAction(back_action)

        forward_action = QAction(QIcon("forward.png"), "Avancer", self)
        forward_action.triggered.connect(self.go_forward)
        self.toolbar.addAction(forward_action)

        reload_action = QAction(QIcon("reload.png"), "Recharger", self)
        reload_action.triggered.connect(self.reload_page)
        self.toolbar.addAction(reload_action)

        self.new_tab_button = QPushButton("Nouvel Onglet")
        self.new_tab_button.clicked.connect(self.add_tab)
        self.toolbar.addWidget(self.new_tab_button)

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Fichier")
        new_tab_action = QAction("Nouvel Onglet", self)
        new_tab_action.triggered.connect(self.add_tab)
        file_menu.addAction(new_tab_action)

        close_tab_action = QAction("Fermer l'Onglet", self)
        close_tab_action.triggered.connect(self.close_current_tab)
        file_menu.addAction(close_tab_action)

        file_menu.addSeparator()

        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("Édition")
        clear_data_action = QAction("Effacer les Données de Navigation", self)
        clear_data_action.triggered.connect(self.clear_browsing_data)
        edit_menu.addAction(clear_data_action)

        view_menu = menu_bar.addMenu("Affichage")
        toggle_fullscreen_action = QAction("Plein Écran", self)
        toggle_fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(toggle_fullscreen_action)

        help_menu = menu_bar.addMenu("Aide")
        about_action = QAction("À Propos", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def add_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout()

        url_bar = QLineEdit()
        url_bar.returnPressed.connect(lambda: self.load_page(url_bar, browser))

        go_button = QPushButton("Go")
        go_button.clicked.connect(lambda: self.load_page(url_bar, browser))

        browser = QWebEngineView()
        browser.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        browser.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)

        tab_layout.addWidget(url_bar)
        tab_layout.addWidget(go_button)
        tab_layout.addWidget(browser)

        tab.setLayout(tab_layout)

        index = self.tabs.addTab(tab, "Nouvel Onglet")
        self.tabs.setCurrentIndex(index)

    def load_page(self, url_bar, browser):
        url_text = url_bar.text()
        if not url_text.startswith("http://") and not url_text.startswith("https://"):
            # Assume it's a search query and use Brave search engine
            search_url = f"https://search.brave.com/search?q={url_text}"
            browser.setUrl(QUrl(search_url))
        else:
            browser.setUrl(QUrl(url_text))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            self.tabs.removeTab(current_index)

    def navigate_home(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(2).widget()
        current_browser.setUrl(QUrl("http://www.google.com"))

    def go_back(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(2).widget()
        current_browser.back()

    def go_forward(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(2).widget()
        current_browser.forward()

    def reload_page(self):
        current_browser = self.tabs.currentWidget().layout().itemAt(2).widget()
        current_browser.reload()

    def clear_browsing_data(self):
        QWebEngineProfile.defaultProfile().cookieStore().deleteAllCookies()
        QMessageBox.information(self, "Données Effacées", "Les données de navigation ont été effacées.")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_about_dialog(self):
        QMessageBox.about(self, "À Propos", "Navigateur Web Optimisé\nVersion 1.0\nDéveloppé avec PyQt5")

    def closeEvent(self, event):
        self.settings.sync()
        event.accept()

app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec_())