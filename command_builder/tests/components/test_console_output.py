"""
Tests unitaires pour le composant ConsoleOutput.
Teste l'exécution séquentielle des commandes et l'arrêt en cas d'erreur.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from command_builder.components.console_output.console_output import ConsoleOutput


@pytest.fixture
def qapp():
    """Fixture pour l'application Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def console_output(qapp):
    """Fixture pour le composant ConsoleOutput."""
    return ConsoleOutput()


class TestConsoleOutputSequentialExecution:
    """Tests pour l'exécution séquentielle des commandes."""

    def test_execute_commands_initializes_queue(self, console_output):
        """Teste que execute_commands initialise la file d'attente."""
        commands = [
            {"name": "cmd1", "command": "echo test1"},
            {"name": "cmd2", "command": "echo test2"},
        ]

        with patch.object(console_output, "_execute_next_command"):
            console_output.execute_commands(commands)

        assert console_output.commands_queue == commands
        assert console_output.current_command_index == 0

    def test_execute_commands_empty_list(self, console_output):
        """Teste que execute_commands gère une liste vide."""
        with patch.object(console_output, "_execute_next_command") as mock_execute:
            console_output.execute_commands([])

        mock_execute.assert_not_called()

    def test_execute_next_command_calls_executor(self, console_output):
        """Teste que _execute_next_command appelle le service d'exécution."""
        commands = [
            {"name": "cmd1", "command": "echo test1"},
        ]
        console_output.commands_queue = commands
        console_output.current_command_index = 0

        with patch.object(
            console_output.executor_service, "execute_command"
        ) as mock_execute:
            console_output._execute_next_command()

        mock_execute.assert_called_once()

    def test_execute_next_command_all_done(self, console_output):
        """Teste que _execute_next_command appelle _on_all_commands_finished quand c'est fini."""
        commands = [
            {"name": "cmd1", "command": "echo test1"},
        ]
        console_output.commands_queue = commands
        console_output.current_command_index = 1  # Index au-delà de la liste

        with patch.object(console_output, "_on_all_commands_finished") as mock_finished:
            console_output._execute_next_command()

        mock_finished.assert_called_once()


class TestConsoleOutputErrorHandling:
    """Tests pour la gestion des erreurs et l'arrêt en cas d'erreur."""

    def test_on_single_command_finished_success(self, console_output):
        """Teste que le succès continue avec la commande suivante."""
        commands = [
            {"name": "cmd1", "command": "echo test1"},
            {"name": "cmd2", "command": "echo test2"},
        ]
        console_output.commands_queue = commands
        console_output.current_command_index = 0
        console_output.command_start_time = __import__("datetime").datetime.now()

        with patch.object(console_output, "_execute_next_command") as mock_next:
            console_output._on_single_command_finished(0)  # Code de retour 0 = succès

        # Vérifier que l'index a été incrémenté
        assert console_output.current_command_index == 1
        # Vérifier que la commande suivante a été appelée
        mock_next.assert_called_once()

    def test_on_single_command_finished_error(self, console_output):
        """Teste que l'erreur arrête l'exécution."""
        commands = [
            {"name": "cmd1", "command": "echo test1"},
            {"name": "cmd2", "command": "echo test2"},
        ]
        console_output.commands_queue = commands
        console_output.current_command_index = 0
        console_output.command_start_time = __import__("datetime").datetime.now()

        with patch.object(
            console_output, "_on_execution_stopped_with_error"
        ) as mock_error:
            console_output._on_single_command_finished(1)  # Code de retour 1 = erreur

        # Vérifier que l'arrêt en cas d'erreur a été appelé
        mock_error.assert_called_once()

    def test_on_execution_stopped_with_error(self, console_output):
        """Teste que _on_execution_stopped_with_error émet le signal."""
        commands = [
            {"name": "cmd1", "command": "echo test1"},
            {"name": "cmd2", "command": "echo test2"},
            {"name": "cmd3", "command": "echo test3"},
        ]
        console_output.commands_queue = commands
        console_output.current_command_index = 1  # Erreur à la 2e commande

        signal_emitted = []
        console_output.all_commands_finished.connect(
            lambda: signal_emitted.append(True)
        )

        console_output._on_execution_stopped_with_error()

        # Vérifier que le signal a été émis
        assert len(signal_emitted) > 0
        # Vérifier que le texte contient le nombre de commandes non exécutées
        console_text = console_output.text_edit_console.toPlainText()
        assert "EXÉCUTION ARRÊTEE" in console_text
        assert "Commandes non exécutées: 1" in console_text

    def test_on_all_commands_finished(self, console_output):
        """Teste que _on_all_commands_finished émet le signal."""
        signal_emitted = []
        console_output.all_commands_finished.connect(
            lambda: signal_emitted.append(True)
        )

        console_output._on_all_commands_finished()

        # Vérifier que le signal a été émis
        assert len(signal_emitted) > 0
        # Vérifier que le texte contient le message de fin
        console_text = console_output.text_edit_console.toPlainText()
        assert "TOUTES LES COMMANDES TERMINÉES" in console_text


class TestConsoleOutputAppendMethods:
    """Tests pour les méthodes d'ajout de texte."""

    def test_append_text(self, console_output):
        """Teste l'ajout de texte simple."""
        console_output.append_text("Test message")
        assert "Test message" in console_output.text_edit_console.toPlainText()

    def test_append_command(self, console_output):
        """Teste l'ajout d'une commande."""
        console_output.append_command("echo test")
        text = console_output.text_edit_console.toPlainText()
        assert "[CMD]" in text
        assert "echo test" in text

    def test_append_error(self, console_output):
        """Teste l'ajout d'une erreur."""
        console_output.append_error("Erreur test")
        text = console_output.text_edit_console.toPlainText()
        assert "[ERR]" in text
        assert "Erreur test" in text

    def test_clear(self, console_output):
        """Teste l'effacement de la console."""
        console_output.append_text("Test message")
        assert len(console_output.text_edit_console.toPlainText()) > 0

        console_output.clear()
        assert console_output.text_edit_console.toPlainText() == ""
