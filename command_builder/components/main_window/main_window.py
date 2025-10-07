"""
Module contenant la classe MainWindow qui représente la fenêtre principale de l'application.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSplitter,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtUiTools import QUiLoader
from command_builder.components.task_list import TaskList
from command_builder.components.command_form import CommandForm
from command_builder.components.console_output import ConsoleOutput


class MainWindow(QMainWindow):
    """
    Classe représentant la fenêtre principale de l'application CommandBuilder.
    Cette fenêtre contient tous les composants principaux de l'interface.
    """

    def __init__(self, parent=None):
        """
        Initialise la fenêtre principale.

        Args:
            parent: Le widget parent (par défaut: None)
        """
        super().__init__(parent)
        self._load_ui()
        self._setup_components()
        self._load_stylesheet()
        self._connect_signals()

    def _load_ui(self):
        """Charge le fichier UI de la fenêtre principale."""
        current_dir = Path(__file__).parent
        ui_file = current_dir / "main_window.ui"

        loader = QUiLoader()
        ui = loader.load(str(ui_file))

        # Copier les propriétés de l'UI chargée vers cette instance
        self.setWindowTitle(ui.windowTitle())
        self.resize(ui.size())

        # Récupérer le widget central et son layout
        central_widget = ui.centralWidget()
        central_layout = central_widget.layout()

        # Créer un nouveau widget central qui contiendra nos splitters
        new_central_widget = QWidget()
        self.setCentralWidget(new_central_widget)

        # Créer le layout principal
        main_layout = QHBoxLayout(new_central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Créer le splitter horizontal principal
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setHandleWidth(2)

        # Créer le splitter vertical pour le côté droit
        self.right_splitter = QSplitter(Qt.Vertical)
        self.right_splitter.setHandleWidth(2)

        # Récupérer les conteneurs depuis l'UI chargée
        self.task_list_container = ui.findChild(QWidget, "taskListContainer")
        command_form_container = ui.findChild(QWidget, "commandFormContainer")
        console_output_container = ui.findChild(QWidget, "consoleOutputContainer")

        # Configurer les conteneurs
        self.task_list_container.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        command_form_container.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        console_output_container.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        # Ajouter les conteneurs aux splitters
        self.main_splitter.addWidget(self.task_list_container)
        self.right_splitter.addWidget(command_form_container)
        self.right_splitter.addWidget(console_output_container)

        # Configurer les tailles initiales
        self.right_splitter.setStretchFactor(0, 2)  # CommandForm plus grand
        self.right_splitter.setStretchFactor(1, 1)  # Console plus petit

        # Ajouter le splitter droit au splitter principal
        self.main_splitter.addWidget(self.right_splitter)

        # Configurer les tailles du splitter principal
        self.main_splitter.setStretchFactor(0, 1)  # TaskList
        self.main_splitter.setStretchFactor(
            1, 3
        )  # Zone de droite (CommandForm + Console)

        # Ajouter le splitter principal au layout
        main_layout.addWidget(self.main_splitter)

        # Configurer la fenêtre
        self.setMenuBar(ui.menuBar())
        self.setStatusBar(ui.statusBar())

        # Stocker les références aux conteneurs pour une utilisation ultérieure
        self.command_form_container = command_form_container
        self.console_output_container = console_output_container

    def _setup_components(self):
        """Configure les composants de l'interface."""
        # Créer et configurer le composant TaskList
        self.task_list = TaskList()
        if self.task_list_container:
            # Trouver le layout existant
            layout = self.task_list_container.layout()
            if layout:
                # Ajouter le composant au layout existant
                layout.addWidget(self.task_list)
            else:
                # Créer un nouveau layout si nécessaire
                layout = QVBoxLayout(self.task_list_container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(self.task_list)

        # Créer et configurer le composant CommandForm
        self.command_form = CommandForm()
        if self.command_form_container:
            layout = QVBoxLayout(self.command_form_container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(self.command_form)

        # Créer et configurer le composant ConsoleOutput
        self.console_output = ConsoleOutput()
        if self.console_output_container:
            layout = QVBoxLayout(self.console_output_container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(self.console_output)

        # Définir les tailles initiales des panneaux
        self._restore_splitter_sizes()

    def _restore_splitter_sizes(self):
        """Définit les tailles initiales des splitters."""
        # Définir des tailles par défaut si nécessaire
        if hasattr(self, "main_splitter") and hasattr(self, "right_splitter"):
            # Ajuster les tailles après que la fenêtre soit affichée
            from PySide6.QtCore import QTimer

            QTimer.singleShot(0, self._adjust_splitter_sizes)

    def _adjust_splitter_sizes(self):
        """Ajuste les tailles des splitters après l'affichage initial."""
        if hasattr(self, "main_splitter") and hasattr(self, "right_splitter"):
            # Calculer les tailles proportionnelles
            total_width = self.width()
            left_width = int(total_width * 0.25)  # 25% pour la liste des tâches
            right_width = total_width - left_width

            # Définir les tailles du splitter principal
            self.main_splitter.setSizes([left_width, right_width])

            # Définir les tailles du splitter droit (70% formulaire, 30% console)
            right_height = self.right_splitter.height()
            form_height = int(right_height * 0.7)
            console_height = right_height - form_height
            self.right_splitter.setSizes([form_height, console_height])

    def resizeEvent(self, event):
        """Surcharge de la méthode de redimensionnement pour ajuster les splitters."""
        super().resizeEvent(event)
        self._adjust_splitter_sizes()

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "main_window.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _connect_signals(self):
        """Connecte les signaux aux slots."""
        if self.task_list:
            # Connecter le signal de sélection de commande à l'affichage du formulaire
            self.task_list.command_selected.connect(self._on_command_selected)

    def _on_command_selected(self, _unused, task_name):
        """Gère la sélection d'une tâche dans la liste."""
        if task := next((t for t in self.task_list.tasks if t.name == task_name), None):
            if task.commands and self.command_form:
                self.command_form.set_commands(task.commands, task.name)

    def set_tasks(self, tasks):
        """Définit les tâches à afficher dans l'interface."""
        if self.task_list:
            self.task_list.set_tasks(tasks)
