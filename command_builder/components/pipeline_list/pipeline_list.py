"""
Module contenant la classe PipelineList qui représente la liste des pipelines disponibles.
"""
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader

from command_builder.models.pipeline import Pipeline


class PipelineList(QWidget):
    """
    Classe représentant le composant de liste des pipelines.
    Ce composant affiche la liste des pipelines disponibles et permet de les sélectionner.
    """
    
    # Signal émis lorsqu'un pipeline est sélectionné
    pipeline_selected = Signal(Pipeline)
    # Signal émis lorsqu'une commande est sélectionnée
    command_selected = Signal(str, str)  # (pipeline_name, command_name)

    def __init__(self, parent=None):
        """
        Initialise le composant PipelineList.

        Args:
            parent: Le widget parent (par défaut: None)
        """
        super().__init__(parent)
        self.pipelines = []
        self._load_ui()
        self._load_stylesheet()
        self._connect_signals()

    def _load_ui(self):
        """Charge le fichier UI du composant."""
        current_dir = Path(__file__).parent
        ui_file = current_dir / "pipeline_list.ui"
        
        loader = QUiLoader()
        ui = loader.load(str(ui_file), self)
        
        # Configurer le layout pour inclure l'UI chargée
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui)
        self.setLayout(layout)
        
        # Stocker les références aux widgets importants
        self.pipeline_items_container = ui.findChild(QWidget, "pipelineItemsContainer")
        self.pipeline_items_layout = ui.findChild(QVBoxLayout, "pipelineItemsLayout")

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "pipeline_list.qss"
        
        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _connect_signals(self):
        """Connecte les signaux aux slots."""
        # À implémenter lorsque les données réelles seront disponibles
        pass
        
    def set_pipelines(self, pipelines):
        """
        Définit la liste des pipelines à afficher.
        
        Args:
            pipelines: Liste des objets Pipeline à afficher
        """
        self.pipelines = pipelines
        self._update_pipeline_list()
        
    def _update_pipeline_list(self):
        """Met à jour l'affichage de la liste des pipelines."""
        # Cette méthode sera implémentée plus tard pour afficher dynamiquement les pipelines
        pass
