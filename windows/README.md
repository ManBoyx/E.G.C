# EGC Suite - Version Windows

Applications EGC avec theme sombre (Catppuccin Mocha) et police Segoe UI.

## Installation

### Prerequis
- Python 3.8+ ([python.org](https://www.python.org/downloads/))
- Cocher "Add Python to PATH" lors de l'installation

### Installation rapide
```
Double-cliquer sur install.bat
```

### Installation manuelle
```cmd
pip install PyQt5 PyQtWebEngine Pillow numpy sounddevice
```

## Lancement

### Via le launcher
```cmd
python launcher.py
```

### Applications individuelles
```cmd
python antivirus_scanner.py
python photo_editor.py
python web_browser.py
python audio_amplifier.py
```

## Applications

| Application | Description |
|---|---|
| **Antivirus Scanner** | Scanner de fichiers avec quarantaine et historique |
| **Photo Editor** | Editeur d'images avec filtres, dessin et raccourcis |
| **Web Browser** | Navigateur web avec onglets et recherche Brave |
| **Audio Amplifier** | Amplificateur audio en temps reel (1x-10x) |

## Differences avec la version Linux

- Theme sombre Catppuccin Mocha (au lieu du theme clair)
- Police Segoe UI (native Windows)
- Chemins Windows natifs (Path gere automatiquement)
- Fichier `install.bat` pour installation en un clic
