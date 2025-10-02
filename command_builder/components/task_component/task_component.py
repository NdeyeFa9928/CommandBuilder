"""
Module contenant la classe TaskComponent qui représente un composant de tâche individuel.
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtUiTools import QUiLoader

from command_builder.models.task import Task


class TaskComponent(QWidget):
    """
    Composant représentant une tâche individuelle.
    Affiche le nom de la tâche sous forme de bouton cliquable.
    """

    # Signal émis lorsque la tâche est cliquée
    task_clicked = Signal(Task)

    def __init__(self, task: Task, parent=None):
        """
        Initialise le composant TaskComponent.

        Args:
            task: L'objet Task à afficher
            parent: Le widget parent (par défaut: None)
        """
        super().__init__(parent)
        self.task = task
        self._load_ui()
        self._load_stylesheet()
        self._setup_ui()

    def _load_ui(self):
        """Charge le fichier UI du composant."""
        current_dir = Path(__file__).parent
        ui_file = current_dir / "task_component.ui"

        loader = QUiLoader()
        ui = loader.load(str(ui_file), self)

        # Configurer le layout pour inclure l'UI chargée
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui)
        self.setLayout(layout)

        # Stocker les références aux widgets importants
        self.task_button = ui.findChild(QPushButton, "taskButton")

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "task_component.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _setup_ui(self):
        """Configure l'interface utilisateur avec les données de la tâche."""
        if self.task_button:
            self.task_button.setText(self.task.name)
            self.task_button.setObjectName(f"task_{self.task.name}")
            self.task_button.setCursor(Qt.PointingHandCursor)
            self.task_button.clicked.connect(self._on_clicked)

    def _on_clicked(self):
        """Gère le clic sur le bouton de tâche."""
        self.task_clicked.emit(self.task)

    def get_task(self) -> Task:
        """
        Retourne l'objet Task associé à ce composant.

        Returns:
            L'objet Task
        """
        return self.task
