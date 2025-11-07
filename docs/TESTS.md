# Tests CommandBuilder

Suite de tests unitaires et d'intégration pour assurer le bon fonctionnement des éléments critiques.

## Structure des tests

```
command_builder/tests/
├── services/
│   ├── test_command_executor.py      # Tests du service d'exécution
│   ├── test_yaml_loader.py           # Tests du chargeur YAML
│   └── test_yaml_task_loader.py      # Tests du chargeur de tâches YAML
├── models/
│   └── test_task.py                  # Tests du modèle Task
├── components/
│   ├── test_console_output.py        # Tests du composant ConsoleOutput
│   ├── test_command_component.py     # Tests du composant Command
│   └── test_argument_component.py    # Tests du composant Argument
├── integration/
│   ├── test_sequential_execution.py  # Tests d'intégration (exécution séquentielle)
│   └── test_yaml_integration.py      # Tests d'intégration YAML
└── conftest.py                       # Fixtures partagées
```

## Éléments testés

### 1. **Exécution séquentielle des commandes** ✓
- `test_command_executor.py` : Tests du service d'exécution
- `test_console_output.py` : Tests du composant ConsoleOutput
- `test_sequential_execution.py` : Tests d'intégration complets

**Cas couverts :**
- Exécution d'une seule commande
- Exécution de plusieurs commandes dans l'ordre
- Vérification que les commandes s'exécutent une à la fois

### 2. **Arrêt en cas d'erreur** ✓
- `test_console_output.py::TestConsoleOutputErrorHandling` : Tests de gestion d'erreur
- `test_sequential_execution.py::TestSequentialExecutionFlow::test_execution_stops_on_error`

**Cas couverts :**
- Détection des codes d'erreur non-zéro
- Arrêt immédiat de l'exécution
- Affichage des commandes non exécutées
- Émission du signal de fin

### 3. **Modèle Task** ✓
- `test_task.py` : Tests complets du modèle Task

**Cas couverts :**
- Création de tâches
- Accès aux commandes
- Validation des données
- Gestion des arguments partagés

### 4. **Chargement YAML** ✓
- `test_yaml_loader.py` : Tests du chargeur YAML
- `test_yaml_task_loader.py` : Tests du chargeur de tâches YAML
- `test_yaml_integration.py` : Tests d'intégration YAML

## Exécuter les tests

### Tous les tests
```bash
pytest
```

### Tests spécifiques
```bash
# Tests du service d'exécution
pytest command_builder/tests/services/test_command_executor.py

# Tests du composant ConsoleOutput
pytest command_builder/tests/components/test_console_output.py

# Tests du modèle Task
pytest command_builder/tests/models/test_task.py

# Tests d'intégration (exécution séquentielle)
pytest command_builder/tests/integration/test_sequential_execution.py
```

### Avec rapport de couverture
```bash
pytest --cov=command_builder --cov-report=html
```

### Mode verbose
```bash
pytest -v
```

### Tests avec arrêt au premier échec
```bash
pytest -x
```

## Utiliser avec Taskfile

```bash
# Exécuter les tests (défini dans taskfile.yml)
task test

# Exécuter les tests avec couverture
task test:coverage
```

## Points clés testés

### ✓ Exécution séquentielle
- Les commandes s'exécutent une à la fois
- L'ordre est préservé
- Chaque commande attend la fin de la précédente

### ✓ Gestion des erreurs
- Code de retour non-zéro = erreur
- Arrêt immédiat en cas d'erreur
- Les commandes suivantes ne s'exécutent pas
- Message clair indiquant l'arrêt

### ✓ Signaux Qt
- `all_commands_finished` émis à la fin
- Fonctionne en cas de succès ou d'erreur

### ✓ Affichage console
- Chaque commande affichée avec timestamp
- Sortie standard capturée
- Erreurs affichées avec préfixe [ERR]
- Résumé final avec durée totale

## Ajouter de nouveaux tests

Pour ajouter un test :

1. Créer un fichier `test_*.py` dans le répertoire approprié
2. Importer les fixtures de `conftest.py` si nécessaire
3. Utiliser les conventions de nommage : `test_*` pour les fonctions
4. Exécuter `pytest` pour vérifier

Exemple :
```python
def test_my_feature(console_output):
    """Teste ma nouvelle fonctionnalité."""
    # Arrange
    commands = [{"name": "test", "command": "echo test"}]
    
    # Act
    console_output.execute_commands(commands)
    
    # Assert
    assert "test" in console_output.text_edit_console.toPlainText()
```

## Dépendances de test

- `pytest` : Framework de test
- `pytest-cov` : Couverture de code
- `PySide6` : Framework Qt
- `unittest.mock` : Mocking et patching

Toutes les dépendances sont dans `Pipfile`.
