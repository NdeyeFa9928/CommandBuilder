"""
Module contenant la classe ArgumentComponent qui représente un composant d'argument individuel.
"""

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from command_builder.models.arguments import Argument


class ArgumentComponent(QWidget):
    """
    Composant représentant un argument individuel.
    Affiche un champ de saisie pour l'argument avec un bouton de parcours optionnel.
    """

    # Signal émis lorsque la valeur de l'argument change
    value_changed = Signal(str, str)  # (code, value)

    def __init__(
        self,
        argument: Argument,
        parent=None,
        affected_commands: Optional[List[str]] = None,
    ):
        """
        Initialise le composant ArgumentComponent.

        Args:
            argument: L'objet Argument à afficher
            parent: Le widget parent (par défaut: None)
            affected_commands: Liste des noms de commandes concernées par cet argument (pour les arguments partagés)
        """
        super().__init__(parent)
        self.argument = argument
        self.affected_commands = affected_commands or []
        self._has_default_value = False
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
        self.checkbox = ui.findChild(QCheckBox, "checkBox")
        self.commands_label = ui.findChild(QLabel, "commandsLabel")

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "argument_component.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _setup_ui(self):
        """Configure l'interface utilisateur avec les données de l'argument."""
        arg_type = self.argument.type or "string"

        # Masquer/afficher les widgets selon le type
        if arg_type == "flag":
            # Pour les flags : checkbox visible, line_edit caché
            self.checkbox.setVisible(True)
            self.line_edit.setVisible(False)
            self.browse_button.setVisible(False)
            self.checkbox.setToolTip(f"Activer {self.argument.name}")
            # Cocher si une valeur par défaut existe
            if self.argument.default:
                self.checkbox.setChecked(True)
            self.checkbox.stateChanged.connect(self._on_checkbox_changed)
        elif arg_type == "valued_option":
            # Pour les options avec valeur : checkbox + line_edit visibles
            self.checkbox.setVisible(True)
            self.line_edit.setVisible(True)
            self.browse_button.setVisible(False)
            self.checkbox.setToolTip(f"Activer {self.argument.name}")
            # Cocher si une valeur par défaut existe
            if self.argument.default:
                self.checkbox.setChecked(True)
                self.line_edit.setText(self.argument.default)
                self._has_default_value = True
            self.line_edit.setPlaceholderText(
                self.argument.description or self.argument.name
            )
            self.checkbox.stateChanged.connect(self._on_checkbox_changed)
            self.line_edit.textChanged.connect(self._on_value_changed)
        else:
            # Type string/file : champ texte classique, pas de checkbox
            self.checkbox.setVisible(False)
            self.line_edit.setPlaceholderText(
                self.argument.description or self.argument.name
            )
            if self.argument.default:
                self.line_edit.setText(self.argument.default)
                self._has_default_value = True
            self.line_edit.textChanged.connect(self._on_value_changed)
            # Afficher le bouton parcourir pour les fichiers/dossiers
            if arg_type in ["file", "directory"]:
                self.browse_button.setVisible(True)
                self.browse_button.clicked.connect(self._on_browse_clicked)
            else:
                self.browse_button.setVisible(False)

        # Afficher les commandes concernées si disponibles
        if self.commands_label:
            if self.affected_commands:
                commands_text = f"Utilisé par : {', '.join(self.affected_commands)}"
                self.commands_label.setText(commands_text)
                self.commands_label.setVisible(True)
            else:
                self.commands_label.setVisible(False)

    def _on_value_changed(self, text: str):
        """Gère le changement de valeur dans le champ de saisie."""
        self.value_changed.emit(self.argument.code, text)

    def _on_checkbox_changed(self, state: int):
        """Gère le changement d'état de la checkbox."""
        arg_type = self.argument.type or "string"

        if arg_type == "flag":
            # Pour les flags, émettre la valeur définie ou "1" par défaut si coché
            if state:
                value = self.argument.value if self.argument.value else "1"
            else:
                value = ""
            self.value_changed.emit(self.argument.code, value)
        elif arg_type == "valued_option":
            # Pour les options avec valeur, émettre la valeur du champ si coché, "" si décoché
            if state and self.line_edit:
                self.value_changed.emit(self.argument.code, self.line_edit.text())
            else:
                self.value_changed.emit(self.argument.code, "")

    def _on_browse_clicked(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier ou dossier."""
        arg_type = self.argument.type or "string"
        
        if arg_type == "directory":
            # Pour les dossiers, utiliser getExistingDirectory
            path = QFileDialog.getExistingDirectory(
                self, 
                "Sélectionner un dossier",
                "",
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
            )
        else:
            # Pour les fichiers, utiliser getOpenFileName
            path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier")
        
        if path and self.line_edit:
            self.line_edit.setText(path)

    def get_value(self) -> str:
        """
        Retourne la valeur actuelle de l'argument.

        Returns:
            La valeur saisie
        """
        arg_type = self.argument.type or "string"

        if arg_type == "flag":
            # Pour les flags, retourner la valeur définie ou "1" par défaut si coché
            if self.checkbox and self.checkbox.isChecked():
                return self.argument.value if self.argument.value else "1"
            return ""
        elif arg_type == "valued_option":
            # Pour les options avec valeur, retourner le préfixe + valeur si la checkbox est cochée
            if self.checkbox and self.checkbox.isChecked() and self.line_edit:
                user_value = self.line_edit.text().strip()
                if user_value:
                    # Si un préfixe est défini dans argument.value, l'ajouter avant la valeur
                    prefix = self.argument.value if self.argument.value else ""
                    if prefix:
                        return f"{prefix} {user_value}"
                    return user_value
            return ""
        else:
            # Pour les types classiques, retourner le texte du champ
            return self.line_edit.text() if self.line_edit else ""

    def set_value(self, value: str, is_default: bool = False):
        """
        Définit la valeur de l'argument.

        Args:
            value: La valeur à définir
            is_default: Indique si la valeur est une valeur par défaut
        """
        arg_type = self.argument.type or "string"

        if arg_type == "flag":
            # Pour les flags, cocher/décocher la checkbox
            if self.checkbox:
                self.checkbox.setChecked(value in ["1", "true", "True"])
        elif arg_type == "valued_option":
            # Pour les options avec valeur, définir la valeur et cocher si non vide
            if self.line_edit:
                self.line_edit.setText(value)
            if self.checkbox:
                self.checkbox.setChecked(bool(value))
            self._has_default_value = is_default
        else:
            # Pour les types classiques
            if self.line_edit:
                self.line_edit.setText(value)
                self._has_default_value = is_default

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

    def has_default_value(self) -> bool:
        """
        Indique si l'argument a une valeur par défaut.

        Returns:
            True si l'argument a une valeur par défaut
        """
        return self._has_default_value
