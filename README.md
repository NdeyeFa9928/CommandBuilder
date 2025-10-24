# CommandBuilder

> Assistant GUI pour composer des commandes CLI Windows sans erreurs de syntaxe

## Table des matières

- [Description](#description)
- [Démarrage rapide](#démarrage-rapide)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Fonctionnalités clés](#fonctionnalités-clés)
- [Structure du projet](#structure-du-projet)
- [Architecture](#architecture)
  - [Composants modulaires](#composants-modulaires)
  - [Mixin WithArguments](#mixin-witharguments)
  - [Injection de dépendances](#injection-de-dépendances)
- [Outils de développement](#outils-de-développement)
  - [Taskfile](#taskfile)
  - [Pipenv](#pipenv)
  - [Ruff](#ruff)
- [Utilisation](#utilisation)
- [Développement](#développement)
- [Build et distribution](#build-et-distribution)
- [Documentation complémentaire](#documentation-complémentaire)

---

## Description

**CommandBuilder** est une application de bureau développée en Python qui permet de construire et d'exécuter des commandes CLI Windows de manière visuelle et sécurisée. L'application offre une interface graphique moderne pour définir des tâches composées de commandes avec leurs arguments, en éliminant les risques d'erreurs de syntaxe.

Le projet est conçu avec une architecture modulaire et découplée, facilitant la maintenance, l'évolution et les tests. Les commandes sont définies via des fichiers YAML, permettant une extensibilité sans modification du code.

---

## Démarrage rapide

Pour les utilisateurs pressés :

```bash
# Installation complète
task setup

# Lancer l'application
task run
```

Pour plus de détails, consultez la section [Installation](#installation).

---

## Prérequis

- **Python 3.12** ou supérieur
- **Pipenv** pour la gestion des dépendances
- **Task** (go-task) pour l'automatisation des tâches
- **Windows** (l'application est conçue pour générer des commandes Windows)

---

## Installation

### Installation rapide

```bash
# Cloner le dépôt
git clone <repository-url>
cd CommandBuilder

# Installation complète (dépendances + configuration)
task setup
```

### Installation manuelle

```bash
# 1. Installer pipenv si nécessaire
python -m pip install pipenv

# 2. Installer les dépendances
pipenv install --dev

# 3. Activer l'environnement virtuel
pipenv shell

# 4. Lancer l'application
python main.py
```

---

## Fonctionnalités clés

- **Interface utilisateur moderne** avec thème sombre et composants réutilisables
- **Définition des commandes via YAML** pour une extensibilité sans code
- **Validation des entrées utilisateur** avec Pydantic
- **Support de multiples types d'arguments** (fichier, dossier, nombre, texte, booléen, sélection)
- **Générateur de commandes** prêtes à l'exécution ou à l'export en fichiers .bat
- **Architecture modulaire et découplée** avec injection de dépendances
- **Composants UI réutilisables** (TaskComponent, CommandComponent, ArgumentComponent)
- **Système de tâches** regroupant plusieurs commandes liées
- **Gestion des arguments partagés** entre commandes d'une même tâche

---

## Structure du projet

```
CommandBuilder/
├── command_builder/              # Package principal
│   ├── assets/                   # Ressources (icônes, images)
│   ├── components/               # Composants UI modulaires
│   │   ├── task_component/       # Composant d'affichage d'une tâche
│   │   ├── task_list/            # Liste de tâches (conteneur)
│   │   ├── command_component/    # Composant d'affichage d'une commande
│   │   ├── command_form/         # Formulaire de commandes (conteneur)
│   │   ├── argument_component/   # Composant de saisie d'argument
│   │   ├── console_output/       # Affichage des sorties console
│   │   └── main_window/          # Fenêtre principale
│   ├── data/                     # Définitions YAML
│   │   ├── commands/             # Commandes individuelles
│   │   └── tasks/                # Tâches (groupes de commandes)
│   ├── models/                   # Modèles de données Pydantic
│   │   ├── arguments.py          # Modèles d'arguments
│   │   ├── command.py            # Modèle de commande
│   │   ├── task.py               # Modèle de tâche
│   │   └── with_argument.py     # Mixin WithArguments
│   ├── services/                 # Logique métier
│   │   └── yaml_task_loader.py   # Chargement des tâches YAML
│   └── tests/                    # Tests unitaires et d'intégration
├── docs/                         # Documentation détaillée
├── main.py                       # Point d'entrée de l'application
├── build_executable.py           # Script de build PyInstaller
├── taskfile.yml                  # Automatisation des tâches
├── Pipfile                       # Dépendances Python
└── README.md                     # Ce fichier
```

### Organisation des composants

Chaque composant UI suit une structure cohérente :
```
component_name/
├── __init__.py           # Export public du composant
├── component_name.py     # Logique du composant (Python)
├── component_name.ui     # Interface graphique (Qt Designer)
└── component_name.qss    # Styles CSS-like (Qt StyleSheet)
```

Cette organisation garantit :
- **Séparation des responsabilités** (logique / UI / style)
- **Réutilisabilité** des composants
- **Maintenabilité** facilitée
- **Testabilité** améliorée

---

## Architecture

### Composants modulaires

L'architecture repose sur une hiérarchie de composants découplés :

**Composants conteneurs** (gèrent des collections) :
- `TaskList` : Affiche une liste de tâches, gère le tri et la sélection
- `CommandForm` : Affiche les commandes d'une tâche, collecte les valeurs des arguments
- `ConsoleOutput` : Affiche les sorties et commandes générées

**Composants enfants** (affichent un élément unique) :
- `TaskComponent` : Affiche une tâche avec bouton cliquable
- `CommandComponent` : Affiche une commande avec ses arguments (modes simple/complet)
- `ArgumentComponent` : Affiche un champ de saisie avec validation et bouton parcourir

**Orchestrateur** :
- `MainWindow` : Coordonne tous les composants et gère la communication via signaux Qt

**Flux de données** :
```
User → TaskComponent → TaskList → MainWindow → CommandForm → CommandComponent → ArgumentComponent
                                                                                        ↓
User ← ConsoleOutput ← MainWindow ← CommandForm ← CommandComponent ← ArgumentComponent
```

### Mixin WithArguments

Le mixin `WithArguments` est une interface qui factorise le comportement commun entre les modèles `Task` et `Command`. Il élimine la duplication de code et permet un traitement uniforme des arguments.

**Avantages** :
- **Élimination de la duplication** : Une seule implémentation des méthodes de gestion d'arguments
- **Polymorphisme** : Traitement uniforme de `Task` et `Command` via l'interface commune
- **Extensibilité** : Toute nouvelle classe avec arguments peut hériter du mixin
- **Maintenabilité** : Modifications centralisées dans un seul fichier

**Méthodes fournies** :
```python
get_argument_by_code(code: str) -> Optional[Argument]
get_argument_values() -> Dict[str, str]
has_required_arguments() -> bool
get_required_arguments() -> List[Argument]
get_optional_arguments() -> List[Argument]
has_argument(code: str) -> bool
count_arguments() -> int
count_required_arguments() -> int
```

**Exemple d'utilisation** :
```python
def validate_entity(entity: WithArguments) -> bool:
    """Valide n'importe quelle entité avec arguments"""
    if not entity.has_required_arguments():
        return False
    return True

# Fonctionne avec Task ET Command
validate_entity(my_task)
validate_entity(my_command)
```

Pour plus de détails, voir [docs/WITH_ARGUMENTS_INTERFACE.md](docs/WITH_ARGUMENTS_INTERFACE.md).

### Injection de dépendances

Les composants conteneurs (`TaskList`, `CommandForm`) utilisent l'injection de dépendances via des factories pour créer leurs widgets enfants. Cela élimine le couplage fort et facilite les tests.

**Principe** :
```python
# TaskList accepte une factory optionnelle
task_list = TaskList(
    task_widget_factory=lambda task, parent: CustomTaskWidget(task, parent)
)

# CommandForm accepte une factory optionnelle
command_form = CommandForm(
    command_widget_factory=lambda cmd, parent, mode: CustomCommandWidget(cmd, parent, mode)
)
```

**Avantages** :
- **Découplage** : Les conteneurs ne dépendent pas directement des widgets enfants
- **Testabilité** : Injection de mocks pour les tests unitaires
- **Flexibilité** : Possibilité d'utiliser des widgets personnalisés
- **Rétrocompatibilité** : Factories par défaut si non spécifiées

---

## Outils de développement

### Taskfile

Le projet utilise [Task](https://taskfile.dev/) pour automatiser les tâches de développement. Task est un runner de tâches moderne écrit en Go, alternative à Make.

**Pourquoi Task ?**
- **Syntaxe YAML** claire et lisible
- **Multiplateforme** (Windows, Linux, macOS)
- **Gestion des dépendances** entre tâches
- **Variables et templating** intégrés
- **Parallélisation** des tâches

**Commandes principales** :
```bash
task                  # Affiche l'aide et les commandes disponibles
task install          # Installation complète des dépendances
task run              # Lance l'application
task test             # Exécute tous les tests
task test:cov         # Tests avec couverture de code
task lint             # Vérifie le style du code
task fix              # Corrige automatiquement le style
task build            # Crée l'exécutable
task clean            # Nettoie les fichiers générés
task dev              # Workflow complet (fix + test + cov)
task ci               # Workflow CI (lint + test + cov)
```

**Organisation du Taskfile** :
- **Tasks d'installation** : `install`, `update-pip`, `install-deps`
- **Tasks de qualité** : `lint`, `fix`
- **Tasks de test** : `test`, `test:services`, `test:models`, `test:components`, `test:cov`
- **Tasks d'application** : `run`, `build`, `build-dev`
- **Tasks de maintenance** : `clean`, `info`
- **Workflows** : `dev`, `ci`, `setup`

### Pipenv

Le projet utilise [Pipenv](https://pipenv.pypa.io/) pour la gestion des dépendances et des environnements virtuels.

**Pourquoi Pipenv ?**
- **Gestion unifiée** des dépendances et de l'environnement virtuel
- **Fichiers Pipfile et Pipfile.lock** pour un versioning déterministe
- **Séparation** des dépendances de production et de développement
- **Résolution automatique** des conflits de dépendances
- **Sécurité** : Vérification des vulnérabilités avec `pipenv check`

**Dépendances principales** :
- **PySide6** : Framework Qt pour l'interface graphique
- **Pydantic** : Validation des données et modèles
- **PyYAML** : Parsing des fichiers YAML
- **pytest** : Framework de tests
- **ruff** : Linter et formateur ultra-rapide
- **PyInstaller** : Création d'exécutables (dev)

**Commandes utiles** :
```bash
pipenv install              # Installe les dépendances
pipenv install --dev        # Installe avec les dépendances de dev
pipenv shell                # Active l'environnement virtuel
pipenv run python main.py   # Exécute un script dans l'environnement
pipenv check                # Vérifie les vulnérabilités
pipenv graph                # Affiche l'arbre des dépendances
```

### Ruff

Le projet utilise [Ruff](https://github.com/astral-sh/ruff) pour le linting et le formatage du code.

**Pourquoi Ruff ?**
- **Vitesse** : 10-100x plus rapide que Flake8 et Black
- **Tout-en-un** : Remplace Flake8, Black, isort, pyupgrade, etc.
- **Compatible** avec les règles de Flake8, pylint, etc.
- **Configuration simple** via `pyproject.toml` ou `ruff.toml`
- **Corrections automatiques** pour la plupart des erreurs

**Utilisation** :
```bash
# Vérifier le code
ruff check .

# Corriger automatiquement
ruff check --fix .

# Formater le code
ruff format .

# Via Task (recommandé)
task lint    # Vérification
task fix     # Correction + formatage
```

**Règles appliquées** :
- Style PEP 8
- Imports triés et organisés
- Suppression du code mort
- Simplifications de code
- Corrections de sécurité

---

## Utilisation

### Définir des commandes

Créez un fichier YAML dans `command_builder/data/commands/` :

```yaml
# exemple_import.yaml
name: "Importer des données"
description: "Importe un fichier de données pour traitement"
command: "data_import --input {input_file} --output {output_dir} --format {format}"
arguments:
  - code: "input_file"
    name: "Fichier source"
    description: "Sélectionnez le fichier à importer"
    type: "file"
    required: true
    filters: "*.csv *.xlsx"
  
  - code: "output_dir"
    name: "Dossier de sortie"
    description: "Dossier où enregistrer les résultats"
    type: "directory"
    default: "./output"
  
  - code: "format"
    name: "Format de sortie"
    type: "select"
    options:
      - "json"
      - "xml"
      - "csv"
    default: "json"
```

### Créer des tâches

Créez un fichier YAML dans `command_builder/data/tasks/` :

```yaml
# ma_tache.yaml
name: "Traitement complet"
description: "Import et analyse de données"
arguments:
  - code: "db_path"
    name: "Base de données"
    type: "file"
    required: true
    shared: true  # Argument partagé entre toutes les commandes

commands:
  - !include ../commands/exemple_import.yaml
  - !include ../commands/exemple_analyse.yaml
```

### Types d'arguments supportés

| Type | Description | Exemple |
|------|-------------|---------|
| `text` | Champ texte libre | Nom, description |
| `file` | Sélecteur de fichier | Fichier d'entrée |
| `directory` | Sélecteur de dossier | Dossier de sortie |
| `number` | Nombre entier ou décimal | Port, timeout |
| `boolean` | Case à cocher | Verbose, debug |
| `select` | Liste déroulante | Format, mode |

---

## Développement

### Lancer l'application en mode développement

```bash
# Workflow complet (formatage + tests + application)
task dev

# Ou simplement lancer l'application
task run
```

### Exécuter les tests

```bash
# Tous les tests
task test

# Tests avec couverture
task test:cov

# Tests par catégorie
task test:services
task test:models
task test:components

# Tests rapides (sans verbosité)
task test:fast
```

### Vérifier et corriger le style

```bash
# Vérifier uniquement
task lint

# Corriger automatiquement
task fix
```

### Structure des tests

```
command_builder/tests/
├── models/              # Tests des modèles Pydantic
├── services/            # Tests des services métier
├── components/          # Tests des composants UI
└── conftest.py          # Fixtures pytest partagées
```

---

## Build et distribution

### Créer un exécutable

```bash
# Build production (sans console)
task build

# Build développement (avec console pour debug)
task build-dev

# L'exécutable est créé dans dist/CommandBuilder.exe
```

### Gestion du dossier **data/tasks** à l'exécution

| Contexte | Chemin chargé par l'application | Comment ajouter des tâches ? |
|----------|---------------------------------|------------------------------|
| **Développement** (`python main.py`, `task run`) | `command_builder/data/tasks/` dans le dépôt | Créez/éditez directement vos fichiers YAML dans ce dossier. |
| **Exécutable _one-dir_** (`dist/CommandBuilder.exe` + dossier) | `dist/data/tasks/` (s’il existe) sinon ressources embarquées | Déposez des YAML dans `dist/data/tasks/`; ils seront détectés au prochain lancement. |
| **Exécutable _one-file_** (`dist/CommandBuilder.exe` seul) | Ressources embarquées dans l’EXE | Créez manuellement `dist/data/tasks/` pour surcharger, ou rebuild. |

Cette logique est implémentée dans `command_builder/services/yaml_task_loader.py`.

### Script de build

Le script `build_executable.py` utilise PyInstaller pour créer un exécutable autonome :

**Fonctionnalités** :
- Collecte automatique des fichiers `.ui`, `.qss`, `.json`, `.yaml`
- Inclusion des assets (icônes, images)
- Mode windowed (sans console) ou console (debug)
- Icône d'application personnalisée
- Exécutable unique (onefile)

**Personnalisation** :
```python
# Modifier build_executable.py pour ajouter des ressources
def collect_data_files(base_dir):
    # Ajouter vos propres patterns de fichiers
    pass
```

### Nettoyage

```bash
# Supprimer les fichiers générés
task clean
```

---

## Documentation complémentaire

- [WITH_ARGUMENTS_INTERFACE.md](docs/WITH_ARGUMENTS_INTERFACE.md) - Documentation détaillée du mixin WithArguments
- [YAML_SYSTEM.md](docs/YAML_SYSTEM.md) - Système de définition des commandes en YAML
- [SHARED_ARGUMENTS_IMPROVEMENTS.md](docs/SHARED_ARGUMENTS_IMPROVEMENTS.md) - Gestion des arguments partagés
- [adr/](docs/adr/) - Architecture Decision Records

---

## Licence

[Votre licence ici]

## Auteurs

[Vos informations ici]
