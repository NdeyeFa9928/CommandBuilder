# 📘 Guide YAML - L'essentiel

> **Principe** : CommandBuilder utilise deux types de fichiers YAML :
> 1. **Fichiers de commandes** (réutilisables) : définissent une commande CLI
> 2. **Fichiers de tâches** (workflows) : groupent plusieurs commandes à exécuter en séquence

---

## 📁 Structure des fichiers

| Type | Emplacement |
|------|-------------|
| **Commandes** | `command_builder/data/commands/ma_commande.yaml` |
| **Tâches** | `command_builder/data/tasks/ma_tache.yaml` |

⚠️ **Recommandation** : Un fichier = Une commande ou une tâche

---

## 🎯 Structure minimale (copier-coller)

```yaml
name: "Ma tâche"
description: "Ce que fait cette tâche"
commands:
  - name: "Commande 1"
    description: "Description"
    command: "executable.exe {ARG1} {ARG2}"
    arguments:
      - code: "ARG1"
        name: "Nom affiché"
        type: "file"
        required: 1
```

---

## ⚡ Points clés

| Concept | Description |
|---------|-------------|
| **Placeholders** | `{CODE}` dans la commande → remplacé par la valeur saisie |
| **Types d'arguments** | `string` \| `file` \| `directory` \| `flag` \| `valued_option` |
| **Required** | `required: 1` = obligatoire (astérisque rouge) / `required: 0` = optionnel |
| **Arguments partagés** | Saisir UNE FOIS une valeur utilisée par PLUSIEURS commandes |

---

## 🖥️ Comprendre l'interface

| Élément | Signification |
|---------|---------------|
| 🔴 **Astérisque rouge (*)** | Champ obligatoire (`required: 1`). Affiché APRÈS le nom : "Base de données : *" |
| 🟢 **Texte vert** | Valeur pré-remplie (par défaut). Modifiable par l'utilisateur |
| 🔵 **Couleur du label** | Noir = champ vide / Bleu = champ rempli |
| 📋 **Étapes d'exécution** | Les commandes s'exécutent dans l'ordre. Si erreur → arrêt immédiat |
| ✅ **Case à cocher** | Type `flag` ou `valued_option`. Coché = inclus dans la commande |
| 📂 **Listes** | Gauche = tâches disponibles. Cliquez pour voir ses commandes |

---

## 📖 Onglets de cette aide

- **Structure** → Templates complets (fichiers, !include)
- **Arguments** → Les 5 types expliqués
- **Arguments Partagés** → Éviter la répétition
- **Exemples** → Cas réels avec !include

---

## ⚡ Points clés supplémentaires

- **Valeurs par défaut des tâches** → Prioritaires sur celles des commandes
- **!include** → Réutilisez les commandes dans plusieurs tâches
- **Modification post-build** → Les fichiers YAML sont modifiables sans recompilation
