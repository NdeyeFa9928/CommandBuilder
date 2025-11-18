"""
Tests unitaires pour le modèle Task.
Teste la validation, le chargement et la gestion des commandes.
"""

import pytest
from command_builder.models.task import Task
from command_builder.models.command import Command
from command_builder.models.arguments import Argument


@pytest.fixture
def sample_command():
    """Fixture pour une commande de test."""
    return Command(
        name="Test Command",
        description="A test command",
        command="echo {PARAM}",
        arguments=[
            Argument(
                code="PARAM",
                name="Parameter",
                description="Test parameter",
                type="string",
                required=True,
            )
        ],
    )


@pytest.fixture
def sample_task(sample_command):
    """Fixture pour une tâche de test."""
    return Task(
        name="Test Task",
        description="A test task",
        commands=[sample_command],
    )


class TestTaskCreation:
    """Tests pour la création de tâches."""

    def test_task_creation(self, sample_task):
        """Teste la création d'une tâche."""
        assert sample_task.name == "Test Task"
        assert sample_task.description == "A test task"
        assert len(sample_task.commands) == 1

    def test_task_with_multiple_commands(self, sample_command):
        """Teste la création d'une tâche avec plusieurs commandes."""
        task = Task(
            name="Multi Command Task",
            description="Task with multiple commands",
            commands=[sample_command, sample_command],
        )
        assert len(task.commands) == 2

    def test_task_with_empty_commands(self):
        """Teste la création d'une tâche sans commandes."""
        task = Task(
            name="Empty Task",
            description="Task with no commands",
            commands=[],
        )
        assert len(task.commands) == 0


class TestTaskCommandAccess:
    """Tests pour l'accès aux commandes d'une tâche."""

    def test_get_commands(self, sample_task, sample_command):
        """Teste la récupération des commandes."""
        commands = sample_task.commands
        assert len(commands) == 1
        assert commands[0].name == sample_command.name

    def test_task_command_order(self, sample_command):
        """Teste que l'ordre des commandes est préservé."""
        cmd1 = Command(
            name="First",
            description="First command",
            command="echo first",
            arguments=[],
        )
        cmd2 = Command(
            name="Second",
            description="Second command",
            command="echo second",
            arguments=[],
        )
        cmd3 = Command(
            name="Third",
            description="Third command",
            command="echo third",
            arguments=[],
        )

        task = Task(
            name="Ordered Task",
            description="Task with ordered commands",
            commands=[cmd1, cmd2, cmd3],
        )

        assert task.commands[0].name == "First"
        assert task.commands[1].name == "Second"
        assert task.commands[2].name == "Third"


class TestTaskValidation:
    """Tests pour la validation des tâches."""

    def test_task_name_not_empty(self):
        """Teste qu'une tâche avec un nom valide est créée."""
        task = Task(
            name="Valid Task",
            description="Test",
            commands=[],
        )
        assert task.name == "Valid Task"

    def test_task_description_optional(self):
        """Teste que la description peut être vide."""
        task = Task(
            name="Test Task",
            description="",
            commands=[],
        )
        assert task.description == ""


class TestTaskSharedArguments:
    """Tests pour la gestion des arguments partagés."""

    def test_apply_shared_arguments_no_arguments(self, sample_task):
        """Teste apply_shared_arguments quand il n'y a pas d'arguments partagés."""
        # Devrait ne rien faire sans erreur
        sample_task.apply_shared_arguments({"test": "value"})
        # Pas d'assertion, juste vérifier qu'il n'y a pas d'erreur

    def test_apply_shared_arguments_empty_dict(self, sample_task):
        """Teste apply_shared_arguments avec un dictionnaire vide."""
        # Devrait ne rien faire sans erreur
        sample_task.apply_shared_arguments({})
        # Pas d'assertion, juste vérifier qu'il n'y a pas d'erreur


class TestTaskIntegration:
    """Tests d'intégration pour les tâches."""

    def test_task_with_multiple_arguments_per_command(self):
        """Teste une tâche avec plusieurs arguments par commande."""
        cmd = Command(
            name="Complex Command",
            description="Command with multiple arguments",
            command="process {input} {output} {format}",
            arguments=[
                Argument(
                    code="input",
                    name="Input File",
                    description="Input file path",
                    type="string",
                    required=True,
                ),
                Argument(
                    code="output",
                    name="Output File",
                    description="Output file path",
                    type="string",
                    required=True,
                ),
                Argument(
                    code="format",
                    name="Format",
                    description="Output format",
                    type="string",
                    required=False,
                ),
            ],
        )

        task = Task(
            name="Complex Task",
            description="Task with complex command",
            commands=[cmd],
        )

        assert len(task.commands[0].arguments) == 3
        assert task.commands[0].arguments[0].code == "input"
        assert task.commands[0].arguments[1].code == "output"
        assert task.commands[0].arguments[2].code == "format"
