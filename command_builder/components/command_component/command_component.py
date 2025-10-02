"""
Module contenant la classe CommandComponent qui représente un composant de commande individuel.
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader

from command_builder.models.command import Command
from command_builder.components.argument_component import ArgumentComponent


class CommandComponent(QWidget):
    """
    Composant représentant une commande individuelle.
    Affiche le nom, la description, la commande CLI et les arguments.
    """

    # Signal émis lorsque les arguments changent
    arguments_changed = Signal(dict)  # {code: value}

    def __init__(self, command: Command, parent=None):
        """
        Initialise le composant CommandComponent.

        Args:
            command: L'objet Command à afficher
            parent: Le widget parent (par défaut: None)
        """
        super().__init__(parent)
        self.command = command
        self.argument_components = {}  # {code: ArgumentComponent}
        self._load_ui()
        self._load_stylesheet()
        self._setup_ui()

    def _load_ui(self):
        """Charge le fichier UI du composant."""
        current_dir = Path(__file__).parent
        ui_file = current_dir / "command_component.ui"

        loader = QUiLoader()
        ui = loader.load(str(ui_file), self)

        # Configurer le layout pour inclure l'UI chargée
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui)
        self.setLayout(layout)

        # Stocker les références aux widgets importants
        self.label_command_name = ui.findChild(QLabel, "labelCommandName")
        self.label_command_description = ui.findChild(QLabel, "labelCommandDescription")
        self.label_command_cli = ui.findChild(QLabel, "labelCommandCli")
        self.arguments_form_layout = ui.findChild(QFormLayout, "argumentsFormLayout")

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "command_component.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _setup_ui(self):
        """Configure l'interface utilisateur avec les données de la commande."""
        # Mettre à jour les labels
        if self.label_command_name:
            self.label_command_name.setText(self.command.name)

        if self.label_command_description:
            self.label_command_description.setText(self.command.description)

        if self.label_command_cli:
            self.label_command_cli.setText(f"Commande: {self.command.command}")

        # Ajouter les arguments
        if self.arguments_form_layout and self.command.arguments:
            for argument in self.command.arguments:
                self._add_argument(argument)

    def _add_argument(self, argument):
        """
        Ajoute un argument au formulaire.

        Args:
            argument: L'objet Argument à ajouter
        """
        # Créer le label pour l'argument
        label = QLabel(f"{argument.name}:")
        label.setObjectName(f"label_{argument.code}")

        # Créer le composant d'argument
        arg_component = ArgumentComponent(argument, self)
        arg_component.value_changed.connect(self._on_argument_changed)

        # Stocker la référence
        self.argument_components[argument.code] = arg_component

        # Ajouter au formulaire
        if self.arguments_form_layout:
            self.arguments_form_layout.addRow(label, arg_component)

    def _on_argument_changed(self, code: str, value: str):
        """
        Gère le changement de valeur d'un argument.

        Args:
            code: Le code de l'argument
            value: La nouvelle valeur
        """
        # Émettre le signal avec tous les arguments
        self.arguments_changed.emit(self.get_argument_values())

    def get_argument_values(self) -> dict:
        """
        Retourne les valeurs de tous les arguments.

        Returns:
            Dictionnaire {code: value}
        """
        return {
            code: component.get_value()
            for code, component in self.argument_components.items()
        }

    def set_argument_value(self, code: str, value: str):
        """
        Définit la valeur d'un argument spécifique.

        Args:
            code: Le code de l'argument
            value: La valeur à définir
        """
        if code in self.argument_components:
            self.argument_components[code].set_value(value)

    def get_command(self) -> Command:
        """
        Retourne l'objet Command associé à ce composant.

        Returns:
            L'objet Command
        """
        return self.command

    def clear_arguments(self):
        """Efface toutes les valeurs des arguments."""
        for component in self.argument_components.values():
            component.set_value("")
