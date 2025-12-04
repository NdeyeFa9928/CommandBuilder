# 📐 Référence complète YAML

## 🎯 Structure d'un fichier de commande

```yaml
name: "nom_de_la_commande"           # 🔴 OBLIGATOIRE - Nom affiché
description: "Description courte"    # 🔴 OBLIGATOIRE - Texte explicatif
command: "executable {ARG1} {ARG2}"  # 🔴 OBLIGATOIRE - Commande CLI avec placeholders
arguments:                           # 🔴 OBLIGATOIRE - Liste (peut être vide [])
  - code: "ARG1"                     # 🔴 OBLIGATOIRE - Identifiant unique
    name: "Nom affiché"              # 🔴 OBLIGATOIRE - Label dans l'interface
    description: "Texte d'aide"      # 🟡 OPTIONNEL - Tooltip
    type: "string"                   # 🔴 OBLIGATOIRE - string|file|directory|flag|valued_option
    required: 1                      # 🔴 OBLIGATOIRE - 0 ou 1
    default: "valeur_par_defaut"     # 🟡 OPTIONNEL - Valeur pré-remplie
    value: "--flag"                  # 🟠 OBLIGATOIRE pour type "flag"
    validation:                      # 🟡 OPTIONNEL - Pour type "file"
      file_extensions: [".csv", ".txt"]  # Liste des extensions acceptées
```

---

## 🎯 Structure d'un fichier de tâche

```yaml
name: "nom_de_la_tache"            # 🔴 OBLIGATOIRE - Nom affiché
description: "Description"          # 🔴 OBLIGATOIRE - Texte explicatif

arguments:                          # 🟡 OPTIONNEL - Arguments partagés entre commandes
  - code: "SHARED_ARG"              # Même structure qu'un argument normal
    name: "Argument partagé"
    type: "string"
    required: 1
    values:                          # 🔴 OBLIGATOIRE si arguments partagés
    - command: "nom_commande1"      # Nom de la commande cible
      argument: "ARG_DANS_CMD1"     # Code de l'argument dans cette commande
    - command: "nom_commande2"
      argument: "ARG_DANS_CMD2"

commands:                           # 🔴 OBLIGATOIRE - Liste des commandes
  - !include ../commands/cmd1.yaml  # Méthode 1 : Inclusion (RECOMMANDÉ)
  - !include ../commands/cmd2.yaml
  
  - name: "Commande inline"         # Méthode 2 : Définition directe
    description: "Description"
    command: "echo test"
    arguments: []
```

---

## 📝 Règles importantes

- **Indentation** : 2 espaces (pas de tabulations)
- **Placeholders** : `{CODE}` en MAJUSCULES dans la commande
- **Chemins relatifs** : `../commands/` depuis `tasks/`
- **Extensions** : `.yaml` ou `.yml` (les deux fonctionnent)
- **Commentaires** : `# Texte` (ignoré par le parser)
- **Guillemets** : Obligatoires pour les chaînes avec espaces ou caractères spéciaux

---

# 📐 Templates prêts à copier

> 💡 **Bonne pratique** : Créez **un fichier par commande** dans `data/commands/`, puis **réutilisez-les** dans les tâches avec `!include`

---

## Template 1 : Fichier de commande (réutilisable)

**Fichier** : `data/commands/ma_commande.yaml`

```yaml
name: "Ma commande"
description: "Description de la commande"
command: "executable.exe {ARG1} {ARG2}"
arguments:
  - code: "ARG1"
    name: "Argument 1"
    type: "file"
    required: 1
```

✅ Cette commande peut être incluse dans plusieurs tâches

---

## Template 2 : Tâche simple (minimum requis)

```yaml
name: "Ma tâche"
description: "Description de la tâche"
commands:
  - name: "Ma commande"
    description: "Description de la commande"
    command: "echo Hello World"
    arguments: []
```

✅ Tous les champs en rouge sont obligatoires

---

## Template 3 : Tâche avec inclusion de commandes

**Fichier** : `data/tasks/ma_tache.yaml`

```yaml
name: "Ma tâche"
description: "Exécute plusieurs commandes"
commands:
  - !include ../commands/ma_commande.yaml
  - !include ../commands/autre_commande.yaml
```

- ✅ `!include` charge le fichier de commande
- ✅ Les chemins sont relatifs au fichier YAML
- ✅ `../commands/` remonte d'un niveau (de tasks vers data)

---

## Template 4 : Commande avec arguments

```yaml
name: "Traitement de fichier"
description: "Traite un fichier CSV"
commands:
  - name: "Process"
    description: "Traite le fichier"
    command: "process.exe {INPUT_FILE} {OUTPUT_FILE}"
    arguments:
      - code: "INPUT_FILE"
        name: "Fichier d'entrée"
        type: "file"
        required: 1
      
      - code: "OUTPUT_FILE"
        name: "Fichier de sortie"
        type: "file"
        required: 0
        default: "output.csv"
```

💡 `{INPUT_FILE}` et `{OUTPUT_FILE}` sont remplacés par les valeurs saisies

---

## Template 5 : Avec flags et options

```yaml
name: "Traitement avancé"
description: "Avec options CLI"
commands:
  - name: "Process"
    description: "Traite avec options"
    command: "process {INPUT} {DEBUG} --log-level {LOG_LEVEL}"
    arguments:
      # Fichier obligatoire
      - code: "INPUT"
        name: "Fichier"
        type: "file"
        required: 1
      
      # Flag (checkbox seule)
      - code: "DEBUG"
        name: "Mode debug"
        type: "flag"
        required: 0
        value: "--debug"
      
      # Option avec valeur (checkbox + champ)
      - code: "LOG_LEVEL"
        name: "Niveau de log"
        type: "valued_option"
        required: 0
        default: "INFO"
```

⚠️ Pour les `flag` : le champ `value` est obligatoire

---

## Template 6 : Avec arguments partagés

```yaml
name: "Pipeline"
description: "Plusieurs commandes avec argument commun"
shared_arguments:
  - code: "DATABASE"
    name: "Base de données"
    type: "file"
    required: 1

commands:
  - name: "Import"
    description: "Importe les données"
    command: "import.exe --db {DATABASE}"
    arguments: []
  
  - name: "Export"
    description: "Exporte les données"
    command: "export.exe --db {DATABASE}"
    arguments: []
```

💡 L'argument DATABASE est saisi une seule fois et utilisé par toutes les commandes

---

## Template 7 : Construction de chemins

> 💡 **Astuce avancée** : Vous pouvez combiner plusieurs placeholders pour construire des chemins

```yaml
name: "campaignexport"
description: "Export avec construction de chemin"
command: "campaignexport {DATABASE_FILE}\\{PROJECT_NAME}.sqlite {OUTPUT_DIR}"
arguments:
  - code: "DATABASE_FILE"
    name: "Répertoire de base"
    type: "directory"
    required: 1
  
  - code: "PROJECT_NAME"
    name: "Nom du projet"
    type: "string"
    required: 1
  
  - code: "OUTPUT_DIR"
    name: "Dossier de sortie"
    type: "directory"
    required: 1
```

**Résultat** :
Si `DATABASE_FILE = L:\PROJET\BASE` et `PROJECT_NAME = I2_S38`
→ Commande générée : `campaignexport L:\PROJET\BASE\I2_S38.sqlite L:\OUTPUT`

- ✅ Utilisez `\\` pour Windows ou `/` pour Linux
- ✅ Vous pouvez combiner autant de placeholders que nécessaire
