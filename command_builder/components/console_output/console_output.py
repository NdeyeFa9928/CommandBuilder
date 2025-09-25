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
from PySide6.QtUiTools import QUiLoader


class ConsoleOutput(QWidget):
    """
    Classe représentant le composant de sortie console.
    Ce composant affiche les résultats des commandes exécutées.
    """

    def __init__(self, parent=None):
        """
        Initialise le composant ConsoleOutput.

        Args:
            parent: Le widget parent (par défaut: None)
        """
        super().__init__(parent)
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
