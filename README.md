# CommandBuilder

Application graphique pour composer et exécuter des commandes CLI complexes via une interface intuitive.

**Fonctionnalités clés :**
- Interface utilisateur moderne avec thème sombre
- Définition des commandes via des fichiers YAML
- Validation des entrées utilisateur
- Génération de commandes prêtes à l'exécution
- Support des arguments de différents types (fichier, dossier, nombre, etc.)

## Structure

```
command_builder/
├── assets/           # Ressources (icônes, images)
├── components/       # Composants UI modulaires
│   ├── task_component/     # Affichage d'une tâche
│   ├── argument_component/ # Gestion des arguments avec validation
│   ├── command_component/  # Affichage d'une commande et ses arguments
│   ├── task_list/          # Liste des tâches disponibles
│   ├── command_form/       # Formulaire de commandes
│   └── console_output/     # Affichage des sorties console
├── data/             # Définitions YAML
│   ├── commands/     # Commandes individuelles
│   └── tasks/        # Tâches (groupes de commandes)
├── models/           # Modèles de données
└── services/         # Logique métier
```

## Installation

```bash
# 1. Installer les dépendances
pipenv install

# 2. Lancer l'application
task dev
```

## Utilisation

1. **Définir des commandes** dans `data/commands/` :

```yaml
# exemple.yaml
name: "Ma commande"
command: "commande --input {fichier} --option {valeur}"
arguments:
  - code: "fichier"
    name: "Fichier source"
    type: "file"
    required: true
  
  - code: "valeur"
    name: "Option"
    type: "number"
    default: "42"
```

2. **Créer des tâches** dans `data/tasks/` :

```yaml
# ma_tache.yaml
name: "Ma tâche"
commands:
  - !include ../commands/exemple.yaml
```

3. **Types d'arguments** :
   - `text` : Champ texte
   - `file` : Sélecteur de fichier
   - `directory` : Sélecteur de dossier
   - `number` : Nombre
   - `boolean` : Case à cocher
   - `select` : Liste déroulante

## Bonnes pratiques

1. **Organisation des commandes :**
   - Une commande = un fichier YAML
   - Nommer les fichiers de manière descriptive
   - Grouper les commandes liées dans des sous-dossiers

2. **Gestion des arguments :**
   - Toujours définir un `name` et une `description` claire
   - Utiliser `required: true` pour les arguments obligatoires
   - Définir des valeurs par défaut quand c'est pertinent

3. **Conseils de performance :**
   - Éviter les commandes trop complexes
   - Privilégier plusieurs commandes simples plutôt qu'une seule complexe
   - Tester régulièrement les commandes générées

## Développement

### Commandes utiles

```bash
# Lancer les tests
pytest

# Vérifier le style
ruff check .
black .

# Créer l'exécutable
task build

# Nettoyer les fichiers temporaires
task clean
```

### Structure recommandée pour les commandes

```yaml
# command_builder/data/commands/analyse/tdms_import.yaml
name: "Importer TDMS"
description: "Importe un fichier TDMS pour analyse"
command: "tdms_import --input {input_file} --output {output_dir}"
arguments:
  - code: "input_file"
    name: "Fichier source"
    description: "Sélectionnez le fichier .tdms à importer"
    type: "file"
    required: true
    filters: "*.tdms"  # Filtre d'extension de fichier
    
  - code: "output_dir"
    name: "Dossier de sortie"
    description: "Dossier où enregistrer les résultats"
    type: "directory"
    default: "./output"
```

### Débogage

- Activer les logs détaillés :
  ```bash
  set LOG_LEVEL=DEBUG
  task dev
  ```
- Vérifier le fichier `logs/command_builder.log` en cas d'erreur
