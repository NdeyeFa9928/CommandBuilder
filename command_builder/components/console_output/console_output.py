"""
Module contenant la classe ConsoleOutput qui représente la sortie console.
"""

import datetime
import subprocess
from pathlib import Path

from PySide6.QtCore import QTimer, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from command_builder.services.command_executor import CommandExecutorService


class ConsoleOutput(QWidget):
    """
    Classe représentant le composant de sortie console.
    Ce composant affiche les résultats des commandes exécutées
    et gère leur exécution de manière autonome.
    """

    # Signal émis lorsque toutes les commandes sont terminées
    all_commands_finished = Signal()

    # Signal émis quand le bouton Exécuter est cliqué
    execute_requested = Signal()

    def __init__(self, parent=None):
        """
        Initialise le composant ConsoleOutput.

        Args:
            parent: Le widget parent (par défaut: None)
        """
        super().__init__(parent)
        self.executor_service = CommandExecutorService()
        self.commands_queue = []  # File d'attente des commandes à exécuter
        self.current_command_index = 0  # Index de la commande en cours
        self.command_start_time = None  # Timestamp de début de commande
        self._execution_start_time = None  # Timestamp de début d'exécution globale
        self._elapsed_timer = None  # Timer pour le chronomètre visuel
        self._hourglass_frames = ["⏳", "⌛"]  # Animation du sablier
        self._hourglass_index = 0
        self._load_ui()
        self._load_stylesheet()
        self._connect_signals()

    def _load_ui(self):
        """Charge le fichier UI du composant."""
        current_dir = Path(__file__).parent
        ui_file = current_dir / "console_output.ui"

        loader = QUiLoader()
        ui = loader.load(str(ui_file), self)

        # Configurer le layout pour inclure l'UI chargée
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui)
        self.setLayout(layout)

        # Stocker les références aux widgets importants
        self.text_edit_console = ui.findChild(QPlainTextEdit, "textEditConsole")
        self.button_execute = ui.findChild(QPushButton, "buttonExecute")
        self.button_stop = ui.findChild(QPushButton, "buttonStop")
        self.button_effacer = ui.findChild(QPushButton, "buttonEffacer")
        self.button_exporter = ui.findChild(QPushButton, "buttonExporter")
        self.label_timer = ui.findChild(QLabel, "labelTimer")

        # Effacer le texte de simulation
        self.text_edit_console.clear()

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "console_output.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _connect_signals(self):
        """Connecte les signaux aux slots."""
        self.button_execute.clicked.connect(self._on_execute_clicked)
        self.button_stop.clicked.connect(self._on_stop_clicked)
        self.button_effacer.clicked.connect(self.clear)
        self.button_exporter.clicked.connect(self.export_console)

    def _on_execute_clicked(self):
        """Gère le clic sur le bouton Exécuter."""
        self.execute_requested.emit()

    def set_execute_enabled(self, enabled: bool):
        """
        Active ou désactive le bouton Exécuter.

        Args:
            enabled: True pour activer, False pour désactiver
        """
        self.button_execute.setEnabled(enabled)

    def append_text(self, text):
        """
        Ajoute du texte à la console.

        Args:
            text: Le texte à ajouter
        """
        self.text_edit_console.appendPlainText(text)
        self.text_edit_console.verticalScrollBar().setValue(
            self.text_edit_console.verticalScrollBar().maximum()
        )

    def append_command(self, command):
        """
        Ajoute une commande à la console avec un préfixe.

        Args:
            command: La commande à ajouter
        """
        self.append_text(f"[CMD] {command}")

    def append_output(self, output):
        """
        Ajoute une sortie à la console avec un préfixe.

        Args:
            output: La sortie à ajouter
        """
        self.append_text(f"[OUT] {output}")

    def append_error(self, error):
        """
        Ajoute une erreur à la console avec un préfixe.

        Args:
            error: L'erreur à ajouter
        """
        self.append_text(f"[ERR] {error}")

    def clear(self):
        """Efface le contenu de la console."""
        self.text_edit_console.clear()

    def export_console(self):
        """Exporte le contenu de la console dans un fichier texte."""
        # Générer un nom de fichier par défaut avec la date et l'heure
        default_filename = (
            f"console_output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        # Ouvrir une boîte de dialogue pour choisir où enregistrer le fichier
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter la console", default_filename, "Fichiers texte (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.text_edit_console.toPlainText())
                self.append_text(f"[INFO] Console exportée vers {file_path}")
            except Exception as e:
                self.append_error(f"Erreur lors de l'exportation: {str(e)}")

    def _cleanup_orphan_processes(self, commands_list):
        """
        Tue les processus orphelins liés aux exécutables des commandes.
        
        Exclut les exécutables critiques (python, cmd, powershell) pour éviter
        de tuer l'application elle-même ou des shells système.
        """
        # Exécutables à ne JAMAIS tuer (risque de casser l'app ou le système)
        EXCLUSIONS = {"python.exe", "pythonw.exe", "cmd.exe", "powershell.exe", "pwsh.exe"}

        executables = set()
        for cmd_info in commands_list:
            command = cmd_info.get("command", "")
            parts = command.strip().split()

            if not parts:
                continue

            exe_name = parts[0]
            # Nettoyer le nom (enlever le chemin si présent)
            exe_name = exe_name.split("\\")[-1].split("/")[-1]

            # Ajouter .exe seulement si pas d'extension ET pas un script Python
            if not exe_name.lower().endswith(".exe") and "python" not in exe_name.lower():
                exe_name += ".exe"

            # Exclure les exécutables critiques
            if exe_name.lower() not in EXCLUSIONS:
                executables.add(exe_name)

        killed_any = False

        for exe in executables:
            try:
                result = subprocess.run(
                    ["taskkill", "/F", "/IM", exe],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.append_text(f"[CLEANUP] Processus {exe} arrêté")
                    killed_any = True
            except Exception:
                pass  # Ignorer les erreurs (processus non trouvé, etc.)

        if killed_any:
            self.append_text("")

    def execute_commands(self, commands_list):
        """
        Exécute toutes les commandes de la liste séquentiellement.

        Args:
            commands_list: Liste de dictionnaires avec 'name' et 'command'
        """
        if not commands_list:
            return

        # Nettoyer les processus orphelins avant de commencer
        self._cleanup_orphan_processes(commands_list)

        # Réinitialiser le flag d'arrêt
        self.executor_service.reset_stop_flag()

        # Initialiser la file d'attente
        self.commands_queue = commands_list
        self.current_command_index = 0

        # Gérer les états des boutons
        self.button_execute.setEnabled(False)  # Désactiver Exécuter
        self.button_stop.setEnabled(True)  # Activer Stop

        # Démarrer le chronomètre visuel
        self._start_elapsed_timer()

        # Afficher l'en-tête global avec timestamp de début
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.append_text("=" * 80)
        self.append_text(f"EXÉCUTION DES COMMANDES - Début: {start_time}")
        self.append_text("=" * 80)
        self.append_text(f"Nombre de commandes: {len(commands_list)}\n")

        # Exécuter la première commande
        self._execute_next_command()

    def _execute_next_command(self):
        """
        Exécute la prochaine commande dans la file d'attente.
        """
        # Vérifier si un arrêt a été demandé
        if self.executor_service.is_stop_requested():
            self._on_execution_stopped_by_user()
            return

        if self.current_command_index >= len(self.commands_queue):
            # Toutes les commandes ont été exécutées
            self._on_all_commands_finished()
            return

        # Récupérer la commande courante
        cmd_info = self.commands_queue[self.current_command_index]
        command = cmd_info["command"]
        name = cmd_info["name"]

        # Afficher l'en-tête de la commande avec timestamp
        start_time = datetime.datetime.now().strftime("%H:%M:%S")

        self.append_text("-" * 80)
        self.append_text(
            f"[{self.current_command_index + 1}/{len(self.commands_queue)}] {name}"
        )
        self.append_text(f"Heure de début: {start_time}")
        self.append_command(command)
        self.append_text("\nSortie:")

        # Stocker le timestamp de début
        self.command_start_time = datetime.datetime.now()

        # Exécuter la commande
        self.executor_service.execute_command(
            command,
            on_output=self._on_command_output,
            on_error=lambda line: self.append_error(line),
            on_finished=lambda code: self._on_single_command_finished(code),
        )

    def _on_command_output(self, line: str):
        """
        Gère la réception d'une ligne de sortie.
        """
        self.append_text(line)

    def _start_elapsed_timer(self):
        """Démarre le chronomètre visuel."""
        self._stop_elapsed_timer()
        self._execution_start_time = datetime.datetime.now()
        self._hourglass_index = 0
        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.timeout.connect(self._update_elapsed_display)
        self._elapsed_timer.start(1000)  # Mettre à jour chaque seconde
        # Afficher immédiatement
        self._update_elapsed_display()

    def _stop_elapsed_timer(self):
        """Arrête le chronomètre visuel (garde le temps affiché)."""
        if self._elapsed_timer is not None:
            self._elapsed_timer.stop()
            self._elapsed_timer.deleteLater()
            self._elapsed_timer = None
        # Ne pas réinitialiser le label - l'utilisateur peut voir le temps total

    def _reset_timer_display(self):
        """Réinitialise l'affichage du timer à 00:00."""
        if self.label_timer:
            self.label_timer.setText("⏳ 00:00")

    def _update_elapsed_display(self):
        """Met à jour l'affichage du chronomètre."""
        if self._execution_start_time is None:
            return

        # Calculer le temps écoulé
        elapsed = datetime.datetime.now() - self._execution_start_time
        total_seconds = int(elapsed.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        # Alterner le sablier pour l'animation
        hourglass = self._hourglass_frames[self._hourglass_index]
        self._hourglass_index = (self._hourglass_index + 1) % len(
            self._hourglass_frames
        )

        # Mettre à jour le label
        if self.label_timer:
            self.label_timer.setText(f"{hourglass} {minutes:02d}:{seconds:02d}")

    def _on_single_command_finished(self, return_code: int):
        """
        Appelé lorsqu'une commande individuelle est terminée.

        Args:
            return_code: Le code de retour de la commande
        """

        # Calculer la durée d'exécution
        end_time = datetime.datetime.now()
        duration = (end_time - self.command_start_time).total_seconds()
        end_time_str = end_time.strftime("%H:%M:%S")

        # Afficher le résultat
        self.append_text("")
        self.append_text(f"Heure de fin: {end_time_str}")
        self.append_text(f"Durée: {duration:.2f}s")

        if return_code == 0:
            self.append_text("✓ Succès")
            # Passer à la commande suivante
            self.current_command_index += 1
            self._execute_next_command()
        else:
            self.append_error(f"✗ Erreur (code {return_code})")
            # Arrêter l'exécution en cas d'erreur
            self._on_execution_stopped_with_error()

    def _on_execution_stopped_with_error(self):
        """
        Appelé lorsque l'exécution s'arrête en raison d'une erreur.
        """
        # Arrêter le chronomètre visuel
        self._stop_elapsed_timer()

        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.append_text("")
        self.append_text("=" * 80)
        self.append_text(f"EXÉCUTION ARRÊTEE - Erreur détectée - Fin: {end_time}")
        self.append_text(
            f"Commandes non exécutées: {len(self.commands_queue) - self.current_command_index - 1}"
        )
        self.append_text("=" * 80 + "\n")

        # Réactiver le bouton Exécuter et désactiver Stop
        self.button_execute.setEnabled(True)
        self.button_stop.setEnabled(False)

        # Émettre le signal
        self.all_commands_finished.emit()

    def _on_all_commands_finished(self):
        """
        Appelé lorsque toutes les commandes ont été exécutées.
        """
        # Arrêter le chronomètre visuel
        self._stop_elapsed_timer()

        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.append_text("=" * 80)
        self.append_text(f"TOUTES LES COMMANDES TERMINÉES - Fin: {end_time}")
        self.append_text("=" * 80 + "\n")

        # Réactiver le bouton Exécuter et désactiver Stop
        self.button_execute.setEnabled(True)
        self.button_stop.setEnabled(False)

        # Émettre le signal
        self.all_commands_finished.emit()

    def _on_execution_stopped_by_user(self):
        """
        Appelé lorsque l'utilisateur arrête manuellement l'exécution.
        """
        # Arrêter le chronomètre visuel
        self._stop_elapsed_timer()

        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.append_text("")
        self.append_text("=" * 80)
        self.append_text(f"EXÉCUTION ARRÊTÉE PAR L'UTILISATEUR - Fin: {end_time}")
        self.append_text(
            f"Commandes non exécutées: {len(self.commands_queue) - self.current_command_index}"
        )
        self.append_text("=" * 80 + "\n")

        # Réactiver le bouton Exécuter et désactiver Stop
        self.button_execute.setEnabled(True)
        self.button_stop.setEnabled(False)

        # Émettre le signal
        self.all_commands_finished.emit()

    def _on_stop_clicked(self):
        """
        Appelé lorsque l'utilisateur clique sur le bouton Stop.
        """
        self.append_text("\n[STOP] Arrêt demandé par l'utilisateur...")
        self.executor_service.request_stop()
