"""
Module contenant la classe TaskList qui affiche les tâches disponibles.
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtUiTools import QUiLoader

from command_builder.models.task import Task


class TaskList(QWidget):
    """
    Classe représentant le composant de liste des tâches.
    Ce composant affiche la liste des tâches disponibles et permet de les sélectionner.
    """

    # Signal émis lorsqu'une tâche est sélectionnée
    task_selected = Signal(Task)
    # Signal émis lorsqu'une commande est sélectionnée
    command_selected = Signal(str, str)  # (task_name, command_name)

    def __init__(self, parent=None):
        """
        Initialise le composant TaskList.

        Args:
            parent: Le widget parent (par défaut: None)
        """
        super().__init__(parent)
        self.tasks = []
        self.selected_task = None
        self._load_ui()
        self._load_stylesheet()

    def _load_ui(self):
        """Charge le fichier UI du composant."""
        current_dir = Path(__file__).parent
        ui_file = current_dir / "task_list.ui"

        loader = QUiLoader()
        ui = loader.load(str(ui_file), self)

        # Configurer le layout pour inclure l'UI chargée
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui)
        self.setLayout(layout)

        # Stocker les références aux widgets importants
        self.task_items_container = ui.findChild(QWidget, "taskItemsContainer")
        self.task_items_layout = ui.findChild(QVBoxLayout, "taskItemsLayout")

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "task_list.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def set_tasks(self, tasks):
        """
        Définit la liste des tâches à afficher.

        Args:
            tasks: Liste des objets Task à afficher
        """
        self.tasks = tasks
        self._update_task_list()

    def _update_task_list(self):
        """Met à jour l'affichage de la liste des tâches."""
        # Effacer le contenu actuel (sauf le spacer à la fin)
        while self.task_items_layout.count() > 1:
            item = self.task_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Trier les tâches par nom
        sorted_tasks = sorted(self.tasks, key=lambda t: t.name)

        # Ajouter chaque tâche triée
        for task in sorted_tasks:
            self._add_task_widget(task)

    def _add_task_widget(self, task):
        """Ajoute un widget pour une tâche."""
        # Créer un bouton pour la tâche
        task_button = QPushButton(task.name, self)
        task_button.setObjectName(f"task_{task.name}")
        task_button.setCursor(Qt.PointingHandCursor)
        task_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3f55;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 15px;
                margin: 2px;
                text-align: left;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a5065;
            }
            QPushButton:pressed {
                background-color: #2a3045;
            }
        """)
        
        # Connecter le signal pour sélectionner la tâche
        task_button.clicked.connect(
            lambda checked, t=task.name: self.command_selected.emit("", t)
        )
        
        # Ajouter le bouton au layout
        self.task_items_layout.insertWidget(
            self.task_items_layout.count() - 1, task_button
        )

    def clear(self):
        """Efface toutes les tâches de la liste."""
        self.tasks = []
        self.selected_task = None
        self._update_task_list()
