"""
Module contenant la classe CommandForm qui représente le formulaire de commande.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader

from command_builder.components.command_component import CommandComponent



class CommandForm(QWidget):
    """
    Classe représentant le composant de formulaire de commande.
    Ce composant permet de configurer les paramètres d'une commande.
    """

    # Signal émis lorsque le formulaire est complété
    form_completed = Signal(dict)  # Dictionnaire des valeurs du formulaire

    def __init__(self, parent=None):
        """
        Initialise le composant CommandForm.

        Args:
            parent: Le widget parent (par défaut: None)
        """
        super().__init__(parent)
        self.current_command = None
        self.current_commands = []  # Liste des commandes multiples
        self.command_components = []  # Liste des CommandComponent
        self._load_ui()
        self._load_stylesheet()

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

        # Stocker les références aux widgets importants
        self.form_container = ui.findChild(QWidget, "formContainer")
        if not self.form_container:
            # Créer un conteneur pour le formulaire
            self.form_container = QWidget(ui)
            self.form_container.setObjectName("formContainer")
            # Ajouter le conteneur au layout principal
            main_layout = ui.layout()
            if main_layout:
                main_layout.addWidget(self.form_container)
        
        # Créer un layout vertical pour les CommandComponent
        self.commands_layout = QVBoxLayout(self.form_container)
        self.commands_layout.setContentsMargins(10, 10, 10, 10)
        self.commands_layout.setSpacing(5)

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
        
        # Ajouter un label de titre si nécessaire
        if task_name:
            title_label = QLabel(task_name)
            title_label.setObjectName("labelTaskTitle")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-bottom: 10px;")
            self.commands_layout.addWidget(title_label)
        
        # Créer un CommandComponent en mode simple pour chaque commande
        for i, command in enumerate(commands, 1):
            # Créer un label pour le numéro
            number_label = QLabel(f"{i}.")
            number_label.setStyleSheet("font-size: 12px; color: #a0a0a0;")
            self.commands_layout.addWidget(number_label)
            
            # Créer le CommandComponent en mode simple
            command_component = CommandComponent(command, self, simple_mode=True)
            self.command_components.append(command_component)
            self.commands_layout.addWidget(command_component)
        
        # Ajouter un spacer à la fin
        self.commands_layout.addStretch()

    def _clear_form(self):
        """
        Efface tous les CommandComponent du formulaire.
        """
        # Supprimer tous les widgets du layout
        while self.commands_layout.count() > 0:
            item = self.commands_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                # Supprimer le spacer
                pass
        
        # Vider la liste des composants
        self.command_components.clear()
    
    def get_form_values(self):
        """
        Récupère les valeurs de tous les arguments de toutes les commandes.

        Returns:
            Un dictionnaire contenant les valeurs de tous les arguments
        """
        values = {}
        
        # Parcourir tous les CommandComponent
        for command_component in self.command_components:
            # Récupérer les valeurs des arguments de chaque commande
            command_values = command_component.get_argument_values()
            values.update(command_values)
        
        return values
