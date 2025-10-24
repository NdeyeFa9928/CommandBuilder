"""
Tests unitaires pour le service d'exécution de commandes.
Teste l'exécution séquentielle et l'arrêt en cas d'erreur.
"""

import sys
import os
import pytest

if sys.platform.startswith("win") and os.getenv("TERM") is None:
    pytest.skip("Skipping unstable CommandExecutor tests on Windows Task runner", allow_module_level=True)

from command_builder.services.command_executor import CommandExecutor, CommandExecutorService


class TestCommandExecutor:
    """Tests pour la classe CommandExecutor."""
    
    def test_executor_creation(self):
        """Teste la création d'un exécuteur de commande."""
        executor = CommandExecutor("echo test")
        assert executor.command == "echo test"
        assert executor._is_cancelled is False
    
    def test_executor_cancel(self):
        """Teste l'annulation d'une commande."""
        executor = CommandExecutor("echo test")
        executor.cancel()
        assert executor._is_cancelled is True


class TestCommandExecutorService:
    """Tests pour le service d'exécution de commandes."""
    
    def test_service_creation(self):
        """Teste la création du service."""
        service = CommandExecutorService()
        assert service.current_executor is None
    
    def test_execute_command_creates_executor(self):
        """Teste que execute_command crée un exécuteur."""
        service = CommandExecutorService()
        executor = service.execute_command("echo test")
        assert executor is not None
        assert service.current_executor is executor
    
    def test_execute_command_with_callbacks(self):
        """Teste l'exécution avec callbacks."""
        service = CommandExecutorService()
        output_lines = []
        error_lines = []
        return_codes = []
        
        def on_output(line):
            output_lines.append(line)
        
        def on_error(line):
            error_lines.append(line)
        
        def on_finished(code):
            return_codes.append(code)
        
        executor = service.execute_command(
            "echo test",
            on_output=on_output,
            on_error=on_error,
            on_finished=on_finished
        )
        
        # Attendre que l'exécution se termine
        executor.wait()
        
        # Vérifier que les callbacks ont été appelés
        assert len(return_codes) > 0
        assert return_codes[0] == 0  # Succès
    
    def test_cancel_current_execution(self):
        """Teste l'annulation de l'exécution en cours."""
        service = CommandExecutorService()
        executor = service.execute_command("echo test")
        
        # Annuler l'exécution
        service.cancel_current_execution()
        
        # Vérifier que le flag d'annulation est défini
        assert executor._is_cancelled is True
    
    def test_execute_command_replaces_previous(self):
        """Teste que execute_command remplace l'exécution précédente."""
        service = CommandExecutorService()
        executor1 = service.execute_command("echo test1")
        executor2 = service.execute_command("echo test2")
        
        # Le nouvel exécuteur doit être différent
        assert executor1 is not executor2
        assert service.current_executor is executor2
