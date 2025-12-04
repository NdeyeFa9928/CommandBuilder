# 🔧 Les 5 types d'arguments

> 💡 **Principe** : Le `code` est utilisé dans la commande avec `{CODE}` et sera remplacé par la valeur saisie

---

## 1️⃣ Type "string" - Texte libre

```yaml
- code: "TABLE_NAME"
  name: "Nom de la table"
  type: "string"
  required: 0
  default: "MyTable"
```

**Interface** : Champ de texte simple

---

## 2️⃣ Type "file" - Sélection de fichier

```yaml
- code: "INPUT_FILE"
  name: "Fichier d'entrée"
  type: "file"
  required: 1
  validation:
    file_extensions: [".csv", ".txt"]
```

**Interface** : Champ + bouton "Parcourir"

---

## 3️⃣ Type "directory" - Sélection de dossier

```yaml
- code: "OUTPUT_DIR"
  name: "Dossier de sortie"
  type: "directory"
  required: 0
```

**Interface** : Champ + bouton "Parcourir" (dossiers)

---

## 4️⃣ Type "flag" - Case à cocher (--debug, -v)

```yaml
- code: "DEBUG"
  name: "Mode debug"
  type: "flag"
  required: 0
  value: "--debug"  # ⚠️ OBLIGATOIRE pour flag
```

- **Interface** : Case à cocher seule
- **Comportement** : Coché → insère `--debug` | Décoché → supprimé

---

## 5️⃣ Type "valued_option" - Case + champ (--log-level INFO)

```yaml
- code: "LOG_LEVEL"
  name: "Niveau de log"
  type: "valued_option"
  required: 0
  default: "INFO"
```

- **Interface** : Case à cocher + champ de saisie
- **Comportement** : Coché + rempli → insère la valeur | Décoché ou vide → supprimé

---

## 📋 Champs disponibles (résumé)

| Champ | Obligatoire | Description |
|-------|-------------|-------------|
| `code` | 🔴 OUI | Identifiant (MAJUSCULES recommandé) |
| `name` | 🔴 OUI | Label affiché dans l'interface |
| `type` | 🔴 OUI | string \| file \| directory \| flag \| valued_option |
| `required` | 🔴 OUI | 0 = optionnel \| 1 = obligatoire (astérisque rouge) |
| `default` | 🔵 Non | Valeur pré-remplie |
| `value` | 🔴 Pour flag | Valeur insérée si coché (ex: "--debug") |
| `validation` | 🔵 Non | Extensions de fichiers autorisées |

---

## ⚠️ Règles importantes

- `flag` et `valued_option` → toujours `required: 0`
- `flag` → le champ `value` est **OBLIGATOIRE**
- Placeholders vides → automatiquement supprimés de la commande finale
- `default` dans la tâche → **prioritaire** sur celui de la commande
- Les valeurs préremplies s'affichent en **vert**
