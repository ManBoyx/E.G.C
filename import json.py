import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel, QLineEdit
from PyQt5.QtCore import Qt
from web_search import web_search
from generate_image import generate_image
from code_interpreter import code_interpreter

class ChatbotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chatbot")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Entrez votre message ici...")
        self.layout.addWidget(self.user_input)

        self.send_button = QPushButton("Envoyer")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

    def send_message(self):
        user_message = self.user_input.text()
        if user_message.lower() == "quitter":
            self.close()
            return

        self.chat_display.append(f"Vous: {user_message}")
        self.user_input.clear()

        # Analyser la question de l'utilisateur et répondre en conséquence
        if "recherche" in user_message.lower():
            query = user_message.split("recherche", 1)[1].strip()
            self.perform_web_search(query)
        elif "image" in user_message.lower():
            prompt = user_message.split("image", 1)[1].strip()
            self.generate_image(prompt)
        elif "code" in user_message.lower():
            code = user_message.split("code", 1)[1].strip()
            self.execute_code(code)
        else:
            self.chat_display.append("Chatbot: Je ne comprends pas votre demande. Pouvez-vous être plus précis ?")

    def perform_web_search(self, query):
        self.chat_display.append(f"Chatbot: Effectuons une recherche web pour '{query}'...")
        results = web_search(query)
        if results:
            self.chat_display.append("Chatbot: Voici les résultats de la recherche :")
            for result in results:
                self.chat_display.append(f"- {result['title']}: {result['snippet']}")
        else:
            self.chat_display.append("Chatbot: Aucun résultat trouvé pour la recherche.")

    def generate_image(self, prompt):
        self.chat_display.append(f"Chatbot: Génération d'une image basée sur la description : '{prompt}'...")
        image_url = generate_image(prompt)
        if image_url:
            self.chat_display.append(f"Chatbot: Image générée avec succès ! Vous pouvez la voir à l'adresse suivante : {image_url}")
        else:
            self.chat_display.append("Chatbot: Échec de la génération de l'image.")

    def execute_code(self, code):
        self.chat_display.append("Chatbot: Exécution du code Python...")
        try:
            result = code_interpreter(code)
            self.chat_display.append(f"Chatbot: Résultat de l'exécution du code : {result}")
        except Exception as e:
            self.chat_display.append(f"Chatbot: Erreur lors de l'exécution du code : {e}")

if __name__ == "__main__":
    app = QApplication([])
    window = ChatbotWindow()
    window.show()
    app.exec_()
