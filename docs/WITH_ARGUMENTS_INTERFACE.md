# Interface WithArguments

## Vue d'ensemble

L'interface `WithArguments` est un mixin qui fournit des méthodes communes pour gérer les arguments dans les classes `Task` et `Command`. Elle élimine la duplication de code et permet un traitement uniforme des arguments.

## Architecture

```
WithArguments (Interface/Mixin)
    ↑                    ↑
    |                    |
  Task              Command
```

## Avantages

### 1. Élimination de la Duplication
**Avant** : Chaque classe avait sa propre méthode pour chercher un argument
```python
# Dans Task
def get_shared_argument_by_code(self, code: str):
    for arg in self.arguments:
        if arg.code == code:
            return arg
    return None

# Dans Command (code similaire)
def get_argument_by_code(self, code: str):
    for arg in self.arguments:
        if arg.code == code:
            return arg
    return None
```

**Après** : Une seule méthode héritée
```python
# Dans WithArguments (une seule fois)
def get_argument_by_code(self, code: str):
    for arg in self.arguments:
        if hasattr(arg, 'code') and arg.code == code:
            return arg
    return None

# Task et Command héritent automatiquement
```

### 2. Élimination des Conditions if/else

**Avant** :
```python
def process_entity(entity):
    if isinstance(entity, Task):
        arg = entity.get_shared_argument_by_code("db_path")
    elif isinstance(entity, Command):
        arg = entity.get_argument_by_code("db_path")  # Nom différent !
    else:
        raise ValueError("Type non supporté")
```

**Après** :
```python
def process_entity(entity: WithArguments):
    arg = entity.get_argument_by_code("db_path")  # Même méthode !
```

### 3. Extensibilité

Si vous créez une nouvelle classe avec des arguments :
```python
class Template(BaseModel, WithArguments):
    name: str
    template: str
    arguments: List[Argument]

# Toutes les méthodes sont automatiquement disponibles !
template.get_argument_by_code("test")
template.has_required_arguments()
template.get_argument_values()
```

## Méthodes Disponibles

### `get_argument_by_code(code: str) -> Optional[Any]`
Récupère un argument par son code.

```python
task = Task(...)
arg = task.get_argument_by_code("db_path")
if arg:
    print(f"Argument trouvé : {arg.name}")
```

### `get_argument_values() -> Dict[str, str]`
Récupère toutes les valeurs par défaut des arguments.

```python
command = Command(...)
values = command.get_argument_values()
# {'db_path': '/path/to/db', 'verbose': 'true'}
```

### `has_required_arguments() -> bool`
Vérifie si tous les arguments requis ont une valeur.

```python
if not task.has_required_arguments():
    print("Certains arguments requis sont manquants !")
```

### `get_required_arguments() -> List[Any]`
Retourne uniquement les arguments requis.

```python
required = command.get_required_arguments()
for arg in required:
    print(f"Argument requis : {arg.name}")
```

### `get_optional_arguments() -> List[Any]`
Retourne uniquement les arguments optionnels.

```python
optional = task.get_optional_arguments()
```

### `has_argument(code: str) -> bool`
Vérifie si un argument existe.

```python
if task.has_argument("db_path"):
    print("L'argument db_path existe")
```

### `count_arguments() -> int`
Retourne le nombre total d'arguments.

```python
print(f"Nombre d'arguments : {command.count_arguments()}")
```

### `count_required_arguments() -> int`
Retourne le nombre d'arguments requis.

```python
print(f"Arguments requis : {task.count_required_arguments()}")
```

## Utilisation dans le Code

### Exemple 1 : Validation Uniforme

```python
def validate_entity(entity: WithArguments) -> bool:
    """Valide n'importe quelle entité avec arguments"""
    if not entity.has_required_arguments():
        missing = [arg.name for arg in entity.get_required_arguments() 
                   if not arg.default]
        print(f"Arguments manquants : {', '.join(missing)}")
        return False
    return True

# Fonctionne avec Task ET Command
validate_entity(my_task)
validate_entity(my_command)
```

### Exemple 2 : Affichage Générique

```python
def display_arguments(entity: WithArguments, widget):
    """Affiche les arguments de n'importe quelle entité"""
    for arg in entity.arguments:
        label = QLabel(arg.name)
        input_field = QLineEdit(arg.default or "")
        widget.layout().addWidget(label)
        widget.layout().addWidget(input_field)
    
    # Mettre en évidence les requis
    for req_arg in entity.get_required_arguments():
        # Styliser en rouge
        pass
```

### Exemple 3 : Recherche d'Arguments

```python
def find_and_update_argument(entity: WithArguments, code: str, value: str):
    """Trouve et met à jour un argument"""
    arg = entity.get_argument_by_code(code)
    if arg:
        arg.default = value
        return True
    return False

# Même fonction pour Task et Command
find_and_update_argument(task, "db_path", "/new/path")
find_and_update_argument(command, "verbose", "true")
```

## Implémentation Technique

### Héritage Multiple avec Pydantic

```python
class Task(BaseModel, WithArguments):
    name: str
    arguments: Optional[List[TaskArgument]] = []
    # ...
```

**Important** : `BaseModel` doit être en premier pour que Pydantic fonctionne correctement.

### Propriété `arguments`

L'interface s'attend à ce que la classe ait une propriété `arguments` :
```python
@property
def arguments(self) -> List[Any]:
    raise NotImplementedError
```

Avec Pydantic, cette propriété est automatiquement créée via la définition du champ.

## Tests

```python
def test_with_arguments_interface():
    # Créer une tâche avec arguments
    task = Task(
        name="Test",
        description="Test task",
        arguments=[
            TaskArgument(code="arg1", name="Argument 1", required=1),
            TaskArgument(code="arg2", name="Argument 2", default="value2")
        ],
        commands=[]
    )
    
    # Tester les méthodes héritées
    assert task.count_arguments() == 2
    assert task.count_required_arguments() == 1
    assert task.has_argument("arg1")
    assert not task.has_argument("arg3")
    
    arg = task.get_argument_by_code("arg1")
    assert arg is not None
    assert arg.name == "Argument 1"
    
    # Vérifier les arguments requis
    assert not task.has_required_arguments()  # arg1 n'a pas de valeur
    
    # Ajouter une valeur
    arg.default = "value1"
    assert task.has_required_arguments()  # Maintenant OK
```

## Migration du Code Existant

### Avant
```python
# Dans command_form.py
task_arg = self.current_task.get_shared_argument_by_code(task_arg_code)
```

### Après
```python
# Dans command_form.py
task_arg = self.current_task.get_argument_by_code(task_arg_code)
```

### Avant
```python
# Dans task.py
for command in self.commands:
    if command.name == target.command:
        for arg in command.arguments:
            if arg.code == target.argument:
                arg.default = value
                break
```

### Après
```python
# Dans task.py
for command in self.commands:
    if command.name == target.command:
        arg = command.get_argument_by_code(target.argument)
        if arg:
            arg.default = value
```

## Bonnes Pratiques

1. **Utiliser le type hint `WithArguments`** dans les signatures de fonctions qui acceptent Task ou Command
2. **Ne pas dupliquer la logique** : Si vous avez besoin d'une nouvelle méthode commune, ajoutez-la à `WithArguments`
3. **Tester l'existence des attributs** : Utilisez `hasattr()` pour vérifier les propriétés avant de les utiliser
4. **Documenter les nouvelles méthodes** : Ajoutez des docstrings claires pour chaque méthode

## Évolutions Futures

### Méthodes Potentielles à Ajouter

```python
def set_argument_value(self, code: str, value: str) -> bool:
    """Définit la valeur d'un argument"""
    arg = self.get_argument_by_code(code)
    if arg:
        arg.default = value
        return True
    return False

def validate_argument_values(self) -> List[str]:
    """Valide toutes les valeurs et retourne les erreurs"""
    errors = []
    for arg in self.arguments:
        if hasattr(arg, 'validation') and arg.validation:
            # Logique de validation
            pass
    return errors

def get_arguments_by_type(self, arg_type: str) -> List[Any]:
    """Récupère les arguments d'un type spécifique"""
    return [arg for arg in self.arguments 
            if hasattr(arg, 'type') and arg.type == arg_type]
```

## Conclusion

L'interface `WithArguments` simplifie considérablement la gestion des arguments dans CommandBuilder en :
- Éliminant la duplication de code
- Supprimant les conditions if/else
- Facilitant l'extension future
- Améliorant la testabilité
- Rendant le code plus maintenable

C'est un exemple parfait de l'utilisation des interfaces pour créer un code propre et évolutif.
