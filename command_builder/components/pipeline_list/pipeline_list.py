"""
Module contenant la classe PipelineList qui représente la liste des pipelines disponibles.
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Signal, Qt
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
        self.selected_pipeline = None
        self.pipeline_frames = {}  # Pour stocker les références aux frames de pipeline
        self.task_containers = {}  # Pour stocker les références aux conteneurs de tâches
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
        """Ajoute un widget pour un pipeline avec ses tâches."""
        # Créer un frame pour contenir le pipeline et ses tâches
        pipeline_frame = QFrame(self)
        pipeline_frame.setObjectName(f"frame_{pipeline.name}")
        pipeline_frame.setFrameShape(QFrame.NoFrame)
        pipeline_frame.setFrameShadow(QFrame.Plain)

        # Stocker la référence au frame
        self.pipeline_frames[pipeline.name] = pipeline_frame

        # Layout vertical pour le pipeline et ses tâches
        pipeline_layout = QVBoxLayout(pipeline_frame)
        pipeline_layout.setSpacing(0)
        pipeline_layout.setContentsMargins(0, 0, 0, 0)

        # Créer un séparateur pour mieux organiser visuellement
        if (
            self.pipeline_items_layout.count() > 1
        ):  # Si ce n'est pas le premier pipeline
            separator = QWidget(pipeline_frame)
            separator.setFixedHeight(1)
            separator.setStyleSheet("background-color: #3a3f55;")
            pipeline_layout.addWidget(separator)

        # Créer un widget pour l'en-tête du pipeline (cliquable)
        header_widget = QWidget(pipeline_frame)
        header_widget.setCursor(Qt.PointingHandCursor)
        header_widget.setObjectName(f"header_{pipeline.name}")
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Ajouter le titre du pipeline
        pipeline_label = QLabel(f"• {pipeline.name}", header_widget)
        pipeline_label.setObjectName(f"label_{pipeline.name}")
        pipeline_label.setStyleSheet("""
            font-weight: bold; 
            color: white; 
            font-size: 13px; 
            padding: 8px 5px;
        """)
        header_layout.addWidget(pipeline_label)

        # Ajouter l'en-tête au layout du pipeline
        pipeline_layout.addWidget(header_widget)

        # Créer un conteneur pour les tâches
        tasks_container = QWidget(pipeline_frame)
        tasks_container.setObjectName(f"tasks_{pipeline.name}")
        tasks_layout = QVBoxLayout(tasks_container)
        tasks_layout.setContentsMargins(0, 0, 0, 0)
        tasks_layout.setSpacing(2)

        # Stocker la référence au conteneur de tâches
        self.task_containers[pipeline.name] = tasks_container

        # Ajouter les tâches du pipeline
        for task in pipeline.tasks:
            task_name = task.get("name", "Tâche sans nom")
            task_button = QPushButton(task_name, tasks_container)
            task_button.setObjectName(f"task_{pipeline.name}_{task_name}")
            task_button.setCursor(
                Qt.PointingHandCursor
            )  # Changer le curseur pour indiquer qu'il est cliquable
            task_button.setStyleSheet("""
                background-color: #3a3f55;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 10px;
                margin-left: 20px;
                margin-bottom: 5px;
                text-align: left;
                font-size: 12px;
            """)
            task_button.clicked.connect(
                lambda checked,
                p=pipeline.name,
                t=task_name: self.command_selected.emit(p, t)
            )
            tasks_layout.addWidget(task_button)

        # Cacher les tâches par défaut
        tasks_container.setVisible(False)

        # Ajouter le conteneur de tâches au layout du pipeline
        pipeline_layout.addWidget(tasks_container)

        # Connecter l'en-tête pour afficher/masquer les tâches
        header_widget.mousePressEvent = (
            lambda event, p=pipeline.name: self._toggle_pipeline(p)
        )

        # Ajouter le frame du pipeline au layout principal
        self.pipeline_items_layout.insertWidget(
            self.pipeline_items_layout.count() - 1, pipeline_frame
        )

    def _toggle_pipeline(self, pipeline_name):
        """Affiche ou masque les tâches d'un pipeline."""
        # Si un pipeline était déjà sélectionné, masquer ses tâches
        if self.selected_pipeline and self.selected_pipeline != pipeline_name:
            if pipeline_name in self.task_containers:
                self.task_containers[self.selected_pipeline].setVisible(False)
                # Réinitialiser le style du pipeline précédemment sélectionné
                if self.selected_pipeline in self.pipeline_frames:
                    self.pipeline_frames[self.selected_pipeline].setStyleSheet("")

        # Inverser la visibilité des tâches du pipeline sélectionné
        if pipeline_name in self.task_containers:
            is_visible = self.task_containers[pipeline_name].isVisible()
            self.task_containers[pipeline_name].setVisible(not is_visible)

            # Mettre à jour le pipeline sélectionné
            if not is_visible:
                self.selected_pipeline = pipeline_name
                # Mettre en évidence le pipeline sélectionné
                if pipeline_name in self.pipeline_frames:
                    self.pipeline_frames[pipeline_name].setStyleSheet("""
                        QFrame {
                            background-color: #2a3045;
                            border-radius: 3px;
                        }
                    """)
                # Émettre le signal de sélection de pipeline
                for pipeline in self.pipelines:
                    if pipeline.name == pipeline_name:
                        self.pipeline_selected.emit(pipeline)
                        break
            else:
                self.selected_pipeline = None
                # Réinitialiser le style du pipeline
                if pipeline_name in self.pipeline_frames:
                    self.pipeline_frames[pipeline_name].setStyleSheet("")

    def clear(self):
        """Efface tous les pipelines de la liste."""
        self.pipelines = []
        self.selected_pipeline = None
        self.pipeline_frames = {}
        self.task_containers = {}
        self._update_pipeline_list()
