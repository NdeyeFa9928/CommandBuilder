# Architecture et Flux de CommandBuilder

## 1. DÉMARRAGE DE L'APPLICATION

```
main.py (entry point)
    ↓
setup_application()
    ├─ QApplication.create()
    ├─ app.setApplicationName("CommandBuilder")
    └─ app.setWindowIcon(icone.png)
    ↓
load_yaml_tasks()  [services/yaml_task_loader.py]
    ├─ YamlErrorHandler.load_all_tasks()
    │   ├─ Parcourt command_builder/data/tasks/*.yaml
    │   ├─ Parse chaque fichier YAML
    │   ├─ Crée des objets Task (modèle)
    │   └─ Retourne (tasks[], errors[])
    │
    └─ Retourne (tasks, errors)
    ↓
MainWindow() [components/main_window/main_window.py]
    ├─ _load_ui()
    │   ├─ Charge main_window.ui
    │   ├─ Crée les splitters (horizontal + vertical)
    │   └─ Configure les conteneurs
    │
    ├─ _setup_components()
    │   ├─ TaskList (affiche les tâches)
    │   ├─ CommandForm (formulaire de commande)
    │   ├─ ConsoleOutput (sortie console)
    │   └─ HelpButton (bouton aide)
    │
    ├─ _load_stylesheet()
    │   └─ Charge main_window.qss
    │
    └─ _connect_signals()
        ├─ help_button.help_clicked → _show_help_window()
        ├─ task_list.command_selected → _on_command_selected()
        └─ command_form.commands_to_execute → console_output.execute_commands()
    ↓
main_window.set_tasks(tasks)
    └─ task_list.set_tasks(tasks)
        └─ _update_task_list()
            └─ Pour chaque Task:
                ├─ Crée TaskComponent
                ├─ Connecte task_component.task_clicked → command_selected
                └─ Ajoute au layout
    ↓
if errors:
    └─ main_window.show_yaml_errors(errors)
        └─ Affiche ErrorsPanel dans une QDialog
    ↓
main_window.show()
└─ sys.exit(app.exec())
```

---

## 2. SÉLECTION D'UNE TÂCHE

```
USER CLIQUE SUR UNE TÂCHE
    ↓
TaskComponent.task_clicked(task)  [Signal]
    ↓
TaskList.command_selected(task_name, command_name)  [Signal]
    ↓
MainWindow._on_command_selected(task_name, command_name)
    ├─ Trouve la Task dans task_list.tasks
    ├─ Récupère task.commands[]
    └─ command_form.set_task(task)
        ↓
        CommandForm.set_task(task)
            ├─ self.current_task = task
            ├─ self.current_commands = task.commands[]
            ├─ self.shared_argument_values = {}
            │
            └─ _refresh_command_displays()
                ├─ Efface les CommandComponent précédents
                ├─ Pour chaque Command dans task.commands:
                │   ├─ Crée CommandComponent(command, simple_mode=True)
                │   │   └─ Affiche: "Nom: commande CLI"
                │   ├─ Connecte arguments_changed → _on_command_arguments_changed()
                │   └─ Ajoute au layout
                │
                ├─ Affiche les arguments partagés (TaskArgument)
                │   ├─ Pour chaque TaskArgument dans task.shared_arguments:
                │   │   ├─ Crée ArgumentComponent
                │   │   ├─ Connecte value_changed → _on_shared_argument_changed()
                │   │   └─ Ajoute au layout
                │   └─ Crée un bouton "Exécuter"
                │
                └─ Affiche les arguments locaux de la première commande
                    ├─ Crée CommandComponent(command, simple_mode=False)
                    │   └─ Affiche: Nom, Description, Arguments détaillés
                    └─ Connecte arguments_changed → _on_command_arguments_changed()
```

---

## 3. MODIFICATION D'UN ARGUMENT PARTAGÉ

```
USER MODIFIE UN ARGUMENT PARTAGÉ
    ↓
ArgumentComponent.value_changed(code, value)  [Signal]
    ↓
CommandForm._on_shared_argument_changed(code, value)
    ├─ Stocke: shared_argument_values[code] = value
    │
    └─ _refresh_command_displays()
        ├─ Récupère les mappings:
        │   └─ task.get_shared_argument_mappings(shared_argument_values)
        │       └─ Retourne: {
        │           "CommandName": {
        │               "argument_code": "valeur",
        │               ...
        │           },
        │           ...
        │       }
        │
        └─ Met à jour les CommandComponent
            └─ Affiche les valeurs mappées
```

---

## 4. MODIFICATION D'UN ARGUMENT LOCAL

```
USER MODIFIE UN ARGUMENT LOCAL
    ↓
ArgumentComponent.value_changed(code, value)  [Signal]
    ↓
CommandForm._on_command_arguments_changed(command_index, arguments_dict)
    ├─ Stocke les valeurs locales
    └─ Met à jour l'affichage (optionnel)
```

---

## 5. EXÉCUTION DES COMMANDES

```
USER CLIQUE "EXÉCUTER"
    ↓
CommandForm._on_execute_clicked()
    ├─ Valide les arguments obligatoires
    │   └─ command.validate_arguments(values)
    │       └─ Retourne (is_valid, errors[])
    │
    ├─ Si erreurs:
    │   └─ QMessageBox.warning() + STOP
    │
    └─ Si OK:
        ├─ Construit les commandes finales
        │   ├─ Remplace {ARGUMENT_CODE} par les valeurs
        │   └─ Crée CommandToExecute[]
        │
        └─ Émet: commands_to_execute(commands[])  [Signal]
            ↓
            MainWindow reçoit le signal
            └─ Connecté à: console_output.execute_commands(commands)
                ↓
                ConsoleOutput.execute_commands(commands)
                    ├─ self.commands_queue = commands
                    ├─ self.current_command_index = 0
                    │
                    └─ _execute_next_command()
                        ├─ Si current_command_index >= len(commands_queue):
                        │   ├─ Affiche résumé final
                        │   ├─ Émet: all_commands_finished()
                        │   └─ STOP
                        │
                        └─ Sinon:
                            ├─ Récupère command = commands_queue[current_command_index]
                            ├─ Affiche: "[HH:MM:SS] Exécution: commande"
                            │
                            └─ executor_service.create_executor(command)
                                ├─ Crée QProcess
                                ├─ Connecte finished → _on_command_finished()
                                └─ process.start()
                                    ↓
                                    COMMANDE S'EXÉCUTE
                                    ├─ Sortie standard capturée
                                    ├─ Affichée en temps réel
                                    └─ Code de retour récupéré
                                    ↓
                                    QProcess.finished(exit_code)
                                    ↓
                                    ConsoleOutput._on_command_finished(exit_code)
                                        ├─ Si exit_code != 0:
                                        │   ├─ Affiche: "[ERR] Commande échouée (code X)"
                                        │   ├─ Émet: all_commands_finished()
                                        │   └─ STOP (pas de commandes suivantes)
                                        │
                                        └─ Si exit_code == 0:
                                            ├─ Affiche: "[OK] Commande réussie"
                                            ├─ current_command_index += 1
                                            └─ _execute_next_command()  [BOUCLE]
```

---

## 6. STRUCTURE DES MODÈLES

### Task (modèle)
```python
Task:
    ├─ name: str
    ├─ description: str
    ├─ commands: Command[]
    ├─ shared_arguments: TaskArgument[]
    │
    └─ Méthodes:
        ├─ get_shared_argument_mappings(shared_values)
        │   └─ Retourne: {command_name: {arg_code: value}}
        │
        └─ validate_arguments(values)
            └─ Retourne: (is_valid, errors[])
```

### Command (modèle)
```python
Command:
    ├─ name: str
    ├─ description: str
    ├─ command: str  (template avec {ARGUMENT_CODE})
    ├─ arguments: Argument[]
    ├─ shared_argument_mapping: dict  (optionnel)
    │
    └─ Méthodes:
        ├─ validate_arguments(values)
        │   └─ Retourne: (is_valid, errors[])
        │
        └─ build_command(argument_values)
            └─ Remplace {ARGUMENT_CODE} par les valeurs
```

### Argument (modèle)
```python
Argument:
    ├─ code: str  (identifiant unique)
    ├─ name: str  (affiché dans l'UI)
    ├─ required: int  (0=optionnel, 1=obligatoire)
    ├─ type: str  ("text", "file", "folder")
    ├─ default: str  (valeur par défaut)
    ├─ validation: dict  (règles de validation)
    │
    └─ Méthodes:
        └─ is_valid(value)
            └─ Retourne: (is_valid, error_message)
```

### TaskArgument (modèle)
```python
TaskArgument (hérite de Argument):
    ├─ Même structure que Argument
    └─ Utilisé pour les arguments au niveau Task
```

---

## 7. STRUCTURE DES COMPOSANTS UI

### TaskList
```
TaskList (QWidget)
    ├─ task_items_layout (QVBoxLayout)
    │   ├─ TaskComponent 1
    │   ├─ TaskComponent 2
    │   ├─ TaskComponent N
    │   └─ Spacer (pour pousser vers le haut)
    │
    └─ Signaux:
        ├─ task_selected(Task)
        └─ command_selected(task_name, command_name)
```

### TaskComponent
```
TaskComponent (QWidget)
    ├─ Bouton cliquable avec nom de la tâche
    ├─ Affiche la description
    │
    └─ Signaux:
        └─ task_clicked(Task)
```

### CommandForm
```
CommandForm (QWidget)
    ├─ Scroll Area
    │   └─ form_container (QWidget)
    │       ├─ Arguments partagés (TaskArgument)
    │       │   ├─ ArgumentComponent 1
    │       │   ├─ ArgumentComponent 2
    │       │   └─ ...
    │       │
    │       ├─ Commandes (Command)
    │       │   ├─ CommandComponent 1 (simple_mode=True)
    │       │   ├─ CommandComponent 2 (simple_mode=True)
    │       │   └─ ...
    │       │
    │       ├─ Arguments locaux de la commande sélectionnée
    │       │   └─ CommandComponent (simple_mode=False)
    │       │       ├─ Nom
    │       │       ├─ Description
    │       │       └─ ArgumentComponent[]
    │       │
    │       └─ Bouton "Exécuter"
    │
    └─ Signaux:
        └─ commands_to_execute(commands[])
```

### CommandComponent
```
CommandComponent (QWidget)
    ├─ Mode simple (simple_mode=True):
    │   └─ Affiche: "Nom: commande CLI"
    │
    └─ Mode complet (simple_mode=False):
        ├─ Nom de la commande
        ├─ Description
        ├─ Commande CLI
        └─ ArgumentComponent[]
            ├─ Champ de saisie
            ├─ Bouton parcourir (si type=file/folder)
            └─ Validation en temps réel
```

### ArgumentComponent
```
ArgumentComponent (QWidget)
    ├─ Label: "Nom : *" (astérisque si obligatoire)
    ├─ QLineEdit (champ de saisie)
    ├─ Bouton parcourir (optionnel)
    │
    └─ Signaux:
        └─ value_changed(code, value)
```

### ConsoleOutput
```
ConsoleOutput (QWidget)
    ├─ QPlainTextEdit (affichage console)
    ├─ Bouton "Effacer"
    ├─ Bouton "Exporter"
    │
    └─ Signaux:
        └─ all_commands_finished()
```

---

## 8. FLUX DE VALIDATION

```
Avant exécution:
    ↓
CommandForm._on_execute_clicked()
    ├─ Pour chaque Command:
    │   └─ command.validate_arguments(argument_values)
    │       ├─ Pour chaque Argument:
    │       │   ├─ Si required=1 et value vide:
    │       │   │   └─ Erreur: "Champ obligatoire"
    │       │   │
    │       │   └─ Si validation rules:
    │       │       ├─ Applique min_length, max_length
    │       │       ├─ Applique pattern (regex)
    │       │       ├─ Applique file_exists, folder_exists
    │       │       └─ Retourne erreur si non conforme
    │       │
    │       └─ Retourne: (is_valid, errors[])
    │
    └─ Si erreurs:
        └─ QMessageBox.warning()
            ├─ Titre: "Erreurs de validation"
            ├─ Message: Liste des erreurs
            └─ STOP (pas d'exécution)
```

---

## 9. FLUX DE GESTION DES ERREURS YAML

```
Au démarrage:
    ↓
load_yaml_tasks()
    └─ YamlErrorHandler.load_all_tasks()
        ├─ Pour chaque fichier .yaml:
        │   ├─ try:
        │   │   ├─ Parse YAML
        │   │   ├─ Valide avec Pydantic
        │   │   └─ Crée Task
        │   │
        │   └─ except:
        │       ├─ SyntaxError (YAML invalide)
        │       ├─ ValidationError (champs manquants/invalides)
        │       ├─ FileNotFoundError
        │       └─ TypeError
        │           └─ Crée YamlError(file, type, message, line, suggestion)
        │
        └─ Retourne: (tasks[], errors[])
    ↓
Si errors:
    └─ MainWindow.show_yaml_errors(errors)
        ├─ Crée QDialog
        ├─ Ajoute ErrorsPanel
        │   └─ Pour chaque YamlError:
        │       ├─ ErrorDisplay
        │       │   ├─ Titre: "Erreur YAML"
        │       │   ├─ Fichier: error.file_name
        │       │   ├─ Type: error.error_type
        │       │   ├─ Message: error.error_message
        │       │   ├─ Ligne: error.line_number
        │       │   └─ Suggestion: error.suggestion
        │       │
        │       └─ Scroll Area
        │
        └─ dialog.exec()
```

---

## 10. FLUX D'EXÉCUTION SÉQUENTIELLE

```
ConsoleOutput.execute_commands(commands[])
    ├─ commands_queue = commands
    ├─ current_command_index = 0
    │
    └─ _execute_next_command()
        ├─ Affiche: "[HH:MM:SS] Exécution: cmd1"
        ├─ executor_service.create_executor(cmd1)
        │   └─ QProcess.start()
        │       ↓
        │       CMD1 S'EXÉCUTE
        │       ├─ Sortie affichée en temps réel
        │       └─ Émet finished(exit_code)
        │           ↓
        │           _on_command_finished(exit_code)
        │               ├─ Si exit_code != 0:
        │               │   ├─ Affiche: "[ERR] Erreur (code X)"
        │               │   ├─ Émet: all_commands_finished()
        │               │   └─ STOP
        │               │
        │               └─ Si exit_code == 0:
        │                   ├─ current_command_index = 1
        │                   └─ _execute_next_command()
        │                       ├─ Affiche: "[HH:MM:SS] Exécution: cmd2"
        │                       ├─ executor_service.create_executor(cmd2)
        │                       │   └─ QProcess.start()
        │                       │       ↓
        │                       │       CMD2 S'EXÉCUTE
        │                       │       └─ ... (même processus)
        │                       │
        │                       └─ [BOUCLE JUSQU'À DERNIÈRE COMMANDE]
        │
        └─ Quand toutes les commandes sont terminées:
            ├─ Affiche résumé: "Durée totale: X secondes"
            └─ Émet: all_commands_finished()
```

---

## 11. RÉSUMÉ DES SIGNAUX PRINCIPAUX

| Signal | Émetteur | Récepteur | Données |
|--------|----------|-----------|---------|
| `task_clicked` | TaskComponent | TaskList | Task |
| `command_selected` | TaskList | MainWindow | (task_name, command_name) |
| `help_clicked` | HelpButton | MainWindow | - |
| `arguments_changed` | ArgumentComponent | CommandForm | (code, value) |
| `commands_to_execute` | CommandForm | ConsoleOutput | commands[] |
| `all_commands_finished` | ConsoleOutput | (aucun) | - |

---

## 12. FICHIERS CLÉS PAR ÉTAPE

| Étape | Fichiers |
|-------|----------|
| Démarrage | main.py, yaml_task_loader.py, main_window.py |
| Sélection tâche | task_list.py, task_component.py, command_form.py |
| Modification argument | argument_component.py, command_form.py |
| Exécution | command_form.py, console_output.py, command_executor.py |
| Validation | models/command.py, models/arguments.py |
| Erreurs YAML | yaml_error_handler.py, error_display.py |

