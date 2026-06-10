import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Navigateur Web")
        self.setGeometry(100, 100, 800, 600)
        
        self.browser = QWebEngineView()
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_page)
        
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.load_page)
        
        layout = QVBoxLayout()
        layout.addWidget(self.url_bar)
        layout.addWidget(self.go_button)
        layout.addWidget(self.browser)
        
        container = QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)
    
    def load_page(self):
        url = self.url_bar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        self.browser.setUrl(url)

app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec_())
