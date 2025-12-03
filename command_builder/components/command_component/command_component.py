"""
Module contenant la classe CommandComponent qui représente un composant de commande individuel.
"""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QTextEdit, QVBoxLayout, QWidget

from command_builder.components.argument_component import ArgumentComponent
from command_builder.models.command import Command


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

        # Rendre le label de commande cliquable
        if self.label_command_cli:
            self.label_command_cli.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_command_cli.mousePressEvent = self._on_command_clicked

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
        # Créer le label pour l'argument avec astérisque si obligatoire
        label_text = f"{argument.name} :"
        if argument.required == 1:
            label_text = f'{argument.name} :  <span style="color: #e74c3c; font-weight: bold;"> *</span>'

        label = QLabel(label_text)
        label.setObjectName(f"label_{argument.code}")
        label.setWordWrap(False)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        label.setTextFormat(Qt.TextFormat.RichText)  # Permettre le HTML

        # Forcer une taille fixe pour éviter les chevauchements
        label.setMinimumWidth(150)
        label.setMaximumWidth(150)
        label.setSizePolicy(
            label.sizePolicy().horizontalPolicy(), label.sizePolicy().verticalPolicy()
        )

        # Créer le composant d'argument
        arg_component = ArgumentComponent(argument, self)
        arg_component.value_changed.connect(
            lambda code, value: self._on_argument_changed(code, value, label)
        )

        # Stocker la référence avec le label
        self.argument_components[argument.code] = {
            "component": arg_component,
            "label": label,
        }

        # Appliquer le style initial si valeur par défaut
        if arg_component.has_default_value():
            self._apply_default_style(label)

        # Ajouter au formulaire
        if self.arguments_form_layout:
            self.arguments_form_layout.addRow(label, arg_component)

    def _on_argument_changed(self, code: str, value: str, label: QLabel):
        """
        Gère le changement de valeur d'un argument.

        Args:
            code: Le code de l'argument
            value: La nouvelle valeur
            label: Le label associé à l'argument
        """
        # Mettre à jour le style du label selon si la valeur est vide ou non
        if code in self.argument_components:
            arg_data = self.argument_components[code]
            if arg_data["component"].has_default_value() and value:
                self._apply_default_style(label)
            else:
                self._remove_default_style(label)

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
            code: arg_data["component"].get_value()
            for code, arg_data in self.argument_components.items()
        }

    def set_argument_value(self, code: str, value: str, is_default: bool = False):
        """
        Définit la valeur d'un argument spécifique.

        Args:
            code: Le code de l'argument
            value: La valeur à définir
            is_default: Indique si la valeur est une valeur par défaut
        """
        if code in self.argument_components:
            arg_data = self.argument_components[code]
            arg_data["component"].set_value(value, is_default)
            # Appliquer le style si c'est une valeur par défaut
            if is_default and value:
                self._apply_default_style(arg_data["label"])
            else:
                self._remove_default_style(arg_data["label"])

    def get_command(self) -> Command:
        """
        Retourne l'objet Command associé à ce composant.

        Returns:
            L'objet Command
        """
        return self.command

    def clear_arguments(self):
        """Efface toutes les valeurs des arguments."""
        for arg_data in self.argument_components.values():
            arg_data["component"].set_value("")
            self._remove_default_style(arg_data["label"])

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
        import re

        # Commencer avec la commande de base
        full_command = self.command.command

        # Remplacer chaque placeholder par sa valeur
        if self.command.arguments:
            for argument in self.command.arguments:
                # Récupérer la valeur actuelle de l'argument
                value = ""
                if argument.code in self.argument_components:
                    value = self.argument_components[argument.code][
                        "component"
                    ].get_value()

                # Créer le placeholder
                placeholder = f"{{{argument.code}}}"

                # Remplacer le placeholder par la valeur ou un texte indicatif
                if value:
                    full_command = full_command.replace(placeholder, value)
                else:
                    # Pour les options (flag ou valued_option), supprimer complètement le placeholder
                    # Pour les autres types, vérifier si l'argument est optionnel
                    arg_type = argument.type or "string"
                    if arg_type in ["flag", "valued_option"]:
                        # Pour flag et valued_option, supprimer seulement le placeholder
                        # (pour valued_option, le préfixe est déjà inclus dans la valeur retournée par get_value())
                        full_command = full_command.replace(placeholder, "")
                    elif argument.required == 0:
                        # Pour les arguments optionnels (required=0) vides, supprimer le placeholder
                        full_command = full_command.replace(placeholder, "")
                    else:
                        # Pour les arguments obligatoires vides, afficher un placeholder stylisé
                        display_placeholder = argument.name
                        full_command = full_command.replace(
                            placeholder, f"{{{display_placeholder}}}"
                        )

        # Nettoyer les espaces multiples consécutifs
        full_command = re.sub(r"\s+", " ", full_command).strip()

        return full_command

    def _apply_default_style(self, label: QLabel):
        """
        Applique le style pour indiquer une valeur par défaut.

        Args:
            label: Le label à styliser
        """
        label.setProperty("hasDefault", True)
        label.style().unpolish(label)
        label.style().polish(label)

    def _remove_default_style(self, label: QLabel):
        """
        Retire le style de valeur par défaut.

        Args:
            label: Le label à déstyliser
        """
        label.setProperty("hasDefault", False)
        label.style().unpolish(label)
        label.style().polish(label)

    def _on_command_clicked(self, event):
        """
        Affiche la commande complète dans une popup quand on clique dessus.
        """
        full_command = self._build_full_command()

        # Créer une dialog pour afficher la commande complète
        dialog = QDialog(self)
        dialog.setWindowTitle("Commande complète")
        dialog.setMinimumSize(600, 200)
        dialog.setMaximumSize(900, 400)

        layout = QVBoxLayout(dialog)

        # Utiliser un QTextEdit en lecture seule pour permettre la sélection
        text_edit = QTextEdit()
        text_edit.setPlainText(full_command)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                font-family: "Consolas", "Courier New", monospace;
                font-size: 12px;
                color: #58d68d;
                background-color: #1e2330;
                border: 1px solid #3a3f55;
                border-radius: 4px;
                padding: 10px;
            }
        """)

        layout.addWidget(text_edit)

        # Ajouter un label d'aide
        help_label = QLabel("💡 Vous pouvez sélectionner et copier le texte (Ctrl+C)")
        help_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(help_label)

        dialog.exec()
