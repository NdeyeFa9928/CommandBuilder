"""
Module contenant la classe TaskComponent qui représente un composant de tâche individuel.
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QToolTip, QApplication
from PySide6.QtCore import Signal, Qt, QEvent, QPoint
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
        # Install event filter for reactive tooltip display
        if self.info_button:
            self.info_button.installEventFilter(self)

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
        self.info_button = ui.findChild(QPushButton, "infoButton")

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
            
            # Créer un layout horizontal à l'intérieur du bouton
            button_layout = QHBoxLayout(self.task_button)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(0)
            button_layout.addStretch()  # Pousse l'icône vers la droite
        
        if self.info_button:
            self.info_button.setCursor(Qt.PointingHandCursor)
            # Appliquer un style global personnalisé pour les tooltips
            app = QApplication.instance()
            if app is not None:
                app.setStyleSheet("QToolTip { background-color: #2e2e2e; color: #ffffff; border: 1px solid #7aa2f7; padding: 5px; border-radius: 5px; }")
            # Créer un tooltip riche avec la description de la tâche et des commandes
            tooltip = self._build_tooltip()
            self.info_button.setToolTip(tooltip)
            # Empêcher le bouton info de déclencher la sélection de la tâche
            self.info_button.clicked.connect(lambda: None)
            
            # Reparenter l'icône pour qu'elle soit à l'intérieur du bouton
            if self.task_button:
                self.info_button.setParent(self.task_button)
                button_layout = self.task_button.layout()
                if button_layout:
                    button_layout.addWidget(self.info_button)

    # --------------------------
    # Tooltip helpers
    # --------------------------
    def _show_tooltip(self):
        """Show tooltip immediately next to the info button."""
        if not self.info_button:
            return
        # Offset to avoid cursor hiding the first characters
        global_pos = self.info_button.mapToGlobal(QPoint(self.info_button.width() // 2, self.info_button.height()))
        QToolTip.showText(global_pos, self.info_button.toolTip(), self.info_button)

    def eventFilter(self, source, event):
        """React instantly on hover or click events to display tooltip."""
        if source == self.info_button:
            if event.type() in (QEvent.Enter, QEvent.MouseButtonPress):
                self._show_tooltip()
        return super().eventFilter(source, event)

    def _build_tooltip(self) -> str:
        """
        Construit un tooltip HTML formaté avec la description de la tâche et des commandes.
        
        Returns:
            Le texte HTML du tooltip
        """
        # Commencer avec la description de la tâche
        # Style tooltip via inline CSS to ensure theme consistency
        tooltip_parts = [
            "<div style='background-color: #333; color: #dcdcdc; padding: 5px; border-radius: 5px;'>",
            f"<p style='margin: 0 0 10px 0; font-weight: bold; font-size: 13px;'>{self.task.name}</p>",
            f"<p style='margin: 0 0 10px 0; color: #cccccc;'>{self.task.description}</p>",
        ]
        
        # Ajouter les commandes
        if self.task.commands:
            tooltip_parts.append("<p style='margin: 10px 0 5px 0; font-weight: bold;'>Commandes :</p>")
            tooltip_parts.append("<ul style='margin: 0; padding-left: 20px;'>")
            
            for cmd in self.task.commands:
                tooltip_parts.append(
                    f"<li style='margin: 3px 0;'>"
                    f"<span style='font-weight: bold;'>{cmd.name}</span> : "
                    f"<span style='color: #aaaaaa;'>{cmd.description}</span>"
                    f"</li>"
                )
            
            tooltip_parts.append("</ul>")
        
        tooltip_parts.append("</div>")
        
        return "".join(tooltip_parts)
    
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
