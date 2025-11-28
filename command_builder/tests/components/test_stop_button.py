"""
Tests pour la fonctionnalité du bouton Stop dans ConsoleOutput.
"""

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication

from command_builder.components.console_output import ConsoleOutput


@pytest.fixture
def app():
    """Fixture pour créer une application Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def console_output(app):
    """Fixture pour créer un ConsoleOutput."""
    return ConsoleOutput()


class TestStopButton:
    """Tests pour le bouton Stop."""

    def test_stop_button_disabled_initially(self, console_output):
        """Le bouton Stop doit être désactivé initialement."""
        assert console_output.button_stop.isEnabled() is False

    def test_stop_button_enabled_during_execution(self, console_output):
        """Le bouton Stop doit être activé pendant l'exécution."""
        commands = [{"name": "Test", "command": "echo test"}]
        
        # Mock l'executor pour ne pas vraiment exécuter
        with patch.object(console_output.executor_service, 'execute_command'):
            console_output.execute_commands(commands)
            assert console_output.button_stop.isEnabled() is True

    def test_stop_button_disabled_after_completion(self, console_output):
        """Le bouton Stop doit être désactivé après la fin de l'exécution."""
        console_output.button_stop.setEnabled(True)
        console_output._on_all_commands_finished()
        assert console_output.button_stop.isEnabled() is False

    def test_stop_button_disabled_after_error(self, console_output):
        """Le bouton Stop doit être désactivé après une erreur."""
        console_output.commands_queue = [{"name": "Test", "command": "echo test"}]
        console_output.current_command_index = 0
        console_output.button_stop.setEnabled(True)
        console_output._on_execution_stopped_with_error()
        assert console_output.button_stop.isEnabled() is False

    def test_stop_button_disabled_after_user_stop(self, console_output):
        """Le bouton Stop doit être désactivé après un arrêt utilisateur."""
        console_output.commands_queue = [{"name": "Test", "command": "echo test"}]
        console_output.current_command_index = 0
        console_output.button_stop.setEnabled(True)
        console_output._on_execution_stopped_by_user()
        assert console_output.button_stop.isEnabled() is False

    def test_stop_clicked_calls_request_stop(self, console_output):
        """Cliquer sur Stop doit appeler request_stop sur le service."""
        with patch.object(console_output.executor_service, 'request_stop') as mock_stop:
            console_output._on_stop_clicked()
            mock_stop.assert_called_once()

    def test_stop_clicked_appends_message(self, console_output):
        """Cliquer sur Stop doit afficher un message."""
        with patch.object(console_output.executor_service, 'request_stop'):
            console_output._on_stop_clicked()
            text = console_output.text_edit_console.toPlainText()
            assert "[STOP]" in text
            assert "Arrêt demandé" in text

    def test_execute_next_command_stops_if_requested(self, console_output):
        """_execute_next_command doit s'arrêter si stop_requested est True."""
        console_output.commands_queue = [{"name": "Test", "command": "echo test"}]
        console_output.current_command_index = 0
        console_output.executor_service._stop_requested = True
        
        with patch.object(console_output, '_on_execution_stopped_by_user') as mock_stopped:
            console_output._execute_next_command()
            mock_stopped.assert_called_once()

    def test_reset_stop_flag_on_new_execution(self, console_output):
        """Le flag d'arrêt doit être réinitialisé au début d'une nouvelle exécution."""
        console_output.executor_service._stop_requested = True
        commands = [{"name": "Test", "command": "echo test"}]
        
        with patch.object(console_output.executor_service, 'execute_command'):
            console_output.execute_commands(commands)
            assert console_output.executor_service.is_stop_requested() is False


class TestCommandExecutorServiceStop:
    """Tests pour les méthodes d'arrêt du CommandExecutorService."""

    def test_request_stop_sets_flag(self):
        """request_stop doit définir le flag _stop_requested."""
        from command_builder.services.command_executor import CommandExecutorService
        service = CommandExecutorService()
        
        service.request_stop()
        assert service.is_stop_requested() is True

    def test_reset_stop_flag_clears_flag(self):
        """reset_stop_flag doit réinitialiser le flag."""
        from command_builder.services.command_executor import CommandExecutorService
        service = CommandExecutorService()
        
        service._stop_requested = True
        service.reset_stop_flag()
        assert service.is_stop_requested() is False

    def test_request_stop_cancels_current_execution(self):
        """request_stop doit annuler l'exécution en cours."""
        from command_builder.services.command_executor import CommandExecutorService
        service = CommandExecutorService()
        
        # Mock un executor en cours
        mock_executor = MagicMock()
        mock_executor.isRunning.return_value = True
        service.current_executor = mock_executor
        
        service.request_stop()
        
        mock_executor.cancel.assert_called_once()
        mock_executor.wait.assert_called_once()
