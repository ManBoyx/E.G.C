# EGC Suite

Suite d'applications desktop multi-plateforme en Python.  
4 applications : Antivirus, Editeur Photo, Navigateur Web, Amplificateur Audio.

---

## Applications

### Antivirus Scanner
Scanner de fichiers par signatures avec interface graphique.
- Scan rapide/complet avec barre de progression
- Mise en quarantaine automatique des fichiers suspects
- Gestion de la quarantaine (restaurer/supprimer)
- Historique complet des scans

### Photo Editor
Editeur d'images avec outils de dessin et filtres.
- Outils : crayon, gomme, ligne
- Filtres : noir & blanc, flou, nettete, contour, relief
- Reglages : luminosite, contraste
- Undo/redo (30 niveaux), raccourcis clavier

### Web Browser
Navigateur web avec onglets (moteur Chromium via QtWebEngine).
- Barre de navigation : retour, avancer, recharger, accueil
- Barre d'adresse intelligente (URL directe ou recherche Brave)
- Gestion des onglets (Ctrl+T / Ctrl+W)
- Mode plein ecran (F11)

### Audio Amplifier
Amplificateur audio temps reel avec controle du gain.
- Amplification de 1x a 10x
- Indicateur de niveau avec code couleur
- Ecretage automatique pour eviter la distorsion

---

## Installation

### Linux (Debian/Ubuntu)

```bash
# Dependances systeme
sudo apt install python3 python3-pip python3-pyqt5 \
    python3-pyqt5.qtwebengine python3-pil python3-numpy

# Cloner et installer
git clone https://github.com/ManBoyx/E.G.C.git
cd E.G.C
pip3 install -r requirements.txt

# Lancer
./egc-launcher          # menu interactif
./egc-antivirus         # antivirus seul
./egc-photo-editor      # editeur photo seul
./egc-browser           # navigateur seul
./egc-audio-amplifier   # amplificateur seul
```

### Windows

```cmd
cd windows
install.bat

:: Ou manuellement
pip install PyQt5 PyQtWebEngine Pillow numpy sounddevice

:: Lancer
python launcher.py
python antivirus_scanner.py
python photo_editor.py
python web_browser.py
python audio_amplifier.py
```

### Paquet Debian (.deb)

```bash
cd debian && bash rules && cd ..
sudo apt install ./egc-suite_1.0.0_all.deb
```

---

## Structure du projet

```
E.G.C/
├── src/                        # Applications Linux
│   ├── antivirus/scanner.py
│   ├── photo/editor.py
│   ├── browser/navigator.py
│   └── audio/amplifier.py
├── windows/                    # Applications Windows (theme sombre)
│   ├── antivirus_scanner.py
│   ├── photo_editor.py
│   ├── web_browser.py
│   ├── audio_amplifier.py
│   ├── launcher.py
│   └── install.bat
├── debian/                     # Packaging Debian
├── egc-antivirus               # Lanceurs Linux
├── egc-photo-editor
├── egc-browser
├── egc-audio-amplifier
├── egc-launcher
├── orale.html                  # Page web Parcours Avenir
├── setup.py
├── requirements.txt
└── virus_database.txt
```

---

## Technologies

| Composant | Technologie |
|---|---|
| GUI (Antivirus, Browser, Audio) | PyQt5 |
| GUI (Photo Editor) | Tkinter + Pillow |
| Moteur web | QtWebEngine (Chromium) |
| Traitement audio | NumPy + Sounddevice |
| Traitement image | Pillow (PIL) |
| Packaging | setuptools + dpkg |

---

## Differences Linux / Windows

| | Linux (`src/`) | Windows (`windows/`) |
|---|---|---|
| Theme | Clair (natif) | Sombre (Catppuccin Mocha) |
| Police | System default | Segoe UI |
| Installation | apt + pip | install.bat ou pip |
| Lanceurs | Scripts shell `egc-*` | `launcher.py` |

---

## Raccourcis clavier

| Raccourci | Action |
|---|---|
| `Ctrl+T` | Nouvel onglet (navigateur) |
| `Ctrl+W` | Fermer onglet (navigateur) |
| `Ctrl+O` | Ouvrir image (editeur) |
| `Ctrl+S` | Sauvegarder (editeur) |
| `Ctrl+Z` | Annuler (editeur) |
| `Ctrl+Y` | Refaire (editeur) |
| `Ctrl+N` | Nouveau canvas (editeur) |
| `F11` | Plein ecran (navigateur) |
| `Ctrl+Q` | Quitter (navigateur) |

---

## Prerequis

- **Python** >= 3.8
- **Linux** : PyQt5, PyQtWebEngine, Pillow, NumPy, Sounddevice
- **Windows** : memes dependances, installees via `install.bat`

---

## License

MIT

---

## Auteur

**ManBoyx** - [GitHub](https://github.com/ManBoyx)
