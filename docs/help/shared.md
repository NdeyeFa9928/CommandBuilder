# 🔗 Arguments partagés entre commandes

> 💡 **Pourquoi utiliser des arguments partagés ?**
> 
> Quand plusieurs commandes utilisent **la même valeur** (ex: répertoire de base, fichier de sortie) :
> - **Définir une seule fois** au niveau de la tâche
> - L'utilisateur saisit **une seule fois** ✅
> - La valeur est **automatiquement injectée** dans les commandes concernées
> - Les valeurs par défaut de la tâche **remplacent** celles des commandes

---

## 📝 Syntaxe : Section `arguments` avec `values`

⚠️ **IMPORTANT** : La section s'appelle `arguments` (pas `shared_arguments`). Chaque argument contient une liste `values` qui indique où l'injecter.

---

## 🎯 Exemple réel : Traitement de campagne

*Cas d'usage : Import TDMS vers une base, puis export de cette base vers TXT/Images*

```yaml
name: "Traitement campagne"
description: "Import TDMS du dossier + export campagne (TXT + IMAGES)"

arguments:  # ← Arguments partagés de la tâche
  - code: "base"  # ← Code de l'argument partagé
    name: "Répertoire de base"
    description: "Répertoire contenant la base de données"
    type: "directory"
    required: 1
    default: "L:\\PROJET\\BASE"
    values:  # ← Liste des injections
      - command: "tdmsdirimport_tc"  # ← Nom de la commande
        argument: "OUTPUT_DIR"       # ← Code de l'argument cible
      - command: "campaignexport"
        argument: "DATABASE_FILE"    # ← Injecté ici aussi

commands:
  - !include ../commands/tdmsdirimport_commands.yaml
  - !include ../commands/campaignexport_commands.yaml
```

### 🔍 Comment ça fonctionne :

1. L'utilisateur saisit **une seule fois** le répertoire de base : `L:\PROJET\BASE`
2. Cette valeur est injectée dans `OUTPUT_DIR` de `tdmsdirimport_tc`
3. Cette même valeur est injectée dans `DATABASE_FILE` de `campaignexport`
4. Résultat : **cohérence garantie** entre les deux commandes ✅

---

## 🔄 Cas avec plusieurs arguments partagés

```yaml
arguments:
  - code: "projet"  # ← Argument partagé 1
    name: "Nom du projet"
    type: "string"
    required: 1
    default: "E3D_S29"
    values:
      - command: "tdmsdirimport_tc"
        argument: "PNAME"
      - command: "campaignexport"
        argument: "PROJECT_NAME"
  
  - code: "base_dir"  # ← Argument partagé 2
    name: "Répertoire de base"
    type: "directory"
    required: 1
    values:
      - command: "tdmsdirimport_tc"
        argument: "OUTPUT_DIR"
      - command: "campaignexport"
        argument: "DATABASE_FILE"
```

---

## 🔀 Combinaison : Arguments partagés + Arguments locaux

Les commandes peuvent avoir leurs propres arguments EN PLUS des arguments partagés :

```yaml
arguments:  # ← Partagés (niveau tâche)
  - code: "base"
    name: "Base de données"
    type: "directory"
    required: 1
    values:
      - command: "export_cmd"
        argument: "DATABASE"

commands:
  - name: "export_cmd"
    command: "export.exe {DATABASE} {FORMAT}"
    arguments:  # ← Locaux (spécifiques à cette commande)
      - code: "FORMAT"
        name: "Format de sortie"
        type: "string"
        required: 0
        default: "CSV"
```

- ✅ `DATABASE` = partagé (saisi une fois, utilisé partout)
- ✅ `FORMAT` = local (spécifique à la commande export_cmd)

---

## ⚠️ Règles importantes

- Section `arguments` (pas `shared_arguments`)
- Chaque argument doit avoir une liste `values`
- Dans `values` : `command` = nom de la commande, `argument` = code de l'argument cible
- Les valeurs `default` de la tâche **remplacent** celles des commandes
- Un argument partagé peut être injecté dans **plusieurs commandes**
