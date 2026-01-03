# 🎮 Morpion (Tic‑Tac‑Toe) — Pygame + IA apprenante (DQN)

Projet Python de Morpion 3×3 avec **interface Pygame** (menus, boutons, machine à états) et une IA qui **apprend par Deep Reinforcement Learning** via **DQN (PyTorch)**.

Le projet contient aussi une version console (utile pour tester rapidement la logique).

---

## ✅ Fonctionnalités

### Modes de jeu (Pygame)
- **Joueur vs IA** : vous jouez contre l’agent DQN
- **2 Joueurs** : local (sans IA)
- **IA vs IA** : démonstration (self-play)

### Difficulté (mode IA)
Les boutons **Facile / Moyen / Difficile** existent toujours : dans cette version DQN, ils contrôlent surtout l’**exploration ε-greedy** (donc le niveau d’“aléatoire” du comportement).

### IA DQN (conforme cahier)
- Réseau de neurones PyTorch (MLP)
- **Experience Replay**
- **ε-greedy exploration**
- Récompenses : **+1 victoire / -1 défaite / 0 match nul**
- Données générées par le jeu (aucun dataset externe)
- Sauvegarde/chargement du modèle dans `models/dqn_tictactoe.pt`

### Améliorations RL incluses
- **Target Network** (stabilisation)
- **Double DQN** (réduit la surestimation)

---

## 📦 Prérequis

- Python installé
- Pour la version Pygame : `pygame`
- Pour l’IA DQN : `torch`

Remarque Windows : selon votre configuration, `python` peut pointer vers un autre Python. Dans ce dépôt, les commandes ci-dessous utilisent **`python.exe`** (souvent le plus fiable sous Windows).

---

## 🚀 Installation (Windows recommandé)

### Option A — Installation simple (dans le Python système)

```powershell
python.exe -m pip install pygame torch
```

### Option B — Installation propre avec environnement virtuel (recommandé)

```powershell
python.exe -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pygame torch
```

Si vous utilisez un autre shell (cmd), l’activation est différente :
```bat
.venv\Scripts\activate.bat
```

---

## ▶️ Lancer le jeu

### Version Pygame (recommandée)

```powershell
python.exe morpion_pygame.py
```

### Version console

```powershell
python.exe morpion.py
```

---

## 🤖 Entraînement DQN : comment ça marche dans ce projet

### 1) Bootstrap (première exécution)
Au premier lancement, si aucun fichier modèle n’existe (`models/dqn_tictactoe.pt`), le jeu effectue une **phase d’entraînement self-play** (IA vs IA) pour éviter une IA totalement aléatoire.

Le nombre d’épisodes de bootstrap est contrôlé par :
- `DEFAULT_BOOTSTRAP_EPISODES` dans `dqn_agent.py`

Ensuite, le modèle est sauvegardé dans `models/dqn_tictactoe.pt`.

### 2) En jeu (IA vs humain)
L’IA joue ses coups via le réseau $Q(s,a)$. Le code enregistre aussi des transitions pour un apprentissage léger (optionnel) et sauvegarde lorsque l’épisode se termine.

### 3) IA vs IA
Ce mode permet de voir l’agent jouer des parties automatiquement.

---

## 💾 Sauvegarde / chargement du modèle

- Le modèle est lu via `agent.load("models/dqn_tictactoe.pt")`.
- Il est sauvegardé via `agent.save("models/dqn_tictactoe.pt")`.

Le checkpoint contient :
- réseau online
- réseau target
- état de l’optimizer
- epsilon + compteurs

---

## 🧪 Paramètres faciles à modifier (expérimentations PFE)

Dans `dqn_agent.py`, en haut du fichier :
- `DEFAULT_TARGET_UPDATE_INTERVAL`
- `DEFAULT_SELF_PLAY_EPISODES`
- `DEFAULT_BOOTSTRAP_EPISODES`
- `DEFAULT_GAMMA`, `DEFAULT_LR`, `DEFAULT_BATCH_SIZE`
- `DEFAULT_REPLAY_CAPACITY`, `DEFAULT_MIN_REPLAY_SIZE`
- `DEFAULT_EPSILON_START`, `DEFAULT_EPSILON_END`, `DEFAULT_EPSILON_DECAY_STEPS`
- `DEFAULT_TRAIN_STEPS_PER_MOVE`

---

## 🧠 Explication conceptuelle (texte pour rapport/PFE)

### Formulation RL
- **État $s$** : plateau 3×3 encodé en 9 valeurs (vide / moi / adversaire)
- **Action $a$** : choisir une case vide (0..8)
- **Récompense $r$** : +1 victoire, -1 défaite, 0 nul

### Objectif du DQN
Apprendre $Q(s,a)$, la valeur attendue (retour futur) en jouant l’action $a$ dans l’état $s$.

La cible classique est :
$$
y = r + \gamma \max_{a'} Q(s', a')
$$

### Experience Replay
On stocke les transitions $(s,a,r,s',done)$ dans une mémoire, puis on entraîne le réseau sur des mini-batchs aléatoires. Cela stabilise et “décorrèle” les données.

### ε-greedy
Avec probabilité $\varepsilon$, on choisit une action aléatoire (exploration), sinon on choisit l’action qui maximise $Q$ (exploitation).

### Target Network + Double DQN
- **Target Network** : on calcule les cibles avec un réseau “gelé” périodiquement mis à jour, ce qui stabilise l’entraînement.
- **Double DQN** : on choisit l’action avec le réseau online et on l’évalue avec le réseau target, ce qui réduit la surestimation.

### Pourquoi pas de dataset externe ?
Le dataset est **généré automatiquement** par les épisodes du jeu (self-play et parties contre un humain). Le RL apprend à partir des récompenses, pas d’exemples annotés.

---

## 📁 Structure du projet

```
.
├── morpion_pygame.py        # UI Pygame + états (menu/difficulté/jeu/fin) + intégration DQN
├── morpion.py               # version console (logique et règles)
├── dqn_agent.py             # DQN (PyTorch) + replay + Target Network + Double DQN
├── tictactoe_env.py         # helpers d’environnement: encodage état, actions valides, victoire/nul
├── models/
│   └── dqn_tictactoe.pt     # modèle entraîné (checkpoint)
└── INSTALLATION.md
```

---

## 🛠️ Dépannage (problèmes fréquents)

### 1) `ModuleNotFoundError: No module named 'pygame'`
```powershell
python.exe -m pip install pygame
```

### 2) `ModuleNotFoundError: No module named 'torch'`
```powershell
python.exe -m pip install torch
```

Si l’installation échoue, utilisez une version Python compatible avec PyTorch (souvent 3.10–3.12).

### 3) Le jeu se lance mais l’IA est “désactivée”
Si PyTorch n’est pas détecté, les modes IA reviennent au menu avec un message.
Installez `torch` puis relancez.

### 4) Le mauvais Python est utilisé
Vérifiez :
```powershell
python.exe --version
python --version
```
Si les versions diffèrent, privilégiez `python.exe` (ou activez votre `.venv`).

---

## 📝 Licence / Usage

Projet pédagogique (portfolio / PFE). Libre d’utilisation à des fins éducatives.

---

Bon jeu !
