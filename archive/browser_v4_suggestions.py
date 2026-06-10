import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QTabWidget, QListWidget, QListWidgetItem
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Navigateur Web avec Onglets")
        self.setGeometry(100, 100, 800, 600)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.new_tab_button = QPushButton("Nouvel Onglet")
        self.new_tab_button.clicked.connect(self.add_tab)
        
        self.add_tab()
        
        layout = QVBoxLayout()
        layout.addWidget(self.new_tab_button)
        layout.addWidget(self.tabs)
        
        container = QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)
    
    def add_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout()
        
        url_bar = QLineEdit()
        url_bar.returnPressed.connect(lambda: self.load_page(url_bar, browser))
        url_bar.textChanged.connect(lambda: self.suggest_links(url_bar.text(), suggestions_list))
        
        go_button = QPushButton("Go")
        go_button.clicked.connect(lambda: self.load_page(url_bar, browser))
        
        browser = QWebEngineView()
        
        suggestions_list = QListWidget()
        suggestions_list.itemClicked.connect(lambda item: self.select_suggestion(url_bar, item))
        
        tab_layout.addWidget(url_bar)
        tab_layout.addWidget(suggestions_list)
        tab_layout.addWidget(go_button)
        tab_layout.addWidget(browser)
        
        tab.setLayout(tab_layout)
        
        index = self.tabs.addTab(tab, "Nouvel Onglet")
        self.tabs.setCurrentIndex(index)
    
    def load_page(self, url_bar, browser):
        text = url_bar.text().lower()
        special_urls = {
            "youtube": "https://www.youtube.com/",
            "wikipedia": "https://www.wikipedia.org/"
        }
        if text in special_urls:
            browser.setUrl(QUrl(special_urls[text]))
        else:
            url = url_bar.text()
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url
            browser.setUrl(QUrl(url))
            self.set_cookie(browser)
            self.handle_preloaded_resources(browser)
    
    def suggest_links(self, query, suggestions_list):
        api_url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={query}"
        response = requests.get(api_url)
        suggestions_list.clear()
        if response.status_code == 200:
            suggestions = response.json()[1]
            for suggestion in suggestions:
                item = QListWidgetItem(suggestion)
                suggestions_list.addItem(item)
    
    def select_suggestion(self, url_bar, item):
        url_bar.setText(item.text())
        self.load_page(url_bar, self.tabs.currentWidget().findChild(QWebEngineView))
    
    def set_cookie(self, browser):
        script = "document.cookie = 'example_cookie=example_value; SameSite=None; Secure';"
        browser.page().runJavaScript(script)
    
    def handle_preloaded_resources(self, browser):
        script = """
        if (document.readyState === 'complete') {
            const preloadLink = document.querySelector('link[rel="preload"]');
            if (preloadLink) {
                const resource = preloadLink.href;
                console.log('Preloaded resource:', resource);
            }
        }
        """
        browser.page().runJavaScript(script)

app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec_())
