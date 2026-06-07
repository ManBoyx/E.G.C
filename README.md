# 📦 EGC Suite - Applications Optimisées pour Linux

**Version:** 1.0.0  
**Auteur:** ManBoyxv4  
**License:** MIT  
**Plateforme:** Linux (Debian/Ubuntu et dérivés)

---

## 🎯 Contenu du Projet

EGC Suite contient 4 applications optimisées pour Linux:

### 1. **🔒 EGC Antivirus** (`egc-antivirus`)
Scanner antivirus performant avec interface PyQt5
- ✅ Scan rapide avec streaming I/O
- ✅ Quarantaine automatique des fichiers infectés
- ✅ Progress bar en temps réel
- ✅ Logs détaillés

### 2. **🖼️ EGC Photo Editor** (`egc-photo-editor`)
Éditeur photo léger et intuitif
- ✅ Outils de dessin optimisés
- ✅ Annuler/Refaire
- ✅ Choisir les couleurs
- ✅ Sauvegarde en PNG

### 3. **🌐 EGC Browser** (`egc-browser`)
Navigateur web minimaliste avec onglets
- ✅ Gestion des onglets
- ✅ Barre d'adresse intelligente
- ✅ Moteur WebEngine moderne

### 4. **🔊 EGC Audio Amplifier** (`egc-audio-amplifier`)
Ampificateur audio avec interface graphique
- ✅ Contrôle du volume 1-10x
- ✅ Traitement du signal en temps réel
- ✅ Écrêtage automatique

---

## 📋 Prérequis Système

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-pip python3-pyqt5 python3-pyqt5.qtwebengine python3-pil python3-numpy
```

---

## 🚀 Installation

### Option 1: Installation depuis les sources

```bash
# Cloner le repo
git clone https://github.com/ManBoyx/E.G.C.git
cd E.G.C

# Installer les dépendances
pip3 install -r requirements.txt

# Lancer les applications
./egc-antivirus
./egc-photo-editor
./egc-browser
./egc-audio-amplifier
```

### Option 2: Installation du paquet Debian (.deb)

```bash
# Construire le paquet
cd debian
bash rules
cd ..

# Installer le paquet
sudo dpkg -i egc-suite_1.0.0_all.deb

# Ou via apt
sudo apt install ./egc-suite_1.0.0_all.deb
```

Après installation, les applications seront disponibles dans le menu des applications ou via:

```bash
egc-antivirus
egc-photo-editor
egc-browser
egc-audio-amplifier
```

---

## 📂 Structure du Projet

```
E.G.C/
├── src/                          # Code source
│   ├── antivirus/               # Scanner antivirus
│   │   ├── __init__.py
│   │   └── scanner.py
│   ├── photo/                   # Éditeur photo
│   │   ├── __init__.py
│   │   └── editor.py
│   ├── browser/                 # Navigateur web
│   │   ├── __init__.py
│   │   └── navigator.py
│   └── audio/                   # Amplificateur audio
│       ├── __init__.py
│       └── amplifier.py
├── debian/                       # Configuration Debian
│   ├── control
│   ├── changelog
│   ├── rules
│   └── source/
├── egc-antivirus               # Exécutable antivirus
├── egc-photo-editor            # Exécutable éditeur
├── egc-browser                 # Exécutable navigateur
├── egc-audio-amplifier         # Exécutable amplificateur
├── setup.py                    # Configuration Python
├── requirements.txt            # Dépendances
└── README.md                   # Ce fichier
```

---

## 🛠️ Optimisations Appliquées

### Performance
- ✅ Streaming I/O pour les gros fichiers
- ✅ Lectures par chunks (8192 bytes)
- ✅ Gestion mémoire optimisée
- ✅ Threads non-bloquants

### Code Quality
- ✅ Type hints complets
- ✅ Gestion d'erreurs robuste
- ✅ Logging détaillé
- ✅ Code DRY (Don't Repeat Yourself)

### Linux Integration
- ✅ Respect des standards FHS
- ✅ Fichiers .desktop pour le menu
- ✅ Entrées console_scripts
- ✅ Support des dépendances système

---

## 📖 Utilisation

### Antivirus

```bash
egc-antivirus
# 1. Sélectionner le type de scan
# 2. Cliquer sur "Démarrer le scan"
# 3. Sélectionner le dossier à scanner
# 4. Les fichiers infectés sont automatiquement mis en quarantaine
```

### Éditeur Photo

```bash
egc-photo-editor
# 1. Ouvrir une image
# 2. Dessiner avec les outils disponibles
# 3. Changer la couleur si nécessaire
# 4. Sauvegarder le résultat
```

### Navigateur Web

```bash
egc-browser
# 1. Entrer une URL ou une recherche
# 2. Appuyer sur Entrée
# 3. Ouvrir de nouveaux onglets au besoin
```

### Amplificateur Audio

```bash
egc-audio-amplifier
# 1. Ajuster le curseur de volume
# 2. Cliquer "Démarrer"
# 3. Le son du micro est amplifié
```

---

## 🐛 Troubleshooting

### PyQt5 ne se lance pas

```bash
sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine
```

### Erreur "sounddevice not found"

```bash
pip3 install sounddevice
```

### Permission denied sur les exécutables

```bash
chmod +x egc-*
```

---

## 📝 License

MIT License - Voir le fichier LICENSE pour plus de détails.

---

## 🤝 Contribution

Les contributions sont bienvenues! Veuillez:

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing`)
5. Ouvrir une Pull Request

---

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur:
**https://github.com/ManBoyx/E.G.C/issues**

---

**Merci d'utiliser EGC Suite! 🚀**
