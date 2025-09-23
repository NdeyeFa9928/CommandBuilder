# CommandBuilder

Assistant GUI pour composer des commandes CLI Windows sans erreurs de syntaxe.

## Description

CommandBuilder est un outil qui permet de créer et exécuter des commandes complexes via une interface graphique intuitive. L'application est basée sur des définitions JSON de pipelines qui peuvent être facilement étendues.

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

Les pipelines sont définis dans des fichiers JSON dans le dossier `command_builder/data/pipelines/`. Chaque pipeline peut être:

1. **Une commande simple** - Une seule tâche avec une seule commande
2. **Un workflow complexe** - Plusieurs tâches avec dépendances entre elles

### Structure d'un fichier de pipeline

```json
{
  "name": "Nom descriptif du pipeline",
  "description": "Description détaillée",
  "tasks": [
    {
      "name": "Nom de la tâche",
      "description": "Description de la tâche",
      "dependencies": ["Tâche précédente"],  // Optionnel
      "commands": [
        {
          "name": "nom_commande",
          "description": "Description de la commande",
          "command": "commande {PARAM1} {PARAM2} --option {OPTION1}",
          "arguments": [
            {
              "code": "PARAM1",
              "name": "Nom lisible",
              "description": "Description du paramètre",
              "type": "file",  // file, directory, string, integer, float, boolean
              "required": 1,    // 1 = requis, 0 = optionnel
              "validation": {   // Optionnel
                "file_extensions": [".ext"]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## Comment ajouter une nouvelle commande

Pour ajouter une nouvelle commande à CommandBuilder, suivez ces étapes :

1. **Créer un nouveau fichier JSON** dans le dossier `command_builder/data/pipelines/`
   - Nommez le fichier de manière descriptive, par exemple `cmd_macommande.json` ou `analyser_fichier.json`

2. **Définir la structure de base** :
   ```json
   {
     "name": "Nom descriptif",
     "description": "Description détaillée",
     "tasks": [
       {
         "name": "Nom de la tâche",
         "description": "Description de la tâche",
         "commands": [
           {
             "name": "nom_commande",
             "description": "Description de la commande",
             "command": "commande {PARAM1} {PARAM2}",
             "arguments": []
           }
         ]
       }
     ]
   }
   ```

3. **Définir les arguments** pour chaque paramètre de la commande :
   ```json
   "arguments": [
     {
       "code": "PARAM1",
       "name": "Nom lisible",
       "description": "Description du paramètre",
       "type": "file",
       "required": 1,
       "validation": {
         "file_extensions": [".ext"]
       }
     }
   ]
   ```

4. **Utiliser les types appropriés** pour les arguments :
   - `file` : Fichier à sélectionner
   - `directory` : Répertoire à sélectionner
   - `string` : Texte libre
   - `integer` : Nombre entier
   - `float` : Nombre décimal
   - `boolean` : Valeur booléenne (case à cocher)

5. **Indiquer si l'argument est requis** :
   - `"required": 1` pour les arguments obligatoires
   - `"required": 0` pour les arguments optionnels

## Comment créer un workflow complexe

Pour créer un workflow qui combine plusieurs commandes :

1. **Créer un nouveau fichier JSON** dans le dossier `command_builder/data/pipelines/`
   - Utilisez un préfixe comme `workflow_` pour indiquer qu'il s'agit d'un workflow

2. **Définir plusieurs tâches** avec des dépendances entre elles :
   ```json
   {
     "name": "Workflow complet",
     "description": "Description du workflow",
     "tasks": [
       {
         "name": "Première tâche",
         "description": "Description",
         "commands": [...]
       },
       {
         "name": "Deuxième tâche",
         "description": "Description",
         "dependencies": ["Première tâche"],
         "commands": [...]
       }
     ]
   }
   ```

3. **S'assurer que les dépendances sont correctes** pour garantir l'ordre d'exécution

## Exemples

Voir les exemples dans le dossier `command_builder/data/pipelines/` :

- `analyser_tdms.json` - Exemple de commande simple
- `workflow_import_export.json` - Exemple de workflow complexe
