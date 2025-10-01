# CommandBuilder

Assistant GUI pour composer des commandes CLI Windows sans erreurs de syntaxe.

## Description

CommandBuilder est un outil qui permet de créer et exécuter des commandes complexes via une interface graphique intuitive. L'application est basée sur des définitions YAML de pipelines qui peuvent être facilement étendues.

## Installation

```bash
# Installer les dépendances
pipenv install

# Lancer l'application en mode développement
task dev

# Construire l'exécutable
task build
```

## Structure des pipelines

Les pipelines sont définis dans des fichiers YAML dans le dossier `command_builder/data/pipelines/`. Chaque pipeline peut être:

1. **Une commande simple** - Une seule tâche avec une seule commande
2. **Un workflow complexe** - Plusieurs tâches avec dépendances entre elles

### Structure d'un fichier de pipeline

```yaml
name: "Nom descriptif du pipeline"
description: "Description détaillée"
tasks:
  # Inclusion d'une tâche depuis un fichier séparé
  - !include ../tasks/ma_tache.yaml
  
  # Définition directe d'une tâche
  - name: "Nom de la tâche"
    description: "Description de la tâche"
    commands:
      - name: "nom_commande"
        description: "Description de la commande"
        command: "commande {PARAM1} {PARAM2} --option {OPTION1}"
        arguments:
          - code: "PARAM1"
            name: "Nom lisible"
            description: "Description du paramètre"
```

> **Note**: Pour une documentation complète du système YAML, voir [YAML_SYSTEM.md](docs/YAML_SYSTEM.md)

## Comment ajouter une nouvelle commande

Pour ajouter une nouvelle commande à CommandBuilder, suivez ces étapes :

### Option 1: Créer une commande individuelle

1. **Créer un nouveau fichier YAML** dans le dossier `command_builder/data/commands/`
   - Nommez le fichier de manière descriptive, par exemple `ma_commande.yaml`

2. **Définir la structure de la commande** :
   ```yaml
   name: "nom_commande"
   description: "Description détaillée de la commande"
   command: "commande {PARAM1} {PARAM2}"
   arguments:
     - code: "PARAM1"
       name: "Nom lisible"
       description: "Description du paramètre"
   ```

### Option 2: Créer une tâche avec commandes

1. **Créer un nouveau fichier YAML** dans le dossier `command_builder/data/tasks/`
   - Nommez le fichier de manière descriptive, par exemple `ma_tache.yaml`

2. **Définir la structure de la tâche** :
   ```yaml
   name: "Nom de la tâche"
   description: "Description de la tâche"
   commands:
     # Inclure une commande existante
     - !include ../commands/ma_commande.yaml
     
     # Définir une commande directement
     - name: "autre_commande"
       description: "Description de la commande"
       command: "commande {PARAM1}"
       arguments:
         - code: "PARAM1"
           name: "Nom lisible"
           description: "Description du paramètre"
   ```

### Option 3: Créer un pipeline complet

1. **Créer un nouveau fichier YAML** dans le dossier `command_builder/data/pipelines/`
   - Nommez le fichier de manière descriptive, par exemple `mon_pipeline.yaml`

2. **Définir la structure du pipeline** :
   ```yaml
   name: "Nom du pipeline"
   description: "Description du pipeline"
   tasks:
     # Inclure une tâche existante
     - !include ../tasks/ma_tache.yaml
     
     # Définir une tâche directement
     - name: "Autre tâche"
       description: "Description de la tâche"
       commands: [...]
   ```

## Comment créer un workflow complexe

Pour créer un workflow qui combine plusieurs commandes :

1. **Créer un nouveau fichier YAML** dans le dossier `command_builder/data/pipelines/`
   - Utilisez un préfixe comme `workflow_` pour indiquer qu'il s'agit d'un workflow

2. **Définir plusieurs tâches** avec des inclusions :
   ```yaml
   name: "Workflow complet"
   description: "Description du workflow"
   tasks:
     # Inclure des tâches existantes
     - !include ../tasks/premiere_tache.yaml
     - !include ../tasks/deuxieme_tache.yaml
     
     # Ajouter une tâche spécifique au workflow
     - name: "Tâche finale"
       description: "Tâche de finalisation"
       commands: [...]
   ```

3. **Structurer les fichiers de manière modulaire** pour faciliter la réutilisation

## Exemples

Voir les exemples dans les dossiers :

- `command_builder/data/commands/` - Exemples de commandes individuelles
- `command_builder/data/tasks/` - Exemples de tâches
- `command_builder/data/pipelines/` - Exemples de pipelines et workflows

## Documentation complète

Pour une documentation détaillée du système YAML avec inclusions, voir [YAML_SYSTEM.md](docs/YAML_SYSTEM.md).

## Tests

Le système YAML est couvert par des tests unitaires et d'intégration. Pour exécuter les tests :

```bash
# Exécuter tous les tests
task test

# Exécuter uniquement les tests des services YAML
task test:services
```
