"""
Module contenant la classe CommandForm qui représente le formulaire de commande.
"""

from pathlib import Path
from typing import Callable, Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QHBoxLayout,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtUiTools import QUiLoader

from command_builder.models.command import Command


class CommandForm(QWidget):
    """
    Classe représentant le composant de formulaire de commande.
    Ce composant permet de configurer les paramètres d'une commande.
    
    Cette classe est découplée de CommandComponent grâce à l'injection de dépendances.
    """

    # Signal émis lorsque le formulaire est complété
    form_completed = Signal(dict)  # Dictionnaire des valeurs du formulaire

    def __init__(
        self, 
        parent=None,
        command_widget_factory: Optional[Callable[[Command, QWidget, bool], QWidget]] = None
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
        self.command_components = []  # Liste des CommandComponent
        self._command_widget_factory = command_widget_factory or self._default_command_widget_factory
        self._load_ui()
        self._load_stylesheet()
    
    def _default_command_widget_factory(self, command: Command, parent: QWidget, simple_mode: bool = False) -> QWidget:
        """Factory par défaut pour créer un CommandComponent."""
        from command_builder.components.command_component import CommandComponent
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

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "command_form.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())


    def set_commands(self, commands, task_name=None):
        """
        Configure le formulaire pour afficher plusieurs commandes avec CommandComponent.

        Args:
            commands: Liste des commandes à afficher
            task_name: Le nom de la tâche (optionnel)
        """
        self.current_commands = commands
        self.current_command = None
        
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
            # Créer un layout horizontal pour chaque ligne de commande
            command_row_layout = QHBoxLayout()
            command_row_layout.setSpacing(10)
            
            # Créer un label pour le numéro
            number_label = QLabel(f"{i}.")
            number_label.setStyleSheet("font-size: 12px; color: #a0a0a0; font-weight: bold;")
            number_label.setFixedWidth(25)
            number_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
            command_row_layout.addWidget(number_label)
            
            # Utiliser la factory pour créer le widget de commande en mode simple
            command_widget = self._command_widget_factory(command, self, simple_mode=True)
            self.command_components.append(command_widget)
            command_row_layout.addWidget(command_widget, 1)  # stretch factor de 1 pour prendre tout l'espace
            
            # Ajouter le layout horizontal au layout vertical principal
            self.commands_layout.addLayout(command_row_layout)
        
        # Ajouter un spacer à la fin
        self.commands_layout.addStretch()

    def _clear_form(self):
        """
        Efface tous les CommandComponent du formulaire.
        """
        # Nettoyer les arguments de chaque CommandComponent avant de les supprimer
        for command_widget in self.command_components:
            if hasattr(command_widget, 'remove_all_arguments'):
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
        
        # Vider la liste des composants
        self.command_components.clear()
    
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
            if hasattr(command_widget, 'get_argument_values'):
                command_values = command_widget.get_argument_values()
                values.update(command_values)
        
        return values
