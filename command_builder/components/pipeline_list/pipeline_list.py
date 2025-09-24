"""
Module contenant la classe PipelineList qui représente la liste des pipelines disponibles.
"""
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QFrame, QToolButton, QSizePolicy, QHBoxLayout)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon, QFont
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
        # Effacer le contenu actuel (sauf le spacer à la fin)
        while self.pipeline_items_layout.count() > 1:
            item = self.pipeline_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Ajouter chaque pipeline
        for pipeline in self.pipelines:
            self._add_pipeline_widget(pipeline)
    
    def _add_pipeline_widget(self, pipeline):
        """Ajoute un widget pour un pipeline avec un menu déroulant pour ses tâches."""
        # Créer le widget du pipeline
        pipeline_frame = QFrame(self)
        pipeline_frame.setObjectName(f"pipeline_{pipeline.name}")
        pipeline_frame.setFrameShape(QFrame.StyledPanel)
        pipeline_frame.setFrameShadow(QFrame.Raised)
        
        # Layout vertical pour le pipeline et ses tâches
        pipeline_layout = QVBoxLayout(pipeline_frame)
        pipeline_layout.setSpacing(2)
        pipeline_layout.setContentsMargins(5, 5, 5, 5)
        
        # Layout horizontal pour l'en-tête du pipeline (titre + bouton déroulant)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)
        
        # Label pour le nom du pipeline
        pipeline_label = QLabel(pipeline.name, pipeline_frame)
        pipeline_label.setObjectName(f"label_{pipeline.name}")
        font = QFont()
        font.setBold(True)
        pipeline_label.setFont(font)
        
        # Bouton déroulant
        toggle_button = QToolButton(pipeline_frame)
        toggle_button.setObjectName(f"toggle_{pipeline.name}")
        toggle_button.setText("+")
        toggle_button.setCheckable(True)
        toggle_button.setFixedSize(QSize(24, 24))
        
        # Ajouter les widgets à l'en-tête
        header_layout.addWidget(pipeline_label)
        header_layout.addStretch()
        header_layout.addWidget(toggle_button)
        
        # Ajouter l'en-tête au layout du pipeline
        pipeline_layout.addLayout(header_layout)
        
        # Créer un widget pour contenir les tâches
        tasks_container = QWidget(pipeline_frame)
        tasks_container.setObjectName(f"tasks_{pipeline.name}")
        tasks_layout = QVBoxLayout(tasks_container)
        tasks_layout.setSpacing(2)
        tasks_layout.setContentsMargins(15, 0, 5, 5)  # Indentation à gauche
        
        # Ajouter les tâches
        for task in pipeline.tasks:
            task_button = QPushButton(task.get('name', 'Tâche sans nom'), tasks_container)
            task_button.setObjectName(f"task_{pipeline.name}_{task.get('name', '')}")
            task_button.clicked.connect(
                lambda checked, p=pipeline.name, t=task.get('name', ''): 
                self.command_selected.emit(p, t)
            )
            tasks_layout.addWidget(task_button)
        
        # Cacher les tâches par défaut
        tasks_container.setVisible(False)
        
        # Ajouter le conteneur de tâches au layout du pipeline
        pipeline_layout.addWidget(tasks_container)
        
        # Connecter le bouton déroulant
        toggle_button.clicked.connect(
            lambda checked: self._toggle_tasks(tasks_container, toggle_button)
        )
        
        # Ajouter le widget du pipeline au layout principal
        self.pipeline_items_layout.insertWidget(self.pipeline_items_layout.count() - 1, pipeline_frame)
    
    def _toggle_tasks(self, tasks_container, toggle_button):
        """Affiche ou cache les tâches d'un pipeline."""
        is_visible = tasks_container.isVisible()
        tasks_container.setVisible(not is_visible)
        toggle_button.setText("-" if not is_visible else "+")
        
    def clear(self):
        """Efface tous les pipelines de la liste."""
        self.pipelines = []
        self._update_pipeline_list()
