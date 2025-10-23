"""
Module contenant la classe ConsoleOutput qui représente la sortie console.
"""

from pathlib import Path
import datetime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QFileDialog,
)
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader
from command_builder.services.command_executor import CommandExecutorService


class ConsoleOutput(QWidget):
    """
    Classe représentant le composant de sortie console.
    Ce composant affiche les résultats des commandes exécutées
    et gère leur exécution de manière autonome.
    """
    
    # Signal émis lorsque toutes les commandes sont terminées
    all_commands_finished = Signal()

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
        self.button_effacer = ui.findChild(QPushButton, "buttonEffacer")
        self.button_exporter = ui.findChild(QPushButton, "buttonExporter")

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
        self.button_effacer.clicked.connect(self.clear)
        self.button_exporter.clicked.connect(self.export_console)

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
    
    def execute_commands(self, commands_list):
        """
        Exécute toutes les commandes de la liste séquentiellement.
        
        Args:
            commands_list: Liste de dictionnaires avec 'name' et 'command'
        """
        if not commands_list:
            return
        
        # Initialiser la file d'attente
        self.commands_queue = commands_list
        self.current_command_index = 0
        
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
        if self.current_command_index >= len(self.commands_queue):
            # Toutes les commandes ont été exécutées
            self._on_all_commands_finished()
            return
        
        # Récupérer la commande courante
        cmd_info = self.commands_queue[self.current_command_index]
        command = cmd_info['command']
        name = cmd_info['name']
        
        # Afficher l'en-tête de la commande avec timestamp
        start_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        self.append_text("-" * 80)
        self.append_text(f"[{self.current_command_index + 1}/{len(self.commands_queue)}] {name}")
        self.append_text(f"Heure de début: {start_time}")
        self.append_command(command)
        self.append_text("\nSortie:")
        
        # Stocker le timestamp de début
        self.command_start_time = datetime.datetime.now()
        
        # Exécuter la commande
        self.executor_service.execute_command(
            command,
            on_output=lambda line: self.append_text(line),
            on_error=lambda line: self.append_error(line),
            on_finished=lambda code: self._on_single_command_finished(code)
        )
    
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
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.append_text("")
        self.append_text("=" * 80)
        self.append_text(f"EXÉCUTION ARRÊTEE - Erreur détectée - Fin: {end_time}")
        self.append_text(f"Commandes non exécutées: {len(self.commands_queue) - self.current_command_index - 1}")
        self.append_text("=" * 80 + "\n")
        
        # Émettre le signal
        self.all_commands_finished.emit()
    
    def _on_all_commands_finished(self):
        """
        Appelé lorsque toutes les commandes ont été exécutées.
        """
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.append_text("=" * 80)
        self.append_text(f"TOUTES LES COMMANDES TERMINÉES - Fin: {end_time}")
        self.append_text("=" * 80 + "\n")
        
        # Émettre le signal
        self.all_commands_finished.emit()
