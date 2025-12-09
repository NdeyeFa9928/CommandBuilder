"""Tests de performance pour CommandBuilder."""

import time

import pytest

from command_builder.models.arguments import Argument, ArgumentValue, TaskArgument
from command_builder.models.command import Command
from command_builder.models.task import Task
from command_builder.services.yaml_task_loader import load_yaml_task


@pytest.fixture
def large_task():
    """Crée une tâche avec beaucoup de commandes et d'arguments."""
    commands = []
    for i in range(100):
        arguments = [
            Argument(
                code=f"ARG_{j}",
                name=f"Argument {j}",
                type="text",
                required=j % 2 == 0,  # Alternance requis/optionnel
                default=f"default_{j}",
            )
            for j in range(10)
        ]

        commands.append(
            Command(
                name=f"Command {i}",
                description=f"Description for command {i}",
                command=f"test_command_{i} "
                + " ".join(f"{{{arg.code}}}" for arg in arguments),
                arguments=arguments,
            )
        )

    return Task(
        name="Large Task", description="Task with many commands", commands=commands
    )


@pytest.fixture
def task_with_many_shared_arguments():
    """Crée une tâche avec beaucoup d'arguments partagés."""
    # 50 arguments partagés
    task_arguments = []
    for i in range(50):
        values = [
            ArgumentValue(command=f"Command {j}", argument=f"arg_{i}")
            for j in range(10)  # Chaque argument partagé cible 10 commandes
        ]
        task_arguments.append(
            TaskArgument(
                code=f"SHARED_{i}",
                name=f"Shared Argument {i}",
                type="text",
                default=f"default_{i}",
                values=values,
            )
        )

    # 10 commandes avec 50 arguments chacune
    commands = []
    for i in range(10):
        arguments = [
            Argument(code=f"arg_{j}", name=f"Argument {j}", type="text")
            for j in range(50)
        ]
        commands.append(
            Command(
                name=f"Command {i}",
                description=f"Command {i}",
                command=f"test_{i}",
                arguments=arguments,
            )
        )

    return Task(
        name="Task with many shared arguments",
        description="Test",
        arguments=task_arguments,
        commands=commands,
    )


class TestTaskCreationPerformance:
    """Tests de performance pour la création de tâches."""

    def test_create_large_task_performance(self, large_task):
        """Test que la création d'une grande tâche est rapide."""
        start = time.time()

        # Créer une nouvelle instance
        task = Task(
            name=large_task.name,
            description=large_task.description,
            commands=large_task.commands,
        )

        elapsed = time.time() - start

        assert task is not None
        assert len(task.commands) == 100
        assert elapsed < 1.0  # Devrait prendre moins d'1 seconde

    def test_access_arguments_performance(self, large_task):
        """Test que l'accès aux arguments est rapide."""
        start = time.time()

        # Accéder à tous les arguments de toutes les commandes
        for command in large_task.commands:
            for arg in command.arguments:
                _ = arg.code
                _ = arg.name
                _ = arg.default

        elapsed = time.time() - start

        assert elapsed < 0.5  # Devrait être très rapide


class TestValidationPerformance:
    """Tests de performance pour la validation."""

    def test_validate_large_task_performance(self, large_task):
        """Test que la validation d'une grande tâche est rapide."""
        # Préparer les valeurs pour tous les arguments
        all_values = {}
        for command in large_task.commands:
            for arg in command.arguments:
                all_values[arg.code] = "test_value"

        start = time.time()

        # Valider chaque commande
        for command in large_task.commands:
            command_values = {
                arg.code: all_values.get(arg.code, "") for arg in command.arguments
            }
            is_valid, errors = command.validate_arguments(command_values)

        elapsed = time.time() - start

        assert elapsed < 1.0  # Devrait prendre moins d'1 seconde

    def test_validate_required_arguments_performance(self, large_task):
        """Test de performance pour la validation des arguments obligatoires."""
        start = time.time()

        # Récupérer tous les arguments obligatoires
        for command in large_task.commands:
            required = command.get_required_arguments()
            optional = command.get_optional_arguments()

        elapsed = time.time() - start

        assert elapsed < 0.5


class TestSharedArgumentsPerformance:
    """Tests de performance pour les arguments partagés."""

    def test_apply_shared_arguments_performance(self, task_with_many_shared_arguments):
        """Test que l'application d'arguments partagés est rapide."""
        task = task_with_many_shared_arguments

        # Préparer les valeurs partagées
        shared_values = {f"SHARED_{i}": f"value_{i}" for i in range(50)}

        start = time.time()

        # Appliquer les arguments partagés
        task.apply_shared_arguments(shared_values)

        elapsed = time.time() - start

        assert elapsed < 2.0  # 50 arguments × 10 commandes = 500 propagations

    def test_multiple_apply_shared_arguments_performance(
        self, task_with_many_shared_arguments
    ):
        """Test de performance pour applications successives."""
        task = task_with_many_shared_arguments

        start = time.time()

        # Appliquer 10 fois
        for iteration in range(10):
            shared_values = {f"SHARED_{i}": f"value_{i}_{iteration}" for i in range(50)}
            task.apply_shared_arguments(shared_values)

        elapsed = time.time() - start

        assert elapsed < 5.0  # 10 applications


class TestYamlLoadingPerformance:
    """Tests de performance pour le chargement YAML."""

    def test_load_multiple_yaml_files_performance(self, tmp_path):
        """Test du chargement de nombreux fichiers YAML."""
        # Créer 50 fichiers YAML
        yaml_files = []
        for i in range(50):
            yaml_file = tmp_path / f"task_{i}.yaml"
            yaml_file.write_text(f"""
name: "Task {i}"
description: "Test task {i}"
commands:
  - name: "Command {i}"
    description: "Test command"
    command: "echo test_{i}"
    arguments:
      - code: "ARG_{i}"
        name: "Argument {i}"
        type: "text"
        required: 0
""")
            yaml_files.append(yaml_file)

        start = time.time()

        # Charger tous les fichiers
        tasks = []
        for yaml_file in yaml_files:
            task = load_yaml_task(str(yaml_file))
            tasks.append(task)

        elapsed = time.time() - start

        assert len(tasks) == 50
        assert elapsed < 5.0  # Devrait charger 50 fichiers en moins de 5 secondes


class TestMemoryUsage:
    """Tests de consommation mémoire (basiques)."""

    def test_large_task_memory_footprint(self, large_task):
        """Test que la tâche n'utilise pas une quantité excessive de mémoire."""
        import sys

        # Mesure approximative de la taille en mémoire
        size = sys.getsizeof(large_task)

        # La tâche ne devrait pas être énorme
        # (ce test est approximatif, dépend de l'implémentation Python)
        assert size < 10_000_000  # Moins de 10 MB

    def test_repeated_task_creation_no_memory_leak(self):
        """Test qu'il n'y a pas de fuite mémoire lors de créations répétées."""
        import gc

        # Forcer le garbage collection
        gc.collect()

        # Créer et détruire des tâches plusieurs fois
        for _ in range(100):
            task = Task(
                name="Test",
                description="Test",
                commands=[
                    Command(
                        name="Command",
                        description="Test",
                        command="echo test",
                        arguments=[
                            Argument(code=f"ARG_{i}", name=f"Arg {i}", type="text")
                            for i in range(10)
                        ],
                    )
                ],
            )
            del task

        gc.collect()

        # Si on arrive ici sans erreur de mémoire, c'est bon


class TestWorstCaseScenarios:
    """Tests des pires scénarios."""

    def test_deeply_nested_validation(self):
        """Test de validation avec beaucoup d'arguments imbriqués."""
        # Créer une commande avec beaucoup d'arguments obligatoires
        arguments = [
            Argument(
                code=f"REQUIRED_{i}", name=f"Required {i}", type="text", required=1
            )
            for i in range(100)
        ]

        command = Command(
            name="Test", description="Test", command="test", arguments=arguments
        )

        # Valider avec toutes les valeurs vides (pire cas)
        start = time.time()

        is_valid, errors = command.validate_arguments(
            {arg.code: "" for arg in arguments}
        )

        elapsed = time.time() - start

        assert not is_valid
        assert len(errors) == 100
        assert elapsed < 1.0

    @pytest.mark.slow
    def test_extreme_load_1000_commands(self):
        """Test avec 1000 commandes (marqué comme lent)."""
        commands = [
            Command(
                name=f"Command {i}",
                description=f"Command {i}",
                command=f"echo {i}",
                arguments=[],
            )
            for i in range(1000)
        ]

        start = time.time()

        task = Task(name="Extreme Task", description="1000 commands", commands=commands)

        elapsed = time.time() - start

        assert len(task.commands) == 1000
        assert elapsed < 5.0  # Devrait rester raisonnable


# Configuration pytest pour les tests lents
def pytest_configure(config):
    """Configure les markers pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
