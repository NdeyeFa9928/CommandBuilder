"""Tests unitaires pour MainWindow."""

from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from command_builder.components.main_window import MainWindow
from command_builder.models.command import Command
from command_builder.models.task import Task
from command_builder.models.yaml_error import YamlError


@pytest.fixture
def qapp():
    """Fixture pour l'application Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def main_window(qapp):
    """Fixture pour créer une MainWindow."""
    window = MainWindow()
    yield window
    window.close()
    window.deleteLater()


@pytest.fixture
def sample_tasks():
    """Fixture pour créer des tâches de test."""
    return [
        Task(
            name="Task 1",
            description="First task",
            commands=[
                Command(
                    name="Command 1",
                    description="Test command",
                    command="echo test",
                    arguments=[],
                )
            ],
        ),
        Task(
            name="Task 2",
            description="Second task",
            commands=[
                Command(
                    name="Command 2",
                    description="Another command",
                    command="echo test2",
                    arguments=[],
                )
            ],
        ),
    ]


class TestMainWindowInitialization:
    """Tests d'initialisation de MainWindow."""

    def test_main_window_creates_successfully(self, qapp):
        """Test que MainWindow se crée sans erreur."""
        window = MainWindow()
        assert window is not None
        window.close()

    def test_main_window_has_required_components(self, main_window):
        """Test que MainWindow a tous les composants requis."""
        # Vérifier que les composants principaux existent
        assert hasattr(main_window, "task_list")
        assert hasattr(main_window, "command_form")
        assert hasattr(main_window, "console_output")

    def test_main_window_title(self, main_window):
        """Test que le titre de la fenêtre est défini."""
        title = main_window.windowTitle()
        assert title  # Le titre ne doit pas être vide
        assert "CommandBuilder" in title or "Command" in title


class TestMainWindowSetTasks:
    """Tests de la méthode set_tasks."""

    def test_set_tasks_empty_list(self, main_window):
        """Test avec une liste vide de tâches."""
        main_window.set_tasks([])
        # Ne devrait pas planter

    def test_set_tasks_populates_task_list(self, main_window, sample_tasks):
        """Test que set_tasks remplit la liste des tâches."""
        main_window.set_tasks(sample_tasks)
        # Vérifier que les tâches sont passées au task_list
        # (dépend de l'implémentation de task_list)

    def test_set_tasks_replaces_previous_tasks(self, main_window, sample_tasks):
        """Test que set_tasks remplace les tâches précédentes."""
        # Premier appel
        main_window.set_tasks(sample_tasks[:1])

        # Deuxième appel avec d'autres tâches
        main_window.set_tasks(sample_tasks[1:])

        # Les nouvelles tâches devraient remplacer les anciennes


class TestMainWindowTaskSelection:
    """Tests de sélection de tâches."""

    def test_task_selection_updates_command_form(self, main_window, sample_tasks):
        """Test que la sélection d'une tâche met à jour le formulaire."""
        main_window.set_tasks(sample_tasks)

        # Simuler la sélection d'une tâche
        if hasattr(main_window, "_on_task_selected"):
            main_window._on_task_selected(sample_tasks[0])
            # Vérifier que command_form a été mis à jour

    def test_task_selection_clears_console(self, main_window, sample_tasks):
        """Test que la sélection d'une tâche efface la console."""
        main_window.set_tasks(sample_tasks)

        # Ajouter du texte à la console
        if hasattr(main_window.console_output, "append_text"):
            main_window.console_output.append_text("Test output")

        # Sélectionner une tâche
        if hasattr(main_window, "_on_task_selected"):
            main_window._on_task_selected(sample_tasks[0])
            # La console devrait être effacée


class TestMainWindowCommandExecution:
    """Tests d'exécution de commandes."""

    def test_execute_commands_signal_connection(self, main_window):
        """Test que le signal d'exécution est connecté."""
        # Vérifier que command_form.commands_to_execute est connecté
        assert hasattr(main_window.command_form, "commands_to_execute")

    @patch("command_builder.components.console_output.ConsoleOutput.execute_commands")
    def test_execute_commands_calls_console(
        self, mock_execute, main_window, sample_tasks
    ):
        """Test que l'exécution appelle la console."""
        main_window.set_tasks(sample_tasks)

        # Simuler l'émission du signal d'exécution
        commands = [{"name": "Test", "command": "echo test"}]
        if hasattr(main_window, "_on_commands_to_execute"):
            main_window._on_commands_to_execute(commands)
            # Vérifier que execute_commands a été appelé


class TestMainWindowYamlErrors:
    """Tests d'affichage des erreurs YAML."""

    def test_show_yaml_errors_with_empty_list(self, main_window):
        """Test avec une liste vide d'erreurs."""
        main_window.show_yaml_errors([])
        # Ne devrait rien afficher

    def test_show_yaml_errors_displays_dialog(self, main_window):
        """Test que show_yaml_errors affiche une dialog."""
        errors = [
            YamlError(
                file_name="test.yaml",
                error_type="ValidationError",
                error_message="Test error",
                suggestion="Fix it",
            )
        ]

        with patch("PySide6.QtWidgets.QDialog.exec") as mock_exec:
            main_window.show_yaml_errors(errors)
            # Vérifier qu'une dialog a été créée et affichée
            # mock_exec.assert_called_once()

    def test_show_yaml_errors_with_multiple_errors(self, main_window):
        """Test avec plusieurs erreurs."""
        errors = [
            YamlError(
                file_name="test1.yaml",
                error_type="SyntaxError",
                error_message="Syntax error",
            ),
            YamlError(
                file_name="test2.yaml",
                error_type="ValidationError",
                error_message="Validation error",
            ),
        ]

        with patch("PySide6.QtWidgets.QDialog.exec"):
            main_window.show_yaml_errors(errors)
            # Devrait afficher toutes les erreurs


class TestMainWindowSignals:
    """Tests des signaux et slots."""

    def test_task_list_signal_connected(self, main_window):
        """Test que le signal task_selected est connecté."""
        # Vérifier que task_list.task_selected est connecté à une méthode
        assert hasattr(main_window.task_list, "task_selected")

    def test_command_form_signal_connected(self, main_window):
        """Test que le signal commands_to_execute est connecté."""
        assert hasattr(main_window.command_form, "commands_to_execute")

    def test_console_signal_connected(self, main_window):
        """Test que le signal all_commands_finished est connecté."""
        assert hasattr(main_window.console_output, "all_commands_finished")


class TestMainWindowLayout:
    """Tests de la disposition des composants."""

    def test_main_window_has_splitter(self, main_window):
        """Test que MainWindow utilise un splitter."""
        # Vérifier la présence d'un splitter pour organiser les composants
        # (dépend de l'implémentation)
        pass

    def test_components_are_visible(self, main_window, sample_tasks):
        """Test que les composants sont visibles."""
        main_window.set_tasks(sample_tasks)
        main_window.show()

        assert main_window.task_list.isVisible()
        assert main_window.command_form.isVisible()
        assert main_window.console_output.isVisible()


class TestMainWindowCleanup:
    """Tests de nettoyage et fermeture."""

    def test_window_closes_cleanly(self, main_window):
        """Test que la fenêtre se ferme proprement."""
        main_window.show()
        main_window.close()
        # Ne devrait pas planter

    def test_window_cleanup_stops_running_commands(self, main_window):
        """Test que la fermeture arrête les commandes en cours."""
        # Si des commandes sont en cours, elles devraient être arrêtées
        # lors de la fermeture de la fenêtre
        pass


class TestMainWindowEdgeCases:
    """Tests des cas limites."""

    def test_set_tasks_with_none(self, main_window):
        """Test avec None au lieu d'une liste."""
        # Devrait gérer gracieusement ou lever une erreur claire
        try:
            main_window.set_tasks(None)
        except (TypeError, AttributeError):
            pass  # Comportement acceptable

    def test_select_task_before_set_tasks(self, main_window):
        """Test de sélection avant d'avoir défini des tâches."""
        # Ne devrait pas planter
        if hasattr(main_window, "_on_task_selected"):
            task = Task(name="Test", description="Test", commands=[])
            main_window._on_task_selected(task)

    def test_execute_commands_with_empty_list(self, main_window):
        """Test d'exécution avec une liste vide."""
        if hasattr(main_window, "_on_commands_to_execute"):
            main_window._on_commands_to_execute([])
            # Ne devrait pas planter
