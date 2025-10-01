# Système YAML de CommandBuilder

Ce document explique le fonctionnement du système YAML de CommandBuilder, qui permet de définir des pipelines, des tâches et des commandes de manière modulaire et extensible.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Structure des fichiers](#structure-des-fichiers)
3. [Ajouter un nouveau pipeline](#ajouter-un-nouveau-pipeline)
4. [Ajouter une nouvelle tâche](#ajouter-une-nouvelle-tâche)
5. [Ajouter une nouvelle commande](#ajouter-une-nouvelle-commande)
6. [Système d'inclusion](#système-dinclusion)
7. [Tests](#tests)

## Vue d'ensemble

Le système YAML de CommandBuilder permet de définir :

- **Pipelines** : Ensembles de tâches à exécuter
- **Tâches** : Regroupements logiques de commandes
- **Commandes** : Instructions CLI individuelles avec leurs arguments

Avantages du système YAML :
- **Modularité** : Les composants peuvent être réutilisés
- **Lisibilité** : Format plus lisible que JSON
- **Inclusion** : Support des références entre fichiers avec `!include`
- **Extensibilité** : Facile d'ajouter de nouvelles commandes ou tâches

## Structure des fichiers

```
command_builder/
├── data/
│   ├── commands/     # Définitions de commandes individuelles
│   │   └── *.yaml
│   ├── tasks/        # Définitions de tâches (regroupements de commandes)
│   │   └── *.yaml
│   └── pipelines/    # Définitions de pipelines (regroupements de tâches)
│       └── *.yaml
```

## Ajouter un nouveau pipeline

Un pipeline est un ensemble de tâches à exécuter. Pour créer un nouveau pipeline :

1. Créez un fichier YAML dans le dossier `data/pipelines/` (ex: `mon_pipeline.yaml`)
2. Définissez les propriétés du pipeline :

```yaml
name: "Nom du pipeline"
description: "Description détaillée du pipeline"
tasks:
  # Option 1: Inclure une tâche définie dans un fichier séparé
  - !include ../tasks/ma_tache.yaml
  
  # Option 2: Définir une tâche directement
  - name: "Tâche directe"
    description: "Description de la tâche"
    commands:
      - name: "commande_directe"
        description: "Description de la commande"
        command: "echo 'Hello World'"
        arguments: []
```

## Ajouter une nouvelle tâche

Une tâche est un regroupement logique de commandes. Pour créer une nouvelle tâche :

1. Créez un fichier YAML dans le dossier `data/tasks/` (ex: `ma_tache.yaml`)
2. Définissez les propriétés de la tâche :

```yaml
name: "Nom de la tâche"
description: "Description détaillée de la tâche"
commands:
  # Option 1: Inclure une commande définie dans un fichier séparé
  - !include ../commands/ma_commande.yaml
  
  # Option 2: Définir une commande directement
  - name: "commande_directe"
    description: "Description de la commande"
    command: "echo {PARAM1}"
    arguments:
      - code: "PARAM1"
        name: "Premier paramètre"
        description: "Description du paramètre"
```

## Ajouter une nouvelle commande

Une commande est une instruction CLI individuelle. Pour créer une nouvelle commande :

1. Créez un fichier YAML dans le dossier `data/commands/` (ex: `ma_commande.yaml`)
2. Définissez les propriétés de la commande :

```yaml
name: "nom_commande"
description: "Description détaillée de la commande"
command: "executable {ARG1} {ARG2} --option={OPT}"
arguments:
  - code: "ARG1"
    name: "Premier argument"
    description: "Description du premier argument"
  
  - code: "ARG2"
    name: "Deuxième argument"
    description: "Description du deuxième argument"
  
  - code: "OPT"
    name: "Option"
    description: "Description de l'option"
```

## Système d'inclusion

Le système YAML supporte l'inclusion de fichiers avec la directive `!include`. Cela permet de :

- **Réutiliser** des définitions de commandes et de tâches
- **Modulariser** la configuration
- **Maintenir** plus facilement les définitions

Exemples d'inclusion :

```yaml
# Inclusion d'une commande dans une tâche
commands:
  - !include ../commands/ma_commande.yaml

# Inclusion d'une tâche dans un pipeline
tasks:
  - !include ../tasks/ma_tache.yaml
```

Les chemins sont relatifs au fichier qui contient l'inclusion.

