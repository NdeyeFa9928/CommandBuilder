"""
Module contenant la classe CommandComponent qui représente un composant de commande individuel.
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout
from PySide6.QtCore import Signal, Qt
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

    def __init__(self, command: Command, parent=None, simple_mode=False):
        """
        Initialise le composant CommandComponent.

        Args:
            command: L'objet Command à afficher
            parent: Le widget parent (par défaut: None)
            simple_mode: Si True, affiche uniquement le texte de la commande
        """
        super().__init__(parent)
        self.command = command
        self.simple_mode = simple_mode
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
        self.arguments_container = ui.findChild(QWidget, "argumentsContainer")

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "command_component.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _setup_ui(self):
        """Configure l'interface utilisateur avec les données de la commande."""
        if self.simple_mode:
            # Mode simple : masquer le nom et la description (affichés ailleurs)
            if self.label_command_name:
                self.label_command_name.setVisible(False)
            if self.label_command_description:
                self.label_command_description.setVisible(False)

            # Afficher les arguments en mode simple
            if self.arguments_form_layout and self.command.arguments:
                for argument in self.command.arguments:
                    self._add_argument(argument)
            elif (
                self.arguments_form_layout and self.arguments_form_layout.parentWidget()
            ):
                # Pas d'arguments, masquer le conteneur
                self.arguments_form_layout.parentWidget().setVisible(False)
            
            # Afficher le code de la commande en vert après les arguments
            if self.label_command_cli:
                self._update_command_display()
        else:
            # Mode complet : afficher tout
            if self.label_command_name:
                self.label_command_name.setText(self.command.name)

            if self.label_command_description:
                self.label_command_description.setText(self.command.description)

            if self.label_command_cli:
                self._update_command_display()

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
        label = QLabel(f"{argument.name} :")
        label.setObjectName(f"label_{argument.code}")
        label.setWordWrap(False)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Forcer une taille fixe pour éviter les chevauchements
        label.setMinimumWidth(150)
        label.setMaximumWidth(150)
        label.setSizePolicy(
            label.sizePolicy().horizontalPolicy(), label.sizePolicy().verticalPolicy()
        )

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
        # Mettre à jour l'affichage de la commande
        self._update_command_display()

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

    def remove_all_arguments(self):
        """Supprime complètement tous les arguments du formulaire."""
        if self.arguments_form_layout:
            # Supprimer tous les widgets du QFormLayout
            while self.arguments_form_layout.count() > 0:
                item = self.arguments_form_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # Vider le dictionnaire des composants
        self.argument_components.clear()

    def _update_command_display(self):
        """Met à jour l'affichage de la commande avec les valeurs actuelles des arguments."""
        if not self.label_command_cli:
            return

        # Construire la commande complète
        full_command = self._build_full_command()

        # Mettre à jour le label selon le mode
        if self.simple_mode:
            # En mode simple, afficher le code en vert avec HTML
            styled_command = f'<span style="color: #4CAF50;">{full_command}</span>'
            self.label_command_cli.setText(styled_command)
        else:
            self.label_command_cli.setText(f"Commande: {full_command}")

    def _build_full_command(self) -> str:
        """
        Construit la commande complète avec les valeurs des arguments.

        Returns:
            La commande complète sous forme de chaîne
        """
        # Commencer avec la commande de base
        full_command = self.command.command

        # Remplacer chaque placeholder par sa valeur
        if self.command.arguments:
            for argument in self.command.arguments:
                # Récupérer la valeur actuelle de l'argument
                value = ""
                if argument.code in self.argument_components:
                    value = self.argument_components[argument.code].get_value()

                # Créer le placeholder
                placeholder = f"{{{argument.code}}}"

                # Remplacer le placeholder par la valeur ou un texte indicatif
                if value:
                    full_command = full_command.replace(placeholder, value)
                else:
                    # Afficher un placeholder stylisé si pas de valeur
                    display_placeholder = argument.name
                    full_command = full_command.replace(
                        placeholder, f"{{{display_placeholder}}}"
                    )

        return full_command
