# Build & Distribution Guide for CommandBuilder

Cette page détaille le fonctionnement complet du **build PyInstaller** et la gestion du dossier **`data/tasks`** au runtime.

---

## 1. Script `build_executable.py`

| Étape | Description |
|-------|-------------|
| 1 | Nettoie (ou crée) le dossier `dist/`. |
| 2 | Collecte automatiquement toutes les ressources :<br>• fichiers `.ui`, `.qss`<br>• dossier complet `command_builder/data/tasks`<br>• fichiers JSON dans `command_builder/data/commands`<br>• icônes/PNG dans `command_builder/assets` |
| 3 | Construit la commande **PyInstaller** :<br>```bash
pipenv run pyinstaller \
  --onefile --windowed \
  --name=CommandBuilder \
  --distpath=dist \
  --icon=command_builder/assets/icone.png \
  --add-data=command_builder/data/tasks;command_builder/data \
  ...autres --add-data générés... \
  main.py
``` |
| 4 | Exécute PyInstaller ; l’exécutable final est placé dans `dist/CommandBuilder.exe`. |

---

## 2. Modes générés par PyInstaller

| Mode | Contenu de `dist/` | Caractéristiques |
|------|-------------------|------------------|
| **one-file** (par défaut) | `CommandBuilder.exe` unique | ✔ facile à distribuer<br>❗ extraction temporaire à chaque lancement |
| **one-dir** (optionnel) | `CommandBuilder/` + .exe + libs + data | ✔ démarrage plus rapide<br>✔ fichiers visibles pour debug |

Le Taskfile appelle toujours le build **one-file** (`--onefile`). Pour passer en **one-dir**, lance :
```bash
pipenv run pyinstaller --onedir ...
```

---

## 3. Où l’application cherche les YAML de tâches ?

Le service `command_builder/services/yaml_task_loader.py` résout le dossier de deux façons :

1. **Exécutable PyInstaller (`sys.frozen = True`)**
   1. D’abord : `dist/data/tasks/` (dossier externe placé à côté de l’exe).<br>      *Permet à l’utilisateur de déposer de nouveaux YAML sans rebuilder.*
   2. Sinon : ressources internes extraites dans le répertoire temporaire `_MEIPASS/command_builder/data/tasks`.
2. **Développement (`python main.py`, `task run`)**
   - Dossier source du dépôt : `command_builder/data/tasks/`.

Schéma :
```mermaid
graph TD
  dev[Dev run] -->|charge| repoData[command_builder/data/tasks]
  exe_one_dir[EXE one-dir] -->|1. dist/data/tasks| ext
  exe_one_dir -->|2. _MEIPASS| internal
  exe_one_file[EXE one-file] -->|1. dist/data/tasks (si créé)| ext
  exe_one_file -->|2. _MEIPASS| internal
```

---

## 4. Ajouter / mettre à jour des tâches après build

Le dossier `data/` est **automatiquement copié** à côté de l'exe lors du build :

```
dist/
├── CommandBuilder_0.1.0.exe
└── data/
    ├── tasks/
    │   ├── traitement_campagne_task.yaml
    │   ├── import_tdms_task.yaml
    │   └── ...
    └── commands/
        ├── tdmsimport_commands.yaml
        ├── csvexport_commands.yaml
        └── ...
```

**Pour modifier ou ajouter des tâches** :
1. Ouvrir `dist/data/tasks/`
2. Modifier un fichier `.yaml` existant ou en créer un nouveau
3. Relancer `CommandBuilder.exe` : les changements sont pris en compte immédiatement

>  **Avantage** : Les utilisateurs peuvent personnaliser les tâches sans recompiler l'application.

---

## 5. Commandes Taskfile liées

| Commande | Effet |
|----------|-------|
| `task build` | Build one-file, mode fenêtre, sans console. |
| `task build-dev` | Build one-file avec console (debug). |
| `task clean` | Supprime `dist/`, `build/`, `*.spec`. |

---

## 6. Personnalisation rapide

- **Icône** : remplacez `command_builder/assets/icone.png` avant le build.
- **Ressources supplémentaires** : ajoutez vos patterns dans `collect_data_files()`.
- **Mode console** : utilisez `task build-dev` ou ajoutez `--console` à la commande PyInstaller.


