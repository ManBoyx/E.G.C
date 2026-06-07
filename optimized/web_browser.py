"""Optimized Web Browser with Tab Support"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QTabWidget, QToolBar, QAction
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon


class OptimizedBrowser(QMainWindow):
    """Lightweight web browser with tab support"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGC Navigateur Web Optimisé")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Create toolbar
        toolbar = self.addToolBar("Navigation")
        toolbar.addAction("Nouvel Onglet", self.add_tab)

        self.add_tab()

    def add_tab(self):
        """Add a new browser tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # URL bar
        url_bar = QLineEdit()
        url_bar.setPlaceholderText("Entrez une URL...")
        url_bar.returnPressed.connect(lambda: self.load_url(url_bar, browser))
        layout.addWidget(url_bar)

        # Browser view
        browser = QWebEngineView()
        browser.setUrl(QUrl("https://www.google.com"))
        layout.addWidget(browser)

        widget.setLayout(layout)
        self.tabs.addTab(widget, "Nouvel Onglet")
        self.tabs.setCurrentWidget(widget)

    def load_url(self, url_bar: QLineEdit, browser: QWebEngineView):
        """Load URL in browser"""
        url = url_bar.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        browser.setUrl(QUrl(url))

    def close_tab(self, index: int):
        """Close a tab"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = OptimizedBrowser()
    browser.show()
    sys.exit(app.exec_())
