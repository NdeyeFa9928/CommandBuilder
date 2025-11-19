# 🚀 Guide de démarrage - CommandBuilder

> Guide complet pour un nouveau développeur qui prend en main le projet

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation pas à pas](#installation-pas-à-pas)
3. [Premier lancement](#premier-lancement)
4. [Commandes essentielles](#commandes-essentielles)
5. [Structure du projet](#structure-du-projet)
6. [Workflow de développement](#workflow-de-développement)
7. [Tests](#tests)
8. [Dépannage](#dépannage)

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
    arguments: List[TaskArgument] = []

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
    type: str
    required: int
    default: str = ""
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

### 5. Push et PR

```bash
git push origin feature/ma-nouvelle-fonctionnalite
# Créer une Pull Request sur GitHub/GitLab
```

---

## Tests

### Organisation des tests

```
tests/
├── components/        # Tests UI
├── models/           # Tests des modèles
├── services/         # Tests des services
├── integration/      # Tests d'intégration
└── performance/      # Tests de performance
```

### Écrire un test

```python
# tests/models/test_mon_modele.py
import pytest
from command_builder.models.mon_modele import MonModele

def test_creation():
    """Test de création d'un modèle."""
    modele = MonModele(name="Test")
    assert modele.name == "Test"

def test_validation():
    """Test de validation."""
    with pytest.raises(ValidationError):
        MonModele(name="")  # Nom vide = erreur
```

### Exécuter les tests

```bash
# Tous les tests
task test

# Un fichier spécifique
pytest command_builder/tests/models/test_mon_modele.py -v

# Un test spécifique
pytest command_builder/tests/models/test_mon_modele.py::test_creation -v

# Avec couverture détaillée
task test:cov
```

### Couverture actuelle

- **Total : 79%**
- Models : ~90%
- Services : ~80%
- Components : ~70% (normal pour UI)
- Integration : ~95%

**Objectif : 85%+ global**

---

## Dépannage

### Problème : "task: command not found"

**Solution :**
```bash
# Windows (avec Chocolatey)
choco install go-task

# Ou télécharger depuis
# https://taskfile.dev/installation/
```

### Problème : "pipenv: command not found"

**Solution :**
```bash
python -m pip install --user pipenv

# Ajouter au PATH si nécessaire
# Windows : %USERPROFILE%\AppData\Roaming\Python\Python312\Scripts
```

### Problème : "Python version mismatch"

**Solution :**
```bash
# Vérifier la version
python --version

# Doit être 3.12+
# Sinon, installer Python 3.12 depuis python.org
```

### Problème : "Module not found"

**Solution :**
```bash
# Réinstaller les dépendances
pipenv install --dev

# Ou forcer la réinstallation
pipenv --rm
pipenv install --dev
```

### Problème : Tests échouent

**Solution :**
```bash
# Vérifier l'environnement
pipenv --venv

# Réinstaller pytest-cov
pipenv install pytest-cov

# Exécuter avec détails
task test:verbose
```

### Problème : L'application ne se lance pas

**Solution :**
```bash
# Vérifier les dépendances
pipenv check

# Réinstaller PySide6
pipenv install pyside6 --force

# Lancer avec détails d'erreur
pipenv run python main.py
```

### Problème : Erreurs de style (ruff)

**Solution :**
```bash
# Corriger automatiquement
task fix

# Vérifier ce qui reste
task lint
```

---

## Ressources utiles

### Documentation du projet

- `README.md` - Vue d'ensemble
- `docs/TESTS_SUMMARY.md` - Résumé des tests
- `docs/BUILD_AND_DISTRIBUTION.md` - Guide de build
- `docs/SHARED_ARGUMENTS_IMPROVEMENTS.md` - Arguments partagés
- `docs/WITH_ARGUMENTS_INTERFACE.md` - Interface WithArguments

### Technologies utilisées

- **Python 3.12** - https://docs.python.org/3.12/
- **PySide6** - https://doc.qt.io/qtforpython-6/
- **Pydantic** - https://docs.pydantic.dev/
- **pytest** - https://docs.pytest.org/
- **Ruff** - https://docs.astral.sh/ruff/

### Commandes Git utiles

```bash
# Voir l'état
git status

# Voir les différences
git diff

# Annuler les modifications
git checkout -- fichier.py

# Créer une branche
git checkout -b feature/nom

# Mettre à jour depuis main
git pull origin main

# Voir l'historique
git log --oneline
```

---

## Checklist du nouveau développeur

- [ ] Python 3.12+ installé
- [ ] Git installé
- [ ] Task installé
- [ ] Projet cloné
- [ ] `task setup` exécuté avec succès
- [ ] `task test` passe (156 tests)
- [ ] `task run` lance l'application
- [ ] Documentation lue (README.md)
- [ ] Premier test écrit et passant
- [ ] Première modification commitée

---

## Prochaines étapes

1. **Explorer le code**
   - Lire `main.py` (point d'entrée)
   - Explorer `components/main_window/`
   - Comprendre les modèles dans `models/`

2. **Modifier une tâche YAML**
   - Ouvrir `data/tasks/import_task.yaml`
   - Ajouter un argument
   - Relancer l'app pour voir le changement

3. **Écrire un test**
   - Créer `tests/models/test_exemple.py`
   - Écrire un test simple
   - Exécuter avec `pytest`

4. **Contribuer**
   - Choisir une issue sur GitHub
   - Créer une branche
   - Implémenter et tester
   - Créer une Pull Request

---

## Conseils

### Pour bien démarrer

1. **Lisez le README.md en entier** - Vue d'ensemble complète
2. **Lancez l'application** - Comprenez ce qu'elle fait
3. **Explorez les tests** - Exemples de code
4. **Modifiez un YAML** - Voyez l'impact immédiat
5. **Posez des questions** - L'équipe est là pour aider

### Bonnes pratiques

- Toujours exécuter `task test` avant de commit
- Utiliser `task fix` pour formater le code
- Écrire des tests pour le nouveau code
- Commenter le code complexe
- Suivre la structure existante
- Faire des commits atomiques et clairs

### Erreurs à éviter

- Ne pas tester avant de commit
- Modifier le code sans comprendre l'architecture
- Ignorer les erreurs de lint
- Supprimer des tests existants
- Hardcoder des valeurs (utiliser YAML)
- Oublier de documenter les nouvelles fonctionnalités

---

Bienvenue dans l'équipe CommandBuilder !

Si vous avez des questions, n'hésitez pas à :
- Consulter la documentation dans `docs/`
- Demander de l'aide à Ndeye Fatou Mbow
- Ouvrir une issue sur GitHub
