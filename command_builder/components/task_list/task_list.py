"""
Module contenant la classe TaskList qui affiche les tâches disponibles.
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader

from command_builder.models.task import Task
from command_builder.components.task_component import TaskComponent


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
        # Créer un TaskComponent pour la tâche
        task_component = TaskComponent(task, self)
        
        # Connecter le signal pour sélectionner la tâche
        task_component.task_clicked.connect(
            lambda t: self.command_selected.emit("", t.name)
        )
        
        # Ajouter le composant au layout
        self.task_items_layout.insertWidget(
            self.task_items_layout.count() - 1, task_component
        )

    def clear(self):
        """Efface toutes les tâches de la liste."""
        self.tasks = []
        self.selected_task = None
        self._update_task_list()
