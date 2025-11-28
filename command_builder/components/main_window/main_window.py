"""
Module contenant la classe MainWindow qui représente la fenêtre principale de l'application.
"""

from pathlib import Path
from typing import List

from PySide6.QtCore import Qt, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from command_builder.components.command_form import CommandForm
from command_builder.components.console_output import ConsoleOutput
from command_builder.components.error_display.error_display import ErrorsPanel
from command_builder.components.help_button import HelpButton
from command_builder.components.help_window import HelpWindow
from command_builder.components.task_list import TaskList
from command_builder.models.yaml_error import YamlError


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
        self.main_splitter.setHandleWidth(3)

        # Créer le splitter vertical pour le côté droit
        self.right_splitter = QSplitter(Qt.Vertical)
        self.right_splitter.setHandleWidth(3)

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

        # Récupérer et configurer la barre de statut
        status_bar = ui.statusBar()
        self.setStatusBar(status_bar)

        # Stocker les références aux conteneurs pour une utilisation ultérieure
        self.command_form_container = command_form_container
        self.console_output_container = console_output_container

    def _setup_components(self):
        """Configure les composants de l'interface."""
        # Créer et configurer le bouton Help dans la barre de statut
        self.help_button = HelpButton()
        status_bar = self.statusBar()
        if status_bar:
            # Ajouter le bouton à droite de la barre de statut
            status_bar.addPermanentWidget(self.help_button)

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
            # Réduire la hauteur minimale pour permettre à la console de monter davantage
            self.command_form_container.setMinimumSize(0, 0)
            self.command_form.setMinimumSize(0, 0)
            self.command_form_container.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Minimum
            )
            self.command_form.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

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
            QTimer.singleShot(0, self._adjust_splitter_sizes)

    def _adjust_splitter_sizes(self):
        """Ajuste les tailles des splitters après l'affichage initial."""
        if hasattr(self, "main_splitter") and hasattr(self, "right_splitter"):
            # Calculer les tailles proportionnelles
            total_width = self.width()
            left_width = int(total_width * 0.3)  # 30% pour la liste des tâches
            right_width = total_width - left_width

            # Définir les tailles du splitter principal
            self.main_splitter.setSizes([left_width, right_width])

            # Définir les tailles du splitter droit (70% formulaire, 30% console)
            right_height = self.right_splitter.height()
            form_height = int(right_height * 0.7)
            console_height = right_height - form_height
            self.right_splitter.setSizes([form_height, console_height])

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "main_window.qss"

        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _connect_signals(self):
        """Connecte les signaux aux slots."""
        if self.help_button:
            # Connecter le bouton Help pour ouvrir la fenêtre d'aide
            self.help_button.help_clicked.connect(self._show_help_window)

        if self.task_list:
            # Connecter le signal de sélection de commande à l'affichage du formulaire
            self.task_list.command_selected.connect(self._on_command_selected)

        if self.command_form and self.console_output:
            # Connecter directement le formulaire à la console pour l'exécution
            self.command_form.commands_to_execute.connect(
                self.console_output.execute_commands
            )
            # Connecter le bouton Exécuter de la console au formulaire
            self.console_output.execute_requested.connect(
                self.command_form._on_execute_clicked
            )
            # Activer le bouton Exécuter quand une tâche est chargée
            self.command_form.task_loaded.connect(
                lambda: self.console_output.set_execute_enabled(True)
            )

    def _show_help_window(self):
        """Affiche la fenêtre d'aide YAML."""
        help_window = HelpWindow(self)
        help_window.exec()

    def _on_command_selected(self, _unused, task_name):
        """Gère la sélection d'une tâche dans la liste."""
        if task := next((t for t in self.task_list.tasks if t.name == task_name), None):
            if task.commands and self.command_form:
                # Utiliser set_task pour supporter les arguments partagés
                self.command_form.set_task(task)

    def set_tasks(self, tasks):
        """Définit les tâches à afficher dans l'interface."""
        if self.task_list:
            self.task_list.set_tasks(tasks)

    def show_yaml_errors(self, errors: List[YamlError]):
        """
        Affiche les erreurs YAML dans une dialog.

        Args:
            errors: Liste des erreurs YamlError à afficher
        """
        if not errors:
            return

        # Créer une dialog pour afficher les erreurs
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle(f"⚠️ Erreurs YAML détectées ({len(errors)})")
        error_dialog.setGeometry(100, 100, 700, 500)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Ajouter le panel d'erreurs
        errors_panel = ErrorsPanel(errors)
        layout.addWidget(errors_panel)

        error_dialog.setLayout(layout)
        error_dialog.exec()
