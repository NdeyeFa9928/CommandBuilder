"""
Service d'exécution de commandes Windows.
"""

import subprocess
import time
import threading
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
        self._process = None  # Stocker le processus pour pouvoir le tuer de l'extérieur

    def run(self):
        """Exécute la commande dans un thread séparé."""
        process = None
        try:
            # Utiliser CP850 pour la console Windows (OEM)
            encoding = "cp850"

            # Créer le processus avec un nouveau groupe de processus pour pouvoir le tuer proprement
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding=encoding,
                errors="replace",
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
            
            # Stocker le processus pour pouvoir le tuer depuis cancel()
            self._process = process

            # Lire la sortie avec un thread séparé pour éviter le blocage
            def read_output():
                try:
                    for line in iter(process.stdout.readline, ''):
                        if self._is_cancelled:
                            break
                        if line:
                            self.output_received.emit(line.rstrip())
                except Exception:
                    pass

            # Démarrer le thread de lecture
            reader_thread = threading.Thread(target=read_output, daemon=True)
            reader_thread.start()

            # Attendre la fin du processus ou l'annulation
            while process.poll() is None:
                if self._is_cancelled:
                    self._kill_process(process)
                    break
                time.sleep(0.1)  # Vérifier toutes les 100ms

            # Attendre que le thread de lecture se termine
            reader_thread.join(timeout=0.5)

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
                self._kill_process(process)

    def _kill_process(self, process):
        """Tue le processus de manière forcée."""
        try:
            process.terminate()
            try:
                process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=0.5)
        except Exception:
            pass

    def cancel(self):
        """Annule l'exécution de la commande."""
        self._is_cancelled = True
        
        # Tuer le processus immédiatement
        if self._process is not None and self._process.poll() is None:
            self._kill_process(self._process)


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
            # Attendre avec timeout pour ne pas bloquer l'UI
            self.current_executor.wait(1000)  # Max 1 seconde

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
