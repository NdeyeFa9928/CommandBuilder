"""
Service d'exécution de commandes Windows.
"""

import subprocess
from typing import Callable, Optional

from PySide6.QtCore import QObject, QThread, Signal


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
        process = None
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
                    try:
                        process.terminate()
                        # Attendre un peu pour que le processus se termine proprement
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        # Si le processus ne se termine pas, le forcer
                        process.kill()
                    except Exception:
                        pass
                    break

                # Lire stdout
                try:
                    output = process.stdout.readline()
                    if output:
                        self.output_received.emit(output.rstrip())
                except Exception:
                    break

                # Vérifier si le processus est terminé
                if output == "" and process.poll() is not None:
                    break

            # Lire les erreurs restantes (seulement si pas annulé)
            if not self._is_cancelled:
                try:
                    stderr = process.stderr.read()
                    if stderr:
                        self.error_received.emit(stderr.rstrip())
                except Exception:
                    pass

            # Émettre le code de retour
            return_code = process.poll()
            if return_code is None:
                return_code = -1 if self._is_cancelled else 0
            self.execution_finished.emit(return_code)

        except Exception as e:
            self.error_received.emit(f"Erreur lors de l'exécution: {str(e)}")
            self.execution_finished.emit(-1)
        finally:
            # S'assurer que le processus est bien terminé
            if process is not None and process.poll() is None:
                try:
                    process.kill()
                except Exception:
                    pass

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
        self._stop_requested = False

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

    def request_stop(self):
        """
        Demande l'arrêt de toutes les exécutions en cours et futures.
        Cette méthode doit être appelée pour arrêter complètement l'exécution d'une séquence.
        """
        self._stop_requested = True
        self.cancel_current_execution()

    def is_stop_requested(self) -> bool:
        """
        Vérifie si un arrêt a été demandé.

        Returns:
            True si un arrêt a été demandé, False sinon
        """
        return self._stop_requested

    def reset_stop_flag(self):
        """Réinitialise le flag d'arrêt pour permettre de nouvelles exécutions."""
        self._stop_requested = False
