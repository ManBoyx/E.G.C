import sys
import os
import time
import subprocess
import ctypes
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit,
    QLabel, QFileDialog, QProgressBar, QComboBox, QLineEdit, QTabWidget,
    QSystemTrayIcon, QMenu, QAction, QDateTimeEdit, QGraphicsOpacityEffect, QTableWidget, QTableWidgetItem, QCheckBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QDateTime, QTimer, QPropertyAnimation, QUrl
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Signatures de virus (simplifié)
virus_signatures = [
    b"eicar",
    b"malicious"
]

allowed_ips = []
blocked_ips = []
quarantined_files = []

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ScanThread(QThread):
    update_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self, directory, scan_type):
        super().__init__()
        self.directory = directory
        self.scan_type = scan_type
        self.stop_flag = False

    def run(self):
        infected_files = self.scan_files(self.directory)
        if infected_files:
            self.update_signal.emit("Fichiers infectés trouvés :")
            for file in infected_files:
                if self.stop_flag:
                    break
                self.update_signal.emit(f"- {file}")
                self.quarantine_file(file)
        else:
            self.update_signal.emit("Aucun fichier infecté trouvé.")

    def scan_files(self, directory):
        infected_files = []
        total_files = sum([len(files) for r, d, files in os.walk(directory)])
        scanned_files = 0

        for root, dirs, files in os.walk(directory):
            for file in files:
                if self.stop_flag:
                    break
                file_path = os.path.join(root, file)
                if self.scan_file(file_path):
                    infected_files.append(file_path)
                scanned_files += 1
                progress = int((scanned_files / total_files) * 100)
                self.progress_signal.emit(progress)
                # Simulate different scan times
                if self.scan_type == "Scan rapide":
                    time.sleep(0.01)
                else:
                    time.sleep(0.05)
        return infected_files

    def scan_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
                for signature in virus_signatures:
                    if signature in file_content:
                        return True
        except Exception as e:
            self.update_signal.emit(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        return False

    def quarantine_file(self, file_path):
        try:
            quarantine_directory = os.path.join(os.path.dirname(file_path), "quarantine")
            if not os.path.exists(quarantine_directory):
                os.makedirs(quarantine_directory)
            os.rename(file_path, os.path.join(quarantine_directory, os.path.basename(file_path)))
            quarantined_files.append(file_path)
            self.update_signal.emit(f"Fichier déplacé en quarantaine: {file_path}")
        except PermissionError as e:
            self.update_signal.emit(f"Erreur de permission lors de la mise en quarantaine du fichier {file_path}: {e}")
        except Exception as e:
            self.update_signal.emit(f"Erreur lors de la mise en quarantaine du fichier {file_path}: {e}")

    def stop(self):
        self.stop_flag = True

class RealTimeScanThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.stop_flag = False

    def run(self):
        while not self.stop_flag:
            self.scan_new_files(self.directory)
            time.sleep(9000)  # Vérifie toutes les 9000 secondes pour réduire l'utilisation du CPU

    def scan_new_files(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if self.stop_flag:
                    break
                file_path = os.path.join(root, file)
                if self.scan_file(file_path):
                    self.update_signal.emit(f"Infection détectée en temps réel : {file_path}")
                    self.quarantine_file(file_path)

    def scan_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
                for signature in virus_signatures:
                    if signature in file_content:
                        return True
        except Exception as e:
            self.update_signal.emit(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        return False

    def quarantine_file(self, file_path):
        try:
            quarantine_directory = os.path.join(os.path.dirname(file_path), "quarantine")
            if not os.path.exists(quarantine_directory):
                os.makedirs(quarantine_directory)
            os.rename(file_path, os.path.join(quarantine_directory, os.path.basename(file_path)))
            quarantined_files.append(file_path)
            self.update_signal.emit(f"Fichier déplacé en quarantaine: {file_path}")
        except PermissionError as e:
            self.update_signal.emit(f"Erreur de permission lors de la mise en quarantaine du fichier {file_path}: {e}")
        except Exception as e:
            self.update_signal.emit(f"Erreur lors de la mise en quarantaine du fichier {file_path}: {e}")

    def stop(self):
        self.stop_flag = True

class InternetConnectionThread(QThread):
    connection_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.stop_flag = False

    def run(self):
        while not self.stop_flag:
            try:
                # Ping Google's DNS server to check for internet connectivity
                output = subprocess.run(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if output.returncode == 0:
                    self.connection_signal.emit(True)
                else:
                    self.connection_signal.emit(False)
            except Exception:
                self.connection_signal.emit(False)
            time.sleep(10)  # Check every 10 seconds

    def stop(self):
        self.stop_flag = True

class SystemHealthCheckThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.issues = []

    def run(self):
        self.check_disk_errors()
        self.check_outdated_drivers()
        self.check_startup_programs()
        if self.issues:
            self.update_signal.emit("Problèmes détectés :")
            for issue in self.issues:
                self.update_signal.emit(f"- {issue}")
        else:
            self.update_signal.emit("Aucun problème détecté.")

    def check_disk_errors(self):
        # Placeholder for disk error checking logic
        self.issues.append("Erreur de disque détectée.")

    def check_outdated_drivers(self):
        # Placeholder for outdated driver checking logic
        self.issues.append("Pilote obsolète détecté.")

    def check_startup_programs(self):
        # Placeholder for startup program checking logic
        self.issues.append("Programme de démarrage inutile détecté.")

class VirusScanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.setWindowTitle("Antivirus et Pare-feu Optimisé")
        self.setGeometry(100, 100, 800, 600)

        self.system_tray_icon = QSystemTrayIcon(self)
        self.system_tray_icon.setIcon(QIcon("icon.png"))
        tray_menu = QMenu()
        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        self.system_tray_icon.setContextMenu(tray_menu)
        self.system_tray_icon.show()

        self.layout = QVBoxLayout()

        self.mode_button = QPushButton("Basculer en mode sombre")
        self.mode_button.clicked.connect(self.toggle_mode)
        self.layout.addWidget(self.mode_button)

        self.label = QLabel("Cliquez sur 'Scanner complet' pour lancer un scan complet du PC ou 'Scanner fichier' pour scanner un fichier spécifique")
        self.layout.addWidget(self.label)

        if is_admin():
            self.admin_label = QLabel("L'application est exécutée avec des privilèges administratifs.")
            self.admin_label.setStyleSheet("color: red; font-weight: bold;")
            self.layout.addWidget(self.admin_label)

        self.scan_type_combo = QComboBox()
        self.scan_type_combo.addItems(["Scan rapide", "Scan classique"])
        self.layout.addWidget(self.scan_type_combo)

        self.scan_complete_button = QPushButton("Scanner complet")
        self.scan_complete_button.clicked.connect(self.scan_complete_pc)
        self.layout.addWidget(self.scan_complete_button)

        self.scan_file_button = QPushButton("Scanner fichier")
        self.scan_file_button.clicked.connect(self.scan_single_file)
        self.layout.addWidget(self.scan_file_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        # Ajout de la planification des scans
        self.schedule_scan_label = QLabel("Planifier un scan :")
        self.layout.addWidget(self.schedule_scan_label)

        self.date_time_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_time_edit.setCalendarPopup(True)
        self.layout.addWidget(self.date_time_edit)

        self.schedule_button = QPushButton("Planifier")
        self.schedule_button.clicked.connect(self.schedule_scan)
        self.layout.addWidget(self.schedule_button)

        # Indicateur de connexion Internet
        self.internet_label = QLabel("Vérification de la connexion Internet...")
        self.layout.addWidget(self.internet_label)

        # Ajout du navigateur web dans un onglet séparé
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))

        # Onglet Pare-feu
        self.firewall_tab = QWidget()
        self.firewall_layout = QVBoxLayout()

        self.firewall_label = QLabel("Gérez les connexions réseau en ajoutant des adresses IP autorisées ou bloquées")
        self.firewall_layout.addWidget(self.firewall_label)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Entrez une adresse IP")
        self.firewall_layout.addWidget(self.ip_input)

        self.allow_button = QPushButton("Autoriser IP")
        self.allow_button.clicked.connect(self.allow_ip)
        self.firewall_layout.addWidget(self.allow_button)

        self.block_button = QPushButton("Bloquer IP")
        self.block_button.clicked.connect(self.block_ip)
        self.firewall_layout.addWidget(self.block_button)

        self.allowed_ips_text = QTextEdit()
        self.allowed_ips_text.setReadOnly(True)
        self.firewall_layout.addWidget(self.allowed_ips_text)

        self.blocked_ips_text = QTextEdit()
        self.blocked_ips_text.setReadOnly(True)
        self.firewall_layout.addWidget(self.blocked_ips_text)

        self.firewall_tab.setLayout(self.firewall_layout)

        # Onglet Quarantaine
        self.quarantine_tab = QWidget()
        self.quarantine_layout = QVBoxLayout()

        self.quarantine_label = QLabel("Fichiers en quarantaine")
        self.quarantine_layout.addWidget(self.quarantine_label)

        self.quarantine_table = QTableWidget()
        self.quarantine_table.setColumnCount(2)
        self.quarantine_table.setHorizontalHeaderLabels(["Fichier", "Action"])
        self.quarantine_layout.addWidget(self.quarantine_table)

        self.quarantine_tab.setLayout(self.quarantine_layout)

        # Onglet Navigateur
        self.browser_tab = QWidget()
        self.browser_layout = QVBoxLayout()
        self.browser_layout.addWidget(self.browser)
        self.browser_tab.setLayout(self.browser_layout)

        # Onglet Logs
        self.logs_tab = QWidget()
        self.logs_layout = QVBoxLayout()

        self.logs_label = QLabel("Logs des scans")
        self.logs_layout.addWidget(self.logs_label)

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_layout.addWidget(self.logs_text)

        self.logs_tab.setLayout(self.logs_layout)

        # Onglet Performance
        self.performance_tab = QWidget()
        self.performance_layout = QVBoxLayout()

        self.performance_label = QLabel("Optimisation des Performances")
        self.performance_layout.addWidget(self.performance_label)

        self.optimize_button = QPushButton("Optimiser le Système")
        self.optimize_button.clicked.connect(self.optimize_system)
        self.performance_layout.addWidget(self.optimize_button)

        self.battery_saver_checkbox = QCheckBox("Mode Économie de Batterie")
        self.battery_saver_checkbox.stateChanged.connect(self.toggle_battery_saver)
        self.performance_layout.addWidget(self.battery_saver_checkbox)

        self.driver_update_button = QPushButton("Mettre à Jour les Pilotes")
        self.driver_update_button.clicked.connect(self.update_drivers)
        self.performance_layout.addWidget(self.driver_update_button)

        self.health_check_button = QPushButton("Vérifier l'État du Système")
        self.health_check_button.clicked.connect(self.run_health_check)
        self.performance_layout.addWidget(self.health_check_button)

        self.fix_all_button = QPushButton("Résoudre Tous les Problèmes")
        self.fix_all_button.clicked.connect(self.fix_all_issues)
        self.fix_all_button.setEnabled(False)
        self.performance_layout.addWidget(self.fix_all_button)

        self.performance_tab.setLayout(self.performance_layout)

        # Container for the main tab
        container = QWidget()
        container.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.tabs.addTab(container, "Antivirus")
        self.tabs.addTab(self.firewall_tab, "Pare-feu")
        self.tabs.addTab(self.quarantine_tab, "Quarantaine")
        self.tabs.addTab(self.browser_tab, "Navigateur")
        self.tabs.addTab(self.logs_tab, "Logs")
        self.tabs.addTab(self.performance_tab, "Performance")
        self.setCentralWidget(self.tabs)

        self.dark_mode = False

        # Lancement de la détection en temps réel
        self.real_time_scan_thread = RealTimeScanThread("/")
        self.real_time_scan_thread.update_signal.connect(self.update_result_text)
        self.real_time_scan_thread.start()

        # Lancement du thread de vérification de la connexion Internet
        self.internet_connection_thread = InternetConnectionThread()
        self.internet_connection_thread.connection_signal.connect(self.update_internet_status)
        self.internet_connection_thread.start()

        # Mettre à jour l'affichage de la quarantaine
        self.update_quarantine_view()

    def allow_ip(self):
        ip = self.ip_input.text()
        if ip and ip not in allowed_ips:
            allowed_ips.append(ip)
            self.update_firewall_texts()
            self.ip_input.clear()

    def block_ip(self):
        ip = self.ip_input.text()
        if ip and ip not in blocked_ips:
            blocked_ips.append(ip)
            self.update_firewall_texts()
            self.ip_input.clear()

    def update_firewall_texts(self):
        self.allowed_ips_text.setPlainText("IP autorisées :\n" + "\n".join(allowed_ips))
        self.blocked_ips_text.setPlainText("IP bloquées :\n" + "\n".join(blocked_ips))

    def schedule_scan(self):
        scheduled_time = self.date_time_edit.dateTime().toPyDateTime()
        current_time = QDateTime.currentDateTime().toPyDateTime()
        delay = (scheduled_time - current_time).total_seconds()
        QTimer.singleShot(int(delay * 1000), self.scan_complete_pc)

    def toggle_mode(self):
        if self.dark_mode:
            # Switch to light mode
            self.app.setStyleSheet("")
            self.mode_button.setText("Basculer en mode sombre")
        else:
            # Switch to dark mode
            self.app.setStyleSheet("""
                QWidget {
                    background-color: #2E2E2E;
                    color: #FFFFFF;
                }
                QPushButton {
                    background-color: #5A5A5A;
                    color: #FFFFFF;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #757575;
                }
                QTextEdit {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
            """)
            self.mode_button.setText("Basculer en mode clair")

        self.dark_mode = not self.dark_mode

    def scan_complete_pc(self):
        directory = QFileDialog.getExistingDirectory(self, "Sélectionnez le dossier à scanner")
        if directory:
            self.progress_bar.setValue(0)
            self.result_text.clear()
            self.scan_thread = ScanThread(directory, self.scan_type_combo.currentText())
            self.scan_thread.update_signal.connect(self.update_result_text)
            self.scan_thread.progress_signal.connect(self.progress_bar.setValue)
            self.scan_thread.start()

    def scan_single_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionnez le fichier à scanner")
        if file_path:
            self.progress_bar.setValue(0)
            self.result_text.clear()
            self.scan_thread = ScanThread(os.path.dirname(file_path), self.scan_type_combo.currentText())
            self.scan_thread.update_signal.connect(self.update_result_text)
            self.scan_thread.progress_signal.connect(self.progress_bar.setValue)
            self.scan_thread.start()

    def update_result_text(self, message):
        self.result_text.append(message)
        self.logs_text.append(message)  # Log the message
        self.animate_message(self.result_text)

    def animate_message(self, widget):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(1000)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()

    def update_internet_status(self, connected):
        if connected:
            self.internet_label.setText("Connecté à Internet")
            self.internet_label.setStyleSheet("color: green;")
        else:
            self.internet_label.setText("Pas de connexion Internet")
            self.internet_label.setStyleSheet("color: red;")

    def update_quarantine_view(self):
        self.quarantine_table.setRowCount(len(quarantined_files))
        for row, file in enumerate(quarantined_files):
            file_item = QTableWidgetItem(file)
            restore_button = QPushButton("Restaurer")
            restore_button.clicked.connect(lambda _, f=file: self.restore_from_quarantine(f))
            self.quarantine_table.setItem(row, 0, file_item)
            self.quarantine_table.setCellWidget(row, 1, restore_button)

    def restore_from_quarantine(self, file_path):
        try:
            original_path = os.path.join(os.path.dirname(file_path), "quarantine", os.path.basename(file_path))
            if os.path.exists(original_path):
                os.rename(original_path, file_path)
                quarantined_files.remove(file_path)
                self.update_quarantine_view()
                self.update_result_text(f"Fichier restauré : {file_path}")
            else:
                self.update_result_text(f"Fichier introuvable dans la quarantaine : {file_path}")
        except Exception as e:
            self.update_result_text(f"Erreur lors de la restauration du fichier {file_path}: {e}")

    def optimize_system(self):
        # Placeholder for system optimization logic
        self.update_result_text("Optimisation du système en cours...")
        # Implement actual optimization steps here

    def toggle_battery_saver(self, state):
        if state == Qt.Checked:
            self.update_result_text("Mode Économie de Batterie activé.")
            # Implement battery saver logic here
        else:
            self.update_result_text("Mode Économie de Batterie désactivé.")

    def update_drivers(self):
        # Placeholder for driver update logic
        self.update_result_text("Mise à jour des pilotes en cours...")
        # Implement actual driver update steps here

    def run_health_check(self):
        self.health_check_thread = SystemHealthCheckThread()
        self.health_check_thread.update_signal.connect(self.update_result_text)
        self.health_check_thread.start()
        self.health_check_thread.finished.connect(lambda: self.fix_all_button.setEnabled(True))

    def fix_all_issues(self):
        # Placeholder for fixing all issues logic
        self.update_result_text("Résolution de tous les problèmes en cours...")
        # Implement actual issue resolution steps here
        self.fix_all_button.setEnabled(False)

    def closeEvent(self, event):
        self.real_time_scan_thread.stop()
        self.internet_connection_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VirusScanner()
    window.show()
    sys.exit(app.exec_())
