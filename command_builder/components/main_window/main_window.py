"""
Module contenant la classe MainWindow qui représente la fenêtre principale de l'application.
"""
import os
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtUiTools import QUiLoader

from command_builder.components.pipeline_list import PipelineList
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
        self.setCentralWidget(ui.centralWidget())
        self.setMenuBar(ui.menuBar())
        self.setStatusBar(ui.statusBar())

        # Stocker les références aux conteneurs
        self.pipeline_list_container = self.findChild(QWidget, "pipelineListContainer")
        self.command_form_container = self.findChild(QWidget, "commandFormContainer")
        self.console_output_container = self.findChild(QWidget, "consoleOutputContainer")

    def _setup_components(self):
        """Configure les composants de l'interface."""
        # Créer et configurer le composant PipelineList
        self.pipeline_list = PipelineList()
        if self.pipeline_list_container:
            # Trouver le layout existant
            layout = self.pipeline_list_container.layout()
            if layout:
                # Ajouter le composant au layout existant
                layout.addWidget(self.pipeline_list)
            else:
                # Créer un nouveau layout si nécessaire
                layout = QVBoxLayout(self.pipeline_list_container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(self.pipeline_list)
        
        # Créer et configurer le composant CommandForm
        self.command_form = CommandForm()
        if self.command_form_container:
            layout = QVBoxLayout(self.command_form_container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.command_form)
        
        # Créer et configurer le composant ConsoleOutput
        self.console_output = ConsoleOutput()
        if self.console_output_container:
            layout = QVBoxLayout(self.console_output_container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.console_output)

    def _load_stylesheet(self):
        """Charge la feuille de style QSS."""
        current_dir = Path(__file__).parent
        qss_file = current_dir / "main_window.qss"
        
        if qss_file.exists():
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())

    def _connect_signals(self):
        """Connecte les signaux aux slots."""
        if self.pipeline_list:
            # Connecter le signal de sélection de commande à l'affichage du formulaire
            self.pipeline_list.command_selected.connect(self._on_command_selected)
    
    def _on_command_selected(self, pipeline_name, command_name):
        """Gère la sélection d'une commande dans la liste des pipelines."""
        pass

    
    def set_pipelines(self, pipelines):
        """Définit les pipelines à afficher dans l'interface."""
        if self.pipeline_list:
            self.pipeline_list.set_pipelines(pipelines)
