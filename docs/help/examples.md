# 📚 Exemples réels de votre projet

---

## 1️⃣ Commande avec construction de chemin : campaignexport

**Fichier** : `data/commands/campaignexport_commands.yaml`

```yaml
name: "campaignexport"
description: "Exporte les tables SQLite en fichiers texte + images"
command: "campaignexport {DATABASE_FILE}\\{PROJECT_NAME}.sqlite {TXT_OUTPUT_DIRECTORY} {IMG_OUTPUT_DIRECTORY} > {LOG_FILE}"
arguments:
  - code: "PROJECT_NAME"
    name: "Nom de la base"
    type: "string"
    required: 1
    default: "E3D_S29"
  
  - code: "DATABASE_FILE"
    name: "Répertoire de base"
    type: "directory"
    required: 1
    default: "L:\\PROJET\\BASE"
  
  - code: "TXT_OUTPUT_DIRECTORY"
    name: "Répertoire texte"
    type: "directory"
    required: 1
    default: "L:\\PROJET\\TXT"
  
  - code: "IMG_OUTPUT_DIRECTORY"
    name: "Répertoire images"
    type: "directory"
    required: 1
    default: "L:\\PROJET\\IMG"
  
  - code: "LOG_FILE"
    name: "Fichier de log"
    type: "string"
    required: 1
    default: "log_campaignexport.txt"
```

> 💡 **Construction de chemin** : `{DATABASE_FILE}\\{PROJECT_NAME}.sqlite`
> Combine un répertoire + un nom de fichier pour créer le chemin complet
> Résultat : `L:\PROJET\BASE\E3D_S29.sqlite`

✅ Commande générée : `campaignexport L:\PROJET\BASE\E3D_S29.sqlite L:\PROJET\TXT L:\PROJET\IMG > log.txt`

---

## 2️⃣ Commande avec options : tdmsdirimport

**Fichier** : `data/commands/tdmsdirimport_commands.yaml`

```yaml
name: "tdmsdirimport_tc"
description: "Importe tous les fichiers TDMS d'un dossier vers une base SQLite"
command: "tdmsdirimport {TDMS_DIR} {OUTPUT_DIR} --pname {PNAME} --keys {KEYS_FILE} --config {CONFIG} {TOL} {PTABLE} {IMU_LAG_TIME} > {LOG_FILE}"
arguments:
  - code: "TDMS_DIR"
    name: "Répertoire TDMS (entrée)"
    type: "directory"
    required: 1
    default: "L:\\PROJET\\TDMS"
  
  - code: "OUTPUT_DIR"
    name: "Répertoire de sortie (base)"
    type: "directory"
    required: 1
    default: "L:\\PROJET\\BASE"
  
  - code: "PNAME"
    name: "Nom du projet"
    type: "string"
    required: 1
    default: "E3D_S29"
  
  - code: "TOL"
    name: "Tolérance"
    type: "valued_option"  # ← Option avec valeur
    required: 0
    value: "--tol"
    default: "0"
  
  - code: "PTABLE"
    name: "Table de points"
    type: "valued_option"
    required: 0
    value: "--ptable"
    default: "IMU"
```

✅ Commande générée : `tdmsdirimport L:\PROJET\TDMS L:\PROJET\BASE --pname E3D_S29 --tol 0 --ptable IMU ...`

---

## 3️⃣ Tâche avec !include et arguments partagés

**Fichier** : `data/tasks/traitement_campagne_task.yaml`

```yaml
name: "Traitement campagne"
description: "Import TDMS du dossier + export campagne (TXT + IMAGES)"

arguments:  # ← Arguments partagés entre les 2 commandes
  - code: "PROJECT_NAME"
    name: "Nom du projet"
    type: "string"
    required: 1
    default: "E3D_S29"
    values:
      - command: "tdmsdirimport_tc"
        argument: "PNAME"           # → Nom de la table
      - command: "campaignexport"
        argument: "PROJECT_NAME"    # → Nom du fichier .sqlite
  
  - code: "DATABASE_FILE"
    name: "Répertoire de base"
    type: "directory"
    required: 1
    default: "L:\\PROJET\\BASE"
    values:
      - command: "tdmsdirimport_tc"
        argument: "OUTPUT_DIR"      # → Où créer la base
      - command: "campaignexport"
        argument: "DATABASE_FILE"   # → Où lire la base

commands:
  - !include ../commands/tdmsdirimport_commands.yaml
  - !include ../commands/campaignexport_commands.yaml
```

### 🎯 Résultat avec construction de chemin :

1. L'utilisateur saisit : `PROJECT_NAME = "E3D_S29"` et `DATABASE_FILE = "L:\PROJET\BASE"`
2. Commande 1 : `tdmsdirimport ... L:\PROJET\BASE --pname E3D_S29 ...`
3. Commande 2 : `campaignexport L:\PROJET\BASE\E3D_S29.sqlite ...`
4. ✅ Le chemin est construit avec `{DATABASE_FILE}\{PROJECT_NAME}.sqlite`
5. ✅ **Cohérence garantie** : même nom de projet partout

---

## 4️⃣ Conseils pratiques

> 💡 **Bonnes pratiques** :
> - **Commandes réutilisables** : Créez des fichiers de commandes dans `data/commands/`
> - **Tâches spécifiques** : Combinez les commandes avec `!include` dans `data/tasks/`
> - **Arguments partagés** : Utilisez `arguments` + `values` pour éviter la répétition
> - **Valeurs par défaut** : Définissez des `default` pour accélérer la saisie
> - **Validation** : Utilisez `file_extensions` pour les fichiers
> - **Logs** : Redirigez la sortie avec `> {LOG_FILE}`

---

## 5️⃣ Boutons d'exécution

### ▶️ Bouton "Exécuter" (vert)

- Situé dans la **console**, toujours visible à côté du bouton Stop
- **Grisé** au démarrage → **Vert** quand une tâche est sélectionnée
- Lance l'exécution de **toutes les commandes** de la tâche en séquence
- Devient **grisé** pendant l'exécution (désactivé)
- Redevient **vert** à la fin de l'exécution

### ⏹️ Bouton "Stop" (rouge)

- Situé dans la **console**, toujours visible à côté du bouton Exécuter
- **Grisé** par défaut → **Rouge** pendant l'exécution
- Cliquez dessus pour **arrêter immédiatement** la commande en cours
- Les commandes suivantes **ne seront pas exécutées**
- Utile pour les commandes longues (import TDMS, calculs, etc.)
- L'arrêt est **quasi-instantané** même si la commande est avancée

### 🎯 États visuels

| État | Boutons |
|------|---------|
| Au démarrage | `[▶ Exécuter (grisé)]  [⏹ Stop (grisé)]` |
| Tâche sélectionnée | `[▶ Exécuter (VERT)]  [⏹ Stop (grisé)]` |
| En exécution | `[▶ Exécuter (grisé)]  [⏹ Stop (ROUGE)]` |
| Fin d'exécution | `[▶ Exécuter (VERT)]  [⏹ Stop (grisé)]` |
