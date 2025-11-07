# Système YAML de CommandBuilder

> Documentation complète du système YAML pour définir des commandes, tâches et pipelines

Ce document explique le fonctionnement du système YAML de CommandBuilder, qui permet de définir des pipelines, des tâches et des commandes de manière modulaire et extensible.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Structure des fichiers](#structure-des-fichiers)
3. [Types d'arguments](#types-darguments)
4. [Ajouter une nouvelle commande](#ajouter-une-nouvelle-commande)
5. [Ajouter une nouvelle tâche](#ajouter-une-nouvelle-tâche)
6. [Arguments partagés](#arguments-partagés)
7. [Système d'inclusion](#système-dinclusion)
8. [Bonnes pratiques](#bonnes-pratiques)
9. [Exemples complets](#exemples-complets)
10. [Dépannage](#dépannage)

## Vue d'ensemble

Le système YAML de CommandBuilder permet de définir :

- **Tâches** : Regroupements logiques de commandes liées
- **Commandes** : Instructions CLI individuelles avec leurs arguments
- **Arguments** : Paramètres des commandes avec validation

### Hiérarchie

```
Tâche (task)
├── Argument partagé (optionnel)
└── Commandes
    ├── Commande 1
    │   └── Arguments
    ├── Commande 2
    │   └── Arguments
    └── Commande 3
        └── Arguments
```

### Avantages du système YAML

- **Modularité** : Les commandes peuvent être réutilisées dans plusieurs tâches
- **Lisibilité** : Format YAML clair et facile à maintenir
- **Inclusion** : Support des références entre fichiers avec `!include`
- **Extensibilité** : Ajouter de nouvelles commandes/tâches sans modifier le code
- **Validation** : Validation des arguments avec Pydantic

## Structure des fichiers

```
command_builder/
└── data/
    ├── commands/     # Définitions de commandes individuelles
    │   ├── import/
    │   │   ├── tdmsimport.yaml
    │   │   └── csvimport.yaml
    │   ├── export/
    │   │   ├── csvexport.yaml
    │   │   └── kmzexport.yaml
    │   └── compute/
    │       ├── computekey.yaml
    │       └── computeprofile.yaml
    └── tasks/        # Définitions de tâches (regroupements de commandes)
        ├── import_task.yaml
        ├── export_task.yaml
        └── compute_task.yaml
```

### Chargement des tâches

Au démarrage, CommandBuilder charge **automatiquement** tous les fichiers YAML du dossier `data/tasks/`. Chaque fichier YAML représente une tâche qui apparaît dans l'interface.

## Types d'arguments

CommandBuilder supporte plusieurs types d'arguments avec validation :

| Type | Description | Exemple | Validation |
|------|-------------|---------|-----------|
| `text` | Texte libre | `"mon_fichier"` | Longueur min/max |
| `number` | Nombre entier ou décimal | `42`, `3.14` | Min/max |
| `boolean` | Vrai/Faux | `true`, `false` | - |
| `file` | Chemin vers un fichier | `"C:\data\input.csv"` | Extensions autorisées |
| `directory` | Chemin vers un dossier | `"C:\output"` | - |
| `select` | Liste de valeurs | `["option1", "option2"]` | Options prédéfinies |

### Propriétés communes d'un argument

```yaml
arguments:
  - code: "ARG_CODE"              # Identifiant unique (utilisé dans la commande)
    name: "Nom affiché"           # Nom visible dans l'interface
    description: "Explication"    # Aide pour l'utilisateur
    type: "text"                  # Type d'argument
    required: true                # Obligatoire ? (true/false)
    default: "valeur_defaut"      # Valeur par défaut (optionnel)
    validation:                   # Validation (optionnel, selon le type)
      min_length: 1
      max_length: 100
```

---

## Ajouter une nouvelle commande

Une commande est une instruction CLI individuelle. Pour créer une nouvelle commande :

### Étape 1 : Créer le fichier

Créez un fichier YAML dans `command_builder/data/commands/` (ex: `ma_commande.yaml`)

### Étape 2 : Définir la structure

```yaml
name: "nom_commande"
description: "Description détaillée de la commande"
command: "executable {ARG1} {ARG2} --option={OPT}"
arguments:
  - code: "ARG1"
    name: "Premier argument"
    description: "Description du premier argument"
    type: "text"
    required: true
  
  - code: "ARG2"
    name: "Deuxième argument"
    description: "Description du deuxième argument"
    type: "file"
    required: false
    default: "C:\default.txt"
  
  - code: "OPT"
    name: "Option"
    description: "Sélectionnez une option"
    type: "select"
    required: true
    options: ["option1", "option2", "option3"]
```

### Propriétés requises

- **name** : Identifiant unique de la commande
- **description** : Description visible dans l'interface
- **command** : Commande CLI avec placeholders `{CODE}`
- **arguments** : Liste des arguments (peut être vide)

### Exemple complet

```yaml
name: "csvexport"
description: "Exporte les données en fichier CSV"
command: "csvexport.exe --database={DATABASE} --output={OUTPUT_FILE} --format={FORMAT}"
arguments:
  - code: "DATABASE"
    name: "Base de données"
    type: "file"
    required: true
    validation:
      file_extensions: [".db", ".sqlite"]
  
  - code: "OUTPUT_FILE"
    name: "Fichier de sortie"
    type: "file"
    required: true
    default: "export.csv"
  
  - code: "FORMAT"
    name: "Format"
    type: "select"
    required: true
    options: ["csv", "json", "xml"]
    default: "csv"
```

---

## Ajouter une nouvelle tâche

Une tâche est un regroupement logique de commandes. Pour créer une nouvelle tâche :

### Étape 1 : Créer le fichier

Créez un fichier YAML dans `command_builder/data/tasks/` (ex: `ma_tache.yaml`)

### Étape 2 : Définir la structure

```yaml
name: "Nom de la tâche"
description: "Description détaillée de la tâche"

# Arguments partagés (optionnel)
arguments:
  - code: "DATABASE"
    name: "Base de données"
    type: "file"
    required: true
    values:
      - command: "csvexport"
        argument: "DATABASE"
      - command: "computeprofile"
        argument: "DATABASE"

# Commandes de la tâche
commands:
  - !include ../commands/csvexport.yaml
  - !include ../commands/computeprofile.yaml
```

### Propriétés requises

- **name** : Nom de la tâche
- **description** : Description visible dans l'interface
- **commands** : Liste des commandes (au moins une)

### Propriétés optionnelles

- **arguments** : Arguments partagés entre les commandes

### Exemple complet

```yaml
name: "Export complet"
description: "Exporte les données en CSV et génère un profil"

arguments:
  - code: "DATABASE_FILE"
    name: "Base de données"
    description: "Fichier de base de données à traiter"
    type: "file"
    required: true
    validation:
      file_extensions: [".db", ".sqlite"]
    values:
      - command: "csvexport"
        argument: "DATABASE"
      - command: "computeprofile"
        argument: "DATABASE"

commands:
  - !include ../commands/csvexport.yaml
  - !include ../commands/computeprofile.yaml
```

---

## Arguments partagés

Les arguments partagés permettent de définir une valeur une seule fois au niveau de la tâche et de la propager automatiquement à plusieurs commandes.

### Quand les utiliser ?

- Plusieurs commandes utilisent le **même fichier d'entrée**
- Plusieurs commandes utilisent le **même dossier de sortie**
- Plusieurs commandes utilisent la **même base de données**

### Structure d'un argument partagé

```yaml
arguments:
  - code: "DATABASE_FILE"           # Identifiant unique au niveau tâche
    name: "Base de données"         # Nom affiché
    description: "Fichier DB"       # Description
    type: "file"                    # Type
    required: true                  # Obligatoire ?
    validation:                     # Validation (optionnel)
      file_extensions: [".db"]
    values:                         # Où propager la valeur
      - command: "csvexport"        # Nom de la commande
        argument: "DATABASE"        # Code de l'argument dans la commande
      - command: "computeprofile"
        argument: "DATABASE"
```

### Fonctionnement

1. L'utilisateur saisit une valeur dans le champ "Base de données"
2. La valeur est automatiquement propagée à tous les arguments cibles
3. Les modifications en temps réel s'appliquent à toutes les commandes

### Exemple concret

**Fichier tâche** (`export_task.yaml`) :
```yaml
name: "Export complet"
arguments:
  - code: "DATABASE_FILE"
    name: "Base de données"
    type: "file"
    required: true
    values:
      - command: "csvexport"
        argument: "DATABASE"
      - command: "computeprofile"
        argument: "DATABASE"
commands:
  - !include ../commands/csvexport.yaml
  - !include ../commands/computeprofile.yaml
```

**Fichier commande 1** (`csvexport.yaml`) :
```yaml
name: "csvexport"
command: "csvexport.exe --database={DATABASE} --output={OUTPUT}"
arguments:
  - code: "DATABASE"
    name: "Base de données"
    type: "file"
    required: true
  - code: "OUTPUT"
    name: "Fichier de sortie"
    type: "file"
    required: true
```

**Fichier commande 2** (`computeprofile.yaml`) :
```yaml
name: "computeprofile"
command: "computeprofile.exe --database={DATABASE}"
arguments:
  - code: "DATABASE"
    name: "Base de données"
    type: "file"
    required: true
```

**Résultat** : L'utilisateur saisit le chemin de la BD une seule fois, et elle s'applique aux deux commandes.

---

## Système d'inclusion

Le système YAML supporte l'inclusion de fichiers avec la directive `!include`. Cela permet de réutiliser et modulariser les définitions.

### Syntaxe

```yaml
# Inclusion d'une commande
- !include ../commands/ma_commande.yaml

# Inclusion d'une tâche
- !include ../tasks/ma_tache.yaml
```

### Chemins relatifs

Les chemins sont **relatifs au fichier qui contient l'inclusion** :

```
command_builder/data/
├── commands/
│   └── csvexport.yaml
├── tasks/
│   └── export_task.yaml          # Inclut csvexport.yaml
```

**Dans `export_task.yaml`** :
```yaml
commands:
  - !include ../commands/csvexport.yaml  # Remonte d'un niveau, puis entre dans commands/
```


### Avantages

- **Réutilisabilité** : Une commande peut être incluse dans plusieurs tâches
- **Modularité** : Chaque fichier a une responsabilité unique
- **Maintenabilité** : Modifier une commande met à jour toutes les tâches qui l'utilisent

---

## Bonnes pratiques

### 1. Organisation des fichiers

```
data/
├── commands/
│   ├── import/
│   │   ├── tdmsimport.yaml
│   │   └── csvimport.yaml
│   ├── export/
│   │   ├── csvexport.yaml
│   │   └── kmzexport.yaml
│   └── compute/
│       ├── computekey.yaml
│       └── computeprofile.yaml
├── tasks/
│   ├── import_task.yaml
│   ├── export_task.yaml
│   └── compute_task.yaml
```

### 2. Nommage cohérent

- **Fichiers** : `snake_case.yaml` (ex: `csv_export.yaml`)
- **Codes** : `UPPER_SNAKE_CASE` (ex: `DATABASE_FILE`)
- **Noms** : Lisibles et descriptifs (ex: "Exporter en CSV")

### 3. Réutilisabilité

- Créer des commandes **génériques** et **réutilisables**
- Utiliser les **arguments partagés** pour éviter la duplication
- Inclure les commandes dans **plusieurs tâches** si pertinent

### 4. Documentation

- **Descriptions claires** pour chaque commande et tâche
- **Aide explicite** pour chaque argument
- **Exemples** dans les descriptions si complexe

### 5. Validation

- Définir les **extensions de fichier** autorisées
- Définir les **valeurs par défaut** appropriées
- Utiliser les **types corrects** pour chaque argument

---

## Exemples complets

### Exemple 1 : Commande simple (Import TDMS)

**Fichier** : `data/commands/import/tdmsimport.yaml`

```yaml
name: "tdmsimport"
description: "Importe un fichier TDMS dans une base de données"
command: "tdmsimport.exe --input {INPUT_FILE} --output {OUTPUT_DATABASE} --format {FORMAT}"

arguments:
  - code: "INPUT_FILE"
    name: "Fichier TDMS d'entrée"
    description: "Sélectionnez le fichier TDMS à importer"
    type: "file"
    required: true
    validation:
      file_extensions: [".tdms"]
  
  - code: "OUTPUT_DATABASE"
    name: "Base de données de sortie"
    description: "Chemin où créer/mettre à jour la base de données"
    type: "file"
    required: true
    default: "output.db"
  
  - code: "FORMAT"
    name: "Format de sortie"
    description: "Format de la base de données"
    type: "select"
    required: true
    options: ["sqlite", "postgresql"]
    default: "sqlite"
```

**Explication** :
- La commande utilise 3 arguments : `{INPUT_FILE}`, `{OUTPUT_DATABASE}`, `{FORMAT}`
- Les placeholders `{CODE}` sont remplacés par les valeurs saisies par l'utilisateur
- La validation garantit que le fichier d'entrée est un `.tdms`

---

### Exemple 2 : Tâche simple (Export)

**Fichier** : `data/tasks/export_task.yaml`

```yaml
name: "Export complet"
description: "Exporte les données en CSV et génère un profil de calcul"

# Pas d'arguments partagés ici - chaque commande a ses propres arguments

commands:
  - !include ../commands/export/csvexport.yaml
  - !include ../commands/compute/computeprofile.yaml
```

**Explication** :
- Cette tâche contient 2 commandes
- Chaque commande est définie dans un fichier séparé (réutilisabilité)
- L'utilisateur sélectionne cette tâche et voit les 2 commandes avec leurs arguments

---

### Exemple 3 : Tâche avec arguments partagés

**Fichier** : `data/tasks/import_task.yaml`

```yaml
name: "Importer TDMS"
description: "Importe un fichier TDMS et calcule les clés"

# Arguments partagés - utilisés par plusieurs commandes
arguments:
  - code: "DATABASE_FILE"
    name: "Base de données"
    description: "Fichier de base de données SQLite à utiliser"
    type: "file"
    required: true
    validation:
      file_extensions: [".db", ".sqlite"]
    
    # Où propager cette valeur
    values:
      - command: "tdmsimport"
        argument: "OUTPUT_DATABASE"
      - command: "computekey"
        argument: "DATABASE"

commands:
  - !include ../commands/import/tdmsimport.yaml
  - !include ../commands/compute/computekey.yaml
```

**Explication** :
- L'utilisateur saisit **une seule fois** le fichier de base de données
- La valeur est automatiquement propagée à :
  - `OUTPUT_DATABASE` dans la commande `tdmsimport`
  - `DATABASE` dans la commande `computekey`
- Avantage : Pas de risque d'incohérence entre les deux commandes

**Flux utilisateur** :
1. Utilisateur sélectionne la tâche "Importer TDMS"
2. Il voit un champ "Base de données" en haut (argument partagé)
3. Il saisit `C:\data\mydata.db`
4. Cette valeur s'applique automatiquement aux 2 commandes
5. Les 2 commandes s'exécutent avec la même base de données

---

### Exemple 4 : Commande avec plusieurs types d'arguments

**Fichier** : `data/commands/export/csvexport.yaml`

```yaml
name: "csvexport"
description: "Exporte les données en fichier CSV"
command: "csvexport.exe --database={DATABASE} --output={OUTPUT_FILE} --format={FORMAT} --verbose={VERBOSE}"

arguments:
  - code: "DATABASE"
    name: "Base de données"
    description: "Fichier de base de données à exporter"
    type: "file"
    required: true
    validation:
      file_extensions: [".db", ".sqlite"]
  
  - code: "OUTPUT_FILE"
    name: "Fichier de sortie"
    description: "Chemin du fichier CSV à créer"
    type: "file"
    required: true
    default: "export.csv"
  
  - code: "FORMAT"
    name: "Format CSV"
    description: "Format de séparation"
    type: "select"
    required: true
    options: ["comma", "semicolon", "tab"]
    default: "comma"
  
  - code: "VERBOSE"
    name: "Mode verbose"
    description: "Afficher les détails d'exécution"
    type: "boolean"
    required: false
    default: false
```

**Explication** :
- Démontre les 4 types d'arguments : `file`, `select`, `boolean`
- Les valeurs par défaut facilitent l'utilisation
- La validation garantit la cohérence

---

### Exemple 5 : Réutilisation de commandes

**Scénario** : Vous avez 2 tâches qui utilisent la même commande `csvexport`

**Fichier 1** : `data/tasks/export_task.yaml`
```yaml
name: "Export simple"
description: "Exporte les données en CSV"
commands:
  - !include ../commands/export/csvexport.yaml
```

**Fichier 2** : `data/tasks/export_with_profile.yaml`
```yaml
name: "Export complet"
description: "Exporte les données et génère un profil"
commands:
  - !include ../commands/export/csvexport.yaml
  - !include ../commands/compute/computeprofile.yaml
```

**Avantage** :
- La commande `csvexport.yaml` est définie **une seule fois**
- Elle est réutilisée dans 2 tâches différentes
- Si vous modifiez `csvexport.yaml`, les 2 tâches sont mises à jour automatiquement

---

## Dépannage

### La commande n'apparaît pas

- Vérifiez que le fichier est dans `data/commands/`
- Vérifiez que le YAML est valide (pas d'erreur de syntaxe)
- Vérifiez que la tâche inclut bien la commande
- Redémarrez l'application

### L'argument partagé ne se propage pas

- Vérifiez que le nom de la commande est correct
- Vérifiez que le code de l'argument est correct
- Vérifiez que l'argument existe dans la commande
- Vérifiez la structure de `values`

### Erreur de chemin d'inclusion

- Vérifiez que le chemin est relatif au fichier courant
- Vérifiez que le fichier inclus existe
- Vérifiez la syntaxe `!include ../chemin/fichier.yaml`

### Validation échoue

- Vérifiez les extensions de fichier autorisées
- Vérifiez les valeurs min/max pour les nombres
- Vérifiez que la valeur correspond au type attendu

---

## Ressources

- [README.md](../README.md) - Vue d'ensemble du projet
- [WITH_ARGUMENTS_INTERFACE.md](WITH_ARGUMENTS_INTERFACE.md) - Détails des arguments
- [SHARED_ARGUMENTS_IMPROVEMENTS.md](SHARED_ARGUMENTS_IMPROVEMENTS.md) - Arguments partagés avancés

