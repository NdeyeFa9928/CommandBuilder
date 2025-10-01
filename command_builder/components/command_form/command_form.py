"""
Module contenant la classe CommandForm qui représente le formulaire de commande.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QFileDialog,
)
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader



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
        self._load_ui()
        self._load_stylesheet()
        self._connect_signals()

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
        
        self.form_layout = ui.findChild(QFormLayout, "formLayout")
        if not self.form_layout:
            # Créer un layout pour le formulaire
            self.form_layout = QFormLayout(self.form_container)
            self.form_layout.setObjectName("formLayout")
            self.form_layout.setContentsMargins(10, 10, 10, 10)
            self.form_layout.setSpacing(10)
        
        # Vérifier si les labels existent, sinon les créer
        self.label_command_title = ui.findChild(QLabel, "labelCommandTitle")
        if not self.label_command_title:
            self.label_command_title = QLabel("Sélectionnez une commande", ui)
            self.label_command_title.setObjectName("labelCommandTitle")
            self.label_command_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-bottom: 10px;")
            # Ajouter le label au layout principal
            main_layout = ui.layout()
            if main_layout:
                main_layout.insertWidget(0, self.label_command_title)
        
        self.label_command = ui.findChild(QLabel, "labelCommand")
        if not self.label_command:
            self.label_command = QLabel("Commande: ", ui)
            self.label_command.setObjectName("labelCommand")
            self.label_command.setStyleSheet("font-size: 12px; color: #a0a0a0; margin-bottom: 15px;")
            # Ajouter le label au layout principal
            main_layout = ui.layout()
            if main_layout:
                main_layout.insertWidget(1, self.label_command)

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "command_form.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _connect_signals(self):
        """Connecte les signaux aux slots."""
        # Connecter les boutons de parcours aux fonctions de sélection de fichiers
        browse_buttons = self.findChildren(QPushButton, "buttonParcourir*")
        for button in browse_buttons:
            button.clicked.connect(lambda checked, btn=button: self._browse_file(btn))

    def _browse_file(self, button):
        """
        Ouvre une boîte de dialogue pour sélectionner un fichier.

        Args:
            button: Le bouton qui a déclenché l'action
        """
        # Trouver le QLineEdit associé au bouton
        parent_layout = button.parent().layout()
        if parent_layout:
            for i in range(parent_layout.count()):
                item = parent_layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), QLineEdit):
                    line_edit = item.widget()
                    break
            else:
                return

            # Ouvrir la boîte de dialogue
            file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier")
            if file_path:
                line_edit.setText(file_path)

    def set_commands(self, commands, task_name=None):
        """
        Configure le formulaire pour afficher plusieurs commandes en texte.

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
            
        # Mettre à jour le titre avec le nom de la tâche
        if hasattr(self, 'label_command_title') and self.label_command_title:
            self.label_command_title.setText(task_name if task_name else "Commandes multiples")
        
        # Afficher toutes les commandes en texte
        command_text = ""
        for i, command in enumerate(commands, 1):
            if hasattr(command, 'name') and hasattr(command, 'command'):
                command_text += f"{i}. {command.name}: {command.command}\n"
            else:
                name = command.get('name', 'Commande sans nom') if isinstance(command, dict) else 'Commande sans nom'
                cmd = command.get('command', '') if isinstance(command, dict) else ''
                command_text += f"{i}. {name}: {cmd}\n"
        
        # Mettre à jour le label de commande avec toutes les commandes
        if hasattr(self, 'label_command') and self.label_command:
            self.label_command.setText(command_text.strip())

    def _clear_form(self):
        """
        Efface tous les champs du formulaire.
        """
        # Réinitialiser les labels
        if hasattr(self, 'label_command_title') and self.label_command_title:
            self.label_command_title.setText("Sélectionnez une commande")
        
        if hasattr(self, 'label_command') and self.label_command:
            self.label_command.setText("Commande: ")
        
        
        # Supprimer tous les champs du formulaire
        if hasattr(self, 'form_layout') and self.form_layout:
            while self.form_layout.count() > 0:
                # Récupérer le premier item
                label_item = self.form_layout.itemAt(0, QFormLayout.LabelRole)
                field_item = self.form_layout.itemAt(0, QFormLayout.FieldRole)
                
                # Supprimer les widgets
                if label_item and label_item.widget():
                    label_item.widget().deleteLater()
                
                if field_item:
                    if field_item.layout():
                        # Supprimer tous les widgets du layout
                        while field_item.layout().count() > 0:
                            widget_item = field_item.layout().takeAt(0)
                            if widget_item.widget():
                                widget_item.widget().deleteLater()
                
                # Supprimer la ligne
                self.form_layout.takeRow(0)
    
    def get_form_values(self):
        """
        Récupère les valeurs du formulaire.

        Returns:
            Un dictionnaire contenant les valeurs du formulaire
        """
        values = {}

        # Parcourir tous les QLineEdit du formulaire
        for i in range(self.form_layout.rowCount()):
            label_item = self.form_layout.itemAt(i, QFormLayout.LabelRole)
            field_item = self.form_layout.itemAt(i, QFormLayout.FieldRole)

            if label_item and field_item:
                label = label_item.widget()
                field_layout = field_item.layout()

                if label and field_layout:
                    for j in range(field_layout.count()):
                        widget = field_layout.itemAt(j).widget()
                        if isinstance(widget, QLineEdit):
                            field_name = label.text().replace("*", "").strip()
                            values[field_name] = widget.text()
                            break

        return values
