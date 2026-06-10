# EGC Suite - Applications Optimisées pour Linux

**Version:** 1.0.0  
**Auteur:** ManBoyxv4  
**License:** MIT  
**Plateforme:** Linux (Debian/Ubuntu et dérivés)

---

## Contenu du Projet

EGC Suite contient 4 applications optimisées pour Linux:

### 1. EGC Antivirus (`egc-antivirus`)
Scanner antivirus performant avec interface PyQt5
- Scan rapide et complet avec streaming I/O
- Quarantaine automatique des fichiers infectés
- Onglet de gestion de quarantaine
- Historique des scans
- Progress bar en temps réel
- Bouton d'arrêt du scan

### 2. EGC Photo Editor (`egc-photo-editor`)
Éditeur photo complet avec filtres et outils
- Outils de dessin (crayon, gomme, ligne)
- Filtres d'image (N&B, flou, netteté, contour, relief)
- Ajustement luminosité et contraste
- Annuler/Refaire (30 niveaux)
- Réinitialisation à l'image originale
- Raccourcis clavier (Ctrl+O, Ctrl+S, Ctrl+Z, Ctrl+Y)
- Barre de statut avec infos image

### 3. EGC Browser (`egc-browser`)
Navigateur web avec onglets et barre d'outils
- Gestion des onglets (Ctrl+T, Ctrl+W)
- Barre de navigation (retour, avancer, recharger, accueil)
- Barre d'adresse intelligente (URL ou recherche Brave)
- Menu Fichier/Affichage/Aide
- Mode plein écran (F11)
- Mise à jour dynamique des titres d'onglets

### 4. EGC Audio Amplifier (`egc-audio-amplifier`)
Amplificateur audio avec interface graphique
- Contrôle du volume 1-10x avec descriptions
- Indicateur de niveau coloré
- Traitement du signal en temps réel
- Écrêtage automatique
- Gestion propre des erreurs audio

---

## Prérequis Système

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-pip python3-pyqt5 python3-pyqt5.qtwebengine python3-pil python3-numpy
```

---

## Installation

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

# Ou via le lanceur
./egc-launcher
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

## Structure du Projet

```
E.G.C/
├── src/                          # Code source principal
│   ├── __init__.py
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
├── archive/                     # Anciens prototypes (référence)
├── debian/                      # Configuration paquet Debian
│   ├── control
│   ├── changelog
│   ├── rules
│   └── source/
├── egc-antivirus               # Exécutable antivirus
├── egc-photo-editor            # Exécutable éditeur
├── egc-browser                 # Exécutable navigateur
├── egc-audio-amplifier         # Exécutable amplificateur
├── egc-launcher                # Lanceur (menu)
├── setup.py                    # Configuration Python
├── requirements.txt            # Dépendances
├── virus_database.txt          # Base de signatures
└── README.md                   # Ce fichier
```

---

## Optimisations Appliquées

### Performance
- Streaming I/O pour les gros fichiers (chunks de 8192 bytes)
- Gestion mémoire optimisée (limite undo stack)
- Threads non-bloquants pour le scan antivirus
- Redimensionnement intelligent des images

### Code Quality
- Type hints complets
- Gestion d'erreurs robuste avec messages utilisateur
- Logging détaillé
- Fonctions `main()` dans chaque module pour entry_points
- Code DRY (Don't Repeat Yourself)

### UX
- Raccourcis clavier dans toutes les apps
- Barres de statut informatives
- Styles CSS pour les boutons PyQt5
- Barre de navigation complète dans le navigateur
- Filtres d'image dans l'éditeur photo

### Linux Integration
- Respect des standards FHS
- Fichiers .desktop pour le menu
- Entrées console_scripts
- Support des dépendances système

---

## Utilisation

### Antivirus

```bash
egc-antivirus
# 1. Sélectionner le type de scan (rapide/complet/personnalisé)
# 2. Cliquer sur "Démarrer le scan"
# 3. Sélectionner le dossier à scanner
# 4. Les fichiers infectés sont automatiquement mis en quarantaine
# 5. Consulter l'historique et gérer la quarantaine dans les onglets
```

### Éditeur Photo

```bash
egc-photo-editor
# 1. Ouvrir une image (Ctrl+O) ou créer un nouveau canvas (Ctrl+N)
# 2. Dessiner avec les outils (crayon, gomme, ligne)
# 3. Appliquer des filtres via le menu Filtres
# 4. Ajuster luminosité/contraste
# 5. Sauvegarder le résultat (Ctrl+S)
```

### Navigateur Web

```bash
egc-browser
# 1. Entrer une URL ou une recherche dans la barre d'adresse
# 2. Utiliser les boutons de navigation (retour, avancer, recharger, accueil)
# 3. Ouvrir de nouveaux onglets (Ctrl+T)
# 4. Mode plein écran avec F11
```

### Amplificateur Audio

```bash
egc-audio-amplifier
# 1. Ajuster le curseur de volume (1x-10x)
# 2. Cliquer "Démarrer"
# 3. Le son du micro est amplifié en temps réel
# 4. Cliquer "Arrêter" pour couper
```

---

## Troubleshooting

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

## License

MIT License - Voir le fichier LICENSE pour plus de détails.

---

## Contribution

Les contributions sont bienvenues! Veuillez:

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing`)
5. Ouvrir une Pull Request

---

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur:
**https://github.com/ManBoyx/E.G.C/issues**

---

**Merci d'utiliser EGC Suite!**
