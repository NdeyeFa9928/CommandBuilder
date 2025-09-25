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

    def set_command(self, command):
        """
        Définit la commande à configurer.

        Args:
            command: L'objet Command ou un dictionnaire contenant les informations de la commande
        """
        self.current_command = command
        if command:
            # Vérifier si command est un dictionnaire ou un objet
            if isinstance(command, dict):
                name = command.get('name', '')
                cmd = command.get('command', '')
            else:
                # Supposer que c'est un objet avec des attributs
                name = getattr(command, 'name', '')
                cmd = getattr(command, 'command', '')
                
            # Mettre à jour l'interface
            self.label_command_title.setText(name)
            self.label_command.setText(f"Commande: {cmd}")
            self._build_form(command)

    def _build_form(self, command):
        """
        Construit le formulaire en fonction des arguments de la commande.

        Args:
            command: L'objet Command ou un dictionnaire contenant les informations de la commande
        """
        # Effacer le formulaire existant
        while self.form_layout.rowCount() > 0:
            # Supprimer la première ligne (index 0)
            self.form_layout.removeRow(0)
            
        # Obtenir les arguments de la commande
        if isinstance(command, dict):
            arguments = command.get('arguments', [])
        else:
            # Supposer que c'est un objet avec un attribut arguments
            arguments = getattr(command, 'arguments', [])
            
        # Ajouter les champs pour chaque argument
        for arg in arguments:
            # Extraire les informations de l'argument
            if isinstance(arg, dict):
                arg_code = arg.get('code', '')
                arg_name = arg.get('name', arg_code)
                arg_desc = arg.get('description', '')
                arg_required = arg.get('required', False)
            else:
                # Supposer que c'est un objet avec des attributs
                arg_code = getattr(arg, 'code', '')
                arg_name = getattr(arg, 'name', arg_code)
                arg_desc = getattr(arg, 'description', '')
                arg_required = getattr(arg, 'required', False)
                
            # Créer le label avec un astérisque pour les champs requis
            label_text = f"{arg_name}{'*' if arg_required else ''}"
            label = QLabel(label_text)
            label.setToolTip(arg_desc)
            
            # Créer un layout horizontal pour le champ et le bouton de parcours
            field_layout = QVBoxLayout()
            
            # Créer le champ de saisie
            line_edit = QLineEdit()
            line_edit.setObjectName(f"input_{arg_code}")
            line_edit.setPlaceholderText(arg_desc)
            field_layout.addWidget(line_edit)
            
            # Ajouter le champ au formulaire
            self.form_layout.addRow(label, field_layout)

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
