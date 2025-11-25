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

CommandBuilder supporte 5 types d'arguments pour couvrir tous les cas d'usage :

| Type | Interface | Description | Usage |
|------|-----------|-------------|-------|
| `string` |  Champ texte | Texte libre | Noms, identifiants, texte simple |
| `file` |  Champ + Parcourir | Chemin vers un fichier | Fichiers d'entrée/sortie |
| `directory` | Champ + Parcourir | Chemin vers un dossier | Dossiers de travail |
| `flag` | ☑ Checkbox | Option on/off | Flags CLI (`--debug`, `--verbose`) |
| `valued_option` | ☑ +  Checkbox + Champ | Option avec valeur | Options CLI (`--log-level INFO`) |

### 1. Type `string` - Texte simple

```yaml
- code: "PROJECT_NAME"
  name: "Nom du projet"
  type: "string"
  required: 0
  default: ""
```

**Interface** : Champ de saisie texte  
**Usage** : Texte libre, noms, identifiants

### 2. Type `file` - Fichier

```yaml
- code: "INPUT_FILE"
  name: "Fichier d'entrée"
  type: "file"
  required: 1
  validation:
    file_extensions: [".txt", ".csv", ".json"]
```

**Interface** : Champ de saisie + bouton "Parcourir..."  
**Usage** : Chemins de fichiers  
**Validation** : Extensions autorisées

### 3. Type `directory` - Dossier

```yaml
- code: "OUTPUT_DIR"
  name: "Dossier de sortie"
  type: "directory"
  required: 0
```

**Interface** : Champ de saisie + bouton "Parcourir..." (sélection de dossier)  
**Usage** : Chemins de dossiers

### 4. Type `flag` - Flag simple (option booléenne)

```yaml
- code: "DEBUG_FLAG"
  name: "Mode debug"
  type: "flag"
  required: 0
  value: "--debug"  # ← Valeur insérée si coché
  default: ""
```

**Interface** : Case à cocher seule  
**Usage** : Options on/off qui n'ont pas besoin de valeur (`--debug`, `--verbose`, `--force`)  
**Comportement** :
- ✅ Coché → insère la valeur du champ `value` dans la commande
- ❌ Décoché → supprimé complètement de la commande
- Toujours `required: 0` (un flag ne peut pas être obligatoire)

**⚠️ Important** : Le champ `value` est obligatoire pour définir ce qui sera inséré dans la commande.

### 5. Type `valued_option` - Option avec valeur

```yaml
- code: "LOG_LEVEL"
  name: "Niveau de log"
  type: "valued_option"
  required: 0
  default: "INFO"  # Optionnel : valeur par défaut
```

**Interface** : Case à cocher + champ de saisie  
**Usage** : Options qui nécessitent une valeur (`--log-level INFO`, `--threads 4`)  
**Comportement** :
- ✅ Coché + rempli → insère la valeur du champ
- ❌ Décoché ou vide → supprimé complètement de la commande
- Toujours `required: 0` (une valued_option ne peut pas être obligatoire)

### Propriétés communes d'un argument

```yaml
arguments:
  - code: "ARG_CODE"              # Identifiant unique (utilisé dans {ARG_CODE})
    name: "Nom affiché"           # Nom visible dans l'interface
    type: "string"                # Type : "string", "file", "directory", "flag", "valued_option"
    required: 1                   # 1 = obligatoire, 0 = optionnel
    default: "valeur_defaut"      # Valeur par défaut (optionnel)
    value: "--flag"               # Pour type "flag" : valeur à insérer si coché
    description: "Description"    # Description affichée (optionnel)
    validation:                   # Validation (optionnel)
      file_extensions: [".csv"]   # Pour type "file"
      min_length: 1
      max_length: 100
      pattern: "^[a-zA-Z0-9_]+$"  # Regex
      message: "Erreur personnalisée"
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

### Exemple complet avec tous les types

```yaml
name: "process_data"
description: "Traite des données avec options avancées"
command: "process {INPUT} {OUTPUT} {DEBUG} {VERBOSE} --log-level {LOG_LEVEL} --threads {THREADS}"
arguments:
  # Fichier obligatoire
  - code: "INPUT"
    name: "Fichier d'entrée"
    description: "Fichier de données à traiter"
    type: "file"
    required: 1
    validation:
      file_extensions: [".csv", ".json", ".txt"]
  
  # Fichier optionnel
  - code: "OUTPUT"
    name: "Fichier de sortie"
    description: "Fichier de résultat (optionnel)"
    type: "file"
    required: 0
    default: ""
  
  # Flag simple
  - code: "DEBUG"
    name: "Mode debug"
    description: "Activer le mode debug"
    type: "flag"
    required: 0
    value: "--debug"
    default: ""
  
  # Flag simple
  - code: "VERBOSE"
    name: "Mode verbeux"
    description: "Afficher plus d'informations"
    type: "flag"
    required: 0
    value: "-v"
    default: ""
  
  # Option avec valeur
  - code: "LOG_LEVEL"
    name: "Niveau de log"
    description: "Niveau de log (INFO, DEBUG, ERROR)"
    type: "valued_option"
    required: 0
    default: "INFO"
  
  # Option avec valeur
  - code: "THREADS"
    name: "Nombre de threads"
    description: "Nombre de threads pour le traitement"
    type: "valued_option"
    required: 0
    default: "4"
```

**Résultat avec DEBUG coché, VERBOSE décoché, LOG_LEVEL="INFO", THREADS="4"** :
```bash
process input.csv output.csv --debug --log-level INFO --threads 4
```

**Résultat avec tous les flags décochés et options vides** :
```bash
process input.csv
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

## Gestion des erreurs YAML

CommandBuilder inclut un système robuste de gestion des erreurs YAML. Lorsqu'une tâche YAML contient une erreur, elle n'est pas chargée, mais l'erreur est affichée à l'utilisateur.

### Types d'erreurs détectées

| Erreur | Cause | Solution |
|--------|-------|----------|
| **SyntaxError** | YAML invalide (indentation, syntaxe) | Vérifiez l'indentation et la syntaxe YAML |
| **ValidationError** | Champ manquant ou invalide | Vérifiez que tous les champs requis sont présents |
| **FileNotFoundError** | Fichier inclus introuvable | Vérifiez le chemin de l'inclusion `!include` |
| **TypeError** | Type de données incorrect | Vérifiez que les types correspondent (string, list, etc.) |

### Affichage des erreurs

Quand l'application démarre, une dialog s'affiche si des erreurs sont détectées :

```bash
┌─────────────────────────────────────────┐
│ ⚠️ Erreurs YAML détectées (2)           │
├─────────────────────────────────────────┤
│ ❌ SyntaxError - error_example.yaml     │
│    Erreur de syntaxe YAML: ...          │
│    💡 Vérifiez l'indentation...         │
│                                         │
│ ❌ ValidationError - invalid_task.yaml  │
│    Erreur de validation: ...            │
│    💡 Vérifiez que tous les champs...   │
└─────────────────────────────────────────┘
```

### Exemple : Fichier avec erreurs

**Fichier** : `data/tasks/error_example.yaml`

```yaml
# ❌ ERREUR 1 : Argument partagé avec commande inexistante
name: "❌ Exemple d'erreur"
description: "Cette tâche contient des erreurs intentionnelles"

arguments:
  - code: "DATABASE"
    name: "Base de données"
    type: "file"
    required: true
    values:
      - command: "commande_inexistante"  # ❌ Cette commande n'existe pas
        argument: "DB_FILE"

# ❌ ERREUR 2 : Argument avec champ manquant
commands:
  - name: "commande_incomplete"
    description: "Commande avec argument manquant"
    command: "echo {MESSAGE}"
    arguments:
      - code: "MESSAGE"
        name: "Message"
        # ❌ Le champ 'type' est manquant (requis)
        required: true
```

**Résultat** : Cette tâche ne sera pas chargée, et les erreurs s'afficheront dans la dialog au démarrage.

### Bonnes pratiques pour éviter les erreurs

1. **Validez votre YAML** avant de le charger
   - Utilisez un validateur YAML en ligne
   - Vérifiez l'indentation (2 espaces)

2. **Vérifiez les chemins d'inclusion**
   ```yaml
   commands:
     - !include ../commands/ma_commande.yaml  # ✅ Chemin relatif correct
   ```

3. **Assurez-vous que tous les champs requis sont présents**
   - `name` : Obligatoire
   - `description` : Obligatoire
   - `command` : Obligatoire pour les commandes
   - `type` : Obligatoire pour les arguments

4. **Testez les inclusions**
   - Vérifiez que le fichier inclus existe
   - Vérifiez que le chemin est relatif au fichier courant

---

## Dépannage

### La commande n'apparaît pas

- Vérifiez que le fichier est dans `data/commands/`
- Vérifiez que le YAML est valide (pas d'erreur de syntaxe)
- Vérifiez que la tâche inclut bien la commande
- Redémarrez l'application
- Vérifiez la dialog d'erreurs au démarrage

### L'argument partagé ne se propage pas

- Vérifiez que le nom de la commande est correct
- Vérifiez que le code de l'argument est correct
- Vérifiez que l'argument existe dans la commande
- Vérifiez la structure de `values`

### Erreur de chemin d'inclusion

- Vérifiez que le chemin est relatif au fichier courant
- Vérifiez que le fichier inclus existe
- Vérifiez la syntaxe `!include ../chemin/fichier.yaml`
- Vérifiez la dialog d'erreurs pour le message exact

### Validation échoue

-  Vérifiez les extensions de fichier autorisées
-  Vérifiez les valeurs min/max pour les nombres
-  Vérifiez que la valeur correspond au type attendu
- Consultez la dialog d'erreurs pour les détails

---

## Ressources

- [README.md](../README.md) - Vue d'ensemble du projet
- [WITH_ARGUMENTS_INTERFACE.md](WITH_ARGUMENTS_INTERFACE.md) - Détails des arguments
- [SHARED_ARGUMENTS_IMPROVEMENTS.md](SHARED_ARGUMENTS_IMPROVEMENTS.md) - Arguments partagés avancés

