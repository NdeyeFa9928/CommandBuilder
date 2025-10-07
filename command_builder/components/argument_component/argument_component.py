"""
Module contenant la classe ArgumentComponent qui représente un composant d'argument individuel.
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader

from command_builder.models.arguments import Argument


class ArgumentComponent(QWidget):
    """
    Composant représentant un argument individuel.
    Affiche un champ de saisie pour l'argument avec un bouton de parcours optionnel.
    """

    # Signal émis lorsque la valeur de l'argument change
    value_changed = Signal(str, str)  # (code, value)

    def __init__(self, argument: Argument, parent=None):
        """
        Initialise le composant ArgumentComponent.

        Args:
            argument: L'objet Argument à afficher
            parent: Le widget parent (par défaut: None)
        """
        super().__init__(parent)
        self.argument = argument
        self._load_ui()
        self._load_stylesheet()
        self._setup_ui()

    def _load_ui(self):
        """Charge le fichier UI du composant."""
        current_dir = Path(__file__).parent
        ui_file = current_dir / "argument_component.ui"

        loader = QUiLoader()
        ui = loader.load(str(ui_file), self)

        # Configurer le layout pour inclure l'UI chargée
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui)
        self.setLayout(layout)

        # Stocker les références aux widgets importants
        self.line_edit = ui.findChild(QLineEdit, "argumentLineEdit")
        self.browse_button = ui.findChild(QPushButton, "browseButton")

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "argument_component.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _setup_ui(self):
        """Configure l'interface utilisateur avec les données de l'argument."""
        if self.line_edit:
            self.line_edit.setPlaceholderText(
                self.argument.description or self.argument.name
            )
            self.line_edit.textChanged.connect(self._on_value_changed)

        # Par défaut, cacher le bouton de parcours (peut être activé selon le type)
        if self.browse_button:
            self.browse_button.setVisible(False)
            self.browse_button.clicked.connect(self._on_browse_clicked)

    def _on_value_changed(self, text: str):
        """Gère le changement de valeur dans le champ de saisie."""
        self.value_changed.emit(self.argument.code, text)

    def _on_browse_clicked(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier ou dossier."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier")
        if file_path and self.line_edit:
            self.line_edit.setText(file_path)

    def get_value(self) -> str:
        """
        Retourne la valeur actuelle de l'argument.

        Returns:
            La valeur saisie
        """
        return self.line_edit.text() if self.line_edit else ""

    def set_value(self, value: str):
        """
        Définit la valeur de l'argument.

        Args:
            value: La valeur à définir
        """
        if self.line_edit:
            self.line_edit.setText(value)

    def get_argument(self) -> Argument:
        """
        Retourne l'objet Argument associé à ce composant.

        Returns:
            L'objet Argument
        """
        return self.argument

    def enable_browse_button(self, enabled: bool = True):
        """
        Active ou désactive le bouton de parcours.

        Args:
            enabled: True pour activer, False pour désactiver
        """
        if self.browse_button:
            self.browse_button.setVisible(enabled)
