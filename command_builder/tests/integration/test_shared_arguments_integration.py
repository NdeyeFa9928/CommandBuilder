"""Tests d'intégration pour le système d'arguments partagés."""

import pytest

from command_builder.models.arguments import Argument, ArgumentValue, TaskArgument
from command_builder.models.command import Command
from command_builder.models.task import Task


@pytest.fixture
def task_with_shared_arguments():
    """Crée une tâche avec arguments partagés."""
    return Task(
        name="Import and Process",
        description="Import data and process it",
        arguments=[
            TaskArgument(
                code="DATABASE_FILE",
                name="Database",
                type="file",
                required=1,
                default="",
                values=[
                    ArgumentValue(command="Import Data", argument="db_path"),
                    ArgumentValue(command="Process Data", argument="database"),
                ],
            ),
            TaskArgument(
                code="OUTPUT_DIR",
                name="Output Directory",
                type="directory",
                required=0,
                default="./output",
                values=[
                    ArgumentValue(command="Import Data", argument="output"),
                    ArgumentValue(command="Process Data", argument="output_dir"),
                ],
            ),
        ],
        commands=[
            Command(
                name="Import Data",
                description="Import data from file",
                command="import --db {db_path} --output {output}",
                arguments=[
                    Argument(
                        code="db_path", name="Database Path", type="file", required=1
                    ),
                    Argument(
                        code="output", name="Output", type="directory", required=0
                    ),
                ],
            ),
            Command(
                name="Process Data",
                description="Process imported data",
                command="process --database {database} --output-dir {output_dir}",
                arguments=[
                    Argument(code="database", name="Database", type="file", required=1),
                    Argument(
                        code="output_dir",
                        name="Output Directory",
                        type="directory",
                        required=0,
                    ),
                ],
            ),
        ],
    )


class TestSharedArgumentsBasicFlow:
    """Tests du flux de base des arguments partagés."""

    def test_apply_shared_arguments_propagates_values(self, task_with_shared_arguments):
        """Test que apply_shared_arguments propage les valeurs aux commandes."""
        task = task_with_shared_arguments

        # Appliquer les valeurs partagées
        shared_values = {"DATABASE_FILE": "data.db", "OUTPUT_DIR": "./results"}
        task.apply_shared_arguments(shared_values)

        # Vérifier que les valeurs ont été propagées
        import_cmd = task.commands[0]
        process_cmd = task.commands[1]

        assert import_cmd.get_argument_by_code("db_path").default == "data.db"
        assert import_cmd.get_argument_by_code("output").default == "./results"
        assert process_cmd.get_argument_by_code("database").default == "data.db"
        assert process_cmd.get_argument_by_code("output_dir").default == "./results"

    def test_apply_shared_arguments_with_empty_values(self, task_with_shared_arguments):
        """Test avec des valeurs vides."""
        task = task_with_shared_arguments

        shared_values = {"DATABASE_FILE": "", "OUTPUT_DIR": ""}
        task.apply_shared_arguments(shared_values)

        # Les valeurs ne devraient pas être propagées si vides
        import_cmd = task.commands[0]
        # La valeur par défaut de la commande devrait être préservée
        assert import_cmd.get_argument_by_code("db_path").default == ""

    def test_apply_shared_arguments_uses_task_defaults(
        self, task_with_shared_arguments
    ):
        """Test que les valeurs par défaut de la tâche sont utilisées."""
        task = task_with_shared_arguments

        # Ne pas fournir OUTPUT_DIR, devrait utiliser la valeur par défaut de la tâche
        shared_values = {"DATABASE_FILE": "data.db"}
        task.apply_shared_arguments(shared_values)

        # OUTPUT_DIR devrait utiliser sa valeur par défaut "./output"
        import_cmd = task.commands[0]
        process_cmd = task.commands[1]

        assert import_cmd.get_argument_by_code("output").default == "./output"
        assert process_cmd.get_argument_by_code("output_dir").default == "./output"


class TestSharedArgumentsPriority:
    """Tests de priorité des valeurs (tâche > commande)."""

    def test_task_value_overrides_command_default(self):
        """Test que la valeur de tâche écrase la valeur par défaut de commande."""
        task = Task(
            name="Test",
            description="Test",
            arguments=[
                TaskArgument(
                    code="SHARED",
                    name="Shared",
                    default="task_default",
                    values=[ArgumentValue(command="Command", argument="arg")],
                )
            ],
            commands=[
                Command(
                    name="Command",
                    description="Test",
                    command="test {arg}",
                    arguments=[
                        Argument(code="arg", name="Arg", default="command_default")
                    ],
                )
            ],
        )

        # Appliquer avec la valeur par défaut de la tâche
        task.apply_shared_arguments({"SHARED": "task_default"})

        # La valeur de la tâche devrait écraser celle de la commande
        assert task.commands[0].get_argument_by_code("arg").default == "task_default"

    def test_user_value_overrides_all_defaults(self):
        """Test que la valeur utilisateur écrase toutes les valeurs par défaut."""
        task = Task(
            name="Test",
            description="Test",
            arguments=[
                TaskArgument(
                    code="SHARED",
                    name="Shared",
                    default="task_default",
                    values=[ArgumentValue(command="Command", argument="arg")],
                )
            ],
            commands=[
                Command(
                    name="Command",
                    description="Test",
                    command="test {arg}",
                    arguments=[
                        Argument(code="arg", name="Arg", default="command_default")
                    ],
                )
            ],
        )

        # Appliquer avec une valeur utilisateur
        task.apply_shared_arguments({"SHARED": "user_value"})

        # La valeur utilisateur devrait être utilisée
        assert task.commands[0].get_argument_by_code("arg").default == "user_value"


class TestSharedArgumentsMultipleCommands:
    """Tests avec plusieurs commandes partageant des arguments."""

    def test_shared_argument_propagates_to_all_targets(self):
        """Test qu'un argument partagé se propage à toutes les commandes cibles."""
        task = Task(
            name="Test",
            description="Test",
            arguments=[
                TaskArgument(
                    code="SHARED",
                    name="Shared",
                    default="shared_value",
                    values=[
                        ArgumentValue(command="Command 1", argument="arg1"),
                        ArgumentValue(command="Command 2", argument="arg2"),
                        ArgumentValue(command="Command 3", argument="arg3"),
                    ],
                )
            ],
            commands=[
                Command(
                    name="Command 1",
                    description="Test",
                    command="test1 {arg1}",
                    arguments=[Argument(code="arg1", name="Arg1")],
                ),
                Command(
                    name="Command 2",
                    description="Test",
                    command="test2 {arg2}",
                    arguments=[Argument(code="arg2", name="Arg2")],
                ),
                Command(
                    name="Command 3",
                    description="Test",
                    command="test3 {arg3}",
                    arguments=[Argument(code="arg3", name="Arg3")],
                ),
            ],
        )

        task.apply_shared_arguments({"SHARED": "shared_value"})

        # Vérifier que toutes les commandes ont reçu la valeur
        assert task.commands[0].get_argument_by_code("arg1").default == "shared_value"
        assert task.commands[1].get_argument_by_code("arg2").default == "shared_value"
        assert task.commands[2].get_argument_by_code("arg3").default == "shared_value"

    def test_multiple_shared_arguments_to_same_command(self):
        """Test avec plusieurs arguments partagés vers la même commande."""
        task = Task(
            name="Test",
            description="Test",
            arguments=[
                TaskArgument(
                    code="SHARED1",
                    name="Shared 1",
                    default="value1",
                    values=[ArgumentValue(command="Command", argument="arg1")],
                ),
                TaskArgument(
                    code="SHARED2",
                    name="Shared 2",
                    default="value2",
                    values=[ArgumentValue(command="Command", argument="arg2")],
                ),
            ],
            commands=[
                Command(
                    name="Command",
                    description="Test",
                    command="test {arg1} {arg2}",
                    arguments=[
                        Argument(code="arg1", name="Arg1"),
                        Argument(code="arg2", name="Arg2"),
                    ],
                )
            ],
        )

        task.apply_shared_arguments({"SHARED1": "value1", "SHARED2": "value2"})

        # Les deux arguments devraient être propagés
        assert task.commands[0].get_argument_by_code("arg1").default == "value1"
        assert task.commands[0].get_argument_by_code("arg2").default == "value2"


class TestSharedArgumentsEdgeCases:
    """Tests des cas limites."""

    def test_apply_shared_arguments_with_no_task_arguments(self):
        """Test avec une tâche sans arguments partagés."""
        task = Task(
            name="Test",
            description="Test",
            arguments=[],
            commands=[
                Command(
                    name="Command", description="Test", command="test", arguments=[]
                )
            ],
        )

        # Ne devrait pas planter
        task.apply_shared_arguments({"NONEXISTENT": "value"})

    def test_apply_shared_arguments_with_nonexistent_command(self):
        """Test avec un argument ciblant une commande inexistante."""
        task = Task(
            name="Test",
            description="Test",
            arguments=[
                TaskArgument(
                    code="SHARED",
                    name="Shared",
                    default="value",
                    values=[
                        ArgumentValue(command="Nonexistent Command", argument="arg")
                    ],
                )
            ],
            commands=[
                Command(
                    name="Real Command",
                    description="Test",
                    command="test",
                    arguments=[],
                )
            ],
        )

        # Ne devrait pas planter
        task.apply_shared_arguments({"SHARED": "value"})

    def test_apply_shared_arguments_with_nonexistent_argument(self):
        """Test avec un argument ciblant un argument inexistant dans la commande."""
        task = Task(
            name="Test",
            description="Test",
            arguments=[
                TaskArgument(
                    code="SHARED",
                    name="Shared",
                    default="value",
                    values=[
                        ArgumentValue(command="Command", argument="nonexistent_arg")
                    ],
                )
            ],
            commands=[
                Command(
                    name="Command",
                    description="Test",
                    command="test {real_arg}",
                    arguments=[Argument(code="real_arg", name="Real Arg")],
                )
            ],
        )

        # Ne devrait pas planter
        task.apply_shared_arguments({"SHARED": "value"})

        # L'argument réel ne devrait pas être affecté
        assert task.commands[0].get_argument_by_code("real_arg").default == ""

    def test_apply_shared_arguments_multiple_times(self, task_with_shared_arguments):
        """Test d'applications successives d'arguments partagés."""
        task = task_with_shared_arguments

        # Première application
        task.apply_shared_arguments({"DATABASE_FILE": "data1.db"})
        assert task.commands[0].get_argument_by_code("db_path").default == "data1.db"

        # Deuxième application avec une valeur différente
        task.apply_shared_arguments({"DATABASE_FILE": "data2.db"})
        assert task.commands[0].get_argument_by_code("db_path").default == "data2.db"


class TestSharedArgumentsValidation:
    """Tests de validation avec arguments partagés."""

    def test_validate_task_with_shared_required_arguments(self):
        """Test de validation d'une tâche avec arguments partagés obligatoires."""
        task = Task(
            name="Test",
            description="Test",
            arguments=[
                TaskArgument(
                    code="REQUIRED_SHARED",
                    name="Required Shared",
                    required=1,
                    values=[ArgumentValue(command="Command", argument="arg")],
                )
            ],
            commands=[
                Command(
                    name="Command",
                    description="Test",
                    command="test {arg}",
                    arguments=[Argument(code="arg", name="Arg", required=1)],
                )
            ],
        )

        # Sans valeur
        is_valid, errors = task.validate_arguments({"REQUIRED_SHARED": ""})
        assert not is_valid
        assert len(errors) > 0

        # Avec valeur
        is_valid, errors = task.validate_arguments({"REQUIRED_SHARED": "value"})
        assert is_valid
        assert len(errors) == 0
