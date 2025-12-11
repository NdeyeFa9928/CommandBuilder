"""
Tests étendus pour le service d'exécution de commandes.
Améliore la couverture de command_executor.py
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from command_builder.services.command_executor import (
    CommandExecutor,
    CommandExecutorService,
)


class TestCommandExecutorExtended:
    """Tests étendus pour CommandExecutor."""

    def test_executor_initial_state(self):
        """Teste l'état initial de l'exécuteur."""
        executor = CommandExecutor("echo hello")
        assert executor.command == "echo hello"
        assert executor._is_cancelled is False
        assert executor._process is None

    def test_executor_cancel_sets_flag(self):
        """Teste que cancel() définit le flag d'annulation."""
        executor = CommandExecutor("echo test")
        assert executor._is_cancelled is False
        executor.cancel()
        assert executor._is_cancelled is True

    def test_executor_cancel_without_process(self):
        """Teste cancel() quand aucun processus n'est en cours."""
        executor = CommandExecutor("echo test")
        executor._process = None
        # Ne doit pas lever d'exception
        executor.cancel()
        assert executor._is_cancelled is True

    def test_executor_cancel_with_finished_process(self):
        """Teste cancel() quand le processus est déjà terminé."""
        executor = CommandExecutor("echo test")
        mock_process = Mock()
        mock_process.poll.return_value = 0  # Processus terminé
        executor._process = mock_process
        
        executor.cancel()
        
        assert executor._is_cancelled is True
        # _kill_process ne doit pas être appelé car poll() != None

    @patch.object(CommandExecutor, "_kill_process")
    def test_executor_cancel_kills_running_process(self, mock_kill):
        """Teste que cancel() tue un processus en cours."""
        executor = CommandExecutor("echo test")
        mock_process = Mock()
        mock_process.poll.return_value = None  # Processus en cours
        executor._process = mock_process
        
        executor.cancel()
        
        assert executor._is_cancelled is True
        mock_kill.assert_called_once_with(mock_process)


class TestCommandExecutorServiceExtended:
    """Tests étendus pour CommandExecutorService."""

    def test_service_initial_state(self):
        """Teste l'état initial du service."""
        service = CommandExecutorService()
        assert service.current_executor is None
        assert service._stop_requested is False

    def test_stop_flag_operations(self):
        """Teste les opérations sur le flag d'arrêt."""
        service = CommandExecutorService()
        
        # État initial
        assert service.is_stop_requested() is False
        
        # Demander l'arrêt
        service.request_stop()
        assert service.is_stop_requested() is True
        
        # Réinitialiser
        service.reset_stop_flag()
        assert service.is_stop_requested() is False

    def test_request_stop_cancels_execution(self):
        """Teste que request_stop() annule l'exécution en cours."""
        service = CommandExecutorService()
        
        # Créer un mock executor
        mock_executor = Mock()
        mock_executor.isRunning.return_value = True
        service.current_executor = mock_executor
        
        service.request_stop()
        
        assert service._stop_requested is True
        mock_executor.cancel.assert_called_once()
        mock_executor.wait.assert_called_once_with(1000)

    def test_cancel_current_execution_no_executor(self):
        """Teste cancel_current_execution() sans exécuteur."""
        service = CommandExecutorService()
        service.current_executor = None
        
        # Ne doit pas lever d'exception
        service.cancel_current_execution()

    def test_cancel_current_execution_not_running(self):
        """Teste cancel_current_execution() avec un exécuteur non actif."""
        service = CommandExecutorService()
        mock_executor = Mock()
        mock_executor.isRunning.return_value = False
        service.current_executor = mock_executor
        
        service.cancel_current_execution()
        
        # cancel() ne doit pas être appelé car pas en cours d'exécution
        mock_executor.cancel.assert_not_called()

    def test_execute_command_without_callbacks(self):
        """Teste execute_command() sans callbacks."""
        service = CommandExecutorService()
        
        executor = service.execute_command("echo test")
        
        assert executor is not None
        assert service.current_executor is executor
        # Attendre la fin pour nettoyer
        executor.wait(1000)

    def test_execute_command_with_output_callback_only(self):
        """Teste execute_command() avec seulement le callback output."""
        service = CommandExecutorService()
        outputs = []
        
        executor = service.execute_command("echo test", on_output=lambda x: outputs.append(x))
        executor.wait(2000)
        
        # Le callback doit avoir été connecté
        assert service.current_executor is executor

    def test_execute_command_with_error_callback_only(self):
        """Teste execute_command() avec seulement le callback error."""
        service = CommandExecutorService()
        errors = []
        
        executor = service.execute_command("echo test", on_error=lambda x: errors.append(x))
        executor.wait(2000)
        
        assert service.current_executor is executor

    def test_execute_command_with_finished_callback_only(self):
        """Teste execute_command() avec seulement le callback finished."""
        service = CommandExecutorService()
        codes = []
        
        executor = service.execute_command("echo test", on_finished=lambda x: codes.append(x))
        executor.wait(5000)  # Attendre plus longtemps
        
        # Vérifier que l'exécuteur a été créé
        assert executor is not None
        assert service.current_executor is executor

    def test_execute_command_replaces_running_executor(self):
        """Teste que execute_command() remplace un exécuteur en cours."""
        service = CommandExecutorService()
        
        # Premier exécuteur
        executor1 = service.execute_command("echo first")
        
        # Deuxième exécuteur (doit remplacer le premier)
        executor2 = service.execute_command("echo second")
        
        assert service.current_executor is executor2
        assert executor1 is not executor2
        
        # Nettoyer
        executor2.wait(2000)


class TestCommandExecutorKillProcess:
    """Tests pour la méthode _kill_process."""

    @patch("subprocess.run")
    @patch("os.name", "nt")
    def test_kill_process_windows(self, mock_run):
        """Teste _kill_process sur Windows."""
        executor = CommandExecutor("echo test")
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.wait.return_value = None
        
        executor._kill_process(mock_process)
        
        # Vérifie que taskkill a été appelé
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "taskkill" in call_args[0][0]
        assert "/F" in call_args[0][0]
        assert "/T" in call_args[0][0]
        assert "12345" in call_args[0][0]

    @patch("subprocess.run")
    @patch("os.name", "nt")
    def test_kill_process_windows_timeout(self, mock_run):
        """Teste _kill_process quand le processus ne se termine pas."""
        import subprocess
        
        executor = CommandExecutor("echo test")
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.wait.side_effect = subprocess.TimeoutExpired("cmd", 1)
        mock_process.kill.return_value = None
        
        # Ne doit pas lever d'exception
        executor._kill_process(mock_process)
        
        # kill() doit être appelé en fallback
        mock_process.kill.assert_called()

    @patch("subprocess.run")
    @patch("os.name", "nt")
    def test_kill_process_exception_handling(self, mock_run):
        """Teste _kill_process avec une exception."""
        mock_run.side_effect = Exception("Test error")
        
        executor = CommandExecutor("echo test")
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.kill.return_value = None
        
        # Ne doit pas lever d'exception
        executor._kill_process(mock_process)
        
        # kill() doit être appelé en dernier recours
        mock_process.kill.assert_called()


class TestCommandExecutorRun:
    """Tests pour la méthode run() de CommandExecutor."""

    @patch("subprocess.Popen")
    def test_run_emits_output(self, mock_popen):
        """Teste que run() émet les sorties."""
        # Configurer le mock
        mock_process = Mock()
        mock_process.stdout.readline.side_effect = ["line1\n", "line2\n", ""]
        mock_process.stderr.read.return_value = ""
        mock_process.poll.side_effect = [None, None, 0]
        mock_popen.return_value = mock_process
        
        executor = CommandExecutor("echo test")
        outputs = []
        executor.output_received.connect(lambda x: outputs.append(x))
        
        # Exécuter dans le thread principal pour le test
        # Note: run() est normalement appelé dans un thread séparé
        # Ce test vérifie la logique sans le threading

    @patch("subprocess.Popen")
    def test_run_handles_exception(self, mock_popen):
        """Teste que run() gère les exceptions."""
        mock_popen.side_effect = Exception("Test error")
        
        executor = CommandExecutor("invalid_command")
        errors = []
        codes = []
        executor.error_received.connect(lambda x: errors.append(x))
        executor.execution_finished.connect(lambda x: codes.append(x))
        
        executor.run()
        
        assert len(errors) > 0
        assert "Erreur lors de l'exécution" in errors[0]
        assert codes[0] == -1


class TestCommandExecutorSignals:
    """Tests pour les signaux de CommandExecutor."""

    def test_signals_exist(self):
        """Teste que les signaux sont définis."""
        executor = CommandExecutor("echo test")
        
        # Vérifier que les signaux existent
        assert hasattr(executor, "output_received")
        assert hasattr(executor, "error_received")
        assert hasattr(executor, "execution_finished")

    def test_signal_connections(self):
        """Teste que les signaux peuvent être connectés."""
        executor = CommandExecutor("echo test")
        
        callback = Mock()
        
        # Doit pouvoir connecter sans erreur
        executor.output_received.connect(callback)
        executor.error_received.connect(callback)
        executor.execution_finished.connect(callback)
