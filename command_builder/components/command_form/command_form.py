"""
Module contenant la classe CommandForm qui représente le formulaire de commande.
"""

from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from command_builder.components.argument_component import ArgumentComponent
from command_builder.components.command_component import CommandComponent
from command_builder.models.arguments import Argument
from command_builder.models.command import Command
from command_builder.models.task import Task
from command_builder.services.command_builder_service import CommandBuilderService
from command_builder.services.command_validator import CommandValidator
from command_builder.services.form_state_manager import FormStateManager


class CommandForm(QWidget):
    """
    Classe représentant le composant de formulaire de commande.
    Ce composant permet de configurer les paramètres d'une commande.

    Cette classe est découplée de CommandComponent grâce à l'injection de dépendances.
    """

    # Signal émis lorsque le formulaire est complété
    form_completed = Signal(dict)  # Dictionnaire des valeurs du formulaire
    # Signal émis lorsque les commandes doivent être exécutées
    commands_to_execute = Signal(list)  # Liste des commandes à exécuter
    # Signal émis quand une tâche est chargée (pour activer le bouton Exécuter)
    task_loaded = Signal()

    def __init__(
        self,
        parent=None,
        command_widget_factory: Optional[
            Callable[[Command, QWidget, bool], QWidget]
        ] = None,
    ):
        """
        Initialise le composant CommandForm.

        Args:
            parent: Le widget parent (par défaut: None)
            command_widget_factory: Fonction pour créer un widget de commande.
                                   Signature: (command: Command, parent: QWidget, simple_mode: bool) -> QWidget
                                   Si None, utilise CommandComponent par défaut.
        """
        super().__init__(parent)
        self.current_command = None
        self.current_commands = []  # Liste des commandes multiples
        self.current_task = None  # Tâche courante
        self.command_components = []  # Liste des CommandComponent
        self.command_checkboxes = []  # Liste des checkboxes pour activer/désactiver les commandes
        self.task_argument_components = []  # Liste des ArgumentComponent pour les arguments de tâche
        self.shared_argument_values = {}  # Valeurs des arguments partagés
        self._state_manager = FormStateManager()  # Gestionnaire d'état du formulaire
        self._command_widget_factory = (
            command_widget_factory or self._default_command_widget_factory
        )
        self._load_ui()
        self._load_stylesheet()

    def _default_command_widget_factory(
        self, command: Command, parent: QWidget, simple_mode: bool = False
    ) -> QWidget:
        """Factory par défaut pour créer un CommandComponent."""
        return CommandComponent(command, parent, simple_mode)

    def _load_ui(self):
        """Charge le fichier UI du composant."""
        current_dir = Path(__file__).parent
        ui_file = current_dir / "command_form.ui"

        loader = QUiLoader()
        ui = loader.load(str(ui_file), self)

        # Configurer le layout pour inclure l'UI chargée
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui)
        self.setLayout(layout)

        # Créer un scroll area pour le formulaire
        self.scroll_area = QScrollArea(ui)
        self.scroll_area.setMinimumHeight(0)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")

        # Créer un conteneur pour le formulaire
        self.form_container = QWidget()
        self.form_container.setObjectName("formContainer")

        # Créer un layout vertical pour les CommandComponent
        self.commands_layout = QVBoxLayout(self.form_container)
        self.commands_layout.setContentsMargins(10, 10, 10, 10)
        self.commands_layout.setSpacing(10)
        self.commands_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Ajouter le conteneur au scroll area
        self.scroll_area.setWidget(self.form_container)

        # Ajouter le scroll area au layout principal
        main_layout = ui.layout()
        if main_layout:
            main_layout.addWidget(self.scroll_area)

        # Afficher le message d'accueil initial
        self._show_welcome_message()

    def _show_welcome_message(self):
        """Affiche un message d'accueil quand aucune tâche n'est sélectionnée."""
        # Créer un conteneur centré
        welcome_widget = QWidget()
        welcome_widget.setObjectName("welcomeWidget")
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.setSpacing(15)

        # Icône ou emoji
        icon_label = QLabel("📋")
        icon_label.setStyleSheet("font-size: 30px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(icon_label)

        # Message principal
        title_label = QLabel("Sélectionnez une tâche")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4a90e2;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(title_label)

        # Message secondaire
        subtitle_label = QLabel(
            "Choisissez une tâche dans la liste à gauche\npour configurer et exécuter ses commandes."
        )
        subtitle_label.setStyleSheet("font-size: 12px; color: #888888;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(subtitle_label)

        # Ajouter au layout principal
        self.commands_layout.addWidget(welcome_widget)
        self.commands_layout.addStretch()

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "command_form.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
                # Stocker le stylesheet pour l'appliquer aux dialogs
                self._stylesheet = stylesheet
        else:
            self._stylesheet = ""

    def _save_current_values(self):
        """
        Sauvegarde les valeurs actuelles dans le cache avant de changer de tâche.
        Délègue au FormStateManager.
        """
        if not self.current_task:
            return

        self._state_manager.save_state(
            task_name=self.current_task.name,
            task_argument_components=self.task_argument_components,
            command_components=self.command_components,
            command_checkboxes=self.command_checkboxes,
        )

    def _restore_cached_values(self):
        """
        Restaure les valeurs depuis le cache après avoir chargé une tâche.
        Délègue au FormStateManager.
        """
        if not self.current_task:
            return

        # Restaurer les valeurs via le gestionnaire d'état
        restored_shared_values = self._state_manager.restore_state(
            task_name=self.current_task.name,
            task_argument_components=self.task_argument_components,
            command_components=self.command_components,
            command_checkboxes=self.command_checkboxes,
        )

        # Mettre à jour shared_argument_values avec les valeurs restaurées
        self.shared_argument_values.update(restored_shared_values)

        # Propager les valeurs partagées aux commandes
        if self.shared_argument_values and self.current_task:
            self.current_task.apply_shared_arguments(self.shared_argument_values)
            self._refresh_command_displays()

    def set_task(self, task: Task):
        """
        Configure le formulaire pour afficher une tâche complète avec ses arguments partagés.

        Args:
            task: La tâche à afficher
        """
        # Sauvegarder les valeurs de la tâche actuelle avant de changer
        self._save_current_values()

        self.current_task = task
        self.current_commands = task.commands
        self.current_command = None
        self.shared_argument_values = {}

        # Effacer le formulaire actuel
        self._clear_form()

        if not task.commands or len(task.commands) == 0:
            return

        # Initialiser les valeurs partagées avec les valeurs par défaut des arguments de tâche
        if task.arguments:
            for task_arg in task.arguments:
                if task_arg.default:
                    self.shared_argument_values[task_arg.code] = task_arg.default

        # Appliquer les valeurs par défaut aux commandes (priorité tâche > commande)
        if self.shared_argument_values:
            task.apply_shared_arguments(self.shared_argument_values)

        # Titre de la tâche
        task_label = QLabel(task.name)
        task_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.commands_layout.addWidget(task_label)

        # Afficher les arguments partagés de la tâche (s'il y en a)
        if task.arguments and len(task.arguments) > 0:
            self._add_shared_arguments_section(task.arguments)

        # Afficher les commandes
        for i, command in enumerate(task.commands, 1):
            # Créer un layout vertical pour chaque commande (titre + contenu)
            command_container_layout = QVBoxLayout()
            command_container_layout.setSpacing(5)

            # Créer un layout horizontal pour le titre (checkbox + numéro + nom)
            title_layout = QHBoxLayout()
            title_layout.setSpacing(10)

            # Créer une checkbox pour activer/désactiver la commande
            checkbox = QCheckBox()
            checkbox.setChecked(True)  # Cochée par défaut
            checkbox.setToolTip(
                "Décochez pour ignorer cette commande lors de l'exécution"
            )
            checkbox.setStyleSheet("QCheckBox { font-size: 12px; }")
            self.command_checkboxes.append(checkbox)
            title_layout.addWidget(checkbox)

            # Créer un label pour le numéro et le nom
            title_label = QLabel(f"{i}. {command.name}")
            title_label.setStyleSheet(
                "font-size: 12px; color: #ffffff ; font-weight: bold;"
            )
            title_layout.addWidget(title_label)
            title_layout.addStretch()

            command_container_layout.addLayout(title_layout)

            # Utiliser la factory pour créer le widget de commande en mode simple
            command_widget = self._command_widget_factory(
                command, self, simple_mode=True
            )
            self.command_components.append(command_widget)
            command_container_layout.addWidget(command_widget)

            # Ajouter le layout de la commande au layout vertical principal
            self.commands_layout.addLayout(command_container_layout)

        # Ajouter un spacer à la fin
        self.commands_layout.addStretch()

        # Restaurer les valeurs depuis le cache si disponibles
        self._restore_cached_values()

        # Émettre le signal pour activer le bouton Exécuter
        self.task_loaded.emit()

    def set_commands(self, commands, task_name=None):
        """
        Configure le formulaire pour afficher plusieurs commandes avec CommandComponent.
        (Méthode de compatibilité - préférer set_task)

        Args:
            commands: Liste des commandes à afficher
            task_name: Le nom de la tâche (optionnel)
        """
        self.current_commands = commands
        self.current_command = None
        self.current_task = None

        # Effacer le formulaire actuel
        self._clear_form()

        if not commands or len(commands) == 0:
            return

        # titre de la tâche
        if task_name:
            task_label = QLabel(task_name)
            task_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            self.commands_layout.addWidget(task_label)

        # Créer un widget de commande pour chaque commande
        for i, command in enumerate(commands, 1):
            # Créer un layout vertical pour chaque commande (titre + contenu)
            command_container_layout = QVBoxLayout()
            command_container_layout.setSpacing(5)

            # Créer un layout horizontal pour le titre (numéro + nom)
            title_layout = QHBoxLayout()
            title_layout.setSpacing(5)

            # Créer un label pour le numéro et le nom
            title_label = QLabel(f"{i}. {command.name}")
            title_label.setStyleSheet(
                "font-size: 12px; color: #a0a0a0; font-weight: bold;"
            )
            title_layout.addWidget(title_label)
            title_layout.addStretch()

            command_container_layout.addLayout(title_layout)

            # Utiliser la factory pour créer le widget de commande en mode simple
            command_widget = self._command_widget_factory(
                command, self, simple_mode=True
            )
            self.command_components.append(command_widget)
            command_container_layout.addWidget(command_widget)

            # Ajouter le layout de la commande au layout vertical principal
            self.commands_layout.addLayout(command_container_layout)

        # Ajouter un spacer à la fin
        self.commands_layout.addStretch()

    def _add_shared_arguments_section(self, task_arguments):
        """
        Ajoute une section pour les arguments partagés de la tâche.

        Args:
            task_arguments: Liste des TaskArgument
        """
        self._add_section_title("Arguments partagés")

        # Créer un widget pour chaque argument de tâche
        for task_arg in task_arguments:
            self._create_shared_argument_widget(task_arg)

        self._add_section_separator()
        self._add_section_title("Commandes")

    def _add_section_title(self, title: str):
        """
        Ajoute un titre de section.

        Args:
            title: Le texte du titre
        """
        label = QLabel(title)
        label.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #4a90e2; margin-top: 10px;"
        )
        self.commands_layout.addWidget(label)

    def _create_shared_argument_widget(self, task_arg):
        """
        Crée et ajoute un widget pour un argument partagé.

        Args:
            task_arg: L'argument de tâche (TaskArgument)
        """
        # Convertir TaskArgument en Argument
        arg = Argument(
            code=task_arg.code,
            name=task_arg.name,
            description=task_arg.description,
            type=task_arg.type,
            required=task_arg.required,
            default=task_arg.default,
            validation=task_arg.validation,
        )

        # Extraire les noms des commandes concernées
        affected_commands = [value.command for value in task_arg.values]

        # Créer le layout horizontal
        arg_layout = QHBoxLayout()
        arg_layout.setSpacing(10)

        # Créer le label
        arg_label = QLabel(f"{task_arg.name} :")
        arg_label.setObjectName(f"shared_label_{task_arg.code}")
        arg_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        arg_label.setMinimumWidth(200)
        arg_label.setMaximumWidth(200)
        arg_label.setStyleSheet("font-weight: normal;")

        # Créer le composant
        arg_component = ArgumentComponent(
            arg, self, affected_commands=affected_commands
        )

        # Connecter le signal
        def make_handler(lbl):
            return lambda code, value: self._on_shared_argument_changed(
                code, value, lbl
            )

        arg_component.value_changed.connect(make_handler(arg_label))

        # Appliquer le style initial si valeur par défaut
        if arg_component.has_default_value():
            self._apply_default_style(arg_label)

        # Stocker la référence
        self.task_argument_components.append(
            {"component": arg_component, "label": arg_label}
        )

        # Ajouter au layout
        arg_layout.addWidget(arg_label)
        arg_layout.addWidget(arg_component, 1)
        self.commands_layout.addLayout(arg_layout)

    def _add_section_separator(self):
        """Ajoute un séparateur visuel entre les sections."""
        separator = QLabel("―" * 50)
        separator.setStyleSheet("color: #e0e0e0; margin: 10px 0;")
        self.commands_layout.addWidget(separator)

    def _on_shared_argument_changed(self, code: str, value: str, label: QLabel):
        """
        Gère le changement de valeur d'un argument partagé.

        Args:
            code: Code de l'argument
            value: Nouvelle valeur
            label: Le label associé à l'argument
        """
        # Mettre à jour le style du label selon si la valeur est vide ou non
        for arg_data in self.task_argument_components:
            if arg_data["component"].get_argument().code == code:
                if arg_data["component"].has_default_value() and value:
                    self._apply_default_style(label)
                else:
                    self._remove_default_style(label)
                break

        # Stocker la valeur
        self.shared_argument_values[code] = value

        # Propager la valeur aux commandes concernées
        if self.current_task:
            self.current_task.apply_shared_arguments(self.shared_argument_values)
            # Rafraîchir l'affichage des commandes
            self._refresh_command_displays()

    def _clear_form(self):
        """
        Efface tous les CommandComponent du formulaire.
        """
        # Nettoyer les arguments de chaque CommandComponent avant de les supprimer
        for command_widget in self.command_components:
            if hasattr(command_widget, "remove_all_arguments"):
                command_widget.remove_all_arguments()

        # Supprimer tous les widgets et layouts du layout principal
        while self.commands_layout.count() > 0:
            item = self.commands_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Nettoyer les layouts imbriqués (comme les QHBoxLayout)
                self._clear_layout(item.layout())
                item.layout().deleteLater()
            elif item.spacerItem():
                # Supprimer le spacer
                pass

        # Vider les listes des composants
        self.command_components.clear()
        self.command_checkboxes.clear()
        self.task_argument_components.clear()

    def _refresh_command_displays(self):
        """
        Rafraîchit l'affichage des commandes après modification des arguments partagés.
        Met à jour en temps réel les valeurs dans les ArgumentComponent des commandes.
        """
        if not self.current_task:
            return

        # Pour chaque argument partagé modifié
        for task_arg_code, shared_value in self.shared_argument_values.items():
            # Trouver l'argument de tâche correspondant (méthode héritée de WithArguments)
            task_arg = self.current_task.get_argument_by_code(task_arg_code)
            if not task_arg:
                continue

            # Pour chaque cible (commande + argument)
            for target in task_arg.values:
                # Trouver le CommandComponent correspondant
                for command_widget in self.command_components:
                    if (
                        hasattr(command_widget, "command")
                        and command_widget.command.name == target.command
                    ):
                        # Trouver l'ArgumentComponent correspondant dans ce CommandComponent
                        if hasattr(command_widget, "argument_components"):
                            arg_data = command_widget.argument_components.get(
                                target.argument
                            )
                            if arg_data and hasattr(arg_data["component"], "set_value"):
                                # Mettre à jour la valeur en temps réel avec le flag is_default
                                arg_data["component"].set_value(
                                    shared_value, is_default=True
                                )
                        break

    def _clear_layout(self, layout):
        """
        Nettoie récursivement un layout et tous ses enfants.

        Args:
            layout: Le layout à nettoyer
        """
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                item.layout().deleteLater()

    def get_form_values(self):
        """
        Récupère les valeurs de tous les arguments de toutes les commandes.

        Returns:
            Un dictionnaire contenant les valeurs de tous les arguments
        """
        values = {}

        # Parcourir tous les widgets de commande
        for command_widget in self.command_components:
            # Récupérer les valeurs des arguments si le widget a cette méthode
            if hasattr(command_widget, "get_argument_values"):
                command_values = command_widget.get_argument_values()
                values.update(command_values)

        return values

    def _on_execute_clicked(self):
        """
        Gère le clic sur le bouton "Exécuter".
        Valide les arguments obligatoires puis exécute seulement les commandes cochées.
        
        Délègue la validation à CommandValidator et la construction à CommandBuilderService.
        """
        if not self.command_components:
            return

        # Valider tous les arguments obligatoires (délégué au service)
        is_valid, all_errors = CommandValidator.validate_commands(
            self.command_components,
            self.command_checkboxes,
        )

        # Si des erreurs ont été trouvées, afficher un message et ne pas exécuter
        if not is_valid:
            self._show_validation_errors(all_errors)
            return

        # Construire la liste des commandes cochées (délégué au service)
        commands_list = CommandBuilderService.build_commands_list(
            self.command_components,
            self.command_checkboxes,
        )

        # Vérifier qu'au moins une commande est cochée
        if not commands_list:
            self._show_no_command_selected_error()
            return

        # Émettre le signal pour exécuter les commandes cochées
        self.commands_to_execute.emit(commands_list)

    def _show_validation_errors(self, errors: list):
        """
        Affiche une boîte de dialogue avec les erreurs de validation.

        Args:
            errors: Liste des messages d'erreur
        """
        error_text = "\n".join(f"• {err}" for err in errors)
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Arguments manquants")
        msg_box.setText("Veuillez remplir tous les champs obligatoires :")
        msg_box.setInformativeText(error_text)
        msg_box.setStyleSheet(self._stylesheet)
        msg_box.exec()

    def _show_no_command_selected_error(self):
        """
        Affiche une boîte de dialogue indiquant qu'aucune commande n'est sélectionnée.
        """
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Aucune commande sélectionnée")
        msg_box.setText("Veuillez cocher au moins une commande à exécuter.")
        msg_box.setStyleSheet(self._stylesheet)
        msg_box.exec()

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
