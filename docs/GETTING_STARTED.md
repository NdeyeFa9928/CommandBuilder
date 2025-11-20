# Guide de démarrage - CommandBuilder

> Guide complet pour un nouveau développeur qui prend en main le projet

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation pas à pas](#installation-pas-à-pas)
3. [Premier lancement](#premier-lancement)
4. [Commandes essentielles](#commandes-essentielles)

---

## Prérequis

### Logiciels requis

1. **Python 3.12+**
   - Télécharger : https://www.python.org/downloads/
   - Vérifier l'installation : `python --version`
   - Cocher "Add Python to PATH" lors de l'installation

2. **Git**
   - Télécharger : https://git-scm.com/downloads
   - Vérifier : `git --version`

3. **Task (go-task)**
   - Windows (avec Chocolatey) : `choco install go-task`
   - Ou télécharger : https://taskfile.dev/installation/
   - Vérifier : `task --version`

4. **Pipenv** (sera installé automatiquement)
   - Gestionnaire de dépendances Python
   - Installation : `python -m pip install pipenv`

### Système d'exploitation

- **Windows 10/11** (recommandé)
- L'application génère des commandes Windows CLI

---

## Installation pas à pas

### Étape 1 : Cloner le projet

```bash
# Cloner le dépôt
git clone <repository-url>
cd CommandBuilder
```

### Étape 2 : Installation automatique (recommandée)

```bash
# Installation complète en une commande
task setup
```

**Ce que fait `task setup` :**
1. Met à jour pip
2. Installe pipenv
3. Crée l'environnement virtuel
4. Installe toutes les dépendances (production + dev)
5. Vérifie le formatage du code
6. Affiche un message de confirmation

**Durée estimée :** 2-5 minutes (selon votre connexion)

### Étape 3 : Vérification

```bash
# Vérifier que tout fonctionne
task test:fast
```

Si vous voyez `156 passed, 9 skipped` → Installation réussie !

---

## Premier lancement

### Lancer l'application

```bash
# Méthode 1 : Avec Task (recommandé)
task run

# Méthode 2 : Avec Pipenv
pipenv run python main.py

# Méthode 3 : Dans le shell Pipenv
pipenv shell
python main.py
```

### Ce que vous devriez voir

1. **Fenêtre principale** avec 3 zones :
   - **Gauche** : Liste des tâches disponibles
   - **Centre** : Formulaire de commandes avec arguments
   - **Droite** : Console de sortie

2. **Tâches disponibles** (exemples) :
   - Import TDMS
   - Export CSV
   - Validation de données
   - etc.

3. **Fonctionnalités** :
   - Cliquer sur une tâche pour voir ses commandes
   - Remplir les arguments
   - Cliquer "Exécuter" pour lancer les commandes

---

## Commandes essentielles

### Développement quotidien

```bash
# Lancer l'application
task run

# Exécuter les tests (avec couverture)
task test

# Vérifier le style de code
task lint

# Corriger automatiquement le style
task fix
```

### Tests

```bash
# Tests rapides (sans couverture)
task test:fast

# Tests avec couverture détaillée
task test

# Tests avec rapport HTML
task test:cov
# Puis ouvrir : htmlcov/index.html

# Tests par catégorie
task test:services    # Services uniquement
task test:models      # Modèles uniquement
task test:components  # Composants UI uniquement
```

### build

```bash
# Créer un exécutable
task build

# Build avec console (pour debug)
task build-dev

# Nettoyer les fichiers générés
task clean
```

### Workflow complet

```bash
# Workflow de développement complet
task dev
# = fix + test avec couverture

# Workflow CI (comme sur le serveur)
task ci
# = lint + test avec couverture
```

### Aide

```bash
# Voir toutes les commandes disponibles
task

# Ou
task --list
```

---

## Structure du projet

### Vue d'ensemble

```
CommandBuilder/
├── command_builder/          # Code source principal
│   ├── assets/               # Icônes, images
│   ├── components/           # Composants UI (PySide6)
│   ├── data/                 # Définitions YAML
│   ├── models/               # Modèles Pydantic
│   ├── services/             # Logique métier
│   └── tests/                # Tests (pytest)
├── docs/                     # Documentation
├── main.py                   # Point d'entrée
├── taskfile.yml              # Automatisation
├── Pipfile                   # Dépendances
└── README.md                 # Documentation principale
```

### Composants clés

#### 1. **Components** (UI)

Chaque composant a cette structure :
```
component_name/
├── __init__.py              # Export
├── component_name.py        # Logique Python
├── component_name.ui        # Interface Qt Designer
└── component_name.qss       # Styles CSS-like
```

**Composants principaux :**
- `main_window/` - Fenêtre principale
- `task_list/` - Liste des tâches
- `command_form/` - Formulaire de commandes
- `console_output/` - Console de sortie
- `task_component/` - Affichage d'une tâche
- `command_component/` - Affichage d'une commande
- `argument_component/` - Champ de saisie d'argument

#### 2. **Models** (Données)

```python
# models/task.py
class Task(BaseModel):
    name: str
    description: str
    commands: List[Command]
    arguments: List[TaskArgument] = []  # Arguments partagés

# models/command.py
class Command(BaseModel):
    name: str
    description: str
    command: str
    arguments: List[Argument] = []

# models/arguments.py
class Argument(BaseModel):
    code: str
    name: str
    type: str  # "text", "file", "folder"
    required: int  # 0 = optionnel, 1 = obligatoire
    default: str = ""
    validation: Optional[dict] = None
```

#### 3. **Services** (Logique)

- `yaml_task_loader.py` - Charge les tâches depuis YAML
- `yaml_error_handler.py` - Gestion des erreurs YAML
- `command_executor.py` - Exécution des commandes

#### 4. **Data** (Configuration)

```
data/
├── commands/           # Commandes individuelles (YAML)
│   ├── tdms_import.yaml
│   ├── csv_export.yaml
│   └── ...
└── tasks/             # Tâches (groupes de commandes)
    ├── import_task.yaml
    ├── export_task.yaml
    └── ...
``` 

---

## Workflow de développement

### 1. Créer une branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### 2. Développer

```bash
# Lancer l'app en mode dev
task run

# Modifier le code...
# Tester régulièrement
task test:fast
```

### 3. Vérifier la qualité

```bash
# Corriger le style
task fix

# Vérifier les tests avec couverture
task test
```

### 4. Commit

```bash
git add .
git commit -m "feat: ajout de la nouvelle fonctionnalité"
```

