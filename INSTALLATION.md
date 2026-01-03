# Guide d'installation du Jeu de Morpion

## 📦 Installation étape par étape

### Étape 1 : Vérifier Python

1. Ouvrez PowerShell (Windows) ou Terminal (Linux/macOS)
2. Tapez la commande suivante :
   ```powershell
   python --version
   ```
3. Si Python est installé, vous verrez quelque chose comme `Python 3.x.x`
4. Si ce n'est pas le cas, passez à l'étape 2

### Étape 2 : Installer Python (si nécessaire)

#### Windows
1. Rendez-vous sur [python.org/downloads](https://www.python.org/downloads/)
2. Téléchargez la dernière version de Python 3
3. Lancez l'installateur
4. **IMPORTANT** : Cochez la case "Add Python to PATH" avant d'installer
5. Cliquez sur "Install Now"
6. Attendez la fin de l'installation
7. Vérifiez l'installation en ouvrant PowerShell et tapant :
   ```powershell
   python --version
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
```

#### macOS
```bash
# Avec Homebrew
brew install python3
python3 --version
```

### Étape 3 : Télécharger le jeu

1. Créez un dossier pour le jeu (par exemple : `TIk_TAK_TEO`)
2. Placez le fichier `morpion.py` dans ce dossier
3. Ouvrez PowerShell ou Terminal dans ce dossier

### Étape 4 : Lancer le jeu

#### Windows PowerShell
```powershell
cd "C:\Users\B.H\Desktop\TIk_TAK_TEO"
python morpion.py
```

#### Linux/macOS
```bash
cd ~/Desktop/TIk_TAK_TEO
python3 morpion.py
```

## ✅ Vérification de l'installation

Si tout fonctionne, vous devriez voir :
```
==================================================
   MORPION (TIC-TAC-TOE) AVEC INTELLIGENCE ARTIFICIELLE
==================================================

1. Jouer contre l'IA
2. Jouer contre un autre joueur
3. IA contre IA (démonstration)
4. Règles du jeu
5. Quitter

==================================================
```

## 🤖 (Optionnel) Activer l'IA apprenante DQN (PyTorch)

La version DQN nécessite **PyTorch** (module `torch`). Les données d'entraînement sont générées automatiquement par le jeu (pas de dataset externe).

### 1) Installer PyTorch

```powershell
python -m pip install torch
```

Si l'installation échoue, c'est souvent parce que votre version de Python n'est pas supportée par la version de PyTorch disponible. Dans ce cas, installez Python 3.12 (souvent recommandé) puis réessayez.

### 2) Créer un environnement virtuel (recommandé)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install pygame torch
python morpion_pygame.py
```

## 🔧 Résolution des problèmes courants

### Problème 1 : "python n'est pas reconnu"
**Solution** : Python n'est pas dans le PATH
```powershell
# Trouvez où Python est installé
Get-Command python

# Si rien n'apparaît, réinstallez Python en cochant "Add to PATH"
```

### Problème 2 : Caractères bizarres dans l'affichage
**Solution** : Problème d'encodage
```powershell
# Dans PowerShell, tapez :
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python morpion.py
```

### Problème 3 : "Permission denied"
**Solution** : Problème de droits (Linux/macOS)
```bash
chmod +x morpion.py
python3 morpion.py
```

### Problème 4 : Le jeu se ferme immédiatement
**Solution** : Lancez depuis un terminal, pas en double-cliquant

## 🎯 Premier lancement

1. Lancez le jeu avec `python morpion.py`
2. Tapez `4` pour lire les règles
3. Tapez `1` pour jouer contre l'IA
4. Choisissez le niveau `1` (facile) pour commencer
5. Jouez en tapant les numéros de 1 à 9

## 📝 Commandes utiles

### Naviguer vers le dossier du jeu
```powershell
# Windows
cd "C:\Users\B.H\Desktop\TIk_TAK_TEO"

# Linux/macOS
cd ~/Desktop/TIk_TAK_TEO
```

### Lister les fichiers
```powershell
# Windows
dir

# Linux/macOS
ls -la
```

### Ouvrir le code dans un éditeur
```powershell
# Avec Visual Studio Code
code morpion.py

# Avec le Bloc-notes (Windows)
notepad morpion.py

# Avec nano (Linux/macOS)
nano morpion.py
```

## 🎓 Utilisation dans un environnement éducatif

### Pour les enseignants

1. **Installation sur plusieurs postes** :
   - Copiez le dossier complet sur chaque poste
   - Vérifiez Python sur chaque machine
   - Créez un raccourci bureau avec la commande :
     ```powershell
     python C:\chemin\vers\morpion.py
     ```

2. **Version portable** :
   - Utilisez Python Portable si les droits admin sont limités
   - Mettez le jeu et Python sur une clé USB

3. **Modification du code** :
   - Les étudiants peuvent modifier `morpion.py` pour personnaliser
   - Encouragez l'exploration des différentes fonctions

### Pour les étudiants

1. **Apprendre en jouant** :
   - Commencez par jouer au jeu
   - Observez le mode IA vs IA
   - Ouvrez le code et lisez les commentaires

2. **Expérimentation** :
   - Changez les symboles (X et O)
   - Modifiez les messages affichés
   - Ajustez la difficulté moyenne

3. **Défis** :
   - Ajoutez un compteur de coups
   - Créez un système de score
   - Implémentez un historique de parties

## 🆘 Besoin d'aide ?

### Vérification complète du système

```powershell
# Windows PowerShell - Script de diagnostic
Write-Host "=== Diagnostic du système ===" -ForegroundColor Cyan
Write-Host "Version de Python :"
python --version
Write-Host "`nChemin de Python :"
Get-Command python | Select-Object Source
Write-Host "`nDossier actuel :"
Get-Location
Write-Host "`nFichiers présents :"
Get-ChildItem *.py
Write-Host "`nTest d'exécution Python :"
python -c "print('Python fonctionne correctement')"
```

### Contact et ressources

- 📖 Documentation Python : [docs.python.org](https://docs.python.org/fr/)
- 🎓 Tutoriels débutants : [python.org/about/gettingstarted](https://www.python.org/about/gettingstarted/)
- 💡 Relisez le README.md pour plus d'informations sur le jeu

## ✨ Félicitations !

Si vous êtes arrivé jusqu'ici et que le jeu fonctionne, vous êtes prêt à jouer et à apprendre ! 🎉

Bon jeu et bon apprentissage ! 🚀
