"""
Service d'exécution de commandes Windows.
"""

import subprocess
from typing import Optional, Callable
from PySide6.QtCore import QObject, Signal, QThread


class CommandExecutor(QThread):
    """
    Thread pour exécuter une commande de manière asynchrone.
    """

    # Signaux pour communiquer avec l'interface
    output_received = Signal(str)  # Sortie standard
    error_received = Signal(str)  # Sortie d'erreur
    execution_finished = Signal(int)  # Code de retour

    def __init__(self, command: str, parent: Optional[QObject] = None):
        """
        Initialise l'exécuteur de commande.

        Args:
            command: La commande à exécuter
            parent: Le QObject parent
        """
        super().__init__(parent)
        self.command = command
        self._is_cancelled = False

    def run(self):
        """Exécute la commande dans un thread séparé."""
        try:
            # Utiliser CP850 pour la console Windows (OEM)
            # CP850 est l'encodage standard de la console Windows française
            encoding = "cp850"

            # Exécuter la commande avec subprocess
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding=encoding,
                errors="replace",
            )

            # Lire la sortie ligne par ligne
            while True:
                if self._is_cancelled:
                    process.terminate()
                    break

                # Lire stdout
                output = process.stdout.readline()
                if output:
                    self.output_received.emit(output.rstrip())

                # Vérifier si le processus est terminé
                if output == "" and process.poll() is not None:
                    break

            # Lire les erreurs restantes
            stderr = process.stderr.read()
            if stderr:
                self.error_received.emit(stderr.rstrip())

            # Émettre le code de retour
            return_code = process.poll()
            self.execution_finished.emit(return_code if return_code is not None else 0)

        except Exception as e:
            self.error_received.emit(f"Erreur lors de l'exécution: {str(e)}")
            self.execution_finished.emit(-1)

    def cancel(self):
        """Annule l'exécution de la commande."""
        self._is_cancelled = True


class CommandExecutorService:
    """
    Service pour gérer l'exécution de commandes.
    """

    def __init__(self):
        """Initialise le service d'exécution."""
        self.current_executor: Optional[CommandExecutor] = None

    def execute_command(
        self,
        command: str,
        on_output: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_finished: Optional[Callable[[int], None]] = None,
    ) -> CommandExecutor:
        """
        Exécute une commande de manière asynchrone.

        Args:
            command: La commande à exécuter
            on_output: Callback appelé pour chaque ligne de sortie
            on_error: Callback appelé pour chaque ligne d'erreur
            on_finished: Callback appelé à la fin de l'exécution avec le code de retour

        Returns:
            L'instance de CommandExecutor créée
        """
        # Annuler l'exécution précédente si elle existe
        if self.current_executor and self.current_executor.isRunning():
            self.current_executor.cancel()
            self.current_executor.wait()

        # Créer un nouveau thread d'exécution
        self.current_executor = CommandExecutor(command)

        # Connecter les callbacks si fournis
        if on_output:
            self.current_executor.output_received.connect(on_output)
        if on_error:
            self.current_executor.error_received.connect(on_error)
        if on_finished:
            self.current_executor.execution_finished.connect(on_finished)

        # Démarrer l'exécution
        self.current_executor.start()

        return self.current_executor

    def cancel_current_execution(self):
        """Annule l'exécution en cours."""
        if self.current_executor and self.current_executor.isRunning():
            self.current_executor.cancel()
            self.current_executor.wait()
