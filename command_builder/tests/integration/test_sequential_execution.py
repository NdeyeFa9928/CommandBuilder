"""Tests d'intégration pour l'exécution séquentielle des commandes.
Tests simples et robustes pour les éléments critiques.
"""

import sys
import os
import pytest

# Skip entirely on Windows PowerShell/Go-Task environment to éviter exit 255
if sys.platform.startswith("win") and os.getenv("TERM") is None:
    pytest.skip(
        "Skipping unstable PySide6 integration tests on Windows Task runner",
        allow_module_level=True,
    )

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")  # run Qt without GUI
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from command_builder.components.console_output.console_output import ConsoleOutput
from command_builder.services.command_executor import CommandExecutorService


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


class TestSequentialExecutionLogic:
    """Tests pour la logique d'exécution séquentielle."""

    def test_execute_commands_initializes_queue(self, console_output):
        """Teste que execute_commands initialise correctement la file."""
        commands = [
            {"name": "Cmd 1", "command": "echo test1"},
            {"name": "Cmd 2", "command": "echo test2"},
        ]

        with patch.object(console_output, "_execute_next_command"):
            console_output.execute_commands(commands)

        assert console_output.commands_queue == commands
        assert console_output.current_command_index == 0
        console_text = console_output.text_edit_console.toPlainText()
        assert "EXÉCUTION DES COMMANDES" in console_text
        assert "Nombre de commandes: 2" in console_text

    def test_on_command_success_increments_index(self, console_output):
        """Teste que le succès incrémente l'index."""
        commands = [{"name": "Cmd", "command": "echo test"}]
        console_output.commands_queue = commands
        console_output.current_command_index = 0
        console_output.command_start_time = __import__("datetime").datetime.now()

        with patch.object(console_output, "_execute_next_command"):
            console_output._on_single_command_finished(0)

        assert console_output.current_command_index == 1

    def test_on_command_error_stops_execution(self, console_output):
        """Teste que l'erreur arrête l'exécution."""
        commands = [{"name": "Cmd", "command": "echo test"}]
        console_output.commands_queue = commands
        console_output.current_command_index = 0
        console_output.command_start_time = __import__("datetime").datetime.now()

        with patch.object(
            console_output, "_on_execution_stopped_with_error"
        ) as mock_stop:
            console_output._on_single_command_finished(1)

        mock_stop.assert_called_once()

    def test_execution_stopped_with_error_shows_message(self, console_output):
        """Teste que le message d'arrêt est affiché."""
        commands = [
            {"name": "Cmd1", "command": "echo test1"},
            {"name": "Cmd2", "command": "echo test2"},
            {"name": "Cmd3", "command": "echo test3"},
        ]
        console_output.commands_queue = commands
        console_output.current_command_index = 1

        console_output._on_execution_stopped_with_error()

        console_text = console_output.text_edit_console.toPlainText()
        assert "EXÉCUTION ARRÊTEE" in console_text
        assert "Commandes non exécutées: 1" in console_text


class TestCommandExecutorServiceBasic:
    """Tests basiques pour le service d'exécution."""

    def test_service_creation(self):
        """Teste la création du service."""
        service = CommandExecutorService()
        assert service.current_executor is None

    def test_service_execute_command_creates_executor(self):
        """Teste que execute_command crée un exécuteur."""
        service = CommandExecutorService()
        executor = service.execute_command("echo test")

        assert executor is not None
        assert service.current_executor is executor
