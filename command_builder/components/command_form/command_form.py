"""
Module contenant la classe CommandForm qui représente le formulaire de commande.
"""
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QFileDialog
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader

from command_builder.models.command import Command


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
        self.label_command_title = ui.findChild(QLabel, "labelCommandTitle")
        self.label_command = ui.findChild(QLabel, "labelCommand")
        self.form_container = ui.findChild(QWidget, "formContainer")
        self.form_layout = ui.findChild(QFormLayout, "formLayout")

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
            command: L'objet Command à configurer
        """
        self.current_command = command
        if command:
            self.label_command_title.setText(f"{command.name}")
            self.label_command.setText(f"Commande: {command.command}")
            self._build_form(command)
        
    def _build_form(self, command):
        """
        Construit le formulaire en fonction des arguments de la commande.
        
        Args:
            command: L'objet Command dont les arguments doivent être affichés
        """
        # Cette méthode sera implémentée plus tard pour construire dynamiquement le formulaire
        pass
        
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
                            # Extraire le nom du champ à partir du texte du label
                            field_name = label.text().replace("*", "").strip()
                            values[field_name] = widget.text()
                            break
        
        return values
